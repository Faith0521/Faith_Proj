#include "Faith_solvers.h"
#include "utils.h"

MString SwingAmplitude::NodeName = "FAITH_SwingAmplitude";
MTypeId SwingAmplitude::NodeID = MTypeId(0x0020);

MObject SwingAmplitude::aEnvelope;
MObject SwingAmplitude::aAmplitude;
MObject SwingAmplitude::aWaveLength;
MObject SwingAmplitude::aWaveFollow;
MObject SwingAmplitude::aStartPosition;
MObject SwingAmplitude::aReverse;
MObject SwingAmplitude::aOutputTransform;
MObject SwingAmplitude::aResult;

SwingAmplitude::SwingAmplitude()
{
}

SwingAmplitude::~SwingAmplitude()
{
}

MStatus SwingAmplitude::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;

	unsigned i;

	double oEnvelope = data.inputValue(aEnvelope).asDouble();
	double oAmplitude = data.inputValue(aAmplitude).asDouble();
	double oWaveLength = data.inputValue(aWaveLength).asDouble();
	double oWaveFollow = data.inputValue(aWaveFollow).asDouble();
	double oStartPosition = data.inputValue(aStartPosition).asDouble();
	double oReverse = data.inputValue(aReverse).asDouble();

	MArrayDataHandle outputArrayDataHandle = data.outputArrayValue(aOutputTransform);
	unsigned count = outputArrayDataHandle.elementCount();

	for (i=0;i< count;i++)
	{
		outputArrayDataHandle.jumpToElement(i);
		MDataHandle eHandle = outputArrayDataHandle.outputValue(&status).child(aResult);
		double sin01_PA = oWaveFollow * (-1) + oWaveLength * (i * (1.0 / (count - 1)));
		double k = (count - 1) / 2.0;
		double inReverse = oReverse * (k - i) + k;
		double setRange_ = setRange(0.0, double(count), 0.0, 1.0, oStartPosition + inReverse);;
		double startPosition_PA = 1.0 - setRange_;
		double amplitude_MD = oAmplitude * (oEnvelope * startPosition_PA);
		double result = amplitude_MD * sin(sin01_PA);
		if (count <= 1)
		{
			result = 0.0;
		}
		eHandle.setDouble(result);
	}

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

	aResult = n.create("result", "result", MFnNumericData::kDouble, 0.0);
	n.setKeyable(false);
	n.setStorable(false);
	n.setWritable(false);

	aOutputTransform = c.create("outTransform", "ot");
	c.setArray(true);
	c.setUsesArrayDataBuilder(true);
	c.addChild(aResult);
	addAttribute(aOutputTransform);

	aEnvelope = n.create("envelope", "envelope", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setStorable(true);
	n.setWritable(true);
	addAttribute(aEnvelope);
	attributeAffects(aEnvelope, aOutputTransform);

	aAmplitude = n.create("amplitude", "amp", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setStorable(true);
	n.setWritable(true);
	addAttribute(aAmplitude);
	attributeAffects(aAmplitude, aOutputTransform);

	aWaveLength = n.create("waveLength", "wl", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setStorable(true);
	n.setWritable(true);
	addAttribute(aWaveLength);
	attributeAffects(aWaveLength, aOutputTransform);
	
	aWaveFollow = n.create("waveFollow", "wf", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setStorable(true);
	n.setWritable(true);
	addAttribute(aWaveFollow);
	attributeAffects(aWaveFollow, aOutputTransform);

	aStartPosition = n.create("startPosition", "sp", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setStorable(true);
	n.setWritable(true);
	addAttribute(aStartPosition);
	attributeAffects(aStartPosition, aOutputTransform);

	aReverse = n.create("reverse", "reverse", MFnNumericData::kDouble, 0.0);
	n.setKeyable(true);
	n.setStorable(true);
	n.setWritable(true);
	addAttribute(aReverse);
	attributeAffects(aReverse, aOutputTransform);

	return MS::kSuccess;
}
