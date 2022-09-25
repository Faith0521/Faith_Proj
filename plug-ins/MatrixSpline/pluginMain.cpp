#include "MatrixSplineNode.h"

#include <maya/MFnPlugin.h>

MStatus initializePlugin( MObject obj )

{ 
	MStatus   status;
	MFnPlugin plugin( obj, "YinYuFei", "2018", "Any");

	status = plugin.registerNode( "MatrixSpline", MatrixSpline::NodeID, MatrixSpline::creator,
								  MatrixSpline::initialize );
	if (!status) {
		status.perror("registerNode");
		return status;
	}

	return status;
}

MStatus uninitializePlugin( MObject obj)

{
	MStatus   status;
	MFnPlugin plugin( obj );

	status = plugin.deregisterNode( MatrixSpline::NodeID );
	if (!status) {
		status.perror("deregisterNode");
		return status;
	}

	return status;
}
