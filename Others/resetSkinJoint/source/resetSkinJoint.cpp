// --------------------------------------------------------------------------
// resetSkinJoint.cpp - C++ File
// --------------------------------------------------------------------------
// Copyright ?2004 Michael B. Comet 
// --------------------------------------------------------------------------
//
// DESCRIPTION:
//	Code for resetSkinJoint cmd.
//
// AUTHORS:
//		Michael B. Comet - comet@comet-cartoons.com
//
// VERSIONS:
//		1.00 - 07/23/04 - comet - Initial Rev.
//		1.01 - 03/09/05 - comet - Now has -skincl command for reseting only specified skinCluster
//
// --------------------------------------------------------------------------
//
//  resetSkinJoint - Skin Reset Maya Plugin by Michael B. Comet
//  Copyright ?2004,2005 Michael B. Comet
//
//   This program is free software; you can redistribute it and/or modify
//   it under the terms of the GNU General Public License as published by
//   the Free Software Foundation; either version 2 of the License, or
//   (at your option) any later version.
//
//   This program is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU General Public License for more details.
//
//   You should have received a copy of the GNU General Public License
//   along with this program; if not, write to the Free Software
//   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//   For information on poseDeformer contact:
//			Michael B. Comet - comet@comet-cartoons.com
//			or visit http://www.comet-cartooons.com/toons/
//
// --------------------------------------------------------------------------

/*
 * Includes
 */
#include <maya/MGlobal.h>

#include "resetSkinJoint.h"

// --------------------------------------------------------------------------

// --------------------------------------------------------------------------
// resetData class procs
// --------------------------------------------------------------------------

// --------------------------------------------------------------------------

/*
 * resetData::resetData() - Constructor
 */
resetData::resetData()
{
	next = NULL ;
}

// --------------------------------------------------------------------------

// --------------------------------------------------------------------------
//	Main cmd procs
// --------------------------------------------------------------------------

// --------------------------------------------------------------------------

/*
 * resetSkinJoint::creator() - Alloc new cmd
 */
void* resetSkinJoint::creator()
{
	return new resetSkinJoint();
}

// --------------------------------------------------------------------------

/*
 * resetSkinJoint::resetSkinJoint() - Constructor
 */
resetSkinJoint::resetSkinJoint()
{
	ptrResetData = NULL ;
}

// --------------------------------------------------------------------------

/*
 * resetSkinJoint::~resetSkinJoint() - Destructor
 */
resetSkinJoint::~resetSkinJoint()
{
	freeData() ;	// cleanup any alloced ram

}

// --------------------------------------------------------------------------

/*
 * resetSkinJoint::isUndoable() - Set true if is undoable cmd
 */
bool resetSkinJoint::isUndoable() const
{
	return true;
}

// --------------------------------------------------------------------------

// --------------------------------------------------------------------------
//	Worker Cmd Procs
// --------------------------------------------------------------------------

// ---------------------------------------------------------------------------

/*
 * resetSkinJoint::newSyntax() - Make up rules
 */
MSyntax resetSkinJoint::newSyntax()
{
	MSyntax syntax ;

	syntax.addFlag(kHelpFlag, kHelpFlagLong ) ;
	syntax.addFlag(kSkinClusterFlag, kSkinClusterFlagLong, MSyntax::kString ) ;

	
	syntax.useSelectionAsDefault(true);						// allow selection to be used
	syntax.setObjectType(MSyntax::kSelectionList, 1);		// Want at least 1 object...aka joint.

	return syntax;
}

// ---------------------------------------------------------------------------

/*
 * resetSkinJoint::parseArgs() - Parse arguments
 */
MStatus resetSkinJoint::parseArgs(const MArgList &argList)
{
    MStatus stat ;

	MArgDatabase argData(syntax(), argList, &stat);
	
	// Init Internal Vars here.
	//
	strSkinCl = MString("") ;


	// And parse...


	// -help
    if (argData.isFlagSet(kHelpFlag))
		{	
		showUsage() ;
		return MS::kFailure ;
		}


	// -skincl "skinCluster1"
    if (argData.isFlagSet(kSkinClusterFlag))
		{
		argData.getFlagArgument(kSkinClusterFlag, 0, strSkinCl) ;
		
		}



	argData.getObjects( sListComp );	// Finally also get comp's at end.

	return MS::kSuccess;
}

// ---------------------------------------------------------------------------

/*
 * resetSkinJoint::showUsage() - Shows basic help
 */
void resetSkinJoint::showUsage()
{
    MString str;

	str += ("// ---------------------------------------\n") ;
	str += ("// resetSkinJoint USAGE: - Resets bind pose for skin joints.\n") ;
	str += ("// ---------------------------------------\n") ;
	str += ("//     resetSkinJoint OBJECTS ;    // Reset skin joints for following or selected joints.\n");
	str += ("//     resetSkinJoint -skinCl \"skinCluster1\" OBJECTS ;    // Reset skin joints for following or selected joints, but only for provided skinCluster.\n");
	str += ("// \n") ;
	str += ("//   FLAGS:\n") ;
	str += ("//       -h     | -help           :  Get help on this command. \n") ;
	str += ("//       -scl   | -skincl         :  Specify specific skinCluster to reset so if joints is in multiple clusters, only this one gets reset. (optional) \n") ;
	MGlobal::displayInfo( str ) ;
}

// --------------------------------------------------------------------------

/*
 * resetSkinJoint::doIt() - called first time cmd is done
 */
MStatus resetSkinJoint::doIt( const MArgList &argList)
{
	MStatus stat ;


	stat = parseArgs(argList) ;	// Parse the args!
	if (stat != MS::kSuccess)
		return stat ;

	stat = redoIt() ;	// do real work!

	return stat ;
}

// --------------------------------------------------------------------------

/*
 * resetSkinJoint::redoIt() - Main proc of really doing what is needed from
 *							stored data
 */
MStatus resetSkinJoint::redoIt()
{
	MStatus stat ;


		// DOUBLE-CHECK TO MAKE SURE THERE'S A SPECIFIED OBJECT TO EVALUATE ON:
	uJnts = sListComp.length() ;	// How many items?
	if ( uJnts == 0)
		{
		showUsage() ; 
		MGlobal::displayError("resetSkinJoint - You must select or provide one or more joints to reset.");
		return MS::kFailure;
		}

	freeData() ;		// Delete any alloced stuff from before, we'll redo all that...


	// Now go thru the selection list and for each object, if it is connected 
	// to a skin cluster, reset it...  Could test for joints, but user could have hacked
	// a non-joint item into a skinCluster also...so to be nice, we'll handle ANY object
	// transform type node plugged into a skinCluster node.
	//
	// jnt.worldMatrix[0] --> skinCluster1.matrix[#]	// .bindPreMatrix[#] has worldInverseMatrix value.
	// jnt.bindPose	--> bindPose1.worldMatrix[#]	// same as worldMatrix live
	// 
	unsigned u=0, uReset=0 ;
	for (u=0; u < uJnts; ++u)
		{
		MObject oJnt ;
		sListComp.getDependNode(u, oJnt ) ;		// Get an MObject to the u-th thing selected...

        MFnDependencyNode depJnt(oJnt, &stat) ;	// And convert to a simple dependency node.

		// Now see if we even have an attr that is useable...
		MPlug plugWorldMatrix = depJnt.findPlug( MString("worldMatrix"), &stat) ;
		if (stat == MS::kSuccess)
			{
			// Since this is really a multi, get 0th array entry...this will be ".worldMatrix[0]"
			plugWorldMatrix = plugWorldMatrix.elementByLogicalIndex(0, &stat) ;

//			cout << "DEBUG: u=" << u << " depJnt=" << depJnt.name() << " plugWorldMatrix=" << plugWorldMatrix.name() << endl ;

				// Read actual matrix data from the plug......ie: get actual value, like getAttr.
			MObject oMat ;
			plugWorldMatrix.getValue( oMat );	// For matrix plugs, have to get as MObject
			MFnMatrixData fnMat( oMat );		// Then take that to a MfnMatrix Data.    
			MMatrix matWorld = fnMat.matrix() ; // Then finally get the matrix out from that.
			MMatrix invmatWorld = matWorld.inverse() ;	// And get inverse too.
//			cout << "DEBUG:      Matrix=" << matWorld << " Inverse Matrix=" << invmatWorld << endl ;

	
			// Now see if this is connected into anything, and if so, see if the connected object
			// is a skinCluster....
			// This is the REAL reset code for the cluster...
			//
			MPlugArray plugArrOut ;
			plugWorldMatrix.connectedTo( plugArrOut, false, true, &stat) ;
			
			unsigned uOut = plugArrOut.length() ;
			unsigned v ;
			for (v=0; v < uOut; ++v)
				{
				MObject oNode = plugArrOut[v].node() ;	// What MObject node is on this other side?
				if (oNode.hasFn( MFn::kSkinClusterFilter))	// Is it a skinCluster node?
					{
					// It is!  So now we figure what index # this joint is connected to.
					unsigned uIdx = plugArrOut[v].logicalIndex( &stat ) ;
					
					// Now that we have that...we can "get" the current bindPreMatix[uIdx] value and
					//   store it for undo, and then "set" it to what is the live matrix value.

					// First get the actual .bindPreMatrix[#] plug we want...
					MFnDependencyNode depSkinCl( oNode, &stat) ;	// Get a dep node for the skin cluster
					MPlug plugBindPre = depSkinCl.findPlug( MString("bindPreMatrix"), &stat) ;
					plugBindPre = plugBindPre.elementByLogicalIndex( uIdx, &stat) ;
					
					
					// First check name of skinCluster against what user gave, in case we don't want to 
					// handle this cluster.  
					//
					if (strSkinCl != "" && strSkinCl != depSkinCl.name())
						continue ;
					

					// Now get the value
					MObject oMatPre ;
					plugBindPre.getValue( oMatPre );	// For matrix plugs, have to get as MObject
					MFnMatrixData fnMatPre( oMatPre );	// Then take that to a MfnMatrix Data.    
					MMatrix matBindPreOrig = fnMatPre.matrix() ; // Then finally get the matrix out from that.
					
					// Store for undo, alloc a new item in linked list
					resetData *ptrData = new resetData ;
					ptrData->matBindPreOrig = matBindPreOrig ;	// Store matrix
					ptrData->plugBindPre = plugBindPre ;		// Store plug
					ptrData->next = ptrResetData ;				// Point to start of old one, ie: we are adding at the head...
					ptrResetData = ptrData ;					// and keep a ptr to this new "head"

					// And now set it too.
					MFnMatrixData fnMatPreOut ;
					MObject oMatPreOut = fnMatPreOut.create( invmatWorld, &stat) ;
					plugBindPre.setValue( oMatPreOut ) ;


					// Now we'll also see if this has a .bindPose attribute...if it does we'll 
					// reset that also locally on this object, which will have the effect of also
					// reseting the "bindPose node" itself also.
					//
					MPlug plugBindPose = depJnt.findPlug( MString("bindPose"), &stat) ;
					if (stat == MS::kSuccess)
						{
						// Get local bindPose attr
						MObject oMatBind ;
						plugBindPose.getValue( oMatBind );	// For matrix plugs, have to get as MObject
						MFnMatrixData fnMatBind( oMatBind );	// Then take that to a MfnMatrix Data.    
						MMatrix matBindOrig = fnMatBind.matrix() ; // Then finally get the matrix out from that.
					
						// Store for undo
						ptrData->matBindOrig = matBindOrig ;
						ptrData->plugBindPose = plugBindPose ;

						// and set local bindPose attr
						MFnMatrixData fnMatBindOut ;
						MObject oMatBindOut = fnMatBindOut.create( matWorld, &stat) ;
						plugBindPose.setValue( oMatBindOut ) ;
						}



					MGlobal::displayInfo( MString("Reseting ")+depJnt.name()+MString(" and ")+depSkinCl.name() ) ;
					++uReset ;
					} // end of if out is a skinCluster node.

				} // end of each output connection



			}  // end of if found worldMatrix plug

		}	// end of each sel


	MString str ;
	str += ("Reset ") ;
	str += (int)(uReset) ;
	str += (" skinJoint-skinCluster combination") ;
	if (uReset > 1)
		str += ("s.");
	else
		str += (".");
	if (uReset == 0)
		appendToResult("No skin joints or items selected that are part of a skinCluster.  Nothing reset.") ;
	else
		appendToResult(str) ;

	return MS::kSuccess;
}

// --------------------------------------------------------------------------

/*
 * resetSkinJoint::undoIt() - Undoes stuff for cmd based on stored data
 */
MStatus resetSkinJoint::undoIt()
{
	MStatus stat ;

		// Free any stuff in the list
    while (ptrResetData != NULL)
		{
		
		// Set value to the orig undo state...
		//
		MFnMatrixData fnMatPreOut ;
		MObject oMatPreOut = fnMatPreOut.create( ptrResetData->matBindPreOrig, &stat) ;
		ptrResetData->plugBindPre.setValue( oMatPreOut ) ;

		MFnMatrixData fnMatBindOut ;
		MObject oMatBindOut = fnMatBindOut.create( ptrResetData->matBindOrig , &stat) ;
		ptrResetData->plugBindPose.setValue( oMatBindOut ) ;

		ptrResetData = ptrResetData->next ;	// Go to next one
		}


	return MS::kSuccess;
}

// --------------------------------------------------------------------------

/*
 * resetSkinJoint::freeData() - Free any alloced stuff in the list
 */
void resetSkinJoint::freeData(void) 
{
		// Free any stuff in the list
    while (ptrResetData != NULL)
		{
		resetData *toDel = ptrResetData ;	// keep temp copy
		ptrResetData = ptrResetData->next ;	// Go to next one
		delete [] toDel;	// and free
		}
}


// --------------------------------------------------------------------------
