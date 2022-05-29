#include "Faith_solvers.h"

MString Swing::NodeName = "FAITH_Swing";
MTypeId Swing::NodeID = MTypeId(0x0016);

MObject Swing::inOutTime;
MObject Swing::inSwingSpeed;
MObject Swing::inSwingOffset;
MObject Swing::inSwingReductionValue;
MObject Swing::inSwingReduction;
MObject Swing::outputUp;
MObject Swing::outputDn;
MObject Swing::inSwingAmplitudeXAdd;
MObject Swing::inSwingAmplitudeYAdd;
MObject Swing::inRoot_SwingAmplitudeX;
MObject Swing::inRoot_SwingAmplitudeY;
MObject Swing::inIK_SwingAmplitudeX;
MObject Swing::inIK_SwingAmplitudeY;

Swing::Swing()
{
}

Swing::~Swing()
{
}

MStatus Swing::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;

	MTime input_time = data.inputValue(inOutTime).asTime();
	double input_swingSpeed = data.inputValue(inSwingSpeed).asDouble();
	double input_swingOffset = data.inputValue(inSwingOffset).asDouble();
	double input_swingDefault = data.inputValue(inSwingReductionValue).asInt();
	double input_swingReduction = data.inputValue(inSwingReduction).asDouble();
	double input_swingAmplitudeXAdd = data.inputValue(inSwingAmplitudeXAdd).asDouble();
	double input_swingAmplitudeYAdd = data.inputValue(inSwingAmplitudeYAdd).asDouble();
	double input_Root_SwingAmplitudeX = data.inputValue(inRoot_SwingAmplitudeX).asDouble();
	double input_Root_SwingAmplitudeY = data.inputValue(inRoot_SwingAmplitudeY).asDouble();
	double input_IK_SwingAmplitudeX = data.inputValue(inIK_SwingAmplitudeX).asDouble();
	double input_IK_SwingAmplitudeY = data.inputValue(inIK_SwingAmplitudeY).asDouble();
	
	double time = input_time.value() * input_swingSpeed + input_swingOffset -
		input_swingDefault * input_swingReduction;
	
	double outUp = sin(time) * input_Root_SwingAmplitudeX * (1 + input_swingDefault * input_swingAmplitudeXAdd) *
		input_IK_SwingAmplitudeX;
	double outDn = sin(time) * input_Root_SwingAmplitudeY * (1 + input_swingDefault * input_swingAmplitudeYAdd) *
		input_IK_SwingAmplitudeY;

	MDataHandle h_up = data.outputValue(outputUp);
	MDataHandle h_dn = data.outputValue(outputDn);

	h_up.setDouble(outUp);
	h_dn.setDouble(outDn);

	data.setClean(plug);

	return MS::kSuccess;
}

void* Swing::creator()
{
	return new Swing();
}

MStatus Swing::initialize()
{
	MStatus status;
	MFnNumericAttribute n;
	MFnUnitAttribute u;

	inOutTime = u.create("inTime", "inTime", MFnUnitAttribute::kTime, 0.0);
	addAttribute(inOutTime);

	inSwingSpeed = n.create("SwingSpeed", "SwingSpeed", MFnNumericData::kDouble, 1.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inSwingSpeed);

	inSwingOffset = n.create("SwingOffset", "SwingOffset", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inSwingOffset);

	inSwingReductionValue = n.create("SwingDeaultValue", "SwingDeaultValue", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inSwingReductionValue);

	inSwingReduction = n.create("SwingReduction", "SwingReduction", MFnNumericData::kDouble, 1.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inSwingReduction);

	inSwingAmplitudeXAdd = n.create("SwingAmplitudeXAdd", "SwingAmplitudeXAdd", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inSwingAmplitudeXAdd);

	inSwingAmplitudeYAdd = n.create("SwingAmplitudeYAdd", "SwingAmplitudeYAdd", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inSwingAmplitudeYAdd);

	inRoot_SwingAmplitudeX = n.create("Root_SwingAmplitudeX", "Root_SwingAmplitudeX", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inRoot_SwingAmplitudeX);

	inRoot_SwingAmplitudeY = n.create("Root_SwingAmplitudeY", "Root_SwingAmplitudeY", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inRoot_SwingAmplitudeY);

	inIK_SwingAmplitudeX = n.create("IK_SwingAmplitudeX", "IK_SwingAmplitudeX", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inIK_SwingAmplitudeX);

	inIK_SwingAmplitudeY = n.create("IK_SwingAmplitudeY", "IK_SwingAmplitudeY", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inIK_SwingAmplitudeY);

	outputUp = n.create("outputUp", "outputUp", MFnNumericData::kDouble, 0.0);
	n.setKeyable(false);
	n.setWritable(false);
	n.setStorable(false);
	addAttribute(outputUp);

	outputDn = n.create("outputDn", "outputDn", MFnNumericData::kDouble, 0.0);
	n.setKeyable(false);
	n.setWritable(false);
	n.setStorable(false);
	addAttribute(outputDn);

	attributeAffects(inSwingSpeed, outputUp);
	attributeAffects(inSwingSpeed, outputDn);
	attributeAffects(inSwingOffset, outputUp);
	attributeAffects(inSwingOffset, outputDn);
	attributeAffects(inSwingSpeed, outputUp);
	attributeAffects(inSwingSpeed, outputDn);
	attributeAffects(inSwingReductionValue, outputUp);
	attributeAffects(inSwingReductionValue, outputDn);
	attributeAffects(inSwingReduction, outputUp);
	attributeAffects(inSwingReduction, outputDn);
	attributeAffects(inSwingAmplitudeXAdd, outputUp);
	attributeAffects(inSwingAmplitudeYAdd, outputDn);
	attributeAffects(inRoot_SwingAmplitudeX, outputUp);
	attributeAffects(inRoot_SwingAmplitudeY, outputDn);
	attributeAffects(inIK_SwingAmplitudeX, outputUp);
	attributeAffects(inIK_SwingAmplitudeY, outputDn);

	return MS::kSuccess;
}
