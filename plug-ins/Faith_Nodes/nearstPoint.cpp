#include "Faith_solvers.h"

MString nearstPoint::NodeName = "FAITH_neasrestPoint";
MTypeId nearstPoint::NodeID = MTypeId(0x0022);

MObject nearstPoint::ainputCurve;
MObject nearstPoint::aInPosition;
MObject nearstPoint::aPosition;
MObject nearstPoint::aOutputResult;
MObject nearstPoint::aResult;
MObject nearstPoint::aOutputPosition;
MObject nearstPoint::aOutputParameter;

nearstPoint::nearstPoint()
{
}

nearstPoint::~nearstPoint()
{
}

MStatus nearstPoint::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;

	int i;
	MDataHandle hInputCurve = data.inputValue(ainputCurve, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	MArrayDataHandle hInputPosition = data.inputArrayValue(aPosition, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	MArrayDataHandle outputArrayDataHandle = data.outputArrayValue(aResult, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	MFnNurbsCurve nurbsFn = data.inputValue(ainputCurve).asNurbsCurve();

	int numPosition = hInputPosition.elementCount();

	for (i=0; i<numPosition; i++)
	{
		outputArrayDataHandle.jumpToElement(i);
		MDataHandle pHandle = outputArrayDataHandle.outputValue(&status).child(aOutputPosition);
		//MPoint inPoint(hInputPosition.inputValue(&status).asFloatVector());
		//MPoint clstPt = nurbsFn.closestPoint(inPoint, false, NULL, 0.01, MSpace::kWorld);
		pHandle.set3Float(0.0, 1.0, 0.0);
	}

	data.setClean(plug);

	return MS::kSuccess;
}

void* nearstPoint::creator()
{
	return new nearstPoint();
}

MStatus nearstPoint::initialize()
{
	MStatus  status;

	MFnNumericAttribute  nAttr;
	MFnTypedAttribute    tAttr;
	MFnCompoundAttribute cAttr;

	aPosition = nAttr.createPoint("outPosition", "op");
	nAttr.setKeyable(false);
	nAttr.setWritable(false);
	nAttr.setStorable(false);

	aOutputParameter = nAttr.create("parameter", "parameter", MFnNumericData::kDouble, 0.0);
	nAttr.setKeyable(false);
	nAttr.setWritable(false);
	nAttr.setStorable(false);

	aResult = cAttr.create("result", "result");
	nAttr.setKeyable(false);
	nAttr.setWritable(false);
	nAttr.setStorable(false);
	cAttr.setArray(true);
	cAttr.setUsesArrayDataBuilder(true);
	cAttr.addChild(aPosition);
	cAttr.addChild(aOutputParameter);
	addAttribute(aResult);
	
	aPosition = nAttr.createPoint("position", "position");
	nAttr.setArray(true);
	nAttr.setUsesArrayDataBuilder(true);
	nAttr.setKeyable(true);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	addAttribute(aPosition);
	attributeAffects(aPosition, aResult);

	ainputCurve = tAttr.create("inCurve", "ic", MFnData::kNurbsCurve);
	tAttr.setStorable(true);
	tAttr.setKeyable(true);
	tAttr.setWritable(true);
	addAttribute(ainputCurve);
	attributeAffects(ainputCurve, aResult);

	return MS::kSuccess;
}
