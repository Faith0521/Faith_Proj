# -*- coding: utf-8 -*-
# @Author: YinYuFei
# @Date:   2022-04-27 08:55:58
# @Last Modified by:   Admin
# @Last Modified time: 2022-05-01 22:19:51

# basic
from Faith.Guide import Component
import sys,os,re,datetime,getpass

# pymel
from pymel import core as pm
from  pymel.core import datatypes as datatypes

# faith
import Faith
from Faith import Modules as components
from Faith.Guide.Component import guide as g
from Faith.Core import aboutAttribute, aboutDag, aboutIcon, utils,aboutLog,aboutAdd,aboutNode
from . import guide,naming

PY2 = sys.version_info[0] == 2
COMPONENT_ENV_KEY = "FAITH_COMPONENT_PATH"

if not pm.pluginInfo("FaithNodes", q = True, loaded = True):
	try:
		pm.loadPlugin("FaithNodes")
	except RuntimeError:
		pm.displayError("Can not find FaithNodes.mll")
if not pm.pluginInfo("matrixNodes", q = True, loaded = True):
	pm.loadPlugin("matrixNodes")

def getComponentDirectories():
	"""
	获得Modules的路径
	:return:
	"""
    # TODO: ready to support multiple default directories
	return utils.gatherCustomModuleDirectories(
		COMPONENT_ENV_KEY,
		[os.path.join(os.path.dirname(components.__file__))])

def importComponentGuide(guide_type):
	"""
	导入guide模块
	:param guide_type:
	:return:
	"""

	dirs = getComponentDirectories()
	defFmt = "Faith.Guide.Component.{}.guide"
	customFmt = "{}.guide"

	module = utils.importFromStandardOrCustomDirectories(
		dirs, defFmt, customFmt, guide_type)
	return module

def importComponent(comp_type):
	"""
	导入Component
	:param comp_type:
	:return:
	"""
	dirs = getComponentDirectories()
	defFmt = "Faith.Guide.Component.{}"
	customFmt = "{}"

	module = utils.importFromStandardOrCustomDirectories(
		dirs, defFmt, customFmt, comp_type)
	return module

class Rigging(object):

	"""
	Main Rigging Class
	"""
	def __init__(self):
		self.guide = guide.ComponentDraw()
		self.size = g.ComponentGuide().size
		self.groups = {}
		self.subGroups = {}

		self.components = {}
		self.componentsIndex = []

		self.stepDict = {}

		self.build_data = {}

	def build_from_dict(self, dict):
		"""

		:param dict:
		:return:
		"""
		startTime = datetime.datetime.now()

		self.stop = False

		# self.guide.setDict(dict)

	def build(self):
		"""

		:return:
		"""

		self.options = self.guide.values
		self.guides = self.guide.components

		self.stepDict["Run"] = self

		self.initialHierarchy()
		self.processComponents()
		self.finalize()

		return self.model

	def build_from_selected(self):
		"""

		:return:
		"""
		startTime = datetime.datetime.now()
		aboutLog.Logger().info("\n" + " Faith Rigging Start".center(30, "="))
		self.stop = False
		selection = pm.ls(selection = True)
		if not selection:
			aboutLog.Logger().exception("Please select one more guide components!")
			return
		# check if is partial build or full guide build
		if not self.stop:
			aboutLog.Logger().info("\n" + " Guide Setting".center(30, "="))
			self.guide.set_selection()
			if not self.guide.valid:
				return

			# Build
			aboutLog.Logger.info("\n" + " BUILDING FAITH RIGGING ".center(30, "="))
			self.build()

			build_data = self.collect_build_data()

			endTime = datetime.datetime.now()
			finalTime = endTime - startTime
			pm.flushUndo()
			aboutLog.Logger.info("\n" + "= BUILD COMPLETE {} [ {} ] {}".format(
				"=" * 16,
				finalTime,
				"=" * 7
			))

			return build_data

	def collect_build_data(self):
		"""
		Collect post build data
		:return:
		"""
		self.build_data["Components"] = []
		for c,comp in self.stepDict["Run"].components.items():
			self.build_data["Components"].append(comp.build_data)

		# if self.options[""]

		return self.build_data

	def initialHierarchy(self):
		"""
		Build the rig
		:return:
		"""
		aboutLog.Logger.info("Initilize".ljust(40, "-") + ">")

		# -------------------------------------------
		# MODEL
		self.model = aboutAdd.addTransformFromPos(
			None, self.options["rig_name"]
		)
		aboutAttribute.lockAttribute(self.model)

		# INFO
		self.is_Rig = aboutAttribute.addAttribute(
			self.model, "is_rig", "bool", True
		)
		self.rigName = aboutAttribute.addAttribute(
			self.model, "rig_name", "string", self.options["rig_name"]
		)
		self.userPath = aboutAttribute.addAttribute(
			self.model, "user_path", "string", getpass.getuser()
		)
		self.date = aboutAttribute.addAttribute(
			self.model, "now_time", "string", str(datetime.datetime.now())
		)
		self.maya_version = aboutAttribute.addAttribute(
			self.model, "maya_version", "string", str(pm.mel.getApplicationVersionAsFloat())
		)
		self.ctrlVis = aboutAttribute.addAttribute(
			self.model, "ctrl_vis", "bool", True
		)

		self.currentVersion = pm.mel.getApplicationVersionAsFloat()
		if self.currentVersion >= 2016.5:
			self.ctrlVisPlayBack = aboutAttribute.addAttribute(
				self.model, "ctrl_vis_playback", "bool", True
			)

		self.jntVis = aboutAttribute.addAttribute(
			self.model, "jnt_vis", "bool", True
		)
		if self.currentVersion >= 2022.0:
			self.ctrlXray = aboutAttribute.addAttribute(
				self.model, "ctrl_vis_xRay", "bool", True
			)
		
		self.rigGroups = self.model.addAttr("rigGroups", at = "message", m = 1)
		self.rigDagPose = self.model.addAttr("rigDagPose", at = "message", m = 1)
		self.rigCtrlTags = self.model.addAttr("rigCtrlTags", at = "message", m = 1)

		# =========================================================================
		# Global Ctrl
		if self.options["globalCtl"]:
			if self.options["globalCtl_Name"]:
				name = self.options["globalCtl_Name"]
			else:
				name = "global_ctrl"

			icon_type = "Main"
		else:
			name = "global_C0_ctl"
			icon_type = "Main"

		self.global_ctrl = self.addCtl(self.model,
									   name, datatypes.Matrix(), icon_type,
									   w=self.size * 10,
									   h=self.size * 10,
									   d=self.size * 10
									   )

		aboutAttribute.setRotOrder(self.global_ctrl, "ZXY")
		pm.connectAttr(self.ctrlVis, self.global_ctrl.attr("visibility"))
		if self.currentVersion >= 2016.5:
			pm.connectAttr(
				self.ctrlVisPlayBack, self.global_ctrl.attr("hideOnPlayback")
			)
		aboutAttribute.lockAttribute(self.global_ctrl, ['v'])

		# ----------------------------------------------------
		self.setUpWS = aboutAdd.addTransformFromPos(self.model, "Settings")
		aboutAttribute.lockAttribute(self.setUpWS)

		if self.options["joint_rig"]:
			self.jnt_org = aboutAdd.addTransformFromPos(self.model, "skeleton_jnts_org")
			pm.connectAttr(self.jntVis, self.jnt_org.attr("visibility"))

	def processComponents(self):
		"""

		:return:
		"""
		# INIT
		self.components_infos = {}
		for comp in self.guide.componentsIndex:
			guide_ = self.guides[comp]
			aboutLog.Logger.info("Initialize {0} ({1})".format(guide_.fullName, guide_.type))

			module = importComponent(guide_.type)
			component = getattr(module, "Rigging")

			comp = component(self, guide_)
			if comp.fullName not in self.componentsIndex:
				self.components[comp.fullName] = comp
				self.componentsIndex.append(comp.fullName)

				self.components_infos[comp.fullName] = [
					guide_.guideType, guide_.author
				]

		self.steps = Component.Rigging.steps
		for i, name in enumerate(self.steps):
			for compName in self.componentsIndex:
				comp = self.components[compName]
				comp.stepMethods[i]()

			if self.options["step"] >= 1 and i >= self.options["step"] - 1:
				break
				
	def finalize(self):
		"""

		:return:
		"""
		try:
			pm.delete("iconsGroup")
		except:
			pm.displayWarning("Can not find iconsGroup, Please check ! ")
		
		groupIdx = 0

		aboutLog.Logger.info("Final".ljust(40, "-") + ">")

		# if self.options["joint_rig"]:
		# 	aboutLog.Logger.info("Cleaning joints")
		# 	for jnt in aboutDag.findChildrenPartial(self.join)
		aboutLog.Logger.info("Creating transform groups")
		for name in self.componentsIndex:
			component_ = self.components[name]
			for name, objects in component_.groups.items():
				self.addToGroup(objects, name)
			for name, objects in component_.subGroups.items():
				self.addToSubGroup(objects, name)

		masterSet = pm.sets(n=self.model.name() + "_sets", em=True)
		pm.connectAttr(masterSet.message, self.model.rigGroups[groupIdx])
		groupIdx += 1

		# Creating all groups
		pm.select(cl=True)
		for name, objects in self.groups.items():
			s = pm.sets(n=self.model.name() + "_" + name + "_grp")
			s.union(objects)
			pm.connectAttr(s.message, self.model.rigGroups[groupIdx])
			groupIdx += 1
			masterSet.add(s)
		for parentGroup, subgroups in self.subGroups.items():
			pg = pm.PyNode(self.model.name() + "_" + parentGroup + "_grp")
			for sg in subgroups:
				sub = pm.PyNode(self.model.name() + "_" + sg + "_grp")
				if sub in masterSet.members():
					masterSet.remove(sub)
				pg.add(sub)

		# Bind pose ---------------------------------------
		# controls_grp = self.groups["controllers"]
		# pprint(controls_grp, stream=None, indent=1, width=100)
		# ctl_master_grp = pm.PyNode(self.model.name() + "_controllers_grp")
		# pm.select(ctl_master_grp, replace=True)
		# dag_node = pm.dagPose(save=True, selection=True)
		# pm.connectAttr(dag_node.message, self.model.rigPoses[0])
		# print(dag_node)

		# # Bind skin re-apply
		# if self.options["importSkin"]:
		# 	try:
		# 		pm.displayInfo("Importing Skin")
		# 		skin.importSkin(self.options["skin"])

		# 	except RuntimeError:
		# 		pm.displayWarning(
		# 			"Skin doesn't exist or is not correct. "
		# 			+ self.options["skin"] + " Skipped!")


	def addCtl(self, parent, name, m, iconType, **kwargs):
		"""

		:param parent:
		:param name:
		:param m:
		:param iconType:
		:return:
		"""
		bufferName = name + "_controlBuffer"
		if bufferName in self.guide.controllers.keys():
			ctl_ref = self.guide.controllers[bufferName]
			ctl = aboutAdd.addTransform(parent, name, m)
			for shape in ctl_ref.getShapes():
				ctl.addChild(shape, shape = True, add = True)
				pm.rename(shape, name + "Shape")
		else:
			ctl = aboutIcon.CreateControl(parent, iconType, name, m, **kwargs)

		for shape in ctl.getShapes():
			shape.isHistoricallyInteresting.set(False)
			if self.currentVersion >= 2022.0:
				pm.connectAttr(self.ctrlXray, shape.attr("alwaysDrawOnTop"))

		if self.currentVersion >= 2016.5:
			pm.controller(ctl)
			self.add_controller_tag(ctl, None)
			
		aboutAttribute.addAttribute(ctl, "is_ctrl", "bool", keyable = False)

		return ctl

	def addToGroup(self, objects, names = ["hidden"]):
		"""

		:param objects:
		:param names:
		:return:
		"""
		if not isinstance(names, list):
			names = [names]

		if not isinstance(objects, list):
			objects = [objects]

		for name in names:
			if name not in self.groups.keys():
				self.groups[name] = []

			self.groups[name].extend(objects)

	def addToSubGroup(self, subGroups, parentGroups=["hidden"]):
		"""
		将对象添加到字典中以供以后创建SubGroup
		:param subGroups: 需要添加的Groups
		:param parentGroups: 需要创建的parent groups
		:return:
		"""

		if not isinstance(parentGroups, list):
			parentGroups = [parentGroups]

		if not isinstance(subGroups, list):
			subGroups = [subGroups]

		for pg in parentGroups:
			if pg not in self.subGroups.keys():
				self.subGroups[pg] = []
			self.subGroups[pg].extend(subGroups)

	def add_controller_tag(self, ctl, tagParent):
		"""

		:param ctl:
		:param tagParent:
		:return:
		"""
		ctt = aboutNode.add_controller_tag(ctl, tagParent)
		if ctt:
			ni = aboutAttribute.get_next_available_index(self.model.rigCtrlTags)
			pm.connectAttr(ctt.message,
							self.model.attr("rigCtrlTags[{}]".format(str(ni))))

	def findRelative(self, guideName):
		"""
		返回与guide对象相匹配的物体
		:param guideName: guide的名称
		:return: 找到的物体
		"""

		if guideName is None:
			return self.global_ctrl
		# elif guideName == "":
		# 	return self.global_ctrl

		comp_name = self.getComponentName(guideName)
		relative_name = self.getRelativeName(guideName)

		if comp_name not in self.components.keys():
			return self.global_ctrl
		return self.components[comp_name].getRelation(relative_name)

	def getComponentName(self, guideName, local=True):
		"""
		此函数返回组件名称
		ex."arm_C0_root" return "arm_C0"
		:param guideName: guide名称
		:param local:
		:return: 组件名称
		"""

		if guideName is None:
			return None

		if local:
			guideName = self.getLocalName(guideName)

		names = naming.get_component_and_relative_name(guideName)
		if names:
			return names[0]

	def getLocalName(self, guideName):
		"""

		:param guideName:
		:return:
		"""

		if guideName is None:
			return None
		localName = guideName.split("|")[-1]
		return localName

	def getRelativeName(self, guideName):
		"""

		:param guideName:
		:return:
		"""

		if guideName is None:
			return None

		localName = self.getLocalName(guideName)
		names = naming.get_component_and_relative_name(localName)
		if names:
			return names[1]

	def findControlRelative(self, guideName):
		"""

		:param guideName:
		:return:
		"""
		if guideName is None:
			return self.global_ctrl

		# localName = self.getLocalName(guideName)
		comp_name = self.getComponentName(guideName)
		relative_name = self.getRelativeName(guideName)

		if comp_name not in self.components.keys():
			return self.global_ctrl
		return self.components[comp_name].getControlRelation(relative_name)

	def findComponent(self, guideName):
		"""

		:param guideName:
		:return:
		"""
		if guideName is None:
			return None

		comp_name = self.getComponentName(guideName, False)

		if comp_name not in self.components.keys():
			return None

		return self.components[comp_name]









































