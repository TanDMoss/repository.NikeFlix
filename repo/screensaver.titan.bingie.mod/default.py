# -*- coding: utf-8 -*-
import xbmcaddon

import sys

from resources.lib.screensaver import Screensaver

_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo('path')
_xml = 'screensaver-titan-bingie-mod.xml'


if __name__ == '__main__':
    screensaver_gui = Screensaver(_xml, _path, 'Default', 'xml')
    screensaver_gui.doModal()
    
    del screensaver_gui
    sys.modules.clear()
