#include "wtAddMatrix.h"

MString wtAddMatrix::NodeName = "FAITH_wtAddMatrix";
MTypeId wtAddMatrix::NodeID = MTypeId(0x0ac052);

MObject wtAddMatrix::aMatrix;
MObject wtAddMatrix::aInMatrix;
MObject wtAddMatrix::aInWeight;
MObject wtAddMatrix::aOutputMatrix;

wtAddMatrix::wtAddMatrix()
{
}

wtAddMatrix::~wtAddMatrix()
{
}

MStatus wtAddMatrix::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;
	unsigned i,j;

	MArrayDataHandle inMatrixHandle = data.inputArrayValue(aMatrix);
	unsigned count = inMatrixHandle.elementCount(&status);

	MMatrixArray sumArray;
	for (i=0; i<count; i++, inMatrixHandle.next())
	{
		inMatrixHandle.jumpToElement(i);
		MMatrix inMatrix = inMatrixHandle.inputValue(&status).child(aInMatrix).asMatrix();
		double inWeight = inMatrixHandle.inputValue(&status).child(aInWeight).asDouble();
		MMatrix sumMatrix = inWeight * inMatrix;
		sumArray.append(sumMatrix);
	}

	// sum matrix
	MMatrix addMatrix = sumArray[0];
	for (j = 1; j < sumArray.length(); j++)
	{
		addMatrix += sumArray[j];
	}
	MDataHandle outMatrixHandle = data.outputValue(aOutputMatrix);
	outMatrixHandle.setMMatrix(addMatrix);

	data.setClean(plug);

	return MS::kSuccess;
}

void* wtAddMatrix::creator()
{
	return new wtAddMatrix();
}

MStatus wtAddMatrix::initialize()
{
	MFnCompoundAttribute cAttr;
	MFnMatrixAttribute mAttr;
	MFnNumericAttribute nAttr;

	aOutputMatrix = mAttr.create("outputMatrix", "omat");
	cAttr.setKeyable(false);
	cAttr.setWritable(false);
	cAttr.setStorable(false);
	addAttribute(aOutputMatrix);

	aInMatrix = mAttr.create("inMatrix", "ima");

	aInWeight = nAttr.create("inWeight", "iw", MFnNumericData::kDouble, 0.0);

	aMatrix = cAttr.create("inputMatrix", "imat");
	cAttr.setArray(true);
	cAttr.setUsesArrayDataBuilder(true);
	cAttr.addChild(aInMatrix);
	cAttr.addChild(aInWeight);
	cAttr.setKeyable(true);
	cAttr.setWritable(true);
	cAttr.setStorable(true);
	addAttribute(aMatrix);

	attributeAffects(aInMatrix, aOutputMatrix);
	attributeAffects(aInWeight, aOutputMatrix);

	return MS::kSuccess;
}
