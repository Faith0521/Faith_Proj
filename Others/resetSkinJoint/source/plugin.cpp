// --------------------------------------------------------------------------
// plugin.cpp - C++ File
// --------------------------------------------------------------------------
// Copyright ©2004 Michael B. Comet
// --------------------------------------------------------------------------
//
// DESCRIPTION:
//	Main loading file for resetSkinJoint command.
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
//  Copyright ©2004,2005 Michael B. Comet
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
#include <maya/MFnPlugin.h>
#include <maya/MGlobal.h>

#include "resetSkinJoint.h"

/*
 * Defines
 */
#define VERSION		"1.01"

// --------------------------------------------------------------------------


/*
 * initializePlugin() - Main load of plugin
 *
 *	Description:
 *		this method is called when the plug-in is loaded into Maya.  It 
 *		registers all of the services that this plug-in provides with 
 *		Maya.
 *
 *	Arguments:
 *		obj - a handle to the plug-in object (use MFnPlugin to access it)
 *
 */
MStatus initializePlugin( MObject obj )
{ 
	MStatus   stat ;

	MFnPlugin plugin( obj, "CometCartoons", "6.0", "Any");
	stat = plugin.registerCommand("resetSkinJoint", resetSkinJoint::creator, resetSkinJoint::newSyntax) ;
	if (!stat) 
		{
		stat.perror("registerCommand");
		return stat;
		}


	MGlobal::displayInfo(MString("resetSkinJoint ")+MString(VERSION)+MString(" - Built On: ") + MString(__DATE__) + MString(" ") + MString(__TIME__) ) ;
	MGlobal::displayInfo("resetSkinJoint Copyright ©2004,2005 Michael B. Comet") ;
	MGlobal::displayInfo("resetSkinJoint comes with ABSOLUTELY NO WARRANTY; for details read the") ;
	MGlobal::displayInfo("license.txt file.  This is free software, and you are welcome to") ;
	MGlobal::displayInfo("redistribute it under certain conditions; See license.txt for details.") ;


	return stat;
}


// --------------------------------------------------------------------------

/*
 * uninitializePlugin() - Disable/unload main plugin
 *	
 *	Description:
 *		this method is called when the plug-in is unloaded from Maya. It 
 *		deregisters all of the services that it was providing.
 *
 *	Arguments:
 *		obj - a handle to the plug-in object (use MFnPlugin to access it)
 *
 */
MStatus uninitializePlugin( MObject obj )
{
	MStatus   stat;
	MFnPlugin plugin( obj );

	stat = plugin.deregisterCommand( "resetSkinJoint" );
	if (!stat) 
		{
		stat.perror("deregisterCommand");
		return stat;
		}

	return stat;
}

// --------------------------------------------------------------------------

