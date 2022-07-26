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

	int i,j;
	MDataHandle hInputCurve = data.inputValue(ainputCurve, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	MArrayDataHandle hInputPosition = data.inputArrayValue(aPosition, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	MArrayDataHandle outputArrayDataHandle = data.outputArrayValue(aResult, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	MFnNurbsCurve nurbsFn = data.inputValue(ainputCurve).asNurbsCurve();

	int numPosition = hInputPosition.elementCount();

	MPointArray ptArray;
	MDoubleArray paramArray;
	double param;

	for (i=0; i<numPosition; i++, hInputPosition.next())
	{
		hInputPosition.jumpToElement(i);
		MPoint inPoint(hInputPosition.inputValue(&status).asFloatVector());
		MPoint clstPt = nurbsFn.closestPoint(inPoint, false, NULL, 0.01, MSpace::kWorld);
		nurbsFn.getParamAtPoint(clstPt, param, MSpace::kWorld);
		ptArray.append(clstPt);
		paramArray.append(param);
	}

	for (j=0; j<outputArrayDataHandle.elementCount(); j++, outputArrayDataHandle.next())
	{
		outputArrayDataHandle.jumpToElement(j);
		MDataHandle h_position = outputArrayDataHandle.outputValue(&status).child(aPosition);
		MDataHandle h_param = outputArrayDataHandle.outputValue(&status).child(aOutputParameter);
		h_position.set3Float(ptArray[j].x, ptArray[j].y, ptArray[j].z);
		h_param.setDouble(paramArray[j]);
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
