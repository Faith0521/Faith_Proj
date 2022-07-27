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
#include <maya/MMatrixArray.h>
#include <maya/MFnPointArrayData.h>
#include <maya/MDoubleArray.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MRampAttribute.h>
#include <maya/MFnComponentListData.h>
#include <maya/MPxCommand.h>
#include <maya/MSyntax.h>
#include <maya/MPxDeformerNode.h>
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
#include <maya/MCurveAttribute.h>
#include <maya/MEulerRotation.h>
#include <maya/MPxFileTranslator.h>
#include <maya/MItSelectionList.h>
#include <maya/MFnMatrixData.h>
#include <maya/MItDag.h>
#include <maya/MScriptUtil.h>
#include <maya/MFnMeshData.h>
#include <Eigen/Dense>
#include <Eigen/Eigenvalues>

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

	static MString			NodeName;
	static MTypeId			NodeID;

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
	static  MObject			aOutputDriverOffsetMatrix;
	static  MObject			aOffsetMatrix;
	static  MObject			aRestMatrix;
	static  MObject			aParentInverseMatrix;
	static  MObject			aBlendInputMatrix;
	static  MObject			aBlendOffsetMatrix;
	static  MObject			aDriverRotationOffset;
	static  MObject			aDriverRotationOffsetX;
	static  MObject			aDriverRotationOffsetY;
	static  MObject			aDriverRotationOffsetZ;
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

	static  MObject			aEnvelope;
	static  MObject			aAmplitude;
	static  MObject			aWaveLength;
	static  MObject			aWaveFollow;
	static  MObject			aStartPosition;
	static  MObject			aReverse;
	static  MObject			aOutputTransform;
	static  MObject			aResult;

};

class MatrixMult : public MPxNode
{
public:
	MatrixMult();
	virtual					~MatrixMult() override;
	virtual	MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	static  void*			creator();
	static  MStatus			initialize();
	static  MString			NodeName;
	static  MTypeId			NodeID;

	static  MObject			inMatrixA;
	static  MObject			inMatrixB;
	static  MObject			outMatrix;

};

class CorrectiveShape : public MPxDeformerNode
{
public:
							CorrectiveShape();
	virtual					~CorrectiveShape();
	virtual MStatus			deform(MDataBlock& block, MItGeometry& iter, const MMatrix& mat, unsigned int multiIndex);
	static  void*			creator();
	static  MStatus			initialize();
	static  MString			NodeName;
	static  MTypeId			NodeID;

	static  MObject			aMatrix;
	static  MObject			aCorrectiveGeo;
	static  MObject			aDeformedPoints;
	static  bool			_initialized;
	static  MPointArray		_deformedPoints;
	static  MMatrixArray	_matrices;
};

class splineMatrix : public MPxNode
{
public:
							splineMatrix();
	virtual					~splineMatrix();
	virtual	MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	static  void*			creator();
	static  MStatus			initialize();
	static  MString			NodeName;
	static  MTypeId			NodeID;

	MStatus					updateCurveInfo(MObject oInputCurve);
	MMatrix*				getMatrixArrayFromParamList(MMatrix upMatrix, 
														double* paramList, 
														MMatrix mtxCurve,
														MObject* p_oCurve,
														int paramListLength);
public:
	static  MObject			aInputCurve;
	static  MObject			aInputCurveMatrix;
	static  MObject			aTopMatrix;
	static  MObject			aAngleByTangent;
	static  MObject			aParameter;
	static  MObject			aOutputMatrix;

public:
	double					minParam;
	double					maxParam;
	bool					angleByTangent;

};

class nearstPoint : public MPxNode
{
public:
							nearstPoint();
	virtual					~nearstPoint() override;
	virtual	MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	static  void*			creator();
	static  MStatus			initialize();
	static  MString			NodeName;
	static  MTypeId			NodeID;

	static  MObject			ainputCurve;
	static  MObject			aInPosition;
	static  MObject			aPosition;
	static  MObject			aOutputResult;
	static  MObject			aResult;
	static  MObject			aOutputPosition;
	static  MObject			aOutputParameter;

};

class Curly : public MPxNode
{
public:
							Curly();
	virtual					~Curly() override;
	virtual	MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	static  void*			creator();
	static  MStatus			initialize();
	static  MString			NodeName;
	static  MTypeId			NodeID;

	static  MObject			aCurly;
	static  MObject			aInCurly;
	static  MObject			aInCurlyStrength;
	static  MObject			aInCurlyClamp;

	static  MObject			aBodyCurly;
	static  MObject			aInBodyCurly;
	static  MObject			aInBodyCurlyStrength;
	static  MObject			aInBodyCurlyClamp;

	static  MObject			aResult;
	static  MObject			aOutCurly;
	static  MObject			aOutBodyCurly;

};

class SlideRange : public MPxNode
{
public:
							SlideRange();
	virtual					~SlideRange() override;
	virtual	MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	static  void*			creator();
	static  MStatus			initialize();
	void					postConstructor() override;
	static  MString			NodeName;
	static  MTypeId			NodeID;

	MStatus					postConstructor_init_curveRamp(MObject& nodeObj,
							MObject& rampObj,
							int index,
							float position,
							float value,
							int interpolation);

	static  MObject			aInCurve;
	static  MObject			aCurveRamp;
	static  MObject			aInPosition;
	static  MObject			aInSlidePosition;
	static	MObject			aOutputTransform;
	static	MObject			aOutputTranslate;
	static	MObject			aOutputRotate;
	static	MObject			aOutputScale;
};

#endif // !IKNODE_H

