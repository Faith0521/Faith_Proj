#include "SplitSkinWeights.h"
#include "compute.h"

skinInformation SplitSkin::skinInfo;

MStatus SplitSkin::getShapeNode(MDagPath& path)
{
	MStatus status;

	if (path.apiType() == MFn::kMesh)
	{
		return MS::kSuccess;
	}

	if (path.apiType() != MFn::kTransform)
	{
		return MS::kFailure;
	}

	unsigned int numShapes;
	path.numberOfShapesDirectlyBelow(numShapes);

	if (!numShapes) return MS::kFailure;

	for (int i = 0; i < numShapes; i++)
	{
		status = path.extendToShapeDirectlyBelow(i);
		CHECK_MSTATUS_AND_RETURN_IT(status);

		if (path.apiType() == MFn::kMesh)
		{
			MFnDagNode fnNode = path.node();
			if (!fnNode.isIntermediateObject())
			{
				return MS::kSuccess;
			}
		}
		path.pop();
	}
	return MS::kFailure;
}

MStatus SplitSkin::getWeightValue(MObject& m_oSkinCluster, vector<MDagPath>& jntPathInfluences, weightInformation& weightInfo)
{
	MStatus status;
	unsigned i, j;

	MSelectionList selection;
	selection.add(MFnDependencyNode(skinInfo.m_pathMesh.node()).name() + ".vtx[*]");
	selection.getDagPath(0, weightInfo.path, weightInfo.components);

	MFnSkinCluster skinFn(m_oSkinCluster);
	// 获取蒙皮节点所有的影响骨骼列表
	MDagPathArray influences;
	skinFn.influenceObjects(influences);
	
	// 创建vector容器 来获取给定骨骼在蒙皮骨骼中的序号
	vector<MDagPath> dgPathInfluences;

	for (i=0; i<influences.length(); i++)
	{
		dgPathInfluences.push_back(influences[i]);
	}

	for (unsigned i = 0; i < jntPathInfluences.size(); i++)
	{
		vector <MDagPath>::iterator iElement = find(dgPathInfluences.begin(),
			dgPathInfluences.end(), jntPathInfluences[i]);
		if (iElement != dgPathInfluences.end())
		{
			int nPosition = distance(dgPathInfluences.begin(), iElement);
			weightInfo.indices.append(nPosition);
		}
	}

	status = skinFn.getWeights(weightInfo.path, weightInfo.components, weightInfo.indices, weightInfo.api_weights);

	return status;
}

MStatus SplitSkin::setWeightValue(MObject& m_oSkinCluster, weightInformation& weightInfo)
{
	MStatus status;
	MFnSkinCluster skinFn(m_oSkinCluster);
	status = skinFn.setWeights(weightInfo.path, weightInfo.components, weightInfo.indices, weightInfo.api_weights);
	
	return status;
}

MStatus SplitSkin::getInfomaiton(const MArgDatabase& argData)
{
	MStatus status;

	MSelectionList selList;

	status = argData.getObjects(selList);

	// 获取给定列表中的第一个mesh
	selList.getDagPath(0, skinInfo.m_pathMesh);

	getShapeNode(skinInfo.m_pathMesh);

	// 获取模型的蒙皮节点
	getSkinClusterNode(skinInfo.m_pathMesh, skinInfo.m_oSkinCluster);

	MFnMesh fnMesh = skinInfo.m_pathMesh;


	return MS::kSuccess;
}

MStatus SplitSkin::getSkinClusterNode(MDagPath& path, MObject& oNode)
{
	MStatus status;

	MItDependencyGraph itGraph(path.node(), MFn::kInvalid, MItDependencyGraph::kUpstream);

	while (!itGraph.isDone())
	{
		oNode = itGraph.currentItem();

		if (oNode.apiType() == MFn::kSkinClusterFilter)
		{
			return MS::kSuccess;
		}

		itGraph.next();
	}

	return MS::kFailure;
}

template<typename keyType, typename valType>
vector<keyType> KeySet(map<keyType, valType> test)
{
	vector<keyType> keys;
	for (map<keyType, valType>::iterator it = test.begin(); it != test.end(); ++it) {
		keys.push_back(it->first);
	}
	return keys;
}

template<typename keyType, typename valType>
vector<valType> ValSet(map<keyType, valType> test)
{
	vector<valType> values;
	for (map<keyType, valType>::iterator it = test.begin(); it != test.end(); ++it) {
		values.push_back(it->second);
	}
	return values;
}

template<typename T>
set<T> convertVecToSet(vector<T> inVec)
{
	set<T> s;

	// Traverse the Vector
	for (T x : inVec) {

		// Insert each element
		// into the Set
		s.insert(x);
	}

	// Return the resultant Set
	return s;
}

map<int, set<int>> getCmdResultNumber(MStringArray strArray)
{
	unsigned i,j;
	map<int, set<int>> map_;
	for (i = 0; i < strArray.length(); i++)
	{
		set<int> s;
		vector<string> strs;
		string inStr = strArray[i].asChar();
		smatch result;
		regex pattern("[0-9]+");

		//迭代器声明
		string::const_iterator iterStart = inStr.begin();
		string::const_iterator iterEnd = inStr.end();
		string temp;
		while (regex_search(iterStart, iterEnd, result, pattern))
		{
			temp = result[0];
			strs.push_back(temp);
			iterStart = result[0].second; //更新搜索起始位置,搜索剩下的字符串
		}

		for (j = 1; j < strs.size(); j++)
		{
			s.insert(atoi(strs[j].c_str()));
		}
		map_[i] = s;
	}
	return map_;
}

MMatrix getObjectWorldMatrix(MObject obj)
{
	MMatrix matrix;
	MFnDependencyNode node(obj);
	MFnMatrixData data;
	MPlug matrix_plug = node.findPlug("worldMatrix").elementByLogicalIndex(0);
	data.setObject(matrix_plug.asMObject());
	matrix = data.matrix();

	return matrix;
}

vector<vector<double>> spine_vp(MObject joint1, MObject joint2)
{
	vector<vector<double>> result;
	// 获取joint1的矩阵信息
	MFnDependencyNode jnt1_node(joint1);
	MFnMatrixData jnt1_data;
	MMatrix jnt1_matrix;

	MPlug jnt1_matrix_plug = jnt1_node.findPlug("worldMatrix").elementByLogicalIndex(0);
	jnt1_data.setObject(jnt1_matrix_plug.asMObject());
	jnt1_matrix = jnt1_data.matrix();
	vector<double> jnt1Array = { jnt1_matrix(0,0),  jnt1_matrix(0,1), jnt1_matrix(0,2) };
	
	// 获取joint2的矩阵信息
	MFnDependencyNode jnt2_node(joint2);
	MFnMatrixData jnt2_data;
	MMatrix jnt2_matrix;

	MPlug jnt2_matrix_plug = jnt2_node.findPlug("worldMatrix").elementByLogicalIndex(0);
	jnt2_data.setObject(jnt2_matrix_plug.asMObject());
	jnt2_matrix = jnt2_data.matrix();
	vector<double> jnt2Array = { jnt2_matrix(0,0),  jnt2_matrix(0,1), jnt2_matrix(0,2) };

	// get point data
	MVector p = MTransformationMatrix(jnt2_matrix).getTranslation(MSpace::kWorld);
	vector<double> point = { p.x, p.y, p.z };

	vector<double> v;
	
	transform(jnt1Array.begin(), jnt1Array.end(), jnt2Array.begin(),
		std::back_inserter(v),
		[](const auto& i, const auto& j)
		{
			return (i + j) / 2;
		});
	
	if ((MPoint(p) * jnt1_matrix.inverse())[0] < 0)
	{
		for (unsigned i=0; i<3;i++)
		{
			v[i] = -v[i];
		}
	}

	result.push_back(v);
	result.push_back(point);

	return result;
}

vector<vector<double>> belt_vp(MObject joint1, MObject joint2)
{
	vector<vector<double>> result;
	// 获取joint1的矩阵信息
	MFnDependencyNode jnt1_node(joint1);
	MFnMatrixData jnt1_data;
	MMatrix jnt1_matrix;

	MPlug jnt1_matrix_plug = jnt1_node.findPlug("worldMatrix").elementByLogicalIndex(0);
	jnt1_data.setObject(jnt1_matrix_plug.asMObject());
	jnt1_matrix = jnt1_data.matrix();
	vector<double> jnt1Array = { jnt1_matrix(0,0),  jnt1_matrix(0,1), jnt1_matrix(0,2) };

	// 获取joint2的矩阵信息
	MFnDependencyNode jnt2_node(joint2);
	MFnMatrixData jnt2_data;
	MMatrix jnt2_matrix;

	MPlug jnt2_matrix_plug = jnt2_node.findPlug("worldMatrix").elementByLogicalIndex(0);
	jnt2_data.setObject(jnt2_matrix_plug.asMObject());
	jnt2_matrix = jnt2_data.matrix();
	vector<double> jnt2Array = { jnt2_matrix(0,0),  jnt2_matrix(0,1), jnt2_matrix(0,2) };

	// get point data
	MVector p2 = MTransformationMatrix(jnt2_matrix).getTranslation(MSpace::kWorld);
	MVector p1 = MTransformationMatrix(jnt1_matrix).getTranslation(MSpace::kWorld);
	MVector p = (p1 + p2) / 2;
	vector<double> point = { p.x, p.y, p.z };

	MVector v_ = (p2 - p1).normal();
	vector<double> v = {v_.x, v_.y, v_.z};

	result.push_back(v);
	result.push_back(point);

	return result;
}

vector<vector<double>> brow_vp(MObject joint1, MObject joint2)
{
	vector<vector<double>> result;
	// 获取joint1的矩阵信息
	MFnDependencyNode jnt1_node(joint1);
	MFnMatrixData jnt1_data;
	MMatrix jnt1_matrix;

	MPlug jnt1_matrix_plug = jnt1_node.findPlug("worldMatrix").elementByLogicalIndex(0);
	jnt1_data.setObject(jnt1_matrix_plug.asMObject());
	jnt1_matrix = jnt1_data.matrix();
	vector<double> jnt1Array = { jnt1_matrix(0,0),  jnt1_matrix(0,1), jnt1_matrix(0,2) };

	// 获取joint2的矩阵信息
	MFnDependencyNode jnt2_node(joint2);
	MFnMatrixData jnt2_data;
	MMatrix jnt2_matrix;

	MPlug jnt2_matrix_plug = jnt2_node.findPlug("worldMatrix").elementByLogicalIndex(0);
	jnt2_data.setObject(jnt2_matrix_plug.asMObject());
	jnt2_matrix = jnt2_data.matrix();
	vector<double> jnt2Array = { jnt2_matrix(0,0),  jnt2_matrix(0,1), jnt2_matrix(0,2) };

	// get point data
	MVector p2 = MTransformationMatrix(jnt2_matrix).getTranslation(MSpace::kWorld);
	MVector p1 = MTransformationMatrix(jnt1_matrix).getTranslation(MSpace::kWorld);
	p2.y = p1.y;
	p2.z = p1.z;
	MVector p = (p1 + p2) / 2;
	vector<double> point = { p.x, p.y, p.z };

	MVector v_ = (p2 - p1).normal();
	vector<double> v = { v_.x, v_.y, v_.z };

	result.push_back(v);
	result.push_back(point);

	return result;
}

vector<vector<double>> transverse_vp(MObject joint1, MObject joint2)
{
	vector<vector<double>> result;
	// 获取joint1的矩阵信息
	MFnDependencyNode jnt1_node(joint1);
	MFnMatrixData jnt1_data;
	MMatrix jnt1_matrix;

	MPlug jnt1_matrix_plug = jnt1_node.findPlug("worldMatrix").elementByLogicalIndex(0);
	jnt1_data.setObject(jnt1_matrix_plug.asMObject());
	jnt1_matrix = jnt1_data.matrix();
	vector<double> jnt1Array = { jnt1_matrix(0,0),  jnt1_matrix(0,1), jnt1_matrix(0,2) };

	// 获取joint2的矩阵信息
	MFnDependencyNode jnt2_node(joint2);
	MFnMatrixData jnt2_data;
	MMatrix jnt2_matrix;

	MPlug jnt2_matrix_plug = jnt2_node.findPlug("worldMatrix").elementByLogicalIndex(0);
	jnt2_data.setObject(jnt2_matrix_plug.asMObject());
	jnt2_matrix = jnt2_data.matrix();
	vector<double> jnt2Array = { jnt2_matrix(0,0),  jnt2_matrix(0,1), jnt2_matrix(0,2) };

	// get point data
	MVector p2 = MTransformationMatrix(jnt2_matrix).getTranslation(MSpace::kWorld);
	MVector p1 = MTransformationMatrix(jnt1_matrix).getTranslation(MSpace::kWorld);
	p2.x = p1.x;
	p2.z = p1.z;
	MVector p = (p1 + p2) / 2;
	vector<double> point = { p.x, p.y, p.z };

	MVector v_ = (p2 - p1).normal();
	vector<double> v = { v_.x, v_.y, v_.z };

	result.push_back(v);
	result.push_back(point);

	return result;
}

split_kw split_kwargs(MDagPath skinMesh, weightInformation weightInfo, MObjectArray selJntArray, MObjectArray compJntArray, string type)
{
	unsigned i;
	split_kw dict;

	vector<vector<vector<double>>> vps;
	for (i=0; i< compJntArray.length(); i++)
	{
		if (type == "spine")
		{
			vector<vector<double>> vp = spine_vp(selJntArray[i], compJntArray[i]);
			vps.push_back(vp);
		}
		else if (type == "belt")
		{
			vector<vector<double>> vp = belt_vp(selJntArray[i], compJntArray[i]);
			vps.push_back(vp);
		}
		else if (type == "brow")
		{
			vector<vector<double>> vp = brow_vp(selJntArray[i], compJntArray[i]);
			vps.push_back(vp);
		}
		else if (type == "transverse")
		{
			vector<vector<double>> vp = transverse_vp(selJntArray[i], compJntArray[i]);
			vps.push_back(vp);
		}
	}

	MFnMesh fnMesh(skinMesh);
	MPointArray ps;
	fnMesh.getPoints(ps, MSpace::kWorld);

	vector<vector<double>> pts;
	for (i = 0; i < ps.length(); i++)
	{
		vector<double> pt = { ps[i].x, ps[i].y, ps[i].z };
		pts.push_back(pt);
	}
	vector<vector<double>> wx_matrix = split_wx_matrix(vps, pts);

	vector<double> max_weights = get_max_weights(weightInfo.api_weights, selJntArray.length(), ps.length());

	dict.wx_matrix = wx_matrix;
	dict.max_weights = max_weights;
	return dict;
}

MStatus split_solve(string type, skinInformation skinInfo, weightInformation weightInfo, MObjectArray selJntArray, MObjectArray compJntArray, vector<double> xs, vector<double> ys, double r)
{
	MStatus status;
	unsigned i;
	split_kw dict = split_kwargs(skinInfo.m_pathMesh, weightInfo, selJntArray, compJntArray, type);

	weightInformation weightInfoAfter;
	weightInfoAfter.path = weightInfo.path;
	weightInfoAfter.indices = weightInfo.indices;
	weightInfoAfter.components = weightInfo.components;

	vector<double> weights = split_weights(dict, xs, ys, r);

	weightInfoAfter.api_weights.setLength(weights.size());
	for (i = 0; i < weights.size(); i++)
	{
		weightInfoAfter.api_weights[i] = weights[i];
	}

	status = SplitSkin::setWeightValue(skinInfo.m_oSkinCluster, weightInfoAfter);

	return status;
}

split_kw cloth_kwargs(skinInformation skinInfo, weightInformation weightInfo, MObjectArray selJntArray)
{
	split_kw dict;
	unsigned i;

	weightInformation weightInfoAfter;
	weightInfoAfter.path = weightInfo.path;
	weightInfoAfter.indices = weightInfo.indices;
	weightInfoAfter.components = weightInfo.components;

	MPointArray vtx_points_;
	MFnMesh(skinInfo.m_pathMesh).getPoints(vtx_points_);
	vector<vector<double>> vtx_points;
	for (i = 0; i < vtx_points_.length(); i++)
	{
		vector<double> pt = { vtx_points_[i].x,vtx_points_[i].y ,vtx_points_[i].z };
		vtx_points.push_back(pt);
	}

	vector<vector<double>>joint_points;

	for (i=0; i<selJntArray.length();i++)
	{
		MFnDependencyNode jnt_node(selJntArray[i]);
		MFnMatrixData jnt_data;
		MMatrix jnt_matrix;
		MPlug jnt_matrix_plug = jnt_node.findPlug("worldMatrix").elementByLogicalIndex(0);
		jnt_data.setObject(jnt_matrix_plug.asMObject());
		jnt_matrix = jnt_data.matrix();

		MVector joint_point = MTransformationMatrix(jnt_matrix).getTranslation(MSpace::kWorld);
		vector<double> joint_vec = { joint_point.x, joint_point.y, joint_point.z };
		joint_points.push_back(joint_vec);
	}

	vector<vector<double>> wx_matrix = cloth_wx_matrix(vtx_points, joint_points);

	MFnSkinCluster skinFn(skinInfo.m_oSkinCluster);
	skinFn.getWeights(weightInfoAfter.path, weightInfoAfter.components, weightInfoAfter.indices, weightInfoAfter.api_weights);

	vector<double> max_weights = get_max_weights(weightInfoAfter.api_weights, selJntArray.length(), vtx_points.size());
	
	dict.wx_matrix = wx_matrix;
	dict.max_weights = max_weights;
	return dict;
}

MStatus cloth_solve(skinInformation skinInfo, weightInformation weightInfo, MObjectArray selJntArray, vector<double> xs, vector<double> ys, double r)
{
	MStatus status;

	split_kw dict = cloth_kwargs(skinInfo, weightInfo, selJntArray);
	unsigned i,j;

	for (i = 0; i < ys.size(); i++)
	{
		ys[i] = 1.0 - ys[i];
	}

	// wx_matrix: 模型点到骨骼点之间的距离矩阵
	int vtx_len = dict.wx_matrix[0].size();
	int joint_len = dict.wx_matrix.size();

	vector<double> weights;
	for (i = 0; i < joint_len; i++)
	{
		for (j = 0; j < vtx_len; j++)
		{
			double weight = getWeight(dict.wx_matrix[i][j] / r, xs, ys);
			weights.push_back(weight);
		}
	}

	for (i = 0; i < vtx_len; i++)
	{
		vector<double> vtx_weights;
		for (j = 0; j < joint_len; j++)
		{
			vtx_weights.push_back(weights[i*joint_len+j]);
		}
		double vtx_weight = max(sum<double>(vtx_weights), 0.000000001);
		for (j = 0; j < joint_len; j++)
		{
			unsigned k = i * joint_len + j;
			weights[k] = weights[k] / vtx_weight * dict.max_weights[i];
		}
	}

	MDoubleArray api_weights;
	api_weights.setLength(weightInfo.api_weights.length());
	for (i = 0; i < weights.size(); i++)
	{
		api_weights[i] = weights[i];
	}

	MFnSkinCluster skinFn(skinInfo.m_oSkinCluster);
	status = skinFn.setWeights(weightInfo.path, weightInfo.components, weightInfo.indices, api_weights);

	return status;
}

MItMeshVertex getVertIt(MString str)
{
	MSelectionList selection;
	selection.add(str);
	MItSelectionList selectionIt(selection, MFn::kComponent);
	MDagPath path;
	MObject component;
	selectionIt.getDagPath(path, component);

	MItMeshVertex vtxIter(path, component);
	return vtxIter;
}

MStatus eye_solve(skinInformation skinInfo, weightInformation weightInfo, MObjectArray selJntArray)
{
	MStatus status;
	unsigned i, j;
	MString meshName = MFnDependencyNode(skinInfo.m_pathMesh.node()).name();
	map<int, set<int>> joint_vtx_ids;
	MFnMesh fnMesh(skinInfo.m_pathMesh);
	
	for (i = 0; i < selJntArray.length(); i++)
	{
		MMatrix jnt_matrix = getObjectWorldMatrix(selJntArray[i]);
		MPoint point(MTransformationMatrix(jnt_matrix).getTranslation(MSpace::kWorld));
		MPoint closetPoint;
		
		int faceID, dummyFaceIndex;
		fnMesh.getClosestPoint(point, closetPoint, MSpace::kWorld, &faceID);
		MItMeshPolygon meshIt(skinInfo.m_pathMesh);
		
		meshIt.setIndex(faceID, dummyFaceIndex);

		MIntArray vertices;
		meshIt.getVertices(vertices);
		map<double, int> length_map;

		for (j = 0; j < vertices.length(); j++)
		{
			MString vert_component = meshName + ".vtx[" + vertices[j] + "]";
			MItMeshVertex it = getVertIt(vert_component);
			double length = (it.position(MSpace::kWorld) - point).length();
			length_map[length] = vertices[j];
		}

		set<int> vtxId;

		vector<double> length_map_keys = KeySet<double, int>(length_map);
		double minVal = *min_element(length_map_keys.begin(), length_map_keys.end());
		vtxId.insert(length_map[minVal]);
		//cout << " the lowest distance of joint " << MFnDependencyNode(selJntArray[i]).name() << " vert id is : " << length_map[minVal] << endl;
		joint_vtx_ids[weightInfo.indices[i]] = vtxId;
	}

	MGlobal::executeCommand("select -cl;");
	vector<set<int>> values = ValSet<int, set<int>>(joint_vtx_ids);

	for (i = 0; i < values.size(); i++)
	{
		set<int> idSet = values[i];
		for (auto it = idSet.cbegin(); it != idSet.cend(); it++)
		{
			int index = *it;
			MString cmd = "select -add ";
			MString selectStr = meshName + ".vtx[" + index + "];";
			MGlobal::executeCommand(cmd + selectStr);
		}
	}
	// max weights 可拆分的最大权重
	//MDoubleArray weights;
	MPointArray ps;
	fnMesh.getPoints(ps, MSpace::kWorld);

	vector<double> max_weights = get_max_weights(weightInfo.api_weights, selJntArray.length(), ps.length());
	// weight_ids 拥有权重的点
	vector<int> weight_ids;
	for (i = 0; i < max_weights.size(); i++)
	{
		if (max_weights[i] > 0.0001)
		{
			weight_ids.push_back(i);
		}
	}
	//MGlobal::executeCommand("select -cl;");
	for (i = 0; i < weight_ids.size(); i++)
	{
		MString cmd = "select -add ";
		MString selectStr = (meshName + ".vtx[" + weight_ids[i] + "];");
		MGlobal::executeCommand(cmd + selectStr);
	}

	MSelectionList selection;
	MGlobal::getActiveSelectionList(selection);
	selection.getDagPath(0, weightInfo.path, weightInfo.components);

	// vv = { vtx_id: set(vtx_id) } 模型点的邻接点的点序
	map<int, set<int>> ve, ev, vv;

	MCommandResult ve_result;
	MStringArray ve_strArray;
	status = MGlobal::executeCommand("polyInfo -ve " + meshName + ";", ve_result, false, false);
	if (status == MS::kSuccess)
	{
		ve_result.getResult(ve_strArray);
		ve = getCmdResultNumber(ve_strArray);
	}

	MCommandResult ev_result;
	MStringArray ev_strArray;
	status = MGlobal::executeCommand("polyInfo -ev " + meshName + ";", ev_result, false, false);
	if (status == MS::kSuccess)
	{
		ev_result.getResult(ev_strArray);
		ev = getCmdResultNumber(ev_strArray);
	}

	for (map<int, set<int>>::iterator iter = ve.begin(); iter != ve.end(); iter++)
	{
		set<int> vs;
		int v = iter->first;
		set<int> es = iter->second;
		for (auto it_es = es.cbegin(); it_es != es.cend(); it_es++)
		{
			for (auto it_ev = ev[*it_es].cbegin(); it_ev != ev[*it_es].cend(); it_ev++)
			{
				vs.insert(*it_ev);
			}
		}
		vv[v] = vs;
	}

	// joint_vtx_ids = {joint_id : set([vtx_id])} 骨骼对应可以拥有权重的点
	set<int> weight_ids_set = convertVecToSet(weight_ids);

	set<int> vtx_ids_set;
	vector<set<int>> joint_vtx_ids_values = ValSet(joint_vtx_ids);
	for (i = 0; i < joint_vtx_ids_values.size(); i++)
	{
		set<int> ids = joint_vtx_ids_values[i];
		for (auto iter = ids.cbegin(); iter != ids.cend(); iter++)
		{
			vtx_ids_set.insert(*iter);
		}
	}

	set<int> ids;
	set_difference(weight_ids_set.begin(), weight_ids_set.end(), 
		vtx_ids_set.begin(), vtx_ids_set.end(), 
		insert_iterator<set<int>>(ids, ids.begin()));

	while (ids.size() != 0)
	{
		for (map<int, set<int>>::iterator iter = joint_vtx_ids.begin(); iter != joint_vtx_ids.end(); iter++)
		{
			set<int> vt_ids, intersection_ids, subscribe;
			int joint_id = iter->first;
			set<int> vtx_ids = iter->second;
			for (auto vtx_iter = vtx_ids.cbegin(); vtx_iter != vtx_ids.cend(); vtx_iter++)
			{
				set<int> vv_ids =  vv[*vtx_iter];
				for (auto vv_iter = vv_ids.cbegin(); vv_iter != vv_ids.cend(); vv_iter++)
				{
					vt_ids.insert(*vv_iter);
				}
			}
			set_intersection(vt_ids.begin(), vt_ids.end(), ids.begin(), ids.end(),
				insert_iterator<set<int>>(intersection_ids, intersection_ids.begin()));
			for (auto intersection_iter = intersection_ids.cbegin(); intersection_iter != intersection_ids.cend(); intersection_iter++)
			{
				joint_vtx_ids[joint_id].insert(*intersection_iter);
			}
			set_difference(ids.begin(), ids.end(), 
				joint_vtx_ids[joint_id].begin(), joint_vtx_ids[joint_id].end(), 
				insert_iterator<set<int>>(subscribe, subscribe.begin()));
			ids = subscribe;
		}
	}

	MDoubleArray weights;
	weights.setLength(selJntArray.length()* weight_ids.size());

	for (i = 0; i < selJntArray.length() * weight_ids.size(); i++)
	{
		weights[i] = 0.0;
	}

	vector<int> indicies_;
	for (i = 0; i < weightInfo.indices.length(); i++)
	{
		indicies_.push_back(weightInfo.indices[i]);
	}

	for (map<int, set<int>>::iterator iter = joint_vtx_ids.begin(); iter != joint_vtx_ids.end(); iter++)
	{
		int joint_id = iter->first;
		set<int> vtx_ids = iter->second;
		for (auto id_iter = vtx_ids.cbegin(); id_iter != vtx_ids.cend(); id_iter++)
		{
			int vtx_id = *id_iter;
			int vtx_index, indices_index;
			vector <int>::iterator iElement = find(weight_ids.begin(),
				weight_ids.end(), vtx_id);
			if (iElement != weight_ids.end())
			{
				vtx_index = distance(weight_ids.begin(), iElement);
			}

			vector <int>::iterator iElement_indi = find(indicies_.begin(),
				indicies_.end(), joint_id);
			if (iElement_indi != indicies_.end())
			{
				indices_index = distance(indicies_.begin(), iElement_indi);
			}

			unsigned k = vtx_index * selJntArray.length() + indices_index;
			weights[k] = max_weights[vtx_id];

		}
	}

	MFnSkinCluster fnSkin(skinInfo.m_oSkinCluster);
	fnSkin.setWeights(weightInfo.path, weightInfo.components, weightInfo.indices, weights);
	
	MGlobal::executeCommand("select -cl;");
	MGlobal::executeCommand("select -r " + meshName + ";");

	return status;
}