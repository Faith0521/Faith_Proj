#include "Faith_solvers.h"

MString CorrectiveShape::NodeName = "FAITH_CorrectiveShape";
MTypeId CorrectiveShape::NodeID = MTypeId(0x0017);

MObject CorrectiveShape::aMatrix;
MObject CorrectiveShape::aCorrectiveGeo;
MObject CorrectiveShape::aDeformedPoints;
bool	CorrectiveShape::_initialized = false;
MPointArray CorrectiveShape::_deformedPoints;
MMatrixArray CorrectiveShape::_matrices;

CorrectiveShape::CorrectiveShape()
{
}

CorrectiveShape::~CorrectiveShape()
{
}

MStatus CorrectiveShape::deform(MDataBlock& data, MItGeometry& iter, const MMatrix& mat, unsigned int multiIndex)
{
	MStatus status;
	MFnMesh fnMesh = data.inputValue(aCorrectiveGeo).asMesh();
	
	MPointArray correctivePoints;
	fnMesh.getPoints(correctivePoints);

	if (_initialized == false)
	{
		MArrayDataHandle hMatrix = data.inputArrayValue(aMatrix);
		unsigned int matrixCount = hMatrix.elementCount();
		if (matrixCount == 0)
		{
			return MS::kSuccess;
		}

		for (unsigned int i=0; i<matrixCount; i++)
		{
			hMatrix.jumpToArrayElement(i);
			_matrices.append(hMatrix.inputValue().asMatrix());
		}
		MFnPointArrayData fnData = data.inputValue(aDeformedPoints).data();
		fnData.copyTo(_deformedPoints);
		_initialized = true;
	}

	while (! iter.isDone())
	{
		unsigned int index = iter.index();
		MVector delta = correctivePoints[index] - _deformedPoints[index];
		if (fabs(delta.x) < 0.001 && fabs(delta.y) < 0.001 && fabs(delta.z) < 0.001)
		{
			iter.next();
			continue;
		}

		MVector offset = delta * _matrices[index];
		MPoint pt = iter.position() + offset;
		iter.setPosition(pt);
		iter.next();
	}


	return MS::kSuccess;
}

void* CorrectiveShape::creator()
{
	return new CorrectiveShape();
}

MStatus CorrectiveShape::initialize()
{
	MFnTypedAttribute t;
	MFnMatrixAttribute m;
	aCorrectiveGeo = t.create("correctiveMesh", "cm", MFnData::kMesh);
	addAttribute(aCorrectiveGeo);
	attributeAffects(aCorrectiveGeo, outputGeom);

	aDeformedPoints = t.create("deformedPoints", "dp", MFnData::kPointArray);
	addAttribute(aDeformedPoints);
	attributeAffects(aDeformedPoints, outputGeom);

	aMatrix = m.create("inversionMatrix", "im");
	m.setArray(true);
	addAttribute(aMatrix);
	attributeAffects(aMatrix, outputGeom);

	return MS::kSuccess;
}
