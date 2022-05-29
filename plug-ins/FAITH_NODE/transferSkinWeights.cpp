#include "Faith_solvers.h"
using namespace rapidjson;

MString helpText = "Description: The command exports and imports the skinCluster from selected mesh to/from a file.";

transferSkinWeights::transferSkinWeights()
{
}

transferSkinWeights::~transferSkinWeights()
{
}

MStatus transferSkinWeights::doIt(const MArgList& args)
{
	double modArg = 0;
	MString fileName = "";
	MArgDatabase argData(syntax(), args);
	
	if (argData.isFlagSet("-h"))
	{
		MPxCommand::setResult(helpText);
		return MS::kSuccess;
	}

	if (argData.isFlagSet("-mod"))
	{
		modArg = argData.flagArgumentDouble("-mod", 0);
	}
	if (argData.isFlagSet("-f"))
	{
		fileName = argData.flagArgumentString("-f", 0);
	}
	else
	{
		MGlobal::displayError("transferSkin needs file name flag.");
	}

	if (fileName == "")
	{
		MGlobal::displayError("transferSkin file name is not specified.");
	}

	if (modArg == 0)
	{
		writeWeights(fileName);
	}
	if (modArg == 1)
	{
		readWeights(fileName);
	}

	
	return MS::kSuccess;
}

MSyntax transferSkinWeights::syntax()
{
	MSyntax syntax;
	syntax.addFlag("-h", "-help");
	syntax.addFlag("-f", "-file", MSyntax::kString);
	syntax.addFlag("-mod", "-mode", MSyntax::kLong);
	return syntax;
}

void* transferSkinWeights::creator()
{
	return new transferSkinWeights();
}

bool transferSkinWeights::writeWeights(MString fileName)
{
	clock_t start_time, end_time;
	start_time = clock();

	StringBuffer buf;
	PrettyWriter<rapidjson::StringBuffer> writer(buf); // it can word wrap

	writer.StartObject();

	writer.Key("weights_data");
	writer.StartArray();

	MDagPath path;
	MObject component;
	MIntArray influences;
	MFnSkinCluster skinFn;
	getSelected_skinData(path, component, influences, skinFn);
	MFnDependencyNode node(path.node());
	MDagPathArray infs;
	unsigned int nInfs = skinFn.influenceObjects(infs);

	MDoubleArray weights;
	skinFn.getWeights(path, component, weights, nInfs);
	for (unsigned i = 0; i < weights.length(); i++)
	{
		writer.Double(weights[i]);
	}

	writer.EndArray();
	writer.EndObject();

	string json_content = buf.GetString();

	ofstream outfile;
	outfile.open(fileName.asChar(), ios::out|ios::binary);
	if (!outfile.is_open()) {
		fprintf(stderr, "fail to open file to write: %s\n", fileName);
		return -1;
	}

	outfile.write(json_content.c_str(), sizeof(char)*json_content.size());
	
	outfile.close();

	end_time = clock();
	printf("%lf ", (double)(end_time - start_time) / CLOCKS_PER_SEC);

	return true;
}

bool transferSkinWeights::readWeights(MString fileName)
{
	FILE* fp = fopen(fileName.asChar(), "rb");
	if (!fp) {
		printf("open failed! file: %s", fileName);
	}

	char buf[1024 * 16];
	string result;

	while (int n = fgets(buf, 1024 * 16, fp) != NULL)
	{
		result.append(buf);
	}
	fclose(fp);

	Document d;
	d.Parse(result.c_str());
	const Value& obj = d["weights_data"];
	MDoubleArray weights;
	for (SizeType i=0; i<obj.Size();i++)
	{
		double node = obj[i].GetDouble();
		weights.append(node);
	}

	MDagPath path;
	MObject component;
	MIntArray influences;
	MFnSkinCluster skinFn;
	getSelected_skinData(path, component, influences, skinFn);

	skinFn.setWeights(path, component, influences, weights);

	return true;
}

MStatus transferSkinWeights::getSelected_skinData(MDagPath& path, MObject& component, MIntArray& influences, MFnSkinCluster& skinFn)
{
	MSelectionList selection;
	MGlobal::getActiveSelectionList(selection);
	selection.getDagPath(0, path, component);
	path.extendToShape();
	MItDependencyGraph dgIt(path.node(), MFn::kSkinClusterFilter, MItDependencyGraph::kUpstream);
	skinFn.setObject(dgIt.currentItem());
	MDagPathArray infPathArray;
	skinFn.influenceObjects(infPathArray);
	for (unsigned i = 0; i < infPathArray.length(); i++)
		influences.append(skinFn.indexForInfluenceObject(infPathArray[i]));

	return MS::kSuccess;
}
