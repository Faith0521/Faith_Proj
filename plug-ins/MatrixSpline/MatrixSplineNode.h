#ifndef MatrixSplineNode_h
#define MatrixSplineNode_h

#include <iostream>
#include <vector>
#include <map>
#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MDoubleArray.h>
#include <maya/MMatrixArray.h>
#include <maya/MQuaternion.h>
#include <maya/MPxTransformationMatrix.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MArrayDataHandle.h>
#include <maya/MIntArray.h>
#include <maya/MTypeId.h> 
#include <maya/MString.h>
#include <maya/MMatrix.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MGlobal.h>

using namespace std;
#define pi 3.1415926535897932384626433832795

template<class T>
struct WeightInfo
{
	T  mat_num;
	double  weight;
};


class MatrixSpline : public MPxNode
{
public:
	MatrixSpline();
	virtual      ~MatrixSpline();

	virtual MStatus    compute(const MPlug& plug, MDataBlock& data);

	static  void* creator();
	static  MStatus    initialize();

	MMatrixArray  calculateMatrix(int count, int pCount, int degree,
		MMatrixArray cvMatricies, MVector aimAxis,
		MVector upAxis);

public:

	static  MObject  amatrixIn;
	static MObject  aAxis;
	static MObject  amatrixOut;

	static MString  NodeName;
	static MTypeId  NodeID;
};

#endif