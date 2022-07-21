#include "Faith_solvers.h"

MString SwingAmplitude::NodeName = "FAITH_SwingAmplitude";
MTypeId SwingAmplitude::NodeID = MTypeId(0x0018);

MObject SwingAmplitude::inputTransform;
MObject SwingAmplitude::intranslateX;
MObject SwingAmplitude::intranslateY;
MObject SwingAmplitude::outTransform;
MObject SwingAmplitude::outtranslateX;
MObject SwingAmplitude::outtranslateY;

SwingAmplitude::SwingAmplitude()
{
}

SwingAmplitude::~SwingAmplitude()
{
}

MStatus SwingAmplitude::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;

	MArrayDataHandle InputArrayDataHandle = data.inputArrayValue(inputTransform);

	MArrayDataHandle outputArrayDataHandle = data.outputArrayValue(outTransform);

	MArrayDataBuilder builder(outTransform, outputArrayDataHandle.elementCount());
	for (unsigned i=0;i< outputArrayDataHandle.elementCount();i++)
	{
		MDataHandle outHandle = builder.addElement(i);
		outputArrayDataHandle.jumpToElement(i);
		double tx = outputArrayDataHandle.outputValue().child(outtranslateX).asDouble();
		outHandle.setDouble(tx + i);
	}
	status = outputArrayDataHandle.set(builder);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = outputArrayDataHandle.setAllClean();
	
	return MS::kSuccess;
}

void* SwingAmplitude::creator()
{
	return new SwingAmplitude();
}

MStatus SwingAmplitude::initialize()
{
	MFnCompoundAttribute c; 
	MFnNumericAttribute n;

	intranslateX = n.create("intranslateX", "ix", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setStorable(true);
	n.setWritable(true);
	addAttribute(intranslateX);

	outtranslateX = n.create("outtranslateX", "outtranslateX", MFnNumericData::kDouble, 0.0);
	n.setKeyable(false);
	n.setStorable(false);
	n.setWritable(false);

	outTransform = c.create("outTransform", "outTransform");
	c.setArray(true);
	c.setUsesArrayDataBuilder(true);
	c.addChild(outtranslateX);

	addAttribute(outTransform);
	attributeAffects(intranslateX, outTransform);

	return MS::kSuccess;
}
