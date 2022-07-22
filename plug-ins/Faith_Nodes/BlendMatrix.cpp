#include "Faith_solvers.h"
#include "utils.cpp"

MString BlendMatrix::NodeName = "FAITH_BlendMatrix";
MTypeId BlendMatrix::NodeID = MTypeId(0x0016);

MObject BlendMatrix::aOutputMatrix;
MObject BlendMatrix::aOffsetMatrix;
MObject BlendMatrix::aRestMatrix;
MObject BlendMatrix::aParentInverseMatrix;
MObject BlendMatrix::aBlendInputMatrix;
MObject BlendMatrix::aBlendOffsetMatrix;
MObject BlendMatrix::aDriverRotationOffset;
MObject BlendMatrix::aDriverRotationOffsetX;
MObject BlendMatrix::aDriverRotationOffsetY;
MObject BlendMatrix::aDriverRotationOffsetZ;
MObject BlendMatrix::aBlendTranslateWeight;
MObject BlendMatrix::aBlendRotateWeight;
MObject BlendMatrix::aBlendScaleWeight;
MObject BlendMatrix::aBlendShearWeight;
MObject BlendMatrix::aBlendMatrix;

BlendMatrix::BlendMatrix(){}

BlendMatrix::~BlendMatrix(){}

MStatus BlendMatrix::initialize() {
	MStatus status;

	MFnCompoundAttribute cAttr;
	MFnMatrixAttribute mAttr;
	MFnNumericAttribute nAttr;
	MFnUnitAttribute uAttr;

	aOutputMatrix = mAttr.create("outputMatrix", "outputMatrix");
	mAttr.setWritable(false);
	mAttr.setStorable(false);
	addAttribute(aOutputMatrix);

	aOffsetMatrix = mAttr.create("offsetMatrix", "offsetMatrix");
	mAttr.setWritable(true);
	mAttr.setStorable(true);
	mAttr.setReadable(false);
	addAttribute(aOffsetMatrix);
	attributeAffects(aOffsetMatrix, aOutputMatrix);

	aRestMatrix = mAttr.create("restMatrix", "restMatrix");
	mAttr.setWritable(true);
	mAttr.setStorable(true);
	mAttr.setReadable(false);
	addAttribute(aRestMatrix);
	attributeAffects(aRestMatrix, aOutputMatrix);

	aParentInverseMatrix = mAttr.create("ParentInverseMatrix", "ParentInverseMatrix");
	mAttr.setWritable(true);
	mAttr.setStorable(true);
	mAttr.setReadable(false);
	addAttribute(aParentInverseMatrix);
	attributeAffects(aParentInverseMatrix, aOutputMatrix);

	aBlendInputMatrix = mAttr.create("blendInputMatrix", "blendInputMatrix");
	mAttr.setWritable(true);
	mAttr.setStorable(true);
	mAttr.setReadable(false);

	aBlendOffsetMatrix = mAttr.create("blendOffsetMatrix", "blendOffsetMatrix");
	mAttr.setWritable(true);
	mAttr.setStorable(true);
	mAttr.setReadable(false);

	aDriverRotationOffsetX = nAttr.create("driverRotationOffsetX", "driverRotationOffsetX", MFnNumericData::kDouble);
	nAttr.setKeyable(true);
	nAttr.setMin(-360.0);
	nAttr.setMax(360.0);
	addAttribute(aDriverRotationOffsetX);

	aDriverRotationOffsetY = nAttr.create("driverRotationOffsetY", "driverRotationOffsetY", MFnNumericData::kDouble);
	nAttr.setKeyable(true);
	nAttr.setMin(-360.0);
	nAttr.setMax(360.0);
	addAttribute(aDriverRotationOffsetY);

	aDriverRotationOffsetZ = nAttr.create("driverRotationOffsetZ", "driverRotationOffsetZ", MFnNumericData::kDouble);
	nAttr.setKeyable(true);
	nAttr.setMin(-360.0);
	nAttr.setMax(360.0);
	addAttribute(aDriverRotationOffsetZ);

	aDriverRotationOffset = nAttr.create("driverRotationOffset", "driverRotationOffset", aDriverRotationOffsetX, aDriverRotationOffsetY, aDriverRotationOffsetZ);
	nAttr.setKeyable(true);
	nAttr.setDefault(0.0, 0.0, 0.0);
	addAttribute(aDriverRotationOffset);
	attributeAffects(aDriverRotationOffset, aOutputMatrix);

	aBlendTranslateWeight = nAttr.create("blendTranslateWeight", "blendTranslateWeight", MFnNumericData::kFloat, 1);
	nAttr.setKeyable(true);
	nAttr.setMin(0.0);

	aBlendRotateWeight = nAttr.create("blendRotateWeight", "blendRotateWeight", MFnNumericData::kFloat, 1);
	nAttr.setKeyable(true);
	nAttr.setMin(0.0);

	aBlendScaleWeight = nAttr.create("blendScaleWeight", "blendScaleWeight", MFnNumericData::kFloat, 1);
	nAttr.setKeyable(true);
	nAttr.setMin(0.0);

	aBlendShearWeight = nAttr.create("blendShearWeight", "blendShearWeight", MFnNumericData::kFloat, 1);
	nAttr.setKeyable(true);
	nAttr.setMin(0.0);

	aBlendMatrix = cAttr.create("blendMatrix", "blendMatrix");
	cAttr.setReadable(true);
	cAttr.setArray(true);
	cAttr.addChild(aBlendInputMatrix);
	cAttr.addChild(aBlendOffsetMatrix);
	cAttr.addChild(aBlendTranslateWeight);
	cAttr.addChild(aBlendRotateWeight);
	cAttr.addChild(aBlendScaleWeight);
	cAttr.addChild(aBlendShearWeight);
	addAttribute(aBlendMatrix);
	attributeAffects(aBlendMatrix, aOutputMatrix);

	return MS::kSuccess;
}


void* BlendMatrix::creator() {
	return new BlendMatrix();
}

MStatus BlendMatrix::compute(const MPlug& plug, MDataBlock& data) {
	MStatus status;

	if (plug != aOutputMatrix) {
		return MS::kUnknownParameter;
	}

	MArrayDataHandle hBlendMatrix = data.inputArrayValue(aBlendMatrix);
	int count = hBlendMatrix.elementCount();

	MatrixXd translateMatrix = MatrixXd(count, 3);
	MatrixXd rotateMatrix = MatrixXd(count, 4);
	MatrixXd scaleMatrix = MatrixXd(count, 3);
	MatrixXd shearMatrix = MatrixXd(count, 3);

	VectorXd translateWeights = VectorXd(count);
	VectorXd rotateWeights = VectorXd(count);
	VectorXd scaleWeights = VectorXd(count);
	VectorXd shearWeights = VectorXd(count);

	for (int i = 0; i < count; ++i) {
		MDataHandle hBlendMatrixElement = hBlendMatrix.inputValue();

		// extract matrix components
		MMatrix inputBlendMatrix = hBlendMatrixElement.child(aBlendInputMatrix).asMatrix();
		MMatrix offsetBlendMatrix = hBlendMatrixElement.child(aBlendOffsetMatrix).asMatrix();

		MatrixComponents components = splitMatrix(offsetBlendMatrix * inputBlendMatrix);

		// populate component matrices
		translateMatrix.row(i) = components.translate;
		rotateMatrix.row(i) = components.rotate;
		scaleMatrix.row(i) = components.scale;
		shearMatrix.row(i) = components.shear;

		// populate component weights
		translateWeights(i) = hBlendMatrixElement.child(aBlendTranslateWeight).asFloat();
		rotateWeights(i) = hBlendMatrixElement.child(aBlendRotateWeight).asFloat();
		scaleWeights(i) = hBlendMatrixElement.child(aBlendScaleWeight).asFloat();
		shearWeights(i) = hBlendMatrixElement.child(aBlendShearWeight).asFloat();

		hBlendMatrix.next();
	}

	// extract rest matrix components
	MMatrix restMatrix = data.inputValue(aRestMatrix).asMatrix();
	MatrixComponents restComponents = splitMatrix(restMatrix);

	// calculate output matrix
	Vector3d outputTranslate = calculateComponent(translateMatrix, translateWeights, restComponents.translate);
	Vector4d outputRotate = calculateComponent(rotateMatrix, rotateWeights, restComponents.rotate);
	Vector3d outputScale = calculateComponent(scaleMatrix, scaleWeights, restComponents.scale);
	Vector3d outputShear = calculateComponent(shearMatrix, shearWeights, restComponents.shear);
	MMatrix outputMatrix = constructMatrix(outputTranslate, outputRotate, outputScale, outputShear);

	// extract offset matrix
	MMatrix offsetMatrix = data.inputValue(aOffsetMatrix).asMatrix();
	MMatrix parentInverse = data.inputValue(aParentInverseMatrix).asMatrix();

	MDataHandle hOut = data.outputValue(aOutputMatrix);
	
	MMatrix driver_matrix = offsetMatrix * outputMatrix * parentInverse;
	
	double in_driver_rotation_offset_x = data.inputValue(aDriverRotationOffsetX, &status).asDouble();
	double in_driver_rotation_offset_y = data.inputValue(aDriverRotationOffsetY, &status).asDouble();
	double in_driver_rotation_offset_z = data.inputValue(aDriverRotationOffsetZ, &status).asDouble();

	MEulerRotation  euler_off(
		degrees2radians(in_driver_rotation_offset_x),
		degrees2radians(in_driver_rotation_offset_y),
		degrees2radians(in_driver_rotation_offset_z));

	MTransformationMatrix driver_matrix_tfm(driver_matrix);
	// rotateBy
	MTransformationMatrix driver_matrix_off = driver_matrix_tfm.rotateBy(euler_off, MSpace::kPreTransform);

	hOut.setMMatrix(driver_matrix_off.asMatrix());
	hOut.setClean();

	return MS::kSuccess;
}


Vector3d BlendMatrix::calculateComponent(
	const MatrixXd& matrix,
	const VectorXd& weights,
	const Vector3d& rest
) {
	const double total = weights.sum();
	if (total == 0.0)
		return rest;
	else
		return (MatrixXd)(matrix.transpose() * (weights / total)).rowwise().sum();
}


Vector4d BlendMatrix::calculateComponent(
	const MatrixXd& matrix,
	const VectorXd& weights,
	const Vector4d& rest
) {
	const double total = weights.sum();
	if (total == 0.0)
		return rest;
	else
	{
		MatrixXd Q = matrix.transpose() * (weights / total);
		Q *= Q.transpose();

		Eigen::Index maxIndex;
		Eigen::SelfAdjointEigenSolver<MatrixXd> solver(Q);
		solver.eigenvalues().maxCoeff(&maxIndex);

		return solver.eigenvectors().col(maxIndex);
	}
}


MatrixComponents BlendMatrix::splitMatrix(const MMatrix& matrix) {
	MTransformationMatrix transform = MTransformationMatrix(matrix);

	double dRotateX; double dRotateY; double dRotateZ; double dRotateW;
	double dScale[3];
	double dShear[3];

	MVector vTranslate = transform.getTranslation(MSpace::kWorld);
	transform.getRotationQuaternion(dRotateX, dRotateY, dRotateZ, dRotateW);
	transform.getScale(dScale, MSpace::kWorld);
	transform.getShear(dShear, MSpace::kWorld);

	Vector3d translate(vTranslate.x, vTranslate.y, vTranslate.z);
	Vector4d rotate(dRotateX, dRotateY, dRotateZ, dRotateW);
	Vector3d scale(dScale[0], dScale[1], dScale[2]);
	Vector3d shear(dShear[0], dShear[1], dShear[2]);

	return MatrixComponents{ translate, rotate, scale, shear };
}


MMatrix BlendMatrix::constructMatrix(
	const Vector3d& translate,
	const Vector4d& rotate,
	const Vector3d& scale,
	const Vector3d& shear
) {
	MTransformationMatrix transform = MTransformationMatrix();

	MVector vTranslate = MVector(translate[0], translate[1], translate[2]);
	const double dScale[3] = { scale[0], scale[1], scale[2] };
	const double dShear[3] = { shear[0], shear[1], shear[2] };

	transform.setTranslation(vTranslate, MSpace::kWorld);
	transform.setRotationQuaternion(rotate[0], rotate[1], rotate[2], rotate[3]);
	transform.setScale(dScale, MSpace::kWorld);
	transform.setShear(dShear, MSpace::kWorld);

	return transform.asMatrix();
}