#include "SplitSkinWeights.h"
#include <maya/MFnPlugin.h>

MStatus initializePlugin(MObject obj)
{
	MStatus   stat;

	MFnPlugin plugin(obj, "YinYuFei", "0.1", "Any");
	stat = plugin.registerCommand("splitSkin", SplitSkin::creator, SplitSkin::newSyntax);
	CHECK_MSTATUS_AND_RETURN_IT(stat);
	return stat;
}

MStatus uninitializePlugin(MObject obj)
{
	MStatus   stat;
	MFnPlugin plugin(obj);

	stat = plugin.deregisterCommand("splitSkin");
	CHECK_MSTATUS_AND_RETURN_IT(stat);
	return stat;
}
