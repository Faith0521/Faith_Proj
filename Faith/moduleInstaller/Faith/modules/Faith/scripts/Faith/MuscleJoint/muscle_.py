from maya import cmds as mc
from pymel import core as pm

class Muscle_Joint(object):

    def __init__(self, Side='L',
                 namePrefix=''):
        self.side = Side
        self.namePrefix = namePrefix

    def _create(self, base_joint, parent_joint,
                driver_joint, position_override=None,
                up_vec=None, skip_axis=None,
                volume_y=0.5, volume_z=0.5,
                connect_driver=None, connect_attr=None,
                connect_weight=1.0, mirror=True):
        """

        @param base_joint:
        @param parent_joint:
        @param driver_joint:
        @param position_override:
        @param up_vec:
        @param skip_axis:
        @param volume_y:
        @param volume_z:
        @param connect_driver:
        @param connect_attr:
        @param connect_weight:
        @param mirror:
        @return:
        """


















































