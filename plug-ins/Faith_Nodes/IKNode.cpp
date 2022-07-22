#include "Faith_solvers.h"
#include "utils.h"

MString IKNode::NodeName = "FAITH_IKFKCalculate";

MTypeId IKNode::NodeID = MTypeId(0x0015);

MObject IKNode::blend;
MObject IKNode::inRoot;
MObject IKNode::inEnd;
MObject IKNode::inPole;
MObject IKNode::fkA;
MObject IKNode::fkB;
MObject IKNode::fkC;
MObject IKNode::inAParent;
MObject IKNode::inBParent;
MObject IKNode::inCenterParent;
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
MObject IKNode::outputA;
MObject IKNode::outputB;
MObject IKNode::outputCenter;
MObject IKNode::outputEnd;

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
	MMatrix inputIKend = data.inputValue(inEnd).asMatrix();
	MMatrix inputPole = data.inputValue(inPole).asMatrix();
	MMatrix input_fkA = data.inputValue(fkA).asMatrix();
	MMatrix input_fkB = data.inputValue(fkB).asMatrix();
	MMatrix input_fkC = data.inputValue(fkC).asMatrix();

	MMatrix inputAParent = data.inputValue(inAParent).asMatrix();
	MMatrix inputBParent = data.inputValue(inBParent).asMatrix();
	MMatrix inputCenterParent = data.inputValue(inCenterParent).asMatrix();
	MMatrix inputEndParent = data.inputValue(inEndParent).asMatrix();

	double input_blend = (double)data.inputValue(blend).asFloat();

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

	FK_Info fkData;

	fkData.root = inputRoot;
	fkData.bone1 = input_fkA;
	fkData.bone2 = input_fkB;
	fkData.eff = input_fkC;

	fkData.lengthA = ikData.lengthA;
	fkData.lengthB = ikData.lengthB;
	fkData.negate = ikData.negate;

	MStringArray outNameArray;
	plug.name().split('.', outNameArray);
	MString outName = outNameArray[outNameArray.length() - 1];

	MTransformationMatrix result;
	if (input_blend == 0.0)
	{
		result = GetFKInfo(fkData, outName);
	}
	else if (input_blend == 1.0)
	{
		result = GetIKInfo(ikData, outName);
	}
	else
	{
		MTransformationMatrix ikbone1 = GetIKInfo(ikData, "outputA");
		MTransformationMatrix ikbone2 = GetIKInfo(ikData, "outputB");
		MTransformationMatrix ikeff = GetIKInfo(ikData, "outputEnd");

		MTransformationMatrix fkbone1 = GetFKInfo(fkData, "outputA");
		MTransformationMatrix fkbone2 = GetFKInfo(fkData, "outputB");
		MTransformationMatrix fkeff = GetFKInfo(fkData, "outputEnd");

		// remove scale to avoid shearing issue

		double noScale[3] = { 1,1,1 };
		ikbone1.setScale(noScale, MSpace::kWorld);
		ikbone2.setScale(noScale, MSpace::kWorld);
		ikeff.setScale(noScale, MSpace::kWorld);
		fkbone1.setScale(noScale, MSpace::kWorld);
		fkbone2.setScale(noScale, MSpace::kWorld);
		fkeff.setScale(noScale, MSpace::kWorld);

		// map the secondary transforms from global to local
		ikeff = mapWorldPoseToObjectSpace(ikbone2, ikeff);
		fkeff = mapWorldPoseToObjectSpace(fkbone2, fkeff);
		ikbone2 = mapWorldPoseToObjectSpace(ikbone1, ikbone2);
		fkbone2 = mapWorldPoseToObjectSpace(fkbone1, fkbone2);

		// now blend them!
		fkData.bone1 = interpolateTransform(fkbone1, ikbone1, input_blend);
		fkData.bone2 = interpolateTransform(fkbone2, ikbone2, input_blend);
		fkData.eff = interpolateTransform(fkeff, ikeff, input_blend);


		// now map the local transform back to global!
		fkData.bone2 = mapObjectPoseToWorldSpace(fkData.bone1, fkData.bone2);
		fkData.eff = mapObjectPoseToWorldSpace(fkData.bone2, fkData.eff);

		// calculate the result based on that
		result = GetFKInfo(fkData, outName);
	}
	
	MDataHandle h;
	
	if (plug == outputA)
	{
		h = data.outputValue(outputA);
		h.setMMatrix(result.asMatrix() * inputAParent.inverse());

		data.setClean(plug);
	}

	else if (plug == outputB)
	{
		h = data.outputValue(outputB);
		h.setMMatrix(result.asMatrix() * inputBParent.inverse());
		data.setClean(plug);
	}

	else if (plug == outputCenter)
	{
		h = data.outputValue(outputCenter);
		h.setMMatrix(result.asMatrix() * inputCenterParent.inverse());
		data.setClean(plug);
	}
	else if (plug == outputEnd)
	{
		h = data.outputValue(outputEnd);
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
	if (values.soft > 0 && distance2 > subst && values.pin != 1.0) 
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
	if (outputName == "outputA")
	{
		if (angleA != 0.0)
			xAxis = rotateVectorAlongAxis(xAxis, zAxis, -angleA);

		if (values.negate)
			xAxis *= -1;
		// cross the yAxis and normalize
		yAxis = zAxis ^ xAxis;
		yAxis.normalize();

		// output the rotation
		MQuaternion q = getQuaternionFromAxes(xAxis, yAxis, zAxis);
		result.setRotationQuaternion(q.x, q.y, q.z, q.w);

		// set the scaling + the position
		double s[3] = { values.lengthA, global_scale, global_scale };
		result.setScale(s, MSpace::kWorld);
		result.setTranslation(rootPos, MSpace::kWorld);
	}

	else if (outputName == "outputB")
	{
		if (angleA != 0.0)
			xAxis = rotateVectorAlongAxis(xAxis, zAxis, -angleA);

		// calculate the position of the elbow!
		JointPos = xAxis * values.lengthA;
		JointPos += rootPos;

		// check if we need to rotate the bone
		if (angleB != 0.0)
			xAxis = rotateVectorAlongAxis(xAxis, zAxis, -(angleB - PI));

		if (values.negate)
			xAxis *= -1;

		// cross the yAxis and normalize
		yAxis = zAxis ^ xAxis;
		yAxis.normalize();

		// output the rotation
		MQuaternion q = getQuaternionFromAxes(xAxis, yAxis, zAxis);
		result.setRotationQuaternion(q.x, q.y, q.z, q.w);

		// set the scaling + the position
		double s[3] = { values.lengthB, global_scale, global_scale };
		result.setScale(s, MSpace::kWorld);
		result.setTranslation(JointPos, MSpace::kWorld);
	}

	if (outputName == "outputCenter")
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

	else if (outputName == "outputEnd")
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

MTransformationMatrix IKNode::GetFKInfo(FK_Info values, MString outputName)
{
	MTransformationMatrix result;

	MVector xAxis, yAxis, zAxis;

	if (outputName == "outputA") {
		result = values.bone1;
		xAxis = values.bone2.getTranslation(MSpace::kWorld) - values.bone1.getTranslation(MSpace::kWorld);

		double scale[3] = { xAxis.length(), 1.0, 1.0 };
		result.setScale(scale, MSpace::kWorld);

		if (values.negate)
			xAxis *= -1;

		// cross the yAxis and normalize
		xAxis.normalize();

		zAxis = MVector(0, 0, 1);
		zAxis = zAxis.rotateBy(values.bone1.rotation());
		yAxis = zAxis ^ xAxis;

		// rotation
		MQuaternion q = getQuaternionFromAxes(xAxis, yAxis, zAxis);
		result.setRotationQuaternion(q.x, q.y, q.z, q.w);
	}
	else if (outputName == "outputB") {

		result = values.bone2;
		xAxis = values.eff.getTranslation(MSpace::kWorld) - values.bone2.getTranslation(MSpace::kWorld);

		double scale[3] = { xAxis.length(), 1.0, 1.0 };
		result.setScale(scale, MSpace::kWorld);

		if (values.negate)
			xAxis *= -1;

		// cross the yAxis and normalize
		xAxis.normalize();
		yAxis = MVector(0, 1, 0);
		yAxis = yAxis.rotateBy(values.bone2.rotation());
		zAxis = xAxis ^ yAxis;
		zAxis.normalize();
		yAxis = zAxis ^ xAxis;
		yAxis.normalize();

		// rotation
		MQuaternion q = getQuaternionFromAxes(xAxis, yAxis, zAxis);
		result.setRotationQuaternion(q.x, q.y, q.z, q.w);
	}
	else if (outputName == "outputCenter") {

		// Only +/-180 degree with this one but we don't get the shear issue anymore
		MTransformationMatrix t = mapWorldPoseToObjectSpace(values.bone1, values.bone2);
		MEulerRotation er = t.eulerRotation();
		er *= .5;
		MQuaternion q = er.asQuaternion();
		t.setRotationQuaternion(q.x, q.y, q.z, q.w);
		t = mapObjectPoseToWorldSpace(values.bone1, t);
		q = t.rotation();

		result.setRotationQuaternion(q.x, q.y, q.z, q.w);

		// rotation
		result.setTranslation(values.bone2.getTranslation(MSpace::kWorld), MSpace::kWorld);
	}

	else if (outputName == "outputEnd")
		result = values.eff;

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

	blend = nAttr.create("blend", "blend", MFnNumericData::kFloat, 0.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(blend);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	inRoot = mAttr.create("inRoot", "inRoot");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(inRoot);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	inEnd = mAttr.create("inIKEnd", "inIKEnd");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(inEnd);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	inPole = mAttr.create("inPole", "inPole");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(inPole);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	fkA = mAttr.create("fkA", "fkA");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(fkA);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	fkB = mAttr.create("fkB", "fkB");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(fkB);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	fkC = mAttr.create("fkC", "fkC");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(fkC);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	inAParent = mAttr.create("inAParent", "inAParent");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(inAParent);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	inBParent = mAttr.create("inBParent", "inBParent");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(inBParent);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	inCenterParent = mAttr.create("inCenterParent", "inCenterParent");
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setConnectable(true);
	addAttribute(inCenterParent);
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

	softness = nAttr.create("soft", "soft", MFnNumericData::kFloat, 0.0);
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

	roll = nAttr.create("twist", "twist", MFnNumericData::kFloat, 0.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(roll);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	pin = nAttr.create("pin", "pin", MFnNumericData::kFloat, 0.0);
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	addAttribute(pin);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	outputA = mAttr.create("outputA", "outputA");
	mAttr.setKeyable(false);
	mAttr.setStorable(false);
	mAttr.setConnectable(true);
	addAttribute(outputA);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	outputB = mAttr.create("outputB", "outputB");
	mAttr.setKeyable(false);
	mAttr.setStorable(false);
	mAttr.setConnectable(true);
	addAttribute(outputB);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	outputCenter = mAttr.create("outputCenter", "outputCenter");
	mAttr.setKeyable(false);
	mAttr.setStorable(false);
	mAttr.setConnectable(true);
	addAttribute(outputCenter);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	outputEnd = mAttr.create("outputEnd", "outputEnd");
	mAttr.setKeyable(false);
	mAttr.setStorable(false);
	mAttr.setConnectable(true);
	addAttribute(outputEnd);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	attributeAffects(blend, outputA);
	attributeAffects(inRoot, outputA);
	attributeAffects(inEnd, outputA);
	attributeAffects(inPole, outputA);
	attributeAffects(fkA, outputA);
	attributeAffects(fkB, outputA);
	attributeAffects(fkC, outputA);
	attributeAffects(inAParent, outputA);
	attributeAffects(inBParent, outputA);
	attributeAffects(inCenterParent, outputA);
	attributeAffects(inEndParent, outputA);
	attributeAffects(lengthA, outputA);
	attributeAffects(lengthB, outputA);
	attributeAffects(fatnessA, outputA);
	attributeAffects(fatnessB, outputA);
	attributeAffects(softness, outputA);
	attributeAffects(stretchly, outputA);
	attributeAffects(reverse, outputA);
	attributeAffects(negate, outputA);
	attributeAffects(slide, outputA);
	attributeAffects(roll, outputA);
	attributeAffects(pin, outputA);

	attributeAffects(blend, outputB);
	attributeAffects(inRoot, outputB);
	attributeAffects(inEnd, outputB);
	attributeAffects(inPole, outputB);
	attributeAffects(fkA, outputB);
	attributeAffects(fkB, outputB);
	attributeAffects(fkC, outputB);
	attributeAffects(inAParent, outputB);
	attributeAffects(inBParent, outputB);
	attributeAffects(inCenterParent, outputB);
	attributeAffects(inEndParent, outputB);
	attributeAffects(lengthA, outputB);
	attributeAffects(lengthB, outputB);
	attributeAffects(fatnessA, outputB);
	attributeAffects(fatnessB, outputB);
	attributeAffects(softness, outputB);
	attributeAffects(stretchly, outputB);
	attributeAffects(reverse, outputB);
	attributeAffects(negate, outputB);
	attributeAffects(slide, outputB);
	attributeAffects(roll, outputB);
	attributeAffects(pin, outputB);

	attributeAffects(blend, outputCenter);
	attributeAffects(inRoot, outputCenter);
	attributeAffects(inEnd, outputCenter);
	attributeAffects(inPole, outputCenter);
	attributeAffects(fkA, outputCenter);
	attributeAffects(fkB, outputCenter);
	attributeAffects(fkC, outputCenter);
	attributeAffects(inAParent, outputCenter);
	attributeAffects(inBParent, outputCenter);
	attributeAffects(inCenterParent, outputCenter);
	attributeAffects(inEndParent, outputCenter);
	attributeAffects(lengthA, outputCenter);
	attributeAffects(lengthB, outputCenter);
	attributeAffects(fatnessA, outputCenter);
	attributeAffects(fatnessB, outputCenter);
	attributeAffects(softness, outputCenter);
	attributeAffects(stretchly, outputCenter);
	attributeAffects(reverse, outputCenter);
	attributeAffects(negate, outputCenter);
	attributeAffects(slide, outputCenter);
	attributeAffects(roll, outputCenter);
	attributeAffects(pin, outputCenter);

	attributeAffects(blend, outputEnd);
	attributeAffects(inRoot, outputEnd);
	attributeAffects(inEnd, outputEnd);
	attributeAffects(inPole, outputEnd);
	attributeAffects(fkA, outputEnd);
	attributeAffects(fkB, outputEnd);
	attributeAffects(fkC, outputEnd);
	attributeAffects(inAParent, outputEnd);
	attributeAffects(inBParent, outputEnd);
	attributeAffects(inCenterParent, outputEnd);
	attributeAffects(inEndParent, outputEnd);
	attributeAffects(lengthA, outputEnd);
	attributeAffects(lengthB, outputEnd);
	attributeAffects(fatnessA, outputEnd);
	attributeAffects(fatnessB, outputEnd);
	attributeAffects(softness, outputEnd);
	attributeAffects(stretchly, outputEnd);
	attributeAffects(reverse, outputEnd);
	attributeAffects(negate, outputEnd);
	attributeAffects(slide, outputEnd);
	attributeAffects(roll, outputEnd);
	attributeAffects(pin, outputEnd);
	
	return MS::kSuccess;
}



