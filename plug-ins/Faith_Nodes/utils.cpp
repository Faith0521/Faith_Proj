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