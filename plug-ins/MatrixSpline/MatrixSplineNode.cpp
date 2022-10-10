#include "MatrixSplineNode.h"


MTypeId     MatrixSpline::NodeID(0x00a21);


MObject     MatrixSpline::amatrixIn;
MObject     MatrixSpline::aAxis;
MObject     MatrixSpline::amatrixOut;

MatrixSpline::MatrixSpline() {}
MatrixSpline::~MatrixSpline() {}

MStatus MatrixSpline::compute(const MPlug& plug, MDataBlock& data)

{
	MStatus status;
	unsigned i, j;

	MString axis_str = data.inputValue(aAxis).asString();
	//MVector aimVec = data.inputValue(aprimaryAxis).asFloatVector();
	//MVector upVec = data.inputValue(asecondaryAxis).asFloatVector();
	MStringArray str_array;
	axis_str.split(',', str_array);
	MVector aimVec;
	MVector upVec;

	map<string, MVector> axis_map;

	axis_map["+x"] = MVector::xAxis;
	axis_map["+y"] = MVector::yAxis;
	axis_map["+z"] = MVector::zAxis;

	axis_map["-x"] = -(MVector::xAxis);
	axis_map["-y"] = -(MVector::yAxis);
	axis_map["-z"] = -(MVector::zAxis);

	if (str_array.length() == 2)
	{
		if (axis_map.count(string(str_array[0].asChar())) > 0)
		{
			aimVec = axis_map[string(str_array[0].asChar())];
		}
		if (axis_map.count(string(str_array[1].asChar())) > 0)
		{
			upVec = axis_map[string(str_array[1].asChar())];
		}
		else
		{
			aimVec = MVector::xAxis;
			upVec = MVector::yAxis;
		}
	}
	else
	{
		aimVec = MVector::xAxis;
		upVec = MVector::yAxis;
	}

	MArrayDataHandle inMatrixArrayHandle = data.inputArrayValue(amatrixIn);
	MArrayDataHandle outMatrixArrayHandle = data.outputArrayValue(amatrixOut);

	int in_count = inMatrixArrayHandle.elementCount(&status);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	MMatrixArray cvMatricies;
	for (i = 0; i < in_count; i++)
	{
		inMatrixArrayHandle.jumpToElement(i);
		MMatrix matrix_in(inMatrixArrayHandle.inputValue(&status).asMatrix());
		cvMatricies.append(matrix_in);
	}

	int out_count = outMatrixArrayHandle.elementCount(&status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	MMatrixArray outMatrixArray = calculateMatrix(in_count, out_count, 3, cvMatricies, aimVec, upVec);
	outMatrixArray[0] = cvMatricies[0];
	if (out_count >= 2)
	{
		outMatrixArray[outMatrixArray.length() - 1] = cvMatricies[cvMatricies.length() - 1];
	}
	
	for (j = 0; j < out_count; j++)
	{
		outMatrixArrayHandle.jumpToElement(j);
		MDataHandle h = outMatrixArrayHandle.outputValue(&status);
		h.setMMatrix(outMatrixArray[j]);
	}

	data.setClean(plug);

	return MS::kSuccess;
}

void* MatrixSpline::creator()
{
	return new MatrixSpline();
}

MStatus MatrixSpline::initialize()
{
	MStatus status;
	MFnNumericAttribute nAttr;
	MFnMatrixAttribute mAttr;
	MFnCompoundAttribute cAttr;
	MFnTypedAttribute tAttr;

	amatrixOut = mAttr.create("matrixOut", "mao");
	mAttr.setArray(true);
	mAttr.setKeyable(false);
	mAttr.setStorable(false);
	mAttr.setWritable(false);
	addAttribute(amatrixOut);

	amatrixIn = mAttr.create("matrixIn", "mai");
	mAttr.setArray(true);
	mAttr.setKeyable(true);
	mAttr.setStorable(true);
	mAttr.setWritable(true);
	addAttribute(amatrixIn);
	attributeAffects(amatrixIn, amatrixOut);

	aAxis = tAttr.create("axis", "axis", MFnData::kString);
	nAttr.setStorable(true);
	nAttr.setWritable(true);
	addAttribute(aAxis);
	attributeAffects(aAxis, amatrixOut);

	return MS::kSuccess;
}

MDoubleArray defaultKnots(int count, int degree)
{
	unsigned i, j, k;

	MDoubleArray knots;
	for (i = 0; i < degree; i++)
	{
		knots.append(0);
	}
	for (j = 0; j < count - degree + 1; j++)
	{
		knots.append(j);
	}
	for (k = 0; k < degree; k++)
	{
		knots.append(count - degree);
	}

	return knots;
}

template<typename Ttype, typename cvTypeName>
vector<Ttype> pointOnCurveWeights(cvTypeName cvs, double t, double degree)
{
	unsigned i, j, k, w;
	vector<Ttype> weightsArray;
	int order = degree + 1;
	MDoubleArray knots = defaultKnots(cvs.length(), degree);

	MMatrixArray _cvs = cvs;
	MIntArray _cvs_;
	for (i = 0; i < cvs.length(); i++)
	{
		_cvs_.append(i);
	}

	// Remap the t value to the range of knot values.
	double min = knots[order] - 1.0;
	double max = knots[knots.length() - 1 - order] + 1.0;
	double t_ = (t * (max - min)) + min;

	// Determine which segment the t lies in
	int segment = degree;
	vector<int> indexes;
	for (i = order; i < knots.length() - order; i++)
	{
		indexes.push_back(i);
	}
	for (i = 0; i < indexes.size(); i++)
	{
		if (knots[indexes[i]] <= t_)
		{
			segment = i + order;
		}
	}
	// 创建一个存放矩阵列表序号的vector容器
	vector<int> cvs_;
	for (i = 0; i < degree + 1; i++)
	{
		cvs_.push_back(_cvs_[i + segment - degree]);
	}

	// Run a modified version of de Boors algorithm
	vector<map<int, double>> cvWeights;
	for (j = 0; j < cvs_.size(); j++)
	{
		map<int, double> cvObject;
		cvObject.insert(map<int, double>::value_type(cvs_[j], 1.0));
		cvWeights.push_back(cvObject);
	}

	for (k = 1; k < degree + 1; k++)
	{
		for (j = degree; j > k - 1; j--)
		{
			int right = j + 1 + segment - k;
			int left = j + segment - degree;
			double alpha = (t_ - knots[left]) / (knots[right] - knots[left]);

			map<int, double> weights;
			for (i = 0; i < cvWeights[j].size(); i++)
			{
				double weight = cvWeights[j][i];
				weights[i] = weight * alpha;
			}

			for (i = 0; i < cvWeights[j - 1].size(); i++)
			{
				double weight = cvWeights[j - 1][i];
				if (weights.count(i) > 0)
				{
					double r_weight = weights[i];
					weights[i] = r_weight + weight * (1 - alpha);
				}
				else
				{
					weights.insert(map<int, double>::value_type(i, weight * (1 - alpha)));
				}

			}

			cvWeights[j] = weights;
		}
	}
	map<int, double> cvWeights_ = cvWeights[degree];
	for (auto it = cvWeights_.begin(); it != cvWeights_.end(); it++)
	{
		int index = it->first;
		double weight = it->second;

		Ttype arr;
		arr.mat_num = cvs[index];
		arr.weight = weight;

		weightsArray.push_back(arr);
	}
	return weightsArray;
}

template<typename Ttype, typename cvTypeName>
vector<Ttype> tangentOnCurveWeights(cvTypeName cvs, double t, int degree)
{
	unsigned i, j, k, r;
	vector<Ttype> tangentWeights;

	int order = degree + 1;

	MDoubleArray knots = defaultKnots(cvs.length(), degree);

	double min = knots[order] - 1.0;
	double max = knots[knots.length() - 1 - order] + 1.0;
	double t_ = (t * (max - min)) + min;

	// Determine which segment the t lies in
	int segment = degree;
	vector<int> indexes;
	for (i = order; i < knots.length() - order; i++)
	{
		indexes.push_back(i);
	}
	for (i = 0; i < indexes.size(); i++)
	{
		if (knots[indexes[i]] <= t_)
		{
			segment = i + order;
		}
	}

	vector<int> cvs_;
	for (i = 0; i < cvs.length(); i++)
	{
		cvs_.push_back(i);
	}

	int degree_ = degree - 1;
	vector<map<int, double>> qWeights;
	for (i = 0; i < degree_ + 1; i++)
	{
		map<int, double> cvObject;
		cvObject.insert(map<int, double>::value_type(i, 1.0));
		qWeights.push_back(cvObject);
	}

	// Get the DeBoor weights for this lower degree curve
	for (r = 1; r < degree_ + 1; r++)
	{
		for (j = degree_; j > r - 1; j--)
		{
			int right = j + 1 + segment - r;
			int left = j + segment - degree_;
			double alpha = (t_ - knots[left]) / (knots[right] - knots[left]);

			map<int, double> weights;
			for (i = 0; i < qWeights[j].size(); i++)
			{
				double weight = qWeights[j][i];
				weights.insert(map<int, double>::value_type(i, weight * alpha));
			}
			for (i = 0; i < qWeights[j - 1].size(); i++)
			{
				double weight = qWeights[j - 1][i];

				if (weights.count(i) > 0)
				{
					double r_weight = weights[i];
					weights[i] = r_weight + weight * (1 - alpha);
				}
				else
				{
					weights.insert(map<int, double>::value_type(i, weight * (1 - alpha)));
				}
			}
			qWeights[j] = weights;
		}
	}
	map<int, double> weights_ = qWeights[degree_];

	// Take the lower order weights and match them to our actual cvs
	vector<WeightInfo<int>> cvWeights;
	for (j = 0; j < degree_ + 1; j++)
	{
		double weight = weights_[j];
		int cv0 = j + segment - degree_;
		int cv1 = j + segment - degree_ - 1;
		double alpha = weight * (degree_ + 1) / (knots[j + segment + 1] - knots[j + segment - degree_]);

		WeightInfo<int> info1;
		info1.mat_num = cvs_[cv0];
		info1.weight = alpha;

		WeightInfo<int> info2;
		info2.mat_num = cvs_[cv1];
		info2.weight = -alpha;

		cvWeights.push_back(info1);
		cvWeights.push_back(info2);
	}

	for (i = 0; i < cvWeights.size(); i++)
	{
		double weight = cvWeights[i].weight;
		int num = cvWeights[i].mat_num;
		
		Ttype weightInfos;
		MMatrix matrix = cvs[num];
		weightInfos.mat_num = matrix;
		weightInfos.weight = weight;
		tangentWeights.push_back(weightInfos);
	}

	return tangentWeights;
}

MMatrixArray MatrixSpline::calculateMatrix(int count, int pCount, int degree,
	MMatrixArray cvMatricies, MVector aimAxis,
	MVector upAxis)
{
	MMatrixArray result;
	unsigned i, j;

	for (i = 0; i < pCount; i++)
	{
		double t = double(i) / double(pCount - 1);
		vector<WeightInfo<MMatrix>> pointMatrixWeights = pointOnCurveWeights<WeightInfo<MMatrix>, MMatrixArray>(cvMatricies, t, degree);
		vector<WeightInfo<MMatrix>> tangentMatrixWeights = tangentOnCurveWeights<WeightInfo<MMatrix>, MMatrixArray>(cvMatricies, t, degree);

		// pointMatrix
		MMatrixArray pointSumArray;
		for (j = 0; j < pointMatrixWeights.size(); j++)
		{
			MMatrix matrix = pointMatrixWeights[j].mat_num;
			double weight = pointMatrixWeights[j].weight;
			MMatrix multMat = weight * matrix;
			pointSumArray.append(multMat);
		}

		// do Something like wtAddMatrix node
		MMatrix pointMat = pointSumArray[0];
		if (cvMatricies.length() == 1)
		{
			pointMat = pointSumArray[0];
		}
		else
		{
			for (j = 1; j < pointSumArray.length(); j++)
			{
				pointMat += pointSumArray[j];
			}
		}

		// tangentMatrix
		MMatrixArray tangentSumArray;
		for (j = 0; j < tangentMatrixWeights.size(); j++)
		{
			MMatrix matrix = tangentMatrixWeights[j].mat_num;
			double weight = tangentMatrixWeights[j].weight;
			MMatrix multMat = weight * matrix;
			tangentSumArray.append(multMat);
		}

		MMatrix aimMat = tangentSumArray[0];
		if (cvMatricies.length() == 1)
		{
			aimMat = tangentSumArray[0];
		}
		else
		{
			for (j = 1; j < tangentSumArray.length(); j++)
			{
				aimMat += tangentSumArray[j];
			}
		}

		// aimMatrix
		MVector aimVect = MPxTransformationMatrix(aimMat).translation();
		MVector pointVec = MPxTransformationMatrix(pointMat).translation();
		aimVect.normalize();

		MVector U = aimVect.normal();
		U.normalize();

		MVector worldUp = MVector::zAxis;
		MVector V = worldUp * pointMat;
		V.normalize();

		MVector W = (U ^ V).normal();
		W.normalize();

		V = W ^ U;
		MQuaternion quat;
		MQuaternion quat_u(aimAxis, U);
		quat = quat_u;

		MVector upRotated = upAxis.rotateBy(quat);
		double angle = acos(upRotated * V);
		MQuaternion quat_v(angle, U);

		if (!V.isEquivalent(upRotated.rotateBy(quat_v), 1.0e-5))
		{
			angle = (2 * pi) - angle;
			quat_v = MQuaternion(angle, U);
		}

		quat *= quat_v;

		MPxTransformationMatrix point_matrix(pointMat);
		MTransformationMatrix finalMatrix;

		finalMatrix.setRotationQuaternion(quat.x, quat.y, quat.z, quat.w);
		finalMatrix.setTranslation(point_matrix.translation(), MSpace::kWorld);

		result.append(finalMatrix.asMatrix());
	}

	return result;
}