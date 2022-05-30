#include "Faith_solvers.h"

MString Drum::NodeName = "FAITH_Drum";
MTypeId Drum::NodeID = MTypeId(0x0017);

MObject Drum::inOutTime;
MObject Drum::inDrumSpeed;
MObject Drum::inDrumOffset;
MObject Drum::inDrumDefaultValue;
MObject Drum::inDrumReduction;
MObject Drum::inRoot_DrumStrength;
MObject Drum::inIK_DrumStrength;
MObject Drum::outScale;
MObject Drum::outScaleX;
MObject Drum::outScaleY;
MObject Drum::outScaleZ;

Drum::Drum(){}

Drum::~Drum(){}

MStatus Drum::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;

	MTime outTime = data.inputValue(inOutTime).asTime();
	double DrumSpeed = data.inputValue(inDrumSpeed).asDouble();
	double DrumOffset = data.inputValue(inDrumOffset).asDouble();
	double DrumDefaultValue = data.inputValue(inDrumDefaultValue).asDouble();
	double DrumReduction = data.inputValue(inDrumReduction).asDouble();
	double Root_DrumStrength = data.inputValue(inRoot_DrumStrength).asDouble();
	double IK_DrumStrength = data.inputValue(inIK_DrumStrength).asDouble();

	double time = outTime.value() * DrumSpeed + DrumOffset - DrumDefaultValue * DrumReduction;
	double sclX = 1 + ((1 + sin(time)) * 0.5 * Root_DrumStrength * IK_DrumStrength);
	double sclY = 1 + ((1 + sin(time)) * 0.5 * Root_DrumStrength * IK_DrumStrength);
	double sclZ = 1 + ((1 + sin(time)) * 0.5 * Root_DrumStrength * IK_DrumStrength);

	MDataHandle outputHandle = data.outputValue(outScale);
	MDataHandle scaleX = outputHandle.child(outScaleX);
	scaleX.setDouble(sclX);
	MDataHandle scaleY = outputHandle.child(outScaleY);
	scaleY.setDouble(sclY);
	MDataHandle scaleZ = outputHandle.child(outScaleZ);
	scaleZ.setDouble(sclZ);

	data.setClean(plug);

	return MS::kSuccess;
}

void* Drum::creator()
{
	return new Drum();
}

MStatus Drum::initialize()
{
	MStatus status;
	MFnNumericAttribute n;
	MFnCompoundAttribute c;
	MFnUnitAttribute u;

	inOutTime = u.create("inTime", "inTime", MFnUnitAttribute::kTime, 0.0);
	addAttribute(inOutTime);

	inDrumSpeed = n.create("DrumSpeed", "DrumSpeed", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inDrumSpeed);

	inDrumOffset = n.create("DrumOffset", "DrumOffset", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inDrumOffset);

	inDrumDefaultValue = n.create("DrumValue", "DrumValue", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inDrumDefaultValue);

	inDrumReduction = n.create("DrumReduction", "DrumReduction", MFnNumericData::kDouble, 1.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inDrumReduction);
	
	inRoot_DrumStrength = n.create("Root_DrumStrength", "rstrength", MFnNumericData::kDouble, 1.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inRoot_DrumStrength);

	inIK_DrumStrength = n.create("IK_DrumStrength", "istrength", MFnNumericData::kDouble, 1.0);
	n.setKeyable(true);
	n.setWritable(true);
	n.setStorable(true);
	addAttribute(inIK_DrumStrength);

	outScaleX = n.create("outScaleX", "sclx", MFnNumericData::kDouble);
	n.setWritable(false);
	n.setStorable(false);
	n.setArray(false);

	outScaleY = n.create("outScaleY", "scly", MFnNumericData::kDouble);
	n.setWritable(false);
	n.setStorable(false);
	n.setArray(false);

	outScaleZ = n.create("outScaleZ", "sclz", MFnNumericData::kDouble);
	n.setWritable(false);
	n.setStorable(false);
	n.setArray(false);

	outScale = c.create("outScale", "outScale");
	c.addChild(outScaleX);
	c.addChild(outScaleY);
	c.addChild(outScaleZ);
	addAttribute(outScale);

	attributeAffects(inOutTime, outScale);
	attributeAffects(inDrumSpeed, outScale);
	attributeAffects(inDrumOffset, outScale);
	attributeAffects(inDrumDefaultValue, outScale);
	attributeAffects(inDrumReduction, outScale);
	attributeAffects(inRoot_DrumStrength, outScale);
	attributeAffects(inIK_DrumStrength, outScale);


	return MS::kSuccess;
}
