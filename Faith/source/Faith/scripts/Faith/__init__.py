from pkgutil import extend_path
import sys
from . import menu

__path__ = extend_path(__path__, __name__)
self = sys.modules[__name__]
self.menu_id = None

def install():
    self.menu_name = menu.create()