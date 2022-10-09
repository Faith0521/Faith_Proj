#ifndef SPLITSKINWEIGHTS_H
#define SPLITSKINWEIGHTS_H

#include <iostream>
#include <algorithm>
#include <regex>
#include <iterator>
#include <vector>
#include <map>
#include <set>
#include <maya/MPxCommand.h>
#include <maya/MArgList.h>
#include <maya/MSyntax.h>
#include <maya/MArgDatabase.h>
#include <maya/MFnMesh.h>
#include <maya/MMatrix.h>
#include <maya/MFnSkinCluster.h>
#include <maya/MDagPath.h>
#include <maya/MDagPathArray.h>
#include <maya/MSelectionList.h>
#include <maya/MItSelectionList.h>
#include <maya/MCommandResult.h>
#include <maya/MFnTransform.h>
#include <maya/MFnSingleIndexedComponent.h>
#include <maya/MItMeshPolygon.h>
#include <maya/MItMeshVertex.h>
#include <maya/MFnDagNode.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnMatrixData.h>
#include <maya/MItDependencyGraph.h>
#include <maya/MObjectArray.h>
#include <maya/MPointArray.h>
#include <maya/MGlobal.h>
#include <Eigen/Dense>
#include <Eigen/Eigenvalues>

using namespace std;

struct skinInformation
{
	MObject			m_oSkinCluster;
	MDagPath		m_pathMesh;
};

struct weightInformation
{
	MObject			components;
	MDagPath		path;
	MIntArray		indices;
	MDoubleArray	api_weights;
};

struct split_kw
{
	vector<vector<double>> wx_matrix;
	vector<double> max_weights;
};

class SplitSkin : public MPxCommand
{
public:
							SplitSkin();
	virtual					~SplitSkin();

	MStatus					doIt(const MArgList& argList);
	MStatus					redoIt();
	MStatus					undoIt();
	bool					isUndoable() const;

	static	void*			creator();
	static MSyntax			newSyntax();

	MStatus					getShapeNode(MDagPath& path);
	MStatus					getSkinClusterNode(MDagPath& path, MObject& oNode);
	MStatus					getWeightValue(MObject& m_oSkinCluster, vector<MDagPath>& jntPathInfluences, weightInformation& weightInfo);
	static MStatus			setWeightValue(MObject& m_oSkinCluster, weightInformation& weightInfo);
	MStatus					getInfomaiton(const MArgDatabase& argData);

	static skinInformation  skinInfo;

	vector<MDagPath>		jntPathInfluences;
	weightInformation		weightInfoBefore;

private:
	MStatus					parseArgs(const MArgList& argList);
	void					showUsage(void);


private:
	unsigned uJnts;			 // How many joints passed in?
	MSelectionList sListComp;	 // What is selected/passed in obj?
	string type;
	double	radius;
	vector<double> xsVal;
	vector<double> ysVal;
};

#endif