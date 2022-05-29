#include "Faith_solvers.h"
#include "utils.cpp"

MString SquashNode::NodeName = "FAITH_Squash";
MTypeId SquashNode::NodeID = MTypeId(0x0014);

MObject SquashNode::globalScale;
MObject SquashNode::globalScalex;
MObject SquashNode::globalScaley;
MObject SquashNode::globalScalez;
MObject SquashNode::stretch;
MObject SquashNode::squash;
MObject SquashNode::axis;
MObject SquashNode::blendValue;
MObject SquashNode::driveValue;
MObject SquashNode::driverMin;
MObject SquashNode::driverMax;
MObject SquashNode::driverCtrl;
MObject SquashNode::outputScale;

SquashNode::SquashNode(){}

SquashNode::~SquashNode(){}

void* SquashNode::creator()
{
	return new SquashNode();
}

MStatus SquashNode::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;
	if (plug != outputScale)
	{
		return MS::kUnknownParameter;
	}
	MVector scale = data.inputValue(globalScale).asFloatVector();
	double sx = scale.x;
	double sy = scale.y;
	double sz = scale.z;

	// Slide
	double inputBlendVal = (double)data.inputValue(blendValue).asFloat();
	double inputDriverVal = (double)data.inputValue(driveValue).asFloat();
	double inputDriverMin = (double)data.inputValue(driverMin).asFloat();
	double inputDriverCtrl = (double)data.inputValue(driverCtrl).asFloat();
	double inputDriverMax = (double)data.inputValue(driverMax).asFloat();
	int inputAxis = data.inputValue(axis).asShort();
	double inputStretch = (double)data.inputValue(stretch).asFloat();
	double inputSquash = (double)data.inputValue(squash).asFloat();

	inputStretch *= clamp(std::max(inputDriverVal - inputDriverCtrl , 0.0) / 
		std::max(inputDriverMin - inputDriverCtrl , 0.0001) , 0.0 , 1.0);
	inputSquash *= clamp(std::max(inputDriverCtrl - inputDriverVal, 0.0) /
		std::max(inputDriverCtrl - inputDriverMin, 0.0001), 0.0, 1.0);

	if (inputAxis != 0)
	{
		sx *= std::max(0.0 , 1.0 + inputStretch + inputSquash);
	}
	if (inputAxis != 1)
	{
		sy *= std::max(0.0, 1.0 + inputStretch + inputSquash);
	}
	if (inputAxis != 2)
	{
		sz *= std::max(0.0, 1.0 + inputStretch + inputSquash);
	}

	MVector scl = MVector(sx , sy , sz);
	scl = linearInterpolate(scale, scl, inputBlendVal);
	
	double clampVal = 0.0001;

	double scl_x = std::max(scl.x , clampVal);
	double scl_y = std::max(scl.y, clampVal);
	double scl_z = std::max(scl.z, clampVal);

	// result
	MDataHandle h = data.outputValue(outputScale);
	h.set3Float(float(scl_x) , float(scl_y) , float(scl_z));
	data.setClean(plug);

	return MS::kSuccess;
}

MStatus SquashNode::initialize()
{
	MStatus status;
	MFnNumericAttribute nAttr;
	MFnEnumAttribute eAttr;

	globalScale = nAttr.createPoint("globalScale", "globalScale");
	globalScalex = nAttr.child(0);
	globalScaley = nAttr.child(1);
	globalScalez = nAttr.child(2);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	nAttr.setReadable(true);
	nAttr.setKeyable(false);
	addAttribute(globalScale);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	stretch = nAttr.create("stretchly", "stretchly", MFnNumericData::kFloat, 0.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(stretch);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	squash = nAttr.create("squash", "squash", MFnNumericData::kFloat, 0.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(squash);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	axis = eAttr.create("axis", "axis", 0);
	eAttr.addField("x", 0);
	eAttr.addField("y", 1);
	eAttr.addField("z", 2);
	eAttr.setWritable(true);
	eAttr.setStorable(true);
	eAttr.setReadable(true);
	eAttr.setKeyable(false);
	addAttribute(axis);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	blendValue = nAttr.create("blendValue", "blendValue", MFnNumericData::kFloat, 1);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(blendValue);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	driveValue = nAttr.create("driveValue", "driveValue", MFnNumericData::kFloat, 3);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(driveValue);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	driverMin = nAttr.create("driverMin", "driverMin", MFnNumericData::kFloat, 1);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(driverMin);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	driverCtrl = nAttr.create("driverCtrl", "driverCtrl", MFnNumericData::kFloat, 3);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(driverCtrl);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	driverMax = nAttr.create("driverMax", "driverMax", MFnNumericData::kFloat, 6);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(driverMax);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	outputScale = nAttr.createPoint("outputScale", "outputScale");
	nAttr.setWritable(false);
	nAttr.setStorable(false);
	nAttr.setReadable(true);
	addAttribute(outputScale);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	attributeAffects(globalScale, outputScale);
	attributeAffects(stretch, outputScale);
	attributeAffects(squash, outputScale);
	attributeAffects(axis, outputScale);
	attributeAffects(blendValue, outputScale);
	attributeAffects(driverMin, outputScale);
	attributeAffects(driverCtrl, outputScale);
	attributeAffects(driverMax, outputScale);


	return MS::kSuccess;
}