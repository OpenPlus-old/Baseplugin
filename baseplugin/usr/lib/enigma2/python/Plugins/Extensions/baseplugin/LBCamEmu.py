# baseplugin -- Base Plugin for emu and software download.
# Copyright (C) www.linux-box.es
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or   
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU gv; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
# 
# Author: Lucifer
#         iqas   
#
# Internet: www.linux-box.es
# Based on source emus softcam pli mod panel by Taapat taapat@gmail.com
# Based on original source emu panel by linux-box.es

from Plugins.Plugin import PluginDescriptor
from Components.config import config, getConfigListEntry, ConfigText, ConfigPassword, ConfigSelection, ConfigSubsection, ConfigYesNo,   config, configfile
from Components.ConfigList import ConfigListScreen
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap, NumberActionMap
from Screens.ChoiceBox import ChoiceBox
from Components.config import config, configfile, getConfigListEntry
from Components.ConfigList import ConfigList, ConfigListScreen
from Screens.PluginBrowser import PluginBrowser
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.Screen import Screen
from Components.Label import Label
from enigma import eTimer, RT_HALIGN_LEFT, eListboxPythonMultiContent, gFont, getDesktop, eSize, ePoint
from Components.Language import language
from Components.Sources.StaticText import StaticText
from Tools.Directories import fileExists
from os import environ
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from inspect import getsourcefile
from os.path import abspath
import os
import gettext
import plugin_config

plugin = plugin_config.plugin
plugin_def = plugin_config.plugin_def

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("messages", "%s%s%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/", plugin, "/locale"))

def _(txt):
	t = gettext.dgettext("messages", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

#####################################################################################################
class installCam(Screen):
	skin = """
<screen name="installCam" position="center,160" size="1150,500" title="plugin_title">
    <ePixmap position="715,10" zPosition="1" size="450,700" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/plugin_name/images/fondo10.png" alphatest="blend" transparent="1" />
<widget source="menu" render="Listbox" position="15,10" size="660,450" scrollbarMode="showOnDemand">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryText(pos = (70, 2), size = (630, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
			MultiContentEntryText(pos = (80, 29), size = (630, 18), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
			MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (50, 40), png = 2), # index 4 is the pixmap
				],
	"fonts": [gFont("Regular", 23),gFont("Regular", 16)],
	"itemHeight": 50
	}
	</convert>
	</widget>
	<ePixmap name="red" position="20,488" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/plugin_name/images/red.png" transparent="1" alphatest="on" />
	<ePixmap name="green" position="190,488" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/plugin_name/images/green.png" transparent="1" alphatest="on" />
	<widget name="key_red" position="20,458" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget name="key_green" position="190,458" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
</screen>"""
	skin = skin.replace("plugin_title", plugin_def)
	skin = skin.replace("plugin_name", plugin)
	  
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("DOWNLOAD FEEDS"))
		self.session = session
		self.list = []
		self["menu"] = List(self.list)
		self.feedlist()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.ok,
				"green": self.setup,
				"red": self.cancel,
			},-1)
		self.list = [ ]
		self["key_red"] = Label(_("Close"))
		self["key_green"] = Label(_("Install"))
		
	def feedlist(self):
		self.list = []
		os.system("opkg update")
		camdlist = os.popen("opkg list | grep lbcam")
		softpng = LoadPixmap(cached = True, path="%s%s%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/", plugin, "/images/emumini.png" ))
		for line in camdlist.readlines():
			try:
				self.list.append(("%s %s" % (line.split(' - ')[0], line.split(' - ')[1]), line.split(' - ')[-1], softpng))
			except:
				pass
		camdlist.close()
		self["menu"].setList(self.list)
		
	def ok(self):
		self.setup()
		
	def setup(self):
		config.plugins.baseplugin.addcam.value = "1"
		config.plugins.baseplugin.addcam.save()
		os.system("opkg install -force-overwrite %s" % self["menu"].getCurrent()[0])
		self.mbox = self.session.open(MessageBox, _("%s is installed" % self["menu"].getCurrent()[0]), MessageBox.TYPE_INFO, timeout = 4 )
		
	def cancel(self):
		self.close()
####################################################################

