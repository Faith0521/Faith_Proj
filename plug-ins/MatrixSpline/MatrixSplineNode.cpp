#include "MatrixSplineNode.h"

#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>

#include <maya/MGlobal.h>


MTypeId     MatrixSpline::NodeID( 0x00a21 );


MObject     MatrixSpline::input;        
MObject     MatrixSpline::output;       

MatrixSpline::MatrixSpline() {}
MatrixSpline::~MatrixSpline() {}

MStatus MatrixSpline::compute( const MPlug& plug, MDataBlock& data )

{
	MStatus status;

	return MS::kSuccess;
}

void* MatrixSpline::creator()
{
	return new MatrixSpline();
}

MStatus MatrixSpline::initialize()
{
	return MS::kSuccess;

}

QJsonArray MatrixSpline::pointOnCurveWeights(MIntArray cvs, double t, int degree)
{
	unsigned i,j,k,w;
	QJsonArray weightsArray;
	int order = degree + 1;
	MDoubleArray knots = defaultKnots(cvs.length(), degree);

	// Remap the t value to the range of knot values.
	double min = knots[order] - 1.0;
	double max = knots[knots.length() - 1 - order] + 1.0;
	double t_ = (t * (max - min)) + min;

	// Determine which segment the t lies in
	int segment = degree;
	for (i=order; i<knots.length()-order; i++)
	{
		if (knots[i] <= t_)
		{
			segment = i + order;
		}
	}

	QList<double> cvs_;
	for (i=0; i<degree + 1; i++)
	{
		cvs_.append(cvs[i + segment - degree]);
	}

	// Run a modified version of de Boors algorithm
	QList<QJsonObject> cvWeights;
	for (j= 0; j < cvs_.length(); j++)
	{
		QJsonObject cvObject;
		cvObject.insert(QString(j), QJsonValue(1.0));
		cvWeights.append(cvObject);
	}
	for (k=1; k<degree+1; k++)
	{
		for (j=degree; j<k-1; j--)
		{
			int right = j + 1 + segment - k;
			int left = j + segment - degree;
			double alpha = (t_ - knots[left]) / (knots[right] - knots[left]);

			QJsonObject weights;
			for (auto iter = cvWeights[j].begin(); iter != cvWeights[j].end(); iter++)
			{ 
				double weight = iter.value().toDouble();
				weights.insert(iter.key(), QJsonValue(weight * alpha));
			}
			for (auto iter = cvWeights[j-1].begin(); iter != cvWeights[j-1].end(); iter++)
			{
				double weight = iter.value().toDouble();
				double data = weight * (1 - alpha);
				QJsonArray array;
				if (weights.contains(iter.key()))
				{
					array.append(weights[iter.key()].toDouble());
					array.append(data);
					weights[iter.key()] = QJsonValue(array);
				}
				else
				{
					weights[iter.key()] = QJsonValue(data);
				}
			}

			cvWeights[j] = weights;
				
		}
	}
	for (auto iter = cvWeights[degree].begin(); iter != cvWeights[degree].end(); iter++)
	{
		weightsArray.append(QJsonValue(cvs_[iter.key().toInt()]));
		weightsArray.append(iter.value());
	}

	return weightsArray;
}

MDoubleArray MatrixSpline::defaultKnots(int count, int degree)
{
	unsigned i,j,k;

	MDoubleArray knots;
	for (i=0; i<degree; i++)
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

