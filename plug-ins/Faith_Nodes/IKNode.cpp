#include "Faith_solvers.h"
#include "utils.cpp"

MString NodeName = "FAITH_IKSoftStretch";

MTypeId NodeID = MTypeId(0x0015);

MObject IKNode::inRoot;
MObject IKNode::inIKEnd;
MObject IKNode::inPole;
MObject IKNode::inMidParent;
MObject IKNode::inEndParent;
MObject IKNode::lengthA;
MObject IKNode::lengthB;
MObject IKNode::fatnessA;
MObject IKNode::fatnessB;
MObject IKNode::softness;
MObject IKNode::stretchly;
MObject IKNode::reverse;
MObject IKNode::negate;
MObject IKNode::slide;
MObject IKNode::roll;
MObject IKNode::pin;
MObject IKNode::outMid;
MObject IKNode::outEnd;

IKNode::IKNode()
{
}

IKNode::~IKNode()
{
}

MStatus IKNode::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;
	MMatrix inputRoot = data.inputValue(inRoot).asMatrix();
	MMatrix inputIKend = data.inputValue(inIKEnd).asMatrix();
	MMatrix inputPole = data.inputValue(inPole).asMatrix();
	MMatrix inputMidParent = data.inputValue(inMidParent).asMatrix();
	MMatrix inputEndParent = data.inputValue(inEndParent).asMatrix();

	IK_INfo ikData;
	ikData.root = inputRoot;
	ikData.eff = inputIKend;
	ikData.pole = inputPole;

	ikData.lengthA = (double)data.inputValue(lengthA).asFloat();
	ikData.lengthB = (double)data.inputValue(lengthB).asFloat();
	ikData.fatnessA = (double)data.inputValue(fatnessA).asFloat();
	ikData.fatnessB = (double)data.inputValue(fatnessB).asFloat();
	ikData.soft = (double)data.inputValue(softness).asFloat();
	ikData.slide = (double)data.inputValue(slide).asFloat();
	ikData.negate = (bool)data.inputValue(negate).asBool();
	ikData.reverse = (double)data.inputValue(reverse).asFloat();
	ikData.roll = (double)data.inputValue(roll).asFloat();
	ikData.stretch = (double)data.inputValue(stretchly).asFloat();
	ikData.pin = (double)data.inputValue(pin).asFloat();

	MStringArray outNameArray;
	plug.name().split('.', outNameArray);
	MString outName = outNameArray[outNameArray.length() - 1];

	MTransformationMatrix result;

	result = GetIKInfo(ikData, outName);

	MDataHandle h;
	if (plug == outMid)
	{
		h = data.outputValue(outMid);
		h.setMMatrix(result.asMatrix() * inputMidParent.inverse());
		data.setClean(plug);
	}
	if (plug == outEnd)
	{
		h = data.outputValue(outEnd);
		h.setMMatrix(result.asMatrix() * inputEndParent.inverse());
		data.setClean(plug);
	}
	else
	{
		return MStatus::kUnknownParameter;
	}

	return MS::kSuccess;
}

MTransformationMatrix IKNode::GetIKInfo(IK_INfo values, MString outputName)
{
	MTransformationMatrix result;
	MVector JointPos, rootPos, effPos, polePos, rootEff, xAxis, yAxis, zAxis, rollAxis;

	rootPos = values.root.getTranslation(MSpace::kWorld);
	effPos = values.eff.getTranslation(MSpace::kWorld);
	polePos = values.pole.getTranslation(MSpace::kWorld);
	rootEff = effPos - rootPos;
	rollAxis = rootEff.normal();

	double rootEffDis = rootEff.length();

	// init scale
	double scale[3];
	values.root.getScale(scale , MSpace::kWorld);
	double global_scale = scale[0];

	// set result scale
	result.setScale(scale, MSpace::kWorld);

	// Distance with MaxStretch
	double restLength = (values.lengthA * values.fatnessA + values.lengthB * values.fatnessB) * global_scale;
	double distance = rootEffDis;
	double distance2 = distance;
	if (distance > restLength * values.stretch)
	{
		distance = restLength * values.stretch;
	}
	values.soft = values.soft * restLength * 0.1;

	//Stretch and softness
	double stretch = std::max(1.0 , distance / restLength);
	double subst = restLength - values.soft;
	if (values.soft > 0 && distance2 > subst) 
	{
		double softValue = values.soft * (1.0 - exp(-(distance2 - subst) / values.soft)) + subst;
		stretch = distance / softValue;
	}
	values.lengthA = values.lengthA * stretch * values.fatnessA * global_scale;
	values.lengthB = values.lengthB * stretch * values.fatnessB * global_scale;

	// Reverse -------------------------------------
	double d = distance / (values.lengthA + values.lengthB);

	double reverse_scale;
	if (values.reverse < 0.5)
		reverse_scale = 1 - (values.reverse * 2 * (1 - d));
	else
		reverse_scale = 1 - ((1 - values.reverse) * 2 * (1 - d));

	values.lengthA *= reverse_scale;
	values.lengthB *= reverse_scale;

	bool invert = values.reverse > 0.5;

	// slide
	double slide_add;
	if (values.slide < 0.5)
	{
		slide_add = (values.lengthA * (values.slide * 2)) - (values.lengthA);
	}
	else
	{
		slide_add = (values.lengthB * (values.slide * 2)) - (values.lengthB);
	}

	values.lengthA += slide_add;
	values.lengthB -= slide_add;

	double angleA = 0;
	double angleB = 0;

	if ((rootEffDis < values.lengthA + values.lengthB) && (rootEffDis > abs(values.lengthA - values.lengthB) + 1E-6)) {

		// use the law of cosine for lengthA
		double a = values.lengthA;
		double b = rootEffDis;
		double c = values.lengthB;

		angleA = acos(std::min(1.0, (a * a + b * b - c * c) / (2 * a * b)));

		// use the law of cosine for lengthB
		a = values.lengthB;
		b = values.lengthA;
		c = rootEffDis;
		angleB = acos(std::min(1.0, (a * a + b * b - c * c) / (2 * a * b)));

		// invert the angles if need be
		if (invert) {
			angleA = -angleA;
			angleB = -angleB;
		}
	}

	// start with the X and Z axis
	xAxis = rootEff;
	xAxis.normalize();
	yAxis = linearInterpolate(rootPos, effPos, .5);
	yAxis = polePos - yAxis;
	yAxis.normalize();
	yAxis = rotateVectorAlongAxis(yAxis, rollAxis, values.roll);
	zAxis = xAxis ^ yAxis;
	zAxis.normalize();
	yAxis = zAxis ^ xAxis;
	yAxis.normalize();

	// switch depending
	if (outputName == "outMid")
	{
		if (angleA != 0.0)
		{
			xAxis = rotateVectorAlongAxis(xAxis, zAxis, -angleA);
		}
		if (values.pin > 0.0)
		{
			if (values.pin == 1.0)
			{
				JointPos = polePos;
			}
			else
			{
				JointPos = xAxis * values.lengthA;
				JointPos += rootPos;
				JointPos = lerp(JointPos, polePos, values.pin);
			}
		}
		else
		{
			JointPos = xAxis * values.lengthA;
			JointPos += rootPos;
		}

		if (angleB != 0.0)
		{
			if (invert)
			{
				angleB += PI * 2;
			}
			xAxis = rotateVectorAlongAxis(xAxis , zAxis , -(angleB * 0.5 - PI * 0.5));
		}

		zAxis = xAxis ^ yAxis;
		zAxis.normalize();

		if (values.negate)
		{
			xAxis *= -1;
		}

		yAxis = zAxis ^ xAxis;
		yAxis.normalize();

		MQuaternion q = getQuaternionFromAxes(xAxis, yAxis, zAxis);
		result.setRotationQuaternion(q.x, q.y, q.z, q.w);

		result.setTranslation(JointPos, MSpace::kWorld);
	}

	if (outputName == "outEnd")
	{
		effPos = rootPos;
		if (angleA != 0.0)
		{
			xAxis = rotateVectorAlongAxis(xAxis, zAxis, -angleA);
		}

		JointPos = xAxis * values.lengthA;
		effPos += JointPos;
		if (angleB != 0.0)
		{
			xAxis = rotateVectorAlongAxis(xAxis, zAxis, -(angleB - PI));
		}
		if (values.pin > 0.0)
		{
			if (values.pin == 1.0)
			{
				effPos = values.eff.getTranslation(MSpace::kWorld);
			}
			else
			{
				JointPos = xAxis * values.lengthB;
				effPos += JointPos;
				JointPos = lerp(effPos, values.eff.getTranslation(MSpace::kWorld), values.pin);
			}
		}
		else
		{
			JointPos = xAxis * values.lengthB;
			effPos += JointPos;
		}
		
		// output the rotation
		result = values.eff;
		result.setTranslation(effPos, MSpace::kWorld);
	}
	
	return result;
}

void* IKNode::creator()
{
	return new IKNode();
}

MStatus IKNode::initialize()
{
	MStatus status;
	MFnNumericAttribute nAttr;
	MFnMatrixAttribute mAttr;
	inRoot = mAttr.create("inRoot", "inRoot");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(inRoot);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	inIKEnd = mAttr.create("inIKEnd", "inIKEnd");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(inIKEnd);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	inPole = mAttr.create("inPole", "inPole");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(inPole);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	inMidParent = mAttr.create("inMidParent", "inMidParent");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(inMidParent);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	inEndParent = mAttr.create("inEndParent", "inEndParent");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(inEndParent);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	lengthA = nAttr.create("lengthA" , "lengthA" , MFnNumericData::kFloat , 0.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(lengthA);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	lengthB = nAttr.create("lengthB", "lengthB", MFnNumericData::kFloat, 0.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(lengthB);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	fatnessA = nAttr.create("fatnessA", "fatnessA", MFnNumericData::kFloat, 1.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(fatnessA);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	fatnessB = nAttr.create("fatnessB", "fatnessB", MFnNumericData::kFloat, 1.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(fatnessB);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	softness = nAttr.create("softness", "softness", MFnNumericData::kFloat, 0.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(softness);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	stretchly = nAttr.create("stretchly", "stretchly", MFnNumericData::kFloat, 1.5);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(stretchly);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	reverse = nAttr.create("reverse", "reverse", MFnNumericData::kFloat, 0.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(reverse);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	negate = nAttr.create("negate", "negate", MFnNumericData::kBoolean, false);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(negate);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	slide = nAttr.create("slide", "slide", MFnNumericData::kFloat, 0.5);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(slide);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	roll = nAttr.create("roll", "roll", MFnNumericData::kFloat, 0.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(roll);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	pin = nAttr.create("pin", "pin", MFnNumericData::kFloat, 0.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(pin);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	outMid = mAttr.create("outMid", "outMid");
	mAttr.setKeyable(false);
	mAttr.setStorable(false);
	mAttr.setConnectable(true);
	addAttribute(outMid);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	outEnd = mAttr.create("outEnd", "outEnd");
	mAttr.setKeyable(false);
	mAttr.setStorable(false);
	mAttr.setConnectable(true);
	addAttribute(outEnd);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	attributeAffects(lengthA, outMid);
	attributeAffects(lengthB, outMid);
	attributeAffects(fatnessA, outMid);
	attributeAffects(fatnessB, outMid);
	attributeAffects(softness, outMid);
	attributeAffects(stretchly, outMid);
	attributeAffects(reverse, outMid);
	attributeAffects(negate, outMid);
	attributeAffects(slide, outMid);
	attributeAffects(inRoot, outMid);
	attributeAffects(inIKEnd, outMid);
	attributeAffects(inPole, outMid);
	attributeAffects(inMidParent, outMid);
	attributeAffects(inEndParent, outMid);
	attributeAffects(roll, outMid);
	attributeAffects(pin, outMid);

	attributeAffects(lengthA, outEnd);
	attributeAffects(lengthB, outEnd);
	attributeAffects(fatnessA, outEnd);
	attributeAffects(fatnessB, outEnd);
	attributeAffects(softness, outEnd);
	attributeAffects(stretchly, outEnd);
	attributeAffects(reverse, outEnd);
	attributeAffects(negate, outEnd);
	attributeAffects(slide, outEnd);
	attributeAffects(inRoot, outEnd);
	attributeAffects(inIKEnd, outEnd);
	attributeAffects(inPole, outEnd);
	attributeAffects(inMidParent, outEnd);
	attributeAffects(inEndParent, outEnd);
	attributeAffects(roll, outEnd);
	attributeAffects(pin, outEnd);
	
	return MS::kSuccess;
}

MString IKNode::GetNodeName()
{
	return NodeName;
}

MTypeId IKNode::GetNodeID()
{
	return NodeID;
}


