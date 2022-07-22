#include "Faith_solvers.h"

double linearInterpolate(double first, double second, double blend)
{
	return first * (1 - blend) + second * blend;
}

MVector linearInterpolate(MVector v0, MVector v1, double blend)
{
	MVector v;
	v.x = linearInterpolate(v0.x, v1.x, blend);
	v.y = linearInterpolate(v0.y, v1.y, blend);
	v.z = linearInterpolate(v0.z, v1.z, blend);

	return v;
}

MVector rotateVectorAlongAxis(MVector v, MVector axis, double a) {

	// Angle as to be in radians

	double sa = sin(a / 2.0);
	double ca = cos(a / 2.0);

	MQuaternion q1 = MQuaternion(v.x, v.y, v.z, 0);
	MQuaternion q2 = MQuaternion(axis.x * sa, axis.y * sa, axis.z * sa, ca);
	MQuaternion q2n = MQuaternion(-axis.x * sa, -axis.y * sa, -axis.z * sa, ca);
	MQuaternion q = q2 * q1;
	q *= q2n;

	return MVector(q.x, q.y, q.z);
}

MQuaternion getQuaternionFromAxes(MVector vx, MVector vy, MVector vz)
{
	MMatrix m;
	m[0][0] = vx.x;
	m[0][1] = vx.y;
	m[0][2] = vx.z;
	m[1][0] = vy.x;
	m[1][1] = vy.y;
	m[1][2] = vy.z;
	m[2][0] = vz.x;
	m[2][1] = vz.y;
	m[2][2] = vz.z;

	MTransformationMatrix t(m);

	return t.rotation();
}

double clamp(double d, double min_value, double max_value) {

	d = std::max(d, min_value);
	d = std::min(d, max_value);
	return d;
}

int clamp(int d, int min_value, int max_value) {

	d = std::max(d, min_value);
	d = std::min(d, max_value);
	return d;
}

double smoothstep(double edge0, double edge1, double x) {
	// Scale, bias and saturate x to 0..1 range
	x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
	// Evaluate polynomial
	return x * x * (3 - 2 * x);
}

MTransformationMatrix mapWorldPoseToObjectSpace(MTransformationMatrix objectSpace, MTransformationMatrix pose) {
	return MTransformationMatrix(pose.asMatrix() * objectSpace.asMatrixInverse());
}

MTransformationMatrix  mapObjectPoseToWorldSpace(MTransformationMatrix objectSpace, MTransformationMatrix pose) {
	return MTransformationMatrix(pose.asMatrix() * objectSpace.asMatrix());
}

MTransformationMatrix interpolateTransform(MTransformationMatrix xf1, MTransformationMatrix xf2, double blend) {

	if (blend == 1.0)
		return xf2;
	else if (blend == 0.0)
		return xf1;

	// translate
	MVector t = linearInterpolate(xf1.getTranslation(MSpace::kWorld), xf2.getTranslation(MSpace::kWorld), blend);

	// scale
	double threeDoubles[3];
	xf1.getScale(threeDoubles, MSpace::kWorld);
	MVector xf1_scl(threeDoubles[0], threeDoubles[1], threeDoubles[2]);

	xf2.getScale(threeDoubles, MSpace::kWorld);
	MVector xf2_scl(threeDoubles[0], threeDoubles[1], threeDoubles[2]);

	MVector vs = linearInterpolate(xf1_scl, xf2_scl, blend);
	double s[3] = { vs.x, vs.y, vs.z };

	// rotate
	MQuaternion q = slerp(xf1.rotation(), xf2.rotation(), blend);

	// out
	MTransformationMatrix result;

	result.setTranslation(t, MSpace::kWorld);
	result.setRotationQuaternion(q.x, q.y, q.z, q.w);
	result.setScale(s, MSpace::kWorld);

	return result;
}

double radians2degrees(double a) {
	return a * 57.2957795;
}
double degrees2radians(double a) {
	return a * 0.0174532925;
}

double setRange(double oldMin, double oldMax, double newMin, double newMax, double value)
{
	double result = ((value - oldMin) / (oldMax - oldMin)* (newMax - newMin)) + newMin;
	if (result > newMax)
	{
		return newMax;
	}
	if (result < newMin)
	{
		return newMin;
	}
	else
	{
		return result;
	}
	
}
