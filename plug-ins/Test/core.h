#ifndef CORE_H
#define CORE_H

#include <iostream>
#include <string>
#include <maya/MMatrix.h>
#include <QtCore/QString>
#include <maya/MDoubleArray.h>
#include <maya/MFnSkinCluster.h>
#include <maya/MIntArray.h>
#include <maya/MVector.h>
#include <maya/MQuaternion.h>
#include <maya/MPxTransformationMatrix.h>
#include <maya/MDagPath.h>
#include <maya/MGlobal.h>
#include <QtCore/QList>
#include <QtCore/QJsonArray>
#include <QtCore/QJsonObject>
#include <QtCore/QJsonValue>
#include <QtCore/QVariant>
#include <maya/MIntArray.h>
#include <maya/MMatrixArray.h>
#include <math.h>
#include <vector>
#include <map>
#include <unordered_map>
#include <any>
using namespace std;

#define pi 3.1415926535897932384626433832795

struct WeightInfo
{
	MMatrix		mat;
	double		weight;
};

struct weightInfo2
{
	int			num;
	double		weight;
};

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
	for (i = order; i < knots.length() - order; i++)
	{
		if (knots[i] <= t_)
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
	for (j = 0; j < _cvs_.length(); j++)
	{
		map<int, double> cvObject;
		cvObject.insert(map<int, double>::value_type(j, 1.0));
		//cvObject[j] = 1.0;
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
	for (i = 0; i < cvWeights[degree].size(); i++)
	{
		double weight = cvWeights[degree][i];

		Ttype arr;
		arr.mat = cvs[i];
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
	for (i = order; i < knots.length() - order; i++)
	{
		if (knots[i] <= t_)
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
	vector<weightInfo2> cvWeights;
	for (j = 0; j < degree_ + 1; j++)
	{
		double weight = weights_[j];
		int cv0 = j + segment - degree_;
		int cv1 = j + segment - degree_ - 1;
		double alpha = weight * (degree_ + 1) / (knots[j + segment + 1] - knots[j + segment - degree_]);

		weightInfo2 info1;
		info1.num = cvs_[cv0];
		info1.weight = alpha;

		weightInfo2 info2;
		info2.num = cvs_[cv1];
		info2.weight = -alpha;

		cvWeights.push_back(info1);
		cvWeights.push_back(info2);
	}

	for (i = 0; i < cvWeights.size(); i++)
	{
		double weight = cvWeights[i].weight;
		int num = cvWeights[i].num;
		Ttype weightInfos;
		MMatrix matrix = cvs[num];
		weightInfos.mat = matrix;
		weightInfos.weight = weight;
		tangentWeights.push_back(weightInfos);
	}

	return tangentWeights;
}

MMatrixArray calculateMatrix(int count, int pCount, int degree,
	MMatrixArray cvMatricies, MVector aimAxis,
	MVector upAxis)
{
	MMatrixArray result;
	unsigned i, j;

	for (i = 0; i < pCount; i++)
	{
		double t = double(i) / double(pCount - 1);
		vector<WeightInfo> pointMatrixWeights = pointOnCurveWeights<WeightInfo, MMatrixArray>(cvMatricies, t, degree);
		vector<WeightInfo> tangentMatrixWeights = tangentOnCurveWeights<WeightInfo, MMatrixArray>(cvMatricies, t, degree);

		// pointMatrix
		MMatrixArray pointSumArray;
		for (j = 0; j < pointMatrixWeights.size(); j++)
		{
			MMatrix matrix = pointMatrixWeights[j].mat;
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
			MMatrix matrix = tangentMatrixWeights[j].mat;
			double weight = tangentMatrixWeights[j].weight;
			MMatrix multMat = weight * matrix;
			tangentSumArray.append(multMat);
		}

		// do Something like wtAddMatrix node
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
		MVector U = aimVect.normal();
		MVector V = MGlobal::upAxis();
		MVector W = (U ^ V).normal();
		V = W ^ U;
		MQuaternion quat;
		MQuaternion quat_U = MQuaternion(aimAxis, U);
		quat = quat_U;
		MVector upRotated = upAxis.rotateBy(quat);
		double angle = acos(upRotated * V);
		MQuaternion quat_V = MQuaternion(angle, U);
		if (!V.isEquivalent(upRotated.rotateBy(quat_V), 1.0e-5))
		{
			angle = (2 * pi) - angle;
			quat_V = MQuaternion(angle, U);
		}
		quat *= quat_V;
		MPxTransformationMatrix translate_trMat = MPxTransformationMatrix(pointMat);
		MTransformationMatrix tr_mat;
		tr_mat.setTranslation(translate_trMat.translation(), MSpace::kWorld);
		tr_mat.setRotationQuaternion(quat.x, quat.y, quat.z, quat.w);
		result.append(tr_mat.asMatrix());
	}

	return result;
}



















#endif