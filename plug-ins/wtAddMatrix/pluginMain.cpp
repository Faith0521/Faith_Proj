#include "wtAddMatrix.h"
#include <maya/MFnPlugin.h>

MStatus initializePlugin( MObject obj )
{ 
	MStatus   status;
	MFnPlugin plugin( obj, "yinyufei", "2018", "Any");

	status = plugin.registerNode(wtAddMatrix::NodeName, wtAddMatrix::NodeID,
		wtAddMatrix::creator, wtAddMatrix::initialize, MPxNode::kDependNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	return status;
}

MStatus uninitializePlugin( MObject obj )
{
	MStatus   status;
	MFnPlugin plugin( obj );
	status = plugin.deregisterNode(wtAddMatrix::NodeID);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	return status;
}
