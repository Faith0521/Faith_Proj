#ifndef WTADDMATRIX_H
#define WTADDMATRIX_H

#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MArrayDataHandle.h>
#include <maya/MMatrixArray.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>

class wtAddMatrix : public MPxNode
{
public:
							wtAddMatrix();
	virtual					~wtAddMatrix() override;
	virtual MStatus			compute(const MPlug& plug, MDataBlock& data) override;
	static  void*			creator();
	static  MStatus			initialize();

	static  MString			NodeName;
	static  MTypeId			NodeID;
	
	static  MObject			aMatrix;
	static  MObject			aInMatrix;
	static  MObject			aInWeight;
	static  MObject			aOutputMatrix;
};


#endif
