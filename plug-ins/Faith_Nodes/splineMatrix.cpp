#include "Faith_solvers.h"

MString splineMatrix::NodeName = "FAITH_SplineMatrix";
MTypeId splineMatrix::NodeID = MTypeId(0x0021);

MObject   splineMatrix::aInputCurve;
MObject   splineMatrix::aInputCurveMatrix;
MObject   splineMatrix::aTopMatrix;
MObject   splineMatrix::aParameter;
MObject   splineMatrix::aAngleByTangent;
MObject   splineMatrix::aOutputMatrix;

splineMatrix::splineMatrix()
{
}

splineMatrix::~splineMatrix()
{
}

MStatus splineMatrix::compute(const MPlug& plug, MDataBlock& data)
{
	return MS::kSuccess;
}

void* splineMatrix::creator()
{
	return new splineMatrix();
}

MStatus splineMatrix::initialize()
{
	MStatus  status;

	MFnNumericAttribute  nAttr;
	MFnMatrixAttribute   mAttr;
	MFnTypedAttribute    tAttr;
	MFnCompoundAttribute cAttr;

	aOutputMatrix = mAttr.create("outputMatrix", "outputMatrix");
	mAttr.setArray(true);
	mAttr.setUsesArrayDataBuilder(true);
	CHECK_MSTATUS(addAttribute(aOutputMatrix));

	aInputCurve = tAttr.create("inputCurve", "inputCurve", MFnData::kNurbsCurve);
	tAttr.setStorable(true);
	CHECK_MSTATUS(addAttribute(aInputCurve));
	CHECK_MSTATUS(attributeAffects(aInputCurve, aOutputMatrix));

	aInputCurveMatrix = mAttr.create("inputCurveMatrix", "inputCurveMatrix");
	mAttr.setStorable(true);
	CHECK_MSTATUS(addAttribute(aInputCurveMatrix));
	CHECK_MSTATUS(attributeAffects(aInputCurveMatrix, aOutputMatrix));

	aTopMatrix = mAttr.create("topMatrix", "topMatrix");
	mAttr.setStorable(true);
	CHECK_MSTATUS(addAttribute(aTopMatrix));
	CHECK_MSTATUS(attributeAffects(aTopMatrix, aOutputMatrix));

	aParameter = nAttr.create("parameter", "parameter", MFnNumericData::kDouble, 0.0);
	nAttr.setMin(0.0);
	nAttr.setMax(1.0);
	nAttr.setArray(true);
	nAttr.setStorable(true);
	CHECK_MSTATUS(addAttribute(aParameter));
	CHECK_MSTATUS(attributeAffects(aParameter, aOutputMatrix));

	aAngleByTangent = nAttr.create("angleByTangent", "angleByTangent", MFnNumericData::kBoolean, true);
	nAttr.setStorable(true);
	CHECK_MSTATUS(addAttribute(aAngleByTangent));
	CHECK_MSTATUS(attributeAffects(aAngleByTangent, aOutputMatrix));

	return MS::kSuccess;
}

MStatus splineMatrix::updateCurveInfo(MObject oInputCurve)
{
	return MS::kSuccess;
}

MMatrix* splineMatrix::getMatrixArrayFromParamList(MMatrix upMatrix, double* paramList, MMatrix mtxCurve, MObject* p_oCurve, int paramListLength)
{
	return nullptr;
}
