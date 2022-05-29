#include "Faith_solvers.h"

MString SplitWeights::NodeName = "SplitWeights";
MTypeId SplitWeights::NodeID = MTypeId(0x0018);

SplitWeights::SplitWeights(){}

SplitWeights::~SplitWeights(){}

MStatus SplitWeights::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;

	return MS::kSuccess;
}

void* SplitWeights::creator()
{
	return new SplitWeights;
}

MStatus SplitWeights::initialize()
{
	MStatus status;

	return MS::kSuccess;
}

void SplitWeights::postConstructor()
{
}

MStatus SplitWeights::postConstructor_init_curveRamp(MObject& nodeObj, MObject& rampObj, int index, float position, float value, int interpolation)
{
	MStatus status;

	return MS::kSuccess;
}
