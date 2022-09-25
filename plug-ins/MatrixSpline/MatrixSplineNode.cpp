#include "MatrixSplineNode.h"


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

MDoubleArray MatrixSpline::defaultKnots(int count, int degree)
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

vector<WeightInfo> MatrixSpline::pointOnCurveWeights(MMatrixArray cvs, double t, int degree)
{
	unsigned i, j, k, w;
	vector<WeightInfo> weightsArray;
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

		WeightInfo info;
		info.mat = cvs[i];
		info.weight = weight;

		weightsArray.push_back(info);
	}

	return weightsArray;
}




