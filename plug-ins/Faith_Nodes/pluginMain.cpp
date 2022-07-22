#include <maya/MFnPlugin.h>
#include "Faith_solvers.h"

MStatus initializePlugin( MObject obj )

{ 
	MStatus   status;
	MFnPlugin plugin( obj, "YinYuFei", "2020", "Any");
	
	status = plugin.registerNode(IKNode::NodeName, IKNode::NodeID ,
		IKNode::creator, IKNode::initialize, MPxNode::kDependNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.registerNode(SquashNode::NodeName, SquashNode::NodeID,
		SquashNode::creator, SquashNode::initialize,
		MPxNode::kDependNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.registerFileTranslator(
		"skin", "none", transferSkinWeights::creator,
		(char*)optionScript,
		(char*)defaultOptions);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	MGlobal::executeCommand("global proc int exportWeightOptions( string $parent,string $action,string $initialSettings,string $resultCallback ){return 0;}");

	status = plugin.registerNode(BlendMatrix::NodeName, BlendMatrix::NodeID,
		BlendMatrix::creator, BlendMatrix::initialize,
		MPxNode::kDependNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.registerNode(SwingAmplitude::NodeName, SwingAmplitude::NodeID,
		SwingAmplitude::creator, SwingAmplitude::initialize,
		MPxNode::kDependNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.registerNode(MatrixMult::NodeName, MatrixMult::NodeID,
		MatrixMult::creator, MatrixMult::initialize,
		MPxNode::kDependNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.registerNode(CorrectiveShape::NodeName, CorrectiveShape::NodeID,
		CorrectiveShape::creator, CorrectiveShape::initialize,
		MPxNode::kDeformerNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	return status;
}

MStatus uninitializePlugin( MObject obj )
{
	MStatus   status;
	MFnPlugin plugin( obj );

	status = plugin.deregisterNode(IKNode::NodeID);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.deregisterNode(SquashNode::NodeID);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.deregisterFileTranslator("skin");
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.deregisterNode(BlendMatrix::NodeID);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.deregisterNode(SwingAmplitude::NodeID);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.deregisterNode(MatrixMult::NodeID);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = plugin.deregisterNode(CorrectiveShape::NodeID);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	
	return status;
}
