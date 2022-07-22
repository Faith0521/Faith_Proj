#include "Faith_solvers.h"

MString MatrixMult::NodeName = "FAITH_MatrixMult";
MTypeId MatrixMult::NodeID = MTypeId(0x0018);

MObject MatrixMult::inMatrixA;
MObject MatrixMult::inMatrixB;
MObject MatrixMult::outMatrix;

MatrixMult::MatrixMult(){}

MatrixMult::~MatrixMult(){}

MStatus MatrixMult::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;
	if (plug != outMatrix)
	{
		return MS::kUnknownParameter;
	}

	MMatrix iMa = data.inputValue(inMatrixA).asMatrix();
	MMatrix iMb = data.inputValue(inMatrixB).asMatrix();

	MMatrix result = iMa * iMb;

	MDataHandle h;
	h = data.outputValue(outMatrix);
	h.setMMatrix(result);
	data.setClean(plug);

	return MS::kSuccess;
}

void* MatrixMult::creator()
{
	return new MatrixMult();
}

MStatus MatrixMult::initialize()
{
	MFnMatrixAttribute mAttr;
	MStatus status;

	// INPUTS
	inMatrixA = mAttr.create("inMatrixA", "imA");
	mAttr.setStorable(true);
	mAttr.setKeyable(true);
	mAttr.setConnectable(true);
	status = addAttribute(inMatrixA);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	inMatrixB = mAttr.create("inMatrixB", "imB");
	mAttr.setStorable(true);
	mAttr.setKeyable(true);
	mAttr.setConnectable(true);
	status = addAttribute(inMatrixB);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	// OUTPUTS
	outMatrix = mAttr.create("outMatrix", "outMa");
	mAttr.setStorable(false);
	mAttr.setKeyable(false);
	mAttr.setConnectable(true);
	status = addAttribute(outMatrix);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	// CONNECTIONS
	status = attributeAffects(inMatrixA, outMatrix);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	status = attributeAffects(inMatrixB, outMatrix);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	return MS::kSuccess;
}

