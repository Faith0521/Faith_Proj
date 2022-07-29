#include "Faith_solvers.h"

MString SlideRange::NodeName = "FAITH_SlideRange";
MTypeId SlideRange::NodeID = MTypeId(0x0023);

MObject SlideRange::aInCurve;
MObject SlideRange::aCurveRamp;
MObject SlideRange::aInPosition;
MObject SlideRange::aInSlidePosition;
MObject SlideRange::aOutputTransform;
MObject SlideRange::aOutputTranslate;
MObject SlideRange::aOutputRotate;
MObject SlideRange::aOutputScale;

SlideRange::SlideRange()
{
}

SlideRange::~SlideRange()
{
}

MStatus SlideRange::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;
	float value;
	MObject thisNode = this->thisMObject();
	//float inVal = data.inputValue(aInputVale).asDouble();
	MRampAttribute curveAttr(thisNode, aCurveRamp);
	//curveAttr.getValueAtPosition(inVal, value);

	//MDataHandle h = data.outputValue(aOutputVale);
	//h.setDouble(value);

	data.setClean(plug);

	return status;
}

void* SlideRange::creator()
{
	return new SlideRange();
}

MStatus SlideRange::initialize()
{
	MFnNumericAttribute nAttr;
	MRampAttribute rAttr;
	MFnCompoundAttribute cAttr;
	MFnTypedAttribute tAttr;

	aOutputTranslate = nAttr.createPoint("Translate", "tr");

	aOutputRotate = nAttr.createPoint("Rotate", "ro");

	aOutputScale = nAttr.createPoint("Scale", "scl");

	aOutputTransform = cAttr.create("outputTransform", "ot");
	cAttr.setArray(true);
	cAttr.setUsesArrayDataBuilder(true);
	cAttr.addChild(aOutputTranslate);
	cAttr.addChild(aOutputRotate);
	cAttr.addChild(aOutputScale);
	cAttr.setKeyable(false);
	cAttr.setWritable(false);
	cAttr.setStorable(false);
	addAttribute(aOutputTransform);

	aCurveRamp = rAttr.createCurveRamp("blendCurve", "bc");
	addAttribute(aCurveRamp);
	attributeAffects(aCurveRamp, aOutputTransform);

	aInCurve = tAttr.create("inCurve", "incv", MFnData::kNurbsCurve);
	tAttr.setKeyable(true);
	tAttr.setWritable(true);
	tAttr.setStorable(true);
	addAttribute(aInCurve);
	attributeAffects(aInCurve, aOutputTransform);

	aInPosition = nAttr.createPoint("inPosition", "ip");
	nAttr.setArray(true);
	nAttr.setUsesArrayDataBuilder(true);
	nAttr.setKeyable(true);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	addAttribute(aInPosition);
	attributeAffects(aInPosition, aOutputTransform);

	aInSlidePosition = nAttr.createPoint("inSlidePosition", "isp");
	nAttr.setArray(true);
	nAttr.setUsesArrayDataBuilder(true);
	nAttr.setKeyable(true);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	addAttribute(aInSlidePosition);
	attributeAffects(aInSlidePosition, aOutputTransform);
	
	return MS::kSuccess;
}

void SlideRange::postConstructor()
{
	MStatus status;
	MObject thisNode = this->thisMObject();
	// One entry is the least needed or the attribute editor will
	// produce an error.
	postConstructor_init_curveRamp(thisNode, aCurveRamp, 0, 0.0f, 0.0f, 2);
	postConstructor_init_curveRamp(thisNode, aCurveRamp, 1, 1.0f, 1.0f, 2);
}

MStatus SlideRange::postConstructor_init_curveRamp(MObject& nodeObj, MObject& rampObj, int index, float position, float value, int interpolation)
{
	MStatus status;

	MPlug rampPlug(nodeObj, rampObj);
	MPlug elementPlug = rampPlug.elementByLogicalIndex((unsigned)index, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	MPlug positionPlug = elementPlug.child(0, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	status = positionPlug.setFloat(position);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	MPlug valuePlug = elementPlug.child(1);
	status = valuePlug.setFloat(value);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	MPlug interpolationPlug = elementPlug.child(2);
	interpolationPlug.setInt(interpolation);

	return status;
}

