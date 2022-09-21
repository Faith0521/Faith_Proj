// --------------------------------------------------------------------------
// resetSkinJoint.h - C++ Header File
// --------------------------------------------------------------------------
// Copyright ?2004 Michael B. Comet
// --------------------------------------------------------------------------
//
// DESCRIPTION:
//	Header for resetSkinJoint cmd.
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


#ifndef _resetSkinJointCmd
#define _resetSkinJointCmd

/*
 * Includes
 */
#include <maya/MPxCommand.h>
#include <maya/MArgList.h>
#include <maya/MSyntax.h>
#include <maya/MArgDatabase.h>

#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MMatrix.h>
#include <maya/MFnMatrixData.h>

#include <maya/MDagPath.h>
#include <maya/MFnDagNode.h>
#include <maya/MSelectionList.h>
#include <maya/MObjectArray.h>


// --------------------------------------------------------------------------

/*
 * resetData - Class Definiton for Helper class
 */
class resetData
{
public:
	resetData() ;			// Constructor

public:
	MPlug plugBindPre ;			// What plug are we rebinding to?
    MMatrix matBindPreOrig ;	// If so, what was the orig bindPreMat value on skinCluster?
	MPlug plugBindPose ;		// What local bindPose plug on jnt?
	MMatrix matBindOrig ;		// If so, what was orig bind matrix value on node?
	resetData *next ;			// next one in linked list
} ;

// --------------------------------------------------------------------------


/*
 * resetSkinJoint - Class Definition
 */
class resetSkinJoint : public MPxCommand
{
public:
				resetSkinJoint();
	virtual		~resetSkinJoint();

	MStatus		doIt( const MArgList& );
	MStatus		redoIt();
	MStatus		undoIt();
	bool		isUndoable() const;

	static		void* creator();
	static MSyntax newSyntax();

private:
	MStatus parseArgs(const MArgList &argList);
	void showUsage(void) ;


private:
	unsigned uJnts ;			 // How many objs/joints passed in?
	MSelectionList sListComp ;	 // What is selected/passed in obj.comp wise?
	resetData *ptrResetData ;	 // Ptr to alloc of start of linked list of data needed for undo.
	
	MString strSkinCl ;			// Name of specific skinCluster to reset if we only want to reset that one.
	

	void freeData(void) ;		 // delete any linked list

} ;

#endif

// --------------------------------------------------------------------------


/*
 * Syntax options
 */
#define kHelpFlag									"-h"
#define kHelpFlagLong								"-help"

#define kSkinClusterFlag							"-scl"
#define kSkinClusterFlagLong						"-skincl"


// ---------------------------------------------------------------------------





