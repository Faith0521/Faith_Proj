#ifndef COMPUTE_H
#define COMPUTE_H

#include "SplitSkinWeights.h"

template<class T>
T sum(vector<T> arry)
{
	T first = 0;
	for (unsigned i=0; i<arry.size(); i++)
	{
		first += arry[i];
	}
	return first;
}

double distance(vector<double> p1, vector<double> p2)
{
	vector<double> arr;
	for (unsigned i = 0; i < 3; i++)
	{
		arr.push_back(pow((p1[i] - p2[i]),2));
	}
	return pow(sum<double>(arr), 0.5);
}

double bezier_v(vector<double> p, double t)
{
	return p[0] * pow(1 - t, 3.0) + 3 * p[1] * t * pow(1 - t, 2.0) + 3 * p[2] * pow(t, 2.0) * (1 - t) + p[3] * pow(t, 3.0);
}

double bezier_t(vector<double> p, double v)
{
	double min_t = 0.0;
	double max_t = 1.0;
	while (true)
	{
		double t = (min_t + max_t)/2.0;
		double error_range = bezier_v(p, t) - v;
		if (error_range > 0.0001)
		{
			max_t = t;
		}
		else if (error_range < -0.0001)
		{
			min_t = t;
		}
		else
		{
			return t;
		}
	}
}

double getWeight(double x, vector<double> xs, vector<double> ys)
{
	if (x <= 0.0)
	{
		return ys[0];
	}
	else if (x >= 1.0)
	{
		return ys[3];
	}
	double t = bezier_t(xs, x);
	return bezier_v(ys, t);
}

double ik_x(vector<double> v, vector<double> p)
{
	vector<double> sumVal_a;
	vector<double> sumVal_b;
	for (unsigned i=0; i<3; i++)
	{
		sumVal_a.push_back(v[i] * p[i]);
		sumVal_b.push_back(v[i]*v[i]);
	}
	return sum<double>(sumVal_a) / sum<double>(sumVal_b);
}

vector<double> ik_xs(vector<double> v, vector<double> p, vector<vector<double>> ps)
{
	vector<double> xVal_list;
	double x = ik_x(v, p);
	for (unsigned i=0; i<ps.size(); i++)
	{
		vector<double> p_ = ps[i];
		double value = ik_x(v, p_) - x;
		xVal_list.push_back(value);
	}
	return xVal_list;
}

vector<double> ik_weights(vector<double> wxs, vector<double> xs, vector<double> ys, double r)
{
	vector<double> weights;
	for (unsigned i=0; i<wxs.size(); i++)
	{
		weights.push_back(getWeight(wxs[i]/r + 0.5, xs, ys));
	}
	return weights;
}

vector<double> soft_weights(vector<double> wxs, vector<double> xs, vector<double> ys, double r)
{
	vector<double> weights;
	for (unsigned i = 0; i < wxs.size(); i++)
	{
		weights.push_back(getWeight(wxs[i] / r, xs, ys));
	}
	return weights;
}

vector<double> get_max_weights(MDoubleArray weights, int joint_length, int vtx_length)
{
	vector<double> max_weights;
	unsigned i, j;
	for (j = 0; j < vtx_length; j++)
	{
		vector<double> weightsArray;
		for (i = 0; i < joint_length; i++)
		{
			double value = weights[joint_length*j+i];
			weightsArray.push_back(value);
		}
		max_weights.push_back(sum<double>(weightsArray));
	}
	return max_weights;
}

vector<vector<double>> split_wx_matrix(vector<vector<vector<double>>> vps, vector<vector<double>> ps)
{
	vector<vector<double>> wx_matrix;
	for (unsigned i = 0; i < vps.size(); i++)
	{
		vector<vector<double>> vp = vps[i];
		vector<double> v = vp[0];
		vector<double> p = vp[1];
		vector<double> xList = ik_xs(v, p, ps);
		wx_matrix.push_back(xList);
	}
	return wx_matrix;
}

vector<double> split_weights(split_kw dict, vector<double> xs, vector<double> ys, double r)
{
	vector<double> weights;
	vector<double> wx_matrix;
	for (unsigned i=0; i<dict.wx_matrix[0].size(); i++)
	{
		wx_matrix.push_back(1.0);
	}


	vector<vector<double>> weight_matrix = { wx_matrix };

	for (unsigned i = 0; i < dict.wx_matrix.size(); i++)
	{
		vector<double> weights = ik_weights(dict.wx_matrix[i], xs, ys, r);

		vector<double> weights_;
		transform(weight_matrix[weight_matrix.size()-1].begin(), weight_matrix[weight_matrix.size() - 1].end(), weights.begin(),
			std::back_inserter(weights_),
			[](const auto& w1, const auto& w2)
			{
				return min(w1,w2);
			});
		weight_matrix.push_back(weights_);
		vector<double> wv;
		transform(weight_matrix[weight_matrix.size() - 1].begin(), weight_matrix[weight_matrix.size() - 1].end(), weight_matrix[weight_matrix.size() - 2].begin(),
			std::back_inserter(wv),
			[](const auto& w1, const auto& w2)
			{
				return (w2-w1);
			});
		weight_matrix[weight_matrix.size() - 2] = wv;
	}
	vector<vector<double>> weight_matrix_;
	for (unsigned i = 0; i < weight_matrix.size(); i++)
	{
		vector<double> wv;
		transform(weight_matrix[i].begin(), weight_matrix[i].end(), dict.max_weights.begin(),
			std::back_inserter(wv),
			[](const auto& w, const auto& m)
			{
				return (w*m);
			});
		weight_matrix_.push_back(wv);
	}

	Eigen::MatrixXd weight_Matrix(weight_matrix_.size(), dict.wx_matrix[0].size());

	for (unsigned i = 0; i < weight_matrix_.size(); i++)
	{
		for (unsigned j = 0; j < dict.wx_matrix[0].size(); j++)
		{
			weight_Matrix(i, j) = weight_matrix_[i][j];
		}
	}
	Eigen::MatrixXd weight_Matrix_transpose = weight_Matrix.transpose();

	for (unsigned i = 0; i < weight_Matrix_transpose.rows(); i++)
	{
		for (unsigned j = 0; j < weight_Matrix_transpose.cols(); j++)
		{
			weights.push_back(weight_Matrix_transpose(i, j));
		}
	}
	return weights;
}

vector<vector<double>> cloth_wx_matrix(vector<vector<double>> vtx_points, vector<vector<double>> joint_points)
{
	unsigned i, j;
	vector<vector<double>> wx_matrix;
	for (i = 0; i < joint_points.size(); i++)
	{
		vector<double> distArray;
		for (j = 0; j < vtx_points.size(); j++)
		{
			double dist = distance(vtx_points[j], joint_points[i]);
			distArray.push_back(dist);
		}
		wx_matrix.push_back(distArray);
	}
	return wx_matrix;
}

#endif // !COMPUTE_H

