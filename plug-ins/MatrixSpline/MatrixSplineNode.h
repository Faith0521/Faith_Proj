#ifndef _MatrixSplineNode
#define _MatrixSplineNode

#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MDoubleArray.h>
#include <maya/MIntArray.h>
#include <maya/MTypeId.h> 
#include <maya/MString.h>
#include <QtCore/QJsonObject>
#include <QtCore/QJsonArray>
#include <QtCore/QList>
#include <QtCore/QListIterator>
#include <QtCore/QString>
#include <QtCore/QJsonValue>
 
class MatrixSpline : public MPxNode
{
public:
						MatrixSpline();
	virtual				~MatrixSpline(); 

	virtual MStatus		compute( const MPlug& plug, MDataBlock& data );

	static  void*		creator();
	static  MStatus		initialize();
	QJsonArray			pointOnCurveWeights(MIntArray cvs, double t, int degree);
	MDoubleArray		defaultKnots(int count, int degree);

public:

	static  MObject		input;		
	static  MObject		output;		

	static	MString		NodeName;
	static	MTypeId		NodeID;
};

#endif
