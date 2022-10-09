#include "SplitSkinWeights.h"
#include "skin_def.h"

#define kHelpFlag									"-h"
#define kHelpFlagLong								"-help"

#define kXsFlag										"-xsv"
#define kXsFlagLong									"-xsValue"

#define kYsFlag										"-ysv"
#define kYsFlagLong									"-ysValue"

#define kTypeFlag									"-typ"
#define kTypeFlagLong								"-type"

#define kRadiusFlag									"-r"
#define kRadiusFlagLong								"-radius"

SplitSkin::SplitSkin()
{
}

SplitSkin::~SplitSkin()
{
}

MStatus SplitSkin::doIt(const MArgList& argList)
{
	MStatus status;


	status = parseArgs(argList);	// Parse the args!
	if (status != MS::kSuccess)
		return status;

	uJnts = sListComp.length();

	//if (uJnts == 0)
	//{
	//	showUsage();
	//	MGlobal::displayError("splitSkin - You must select or provide one or more joints to split.");
	//	return MS::kFailure;
	//}
	for (unsigned i=1; i<uJnts; i++)
	{
		MDagPath jntPath;
		sListComp.getDagPath(i, jntPath);
		if (jntPath.apiType() == MFn::kJoint)
		{
			jntPathInfluences.push_back(jntPath);
		}
	}
	status = getWeightValue(skinInfo.m_oSkinCluster, jntPathInfluences, weightInfoBefore);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = redoIt();	// do real work!
	CHECK_MSTATUS_AND_RETURN_IT(status);

	return status;
}

MStatus SplitSkin::redoIt()
{
	MStatus status;

	uJnts = sListComp.length();

	if (uJnts - 3 < 0)
	{
		MGlobal::displayError("Please select at least two joints to split.");
		return MS::kFailure;
	}

	MObjectArray selJntArray;
	MObjectArray compJntArray;
	unsigned u,i;
	for (u=1; u<uJnts;++u)
	{
		MObject oJnt;
		sListComp.getDependNode(u, oJnt);		// Get an MObject to the u-th thing selected...
		selJntArray.append(oJnt);
	}

	for (u = 2; u < uJnts; ++u)
	{
		MObject oJnt;
		sListComp.getDependNode(u, oJnt);	
		compJntArray.append(oJnt);
	}
	if (type == "spine" || type == "brow" || type == "belt" || type == "transverse")
	{
		status = split_solve(type, skinInfo, weightInfoBefore, selJntArray, compJntArray, xsVal, ysVal, radius);
	}
	
	else if (type == "cloth")
	{
		status = cloth_solve(skinInfo, weightInfoBefore, selJntArray, xsVal, ysVal, radius);
	}

	else if (type == "eyes")
	{
		status = eye_solve(skinInfo, weightInfoBefore, selJntArray);
	}

	return MS::kSuccess;
}

MStatus SplitSkin::undoIt()
{
	MStatus status;
	setWeightValue(skinInfo.m_oSkinCluster, weightInfoBefore);

	return MS::kSuccess;
}

bool SplitSkin::isUndoable() const
{
	return true;
}

void* SplitSkin::creator()
{
	return new SplitSkin();
}

MSyntax SplitSkin::newSyntax()
{
	MSyntax syntax;
	syntax.addFlag(kHelpFlag, kHelpFlagLong,MSyntax::kUnsigned);
	syntax.addFlag(kXsFlag, kXsFlagLong, MSyntax::kDouble, MSyntax::kDouble, MSyntax::kDouble, MSyntax::kDouble);
	syntax.addFlag(kYsFlag, kYsFlagLong, MSyntax::kDouble, MSyntax::kDouble, MSyntax::kDouble, MSyntax::kDouble);
	syntax.addFlag(kTypeFlag, kTypeFlagLong, MSyntax::kUnsigned);
	syntax.addFlag(kRadiusFlag, kRadiusFlagLong, MSyntax::kUnsigned);

	syntax.useSelectionAsDefault(true);
	syntax.setObjectType(MSyntax::kSelectionList, 1);

	return syntax;
}

MStatus SplitSkin::parseArgs(const MArgList& argList)
{
	MStatus status;

	MArgDatabase argData(syntax(), argList, &status);

	if (argData.isFlagSet(kHelpFlag))
	{
		showUsage();
		return MS::kFailure;
	}
	if (argData.isFlagSet(kXsFlag))
	{
		xsVal.push_back(argData.flagArgumentDouble(kXsFlag, 0));
		xsVal.push_back(argData.flagArgumentDouble(kXsFlag, 1));
		xsVal.push_back(argData.flagArgumentDouble(kXsFlag, 2));
		xsVal.push_back(argData.flagArgumentDouble(kXsFlag, 3));
	}
	else
	{
		xsVal = { 0, 0.33, 0.67, 1 };
	}
	if (argData.isFlagSet(kYsFlag))
	{
		ysVal.push_back(argData.flagArgumentDouble(kYsFlag, 0));
		ysVal.push_back(argData.flagArgumentDouble(kYsFlag, 1));
		ysVal.push_back(argData.flagArgumentDouble(kYsFlag, 2));
		ysVal.push_back(argData.flagArgumentDouble(kYsFlag, 3));
	}
	else
	{
		ysVal = { 0, 0, 1, 1 };
	}
	if (argData.isFlagSet(kTypeFlag))
	{
		if (argData.flagArgumentInt(kTypeFlag, 0) == 0) type = "spine";
		else if (argData.flagArgumentInt(kTypeFlag, 0) == 1) type = "belt";
		else if (argData.flagArgumentInt(kTypeFlag, 0) == 2) type = "brow";
		else if (argData.flagArgumentInt(kTypeFlag, 0) == 3) type = "transverse";
		else if (argData.flagArgumentInt(kTypeFlag, 0) == 4) type = "cloth";
		else if (argData.flagArgumentInt(kTypeFlag, 0) == 5) type = "eyes";
	}
	if (argData.isFlagSet(kRadiusFlag))
	{
		radius = argData.flagArgumentDouble(kRadiusFlag, 0);
	}

	status = getInfomaiton(argData);

	if (! skinInfo.m_pathMesh.isValid())
	{
		return MS::kFailure;
	}

	argData.getObjects(sListComp);

	return status;
}

void SplitSkin::showUsage()
{
	MString str;

	str += (" ---------------------------------------\n");
	str += (" splitSkin USAGE: - Split skinWeights for skin joints.\n");
	str += (" ---------------------------------------\n");
	str += ("     splitSkin -skinCl \"skinCluster1\" OBJECTS ;\n");
	str += (" \n");
	str += ("   FLAGS:\n");
	str += ("       -h     | -help           :  Get help on this command. \n");
	str += ("       -scl   | -skincl         :  Specify specific skinCluster to split.\n");
	MGlobal::displayInfo(str);
	setResult(str);
}
