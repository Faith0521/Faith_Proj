#ifndef FAITH_SOLVERS_H
#define FAITH_SOLVERS_H

#include <iostream>
#include <fstream>
#include <algorithm>
#include <sstream>
#include <stdio.h>
#include <time.h>
#include <cmath>
#include <cstdlib>
#include <maya/MPxNode.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MQuaternion.h>
#include <maya/MVector.h>
#include <maya/MQuaternion.h>
#include <maya/MMatrix.h>
#include <maya/MTime.h>
#include <maya/MDagModifier.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MStringArray.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MDoubleArray.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MPxCommand.h>
#include <maya/MSyntax.h>
#include <maya/MArgDatabase.h>
#include <maya/MSelectionList.h>
#include <maya/MGlobal.h>
#include <maya/MDagPathArray.h>
#include <maya/MItDependencyGraph.h>
#include <maya/MDagPath.h>
#include <maya/MFnSkinCluster.h>
#include <maya/MItGeometry.h>
#include <maya/MTypes.h>
#include <Eigen/Dense>
#include <Eigen/Eigenvalues>
#include "rapidjson/document.h"
#include "rapidjson/prettywriter.h"
#include "rapidjson/stringbuffer.h"

using namespace Eigen;
using namespace std;

#define PI 3.14159265
#define lerp(a,b,t) ((1 - (t))* (a)+((t) * (b)))

struct IK_INfo
{
	double lengthA;
	double lengthB;
	double roll;
	double fatnessA;
	double fatnessB;
	double stretch;
	double soft;
	double slide;
	double reverse;
	double pin;
	bool negate;
	MTransformationMatrix root;
	MTransformationMatrix eff;
	MTransformationMatrix pole;
};

struct FK_Info
{

};

struct MatrixComponents {
	Vector3d translate;
	Vector4d rotate;
	Vector3d scale;
	Vector3d shear;
};

class transferSkinWeights :public MPxCommand
{
public:
	transferSkinWeights();
	virtual				~transferSkinWeights() override;
	virtual MStatus		doIt(const MArgList& args) override;
	static  MSyntax		syntax();
	static  void*		creator();

	bool				writeWeights(MString fileName);
	bool				readWeights(MString fileName);
	static  MStatus		getSelected_skinData(MDagPath& path, MObject& component, MIntArray& influences, MFnSkinCluster& skinFn);


};

class IKNode :public MPxNode
{
public:
							IKNode();
	virtual					~IKNode() override;
	virtual MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	
	MTransformationMatrix	GetIKInfo(IK_INfo values , MString outputName);
	//double					GetSoftInfo(IK_Stretch data);
	
	static  void*			creator();
	static  MStatus			initialize();

	static MString			GetNodeName();
	static MTypeId			GetNodeID();

	//Attributes
	static MObject inRoot;
	static MObject inIKEnd;
	static MObject inPole;
	static MObject inMidParent;
	static MObject inEndParent;
	static MObject lengthA;
	static MObject lengthB;
	static MObject fatnessA;
	static MObject fatnessB;
	static MObject softness;
	static MObject stretchly;
	static MObject reverse;
	static MObject negate;
	static MObject slide;
	static MObject roll;
	static MObject pin;
	static MObject outMid;
	static MObject outEnd;

};

class SquashNode : public MPxNode
{
public:
							SquashNode();
	virtual					~SquashNode() override;
	virtual MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	static  void*			creator();
	static  MStatus			initialize();

	static MString			NodeName;
	static MTypeId			NodeID;

	// Attribute
	static MObject globalScale;
	static MObject globalScalex;
	static MObject globalScaley;
	static MObject globalScalez;
	static MObject stretch;
	static MObject squash;
	static MObject axis;
	static MObject blendValue;
	static MObject driveValue;
	static MObject driverMin;
	static MObject driverMax;
	static MObject driverCtrl;
	static MObject outputScale;

};

class Swing : public MPxNode
{
public:
							Swing();
	virtual					~Swing() override;
	virtual MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	static  void*			creator();
	static  MStatus			initialize();

	static  MString			NodeName;
	static  MTypeId			NodeID;

public:
	// input attribute
	static MObject inOutTime;
	static MObject inSwingSpeed;
	static MObject inSwingOffset;
	static MObject inSwingReductionValue;
	static MObject inSwingReduction;
	static MObject outputUp;
	static MObject outputDn;
	static MObject inSwingAmplitudeXAdd;
	static MObject inSwingAmplitudeYAdd;
	static MObject inRoot_SwingAmplitudeX;
	static MObject inRoot_SwingAmplitudeY;
	static MObject inIK_SwingAmplitudeX;
	static MObject inIK_SwingAmplitudeY;
	
};

class Drum : public MPxNode
{
public:
							Drum();
	virtual					~Drum() override;
	virtual MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	static  void*			creator();
	static  MStatus			initialize();

	static  MString			NodeName;
	static  MTypeId			NodeID;

public:
	// input attribute
	static MObject inOutTime;
	static MObject inDrumSpeed;
	static MObject inDrumOffset;
	static MObject inDrumDefaultValue;
	static MObject inDrumReduction;
	static MObject inRoot_DrumStrength;
	static MObject inIK_DrumStrength;
	static MObject outScale;
	static MObject outScaleX;
	static MObject outScaleY;
	static MObject outScaleZ;

};

class SplitWeights : public MPxNode
{
public:
							SplitWeights();
	virtual					~SplitWeights() override;
	virtual MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	static  void*			creator();
	static  MStatus			initialize();

	void					postConstructor();
	MStatus					postConstructor_init_curveRamp(MObject& nodeObj,
														   MObject& rampObj,
														   int index,
														   float position,
														   float value,
														   int interpolation);

	static  MString			NodeName;
	static  MTypeId			NodeID;


	// attributs
	static MObject axis;
	static MObject centered;
	static MObject clamp;
	static MObject curve;
	static MObject curveRamp;
	static MObject end;
	static MObject inputComponentsList;
	static MObject inputComponents;
	static MObject invert;
	static MObject invertList;
	static MObject matrixList;
	static MObject mesh;
	static MObject mirror;
	static MObject multiply;
	static MObject offset;
	static MObject placementMatrixList;
	static MObject start;
	static MObject useTransform;
	static MObject weightList;
	static MObject weights;
};

class BlendMatrix : public MPxNode
{
public:
							BlendMatrix();
	virtual					~BlendMatrix() override;
	virtual MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	static  void*			creator();
	static  MStatus			initialize();
	static  MString			NodeName;
	static  MTypeId			NodeID;

	static  MObject			aOutputMatrix;
	static  MObject			aOffsetMatrix;
	static  MObject			aRestMatrix;
	static  MObject			aBlendInputMatrix;
	static  MObject			aBlendOffsetMatrix;
	static  MObject			aBlendTranslateWeight;
	static  MObject			aBlendRotateWeight;
	static  MObject			aBlendScaleWeight;
	static  MObject			aBlendShearWeight;
	static  MObject			aBlendMatrix;
private:
	Vector3d				calculateComponent(const MatrixXd& matrix, const VectorXd& weights, const Vector3d& rest);
	Vector4d				calculateComponent(const MatrixXd& matrix, const VectorXd& weights, const Vector4d& rest);
	MatrixComponents		splitMatrix(const MMatrix& matrix);
	MMatrix					constructMatrix(
							const Vector3d& translate,
							const Vector4d& rotate,
							const Vector3d& scale,
							const Vector3d& shear
	);

};


#endif // !IKNODE_H

