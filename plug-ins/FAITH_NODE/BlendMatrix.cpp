#include "Faith_solvers.h"

MString BlendMatrix::NodeName = "FAITH_BlendMatrix";
MTypeId BlendMatrix::NodeID = MTypeId(0x0019);

MObject BlendMatrix::outputMatrix;
MObject BlendMatrix::offsetMatrix;
MObject BlendMatrix::restMatrix;
MObject BlendMatrix::blendInputMatrix;
MObject BlendMatrix::blendOffsetMatrix;
MObject BlendMatrix::blendTranslateWeight;
MObject BlendMatrix::blendRotateWeight;
MObject BlendMatrix::blendScaleWeight;
MObject BlendMatrix::blendShearWeight;
MObject BlendMatrix::blendMatrix;

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
	MFnCompoundAttribute c;
	MFnMatrixAttribute m;
	MFnNumericAttribute n;
	MFnUnitAttribute u;

	outputMatrix = m.create("outputMatrix", "outputMatrix");
	m.setWritable(false);
	m.setStorable(false);
	addAttribute(outputMatrix);

	offsetMatrix = m.create("offsetMatrix", "offsetMatrix");
	m.setWritable(true);
	m.setStorable(true);
	m.setReadable(false);
	addAttribute(offsetMatrix);
	attributeAffects(offsetMatrix, outputMatrix);

	restMatrix = m.create("restMatrix", "restMatrix");
	m.setWritable(true);
	m.setStorable(true);
	m.setReadable(false);
	addAttribute(restMatrix);
	attributeAffects(restMatrix, outputMatrix);



	return MS::kSuccess;
}

