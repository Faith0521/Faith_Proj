#include "Faith_solvers.h"

MString BlendMatrix::NodeName = "FAITH_BlendMatrix";
MTypeId BlendMatrix::NodeID = MTypeId(0x0019);


BlendMatrix::BlendMatrix(){}

BlendMatrix::~BlendMatrix(){}

MStatus BlendMatrix::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;


	return MS::kSuccess;
}

void* BlendMatrix::creator()
{
	return new BlendMatrix();
}

MStatus BlendMatrix::initialize()
{
	MStatus status;


	return MS::kSuccess;
}

