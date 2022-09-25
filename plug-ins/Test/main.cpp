#include "core.h"

//QList<WeightsInfo> tangentOnCurveWeights(MMatrixArray cvs, double t, int degree)
//{
//	unsigned i, j, k, r;
//	QList<WeightsInfo> tangentWeights;
//
//	int order = degree + 1;
//	MDoubleArray knots = defaultKnots(cvs.length(), degree);
//
//	double min = knots[order] - 1.0;
//	double max = knots[knots.length() - 1 - order] + 1.0;
//	double t_ = (t * (max - min)) + min;
//
//	// Determine which segment the t lies in
//	int segment = degree;
//	for (i = order; i < knots.length() - order; i++)
//	{
//		if (knots[i] <= t_)
//		{
//			segment = i + order;
//		}
//	}
//
//	QList<int> cvs_;
//	for (i = 0; i < cvs.length(); i++)
//	{
//		cvs_.append(i);
//	}
//
//	int degree_ = degree - 1;
//	QList<QJsonObject> qWeights;
//	for (i=0; i<degree_ + 1; i++)
//	{
//		QJsonObject cvObject;
//		cvObject.insert(QString::number(i, 10), 1.0);
//		qWeights.append(cvObject);
//	}
//
//	// Get the DeBoor weights for this lower degree curve
//	for (r=1; r<degree_+1;r++)
//	{
//		for (j=degree_; j>r-1; j--)
//		{
//			int right = j + 1 + segment - r;
//			int left = j + segment - degree_;
//			double alpha = (t_ - knots[left]) / (knots[right] - knots[left]);
//
//			QJsonObject weights;
//			for (auto iter = qWeights[j].begin(); iter != qWeights[j].end(); iter++)
//			{
//				double weight = iter.value().toDouble();
//				weights.insert(iter.key(), QJsonValue(weight * alpha));
//			}
//			for (auto iter = qWeights[j-1].begin(); iter != qWeights[j-1].end(); iter++)
//			{
//				double weight = iter.value().toDouble();
//				QString key_str = iter.key();
//				if (weights.contains(iter.key()))
//				{
//					double r_weight = weights[key_str].toDouble();
//					weights[key_str] = r_weight + weight * (1 - alpha);
//				}
//				else
//				{
//					weights.insert(key_str, weight * (1 - alpha));
//				}
//			}
//			qWeights[j] = weights;
//		}
//	}
//	QJsonObject weights = qWeights[degree_];
//
//	// Take the lower order weights and match them to our actual cvs
//	QList<WeightsInfo> cvWeights;
//	for (j=0; j<degree_+1; j++)
//	{
//		double weight = weights[QString::number(j)].toDouble();
//		int cv0 = j + segment - degree_;
//		int cv1 = j + segment - degree_ - 1;
//		double alpha = weight * (degree_ + 1) / (knots[j + segment + 1] - knots[j + segment - degree_]);
//
//		WeightsInfo info1;
//		info1.mat = cvs[cv0];
//		info1.weight = alpha;
//
//		WeightsInfo info2;
//		info2.mat = cvs[cv1];
//		info2.weight = -alpha;
//
//		cvWeights.append(info1);
//		cvWeights.append(info2);
//	}
//
//	for (i=0; i<cvWeights.size(); i++)
//	{
//		double weight = cvWeights[i].weight;
//		WeightsInfo weightInfo;
//		weightInfo.mat = cvs[i];
//		weightInfo.weight = weight;
//		tangentWeights.append(weightInfo);
//	}
//
//	return tangentWeights;
//}

//MMatrix calculateSpline(int count, int pCount, int degree, MMatrixArray cvMatricies)
//{
//	unsigned i, j;
//	MMatrix resultMat;
//
//	for (i=0; i<pCount; i++)
//	{
//		double t = double(i) / double(pCount - 1);
//		vector<WeightsInfo> pointMatrixWeights = pointOnCurveWeights(cvMatricies, t, degree);
//		MMatrixArray sumArray;
//		for (j=0; j< pointMatrixWeights.size();j++)
//		{
//			MMatrix matrix = pointMatrixWeights[j].mat;
//			double weight = pointMatrixWeights[j].weight;
//			MMatrix multMat = weight * matrix;
//			sumArray.append(multMat);
//		}
//
//		// do Something like wtAddMatrix node
//		MMatrix weightSum = sumArray[0];
//		if (cvMatricies.length() == 1)
//		{
//			weightSum = sumArray[0];
//		}
//		else
//		{
//			for (j = 1; j < sumArray.length(); j++)
//			{
//				weightSum += sumArray[j];
//			}
//		}
//
//
//	}
//
//	return resultMat;
//}


int main()
{
	unsigned i, j;
	MMatrixArray matArray;
	for (i=0;i<4;i++)
	{
		MMatrix mat;
		matArray.append(mat);
	}

	vector<WeightsInfo> infoList = pointOnCurveWeights(matArray, 0.3, 3);
	for (i=0; i<infoList.size(); i++)
	{
		WeightsInfo info = infoList[i];
		cout << info.mat << info.weight << endl;
	}
}