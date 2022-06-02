#include <maya/MFnPlugin.h>
#include "Faith_solvers.h"

MStatus initializePlugin( MObject obj )

{ 
	MStatus   status;
	MFnPlugin plugin( obj, "YinYuFei", "2020", "Any");
	
	status = plugin.registerNode(IKNode::GetNodeName(), IKNode::GetNodeID() ,
		IKNode::creator, IKNode::initialize, MPxNode::kDependNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.registerNode(SquashNode::NodeName, SquashNode::NodeID,
		SquashNode::creator, SquashNode::initialize,
		MPxNode::kDependNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.registerNode(Swing::NodeName, Swing::NodeID,
		Swing::creator, Swing::initialize,
		MPxNode::kDependNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.registerNode(Drum::NodeName, Drum::NodeID,
		Drum::creator, Drum::initialize,
		MPxNode::kDependNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.registerCommand("transferSkin", transferSkinWeights::creator, transferSkinWeights::syntax);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.registerNode(BlendMatrix::NodeName, BlendMatrix::NodeID,
		BlendMatrix::creator, BlendMatrix::initialize,
		MPxNode::kDependNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.registerNode(SwingAmplitude::NodeName, SwingAmplitude::NodeID,
		SwingAmplitude::creator, SwingAmplitude::initialize,
		MPxNode::kDependNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	return status;
}

MStatus uninitializePlugin( MObject obj )
{
	MStatus   status;
	MFnPlugin plugin( obj );

	status = plugin.deregisterNode(IKNode::GetNodeID());
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.deregisterNode(SquashNode::NodeID);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.deregisterNode(Swing::NodeID);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.deregisterNode(Drum::NodeID);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.deregisterCommand("transferSkin");
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.deregisterNode(BlendMatrix::NodeID);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.deregisterNode(SwingAmplitude::NodeID);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	return status;
}
