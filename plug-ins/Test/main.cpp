#include "core.h"



int main()
{
	unsigned i;
	double cv1[4][4] = {
		{1,0,0,0},
		{0,1,0,0},
		{0,0,1,0},
		{0,0,0,1}
	};

	double cv2[4][4] = {
		{1,0,0,0},
		{0,1,0,0},
		{0,0,1,0},
		{5,4,0,1}
	};

	double cv3[4][4] = {
		{1,0,0,0},
		{0,1,0,0},
		{0,0,1,0},
		{10,0,0,1}
	};

	double cv4[4][4] = {
		{1,0,0,0},
		{0,1,0,0},
		{0,0,1,0},
		{15,0,0,1}
	};

	MMatrix cv_mat1(cv1);
	MMatrix cv_mat2(cv2);
	MMatrix cv_mat3(cv3);
	MMatrix cv_mat4(cv4);

	MMatrixArray cmats;
	cmats.append(cv_mat1);
	cmats.append(cv_mat2);
	cmats.append(cv_mat3);
	cmats.append(cv_mat4);

	MVector aim = MVector::xAxis;
	MVector up = MVector::yAxis;

	MMatrixArray result = calculateMatrix(4, 6, 3, cmats, aim, up);
	for (i=0;i<result.length();i++)
	{
		cout << result[i] << endl;
	}

}