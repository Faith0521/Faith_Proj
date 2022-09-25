#ifndef MatrixSplineNode_h
#define MatrixSplineNode_h

#include <iostream>
#include <vector>
#include <map>
#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MDoubleArray.h>
#include <maya/MMatrixArray.h>
#include <maya/MIntArray.h>
#include <maya/MTypeId.h> 
#include <maya/MString.h>
#include <maya/MMatrix.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MGlobal.h>
#include <QtCore/QJsonObject>
#include <QtCore/QJsonArray>
#include <QtCore/QList>
#include <QtCore/QListIterator>
#include <QtCore/QString>
#include <QtCore/QJsonValue>

using namespace std;
 
struct WeightInfo
{
	MMatrix		mat;
	double		weight;
};

class MatrixSpline : public MPxNode
{
public:
								MatrixSpline();
	virtual						~MatrixSpline(); 

	virtual MStatus				compute( const MPlug& plug, MDataBlock& data );

	static  void*				creator();
	static  MStatus				initialize();
	MDoubleArray				defaultKnots(int count, int degree);
	vector<WeightInfo>			pointOnCurveWeights(MMatrixArray cvs, double t, int degree);
	
public:

	static  MObject		input;		
	static  MObject		output;		

	static	MString		NodeName;
	static	MTypeId		NodeID;
};

#endif
