#ifndef CORE_H
#define CORE_H

#include <iostream>
#include <string>
#include <maya/MMatrix.h>
#include <QtCore/QString>
#include <maya/MDoubleArray.h>
#include <QtCore/QList>
#include <QtCore/QJsonArray>
#include <QtCore/QJsonObject>
#include <QtCore/QJsonValue>
#include <maya/MIntArray.h>
#include <maya/MMatrixArray.h>
#include <math.h>
#include <vector>
#include <map>
using namespace std;

struct WeightsInfo
{
	MMatrix mat;
	double weight;
};

double bezier_v(vector<double> p, double t)
{
	return p[0]*pow(1-t, 3.0) + 3*p[1]*t*pow(1-t,2.0) + 3*p[2]*pow(t,2.0)*(1-t) + p[3]*pow(t,3.0);

}

//double bezier_t(QList<double> p, double v)
//{
//	double min_t = 0.0;
//	double max_t = 1.0;
//	while (true)
//	{
//		double t = (min_t + max_t) / 2.0;
//		double error_range = bezier_v(p, t) - v;
//		if (error_range > 0.0001)
//		{
//		}
//	}
//}
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

template<typename cvTypeName>
vector<WeightsInfo> pointOnCurveWeights(cvTypeName cvs, double t, double degree)
{
	unsigned i, j, k, w;
	vector<WeightsInfo> weightsArray;
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

		WeightsInfo arr;
		arr.mat = cvs[i];
		arr.weight = weight;

		weightsArray.push_back(arr);
	}
	return weightsArray;
}




















#endif