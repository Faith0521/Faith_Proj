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
#include <vector>
#include <string>
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
#include <maya/MFnTypedAttribute.h>
#include <maya/MRampAttribute.h>
#include <maya/MFnComponentListData.h>
#include <maya/MPxCommand.h>
#include <maya/MSyntax.h>
#include <maya/MArgDatabase.h>
#include <maya/MSelectionList.h>
#include <maya/MArrayDataBuilder.h>
#include <maya/MFnSingleIndexedComponent.h>
#include <maya/MFnMesh.h>
#include <maya/MMatrixArray.h>
#include <maya/MPointArray.h>
#include <maya/MFloatVectorArray.h>
#include <maya/MFloatMatrix.h>
#include <maya/MFloatPointArray.h>
#include <maya/MRenderUtil.h>
#include <maya/MMeshIntersector.h>
#include <maya/MBoundingBox.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MGlobal.h>
#include <maya/MDagPathArray.h>
#include <maya/MItDependencyGraph.h>
#include <maya/MDagPath.h>
#include <maya/MFnSkinCluster.h>
#include <maya/MFnTransform.h>
#include <maya/MItGeometry.h>
#include <maya/MTypes.h>
#include <maya/MEulerRotation.h>
#include <maya/MPxFileTranslator.h>
#include <maya/MItSelectionList.h>
#include <maya/MFnMatrixData.h>
#include <Eigen/Dense>
#include <Eigen/Eigenvalues>
#include "rapidjson/document.h"
#include "rapidjson/prettywriter.h"
#include "rapidjson/stringbuffer.h"

using namespace Eigen;
using namespace std;

#define PI 3.14159265
#define lerp(a,b,t) ((1 - (t))* (a)+((t) * (b)))

const char* const optionScript = "exportWeightOptions";
const char* const defaultOptions = "";

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
	double lengthA;
	double lengthB;
	bool negate;
	MTransformationMatrix root;
	MTransformationMatrix bone1;
	MTransformationMatrix bone2;
	MTransformationMatrix eff;
};

struct MatrixComponents {
	Vector3d translate;
	Vector4d rotate;
	Vector3d scale;
	Vector3d shear;
};

struct fileInfo
{
	MIntArray				matrixIndices;
	MPointArray				matrixPositions;
	MPointArray				vtxPoints;
	MStringArray			skinJoints;
	vector< MIntArray >		weightListIndices;
	vector< MFloatArray >	weightListValues;
};

class transferSkinWeights : public MPxFileTranslator
{
public:
							transferSkinWeights();
	virtual					~transferSkinWeights();
	static  void*			creator();

	virtual bool			haveReadMethod() const;
	virtual bool			haveWriteMethod() const;
	virtual bool			canBeOpened() const;
	virtual MString			defaultExtension() const;

	virtual MStatus			reader(const MFileObject& file,
							const MString& optionsString,
							FileAccessMode mode);

	virtual MStatus			writer(const MFileObject& file,
							const MString& optionsString,
							FileAccessMode mode);

	MFileKind				identifyFile(const MFileObject& fileName,
							const char* buffer,
							short size) const;

	MStatus					parseOptionsString(const MString& optionsString);
	MStatus					exportAll(std::ofstream& out);
	MStatus					exportSelected(std::ofstream& out);
	MStatus					exportWeightInfo(MDagPath& pathDag, std::ofstream& out);
	MStatus					getFileInfo(std::ifstream& inFile, fileInfo* pInfo, MFnTransform& targetTransform, MMatrix& getMatrix);
	MStatus					getSkinClusterNodeFromPath(MDagPath& pathDag, MFnDependencyNode& skinNode);

	MStatus					setInfoToSkinNode(fileInfo& info, MFnDependencyNode& skinNode, MObjectArray& oJoints);
	MStatus					importWeightInfo(std::ifstream& inFile, MDagPath& targetPath);

	MStatus					getShape(MDagPath& dagPath);
	MString					importString(ifstream& inFile);
	void					exportString(ofstream& out, MString& str);

private:
	bool					m_exportNormals;
	bool					m_exportUVs;
};

class IKNode :public MPxNode
{
public:
							IKNode();
	virtual					~IKNode() override;
	virtual MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	
	MTransformationMatrix	GetIKInfo(IK_INfo values , MString outputName);
	MTransformationMatrix	GetFKInfo(FK_Info values, MString outputName);
	
	static  void*			creator();
	static  MStatus			initialize();

	static  MString			GetNodeName();
	static  MTypeId			GetNodeID();

	//Attributes
	static  MObject			blend;

	static  MObject			inRoot;
	static  MObject			inEnd;
	static  MObject			inPole;
	static  MObject			fkA;
	static  MObject			fkB;
	static  MObject			fkC;

	static  MObject			inAParent;
	static  MObject			inBParent;
	static  MObject			inCenterParent;
	static  MObject			inEndParent;

	static  MObject			lengthA;
	static  MObject			lengthB;
	static  MObject			fatnessA;
	static  MObject			fatnessB;
	static  MObject			softness;
	static  MObject			stretchly;
	static  MObject			reverse;
	static  MObject			negate;
	static  MObject			slide;
	static  MObject			roll;
	static  MObject			pin;

	static  MObject			outputA;
	static  MObject			outputB;
	static  MObject			outputCenter;
	static  MObject			outputEnd;

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

class SwingAmplitude : public MPxNode
{
public:
							SwingAmplitude();
	virtual					~SwingAmplitude() override;
	virtual MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	static  void*			creator();
	static  MStatus			initialize();
	static  MString			NodeName;
	static  MTypeId			NodeID;

	static  MObject			inputTransform;
	static  MObject			intranslateX;
	static  MObject			intranslateY;
	static  MObject			outTransform;
	static  MObject			outtranslateX;
	static  MObject			outtranslateY;

private:

};

class MatrixMult : public MPxNode
{
public:
	MatrixMult();
	virtual	~MatrixMult() override;
	virtual MStatus	compute(const MPlug& plug, MDataBlock& data) override;
	static  void* creator();
	static  MStatus			initialize();
	static  MString			NodeName;
	static  MTypeId			NodeID;

};


#endif // !IKNODE_H

