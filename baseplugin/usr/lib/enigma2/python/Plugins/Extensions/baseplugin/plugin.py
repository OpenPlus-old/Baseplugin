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
#	  iqas
#
# Internet: www.linux-box.es
# Based on source emus softcam pli mod panel by Taapat taapat@gmail.com
# Based on original source emu panel by linux-box.es
# Thanks for translate to it, de, pt to xavi220 on linux-box.es

from Components.ActionMap import ActionMap
from Components.config import config, ConfigSubsection, ConfigText, \
	getConfigListEntry
from Components.Console import Console
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.List import List
from Components.ScrollLabel import ScrollLabel
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from Components.Language import language
from enigma import eTimer
from os import mkdir, path, remove
import os.path
from time import sleep
from inspect import getsourcefile
from os.path import abspath
import gettext
import os
from os import environ
import LBCamEmu
import LBExtra
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
def getcamcmd(cam):
	if getcamscript(cam):
		return config.plugins.baseplugin.camdir.value + "/" + cam + " start"
	else:
		cam = cam.lower()
		if "oscam" in cam:
			return config.plugins.baseplugin.camdir.value + "/" + cam + " -bc " + \
				config.plugins.baseplugin.camconfig.value + "/"
		elif "wicard" in cam:
			return "ulimit -s 512; " + config.plugins.baseplugin.camdir.value + \
			"/" + cam + " -d -c " + config.plugins.baseplugin.camconfig.value + \
			"/wicardd.conf"
		elif "camd3" in cam:
			return config.plugins.baseplugin.camdir.value + "/" + cam + " " + \
				config.plugins.baseplugin.camconfig.value + "/camd3.config"
		elif "mbox" in cam:
			return config.plugins.baseplugin.camdir.value + "/" + cam + " " + \
				config.plugins.baseplugin.camconfig.value + "/mbox.cfg"
		elif "mpcs" in cam:
			return config.plugins.baseplugin.camdir.value + "/" + cam + " -c " + \
				config.plugins.baseplugin.camconfig.value
		elif "newcs" in cam:
			return config.plugins.baseplugin.camdir.value + "/" + cam + " -C " + \
				config.plugins.baseplugin.camconfig.value + "/newcs.conf"
		elif "vizcam" in cam:
			return config.plugins.baseplugin.camdir.value + "/" + cam + " -b -c " + \
				config.plugins.baseplugin.camconfig.value + "/"
		elif "rucam" in cam:
			return config.plugins.baseplugin.camdir.value + "/" + cam + " -b"
		else:
			return config.plugins.baseplugin.camdir.value + "/" + cam

def getcamscript(cam):
	cam = cam.lower()
	if cam.startswith('camemu.'):
		return True
	else:
		return False

def stopcam(cam):
	if getcamscript(cam):
		cmd = config.plugins.baseplugin.camdir.value + "/" + cam + " stop"
	else:
		cmd = "killall -15 " + cam
	Console().ePopen(cmd)
	print plugin_def, _(" stopping"), cam
	try:
		remove("/tmp/ecm.info")
	except:
		pass

def createdir(list):
	dir = ""
	for line in list[1:].split("/"):
		dir += "/" + line
		if not path.exists(dir):
			try:
				mkdir(dir)
			except:
				print plugin_def, _(" Failed to mkdir"), dir

def checkconfigdir():
	if not path.exists(config.plugins.baseplugin.camconfig.value):
		createdir("/var/keys")
		config.plugins.baseplugin.camconfig.value = "/var/keys"
		config.plugins.baseplugin.camconfig.save()
	if not path.exists(config.plugins.baseplugin.camdir.value):
		if path.exists("/usr/bin/cam"):
			config.plugins.baseplugin.camdir.value = "/usr/bin/cam"
		else:
			createdir("/usr/CamEmu")
			config.plugins.baseplugin.camdir.value = "/usr/CamEmu"
		config.plugins.baseplugin.camdir.save()
        # Check if feed is active
        if not os.path.isfile("/etc/opkg/baseplugin.conf"):
                with open ('/etc/opkg/baseplugin.conf', 'a') as f: f.write (plugin_config.repo_feed + '\n')        
 
config.plugins.baseplugin = ConfigSubsection()
config.plugins.baseplugin.actcam = ConfigText(default = "none")
config.plugins.baseplugin.camconfig = ConfigText(default = "/var/keys",
	visible_width = 100, fixed_size = False)
config.plugins.baseplugin.camdir = ConfigText(default = "/usr/CamEmu",
	visible_width = 100, fixed_size = False)
config.plugins.baseplugin.addcam = ConfigText(default="0")
checkconfigdir()

class LBCamManager(Screen):
	skin = """
	<screen position="center,center" size="630,370" title="plugin_title">
	<eLabel position="5,0" size="620,2" backgroundColor="#aaaaaa" />
	<widget source="list" render="Listbox" position="10,15" size="340,300" \
	scrollbarMode="showOnDemand">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (51, 40), png = 1), 
			MultiContentEntryText(pos = (65, 10), size = (275, 40), font=0, \
				flags = RT_HALIGN_LEFT, text = 0), 
			MultiContentEntryText(pos = (5, 25), size = (51, 16), font=1, \
				flags = RT_HALIGN_CENTER, text = 2), 
				],
			"fonts": [gFont("Regular", 26),gFont("Regular", 12)],"itemHeight": 50 }
	</convert>
	</widget>
	<eLabel halign="center" position="390,10" size="210,35" font="Regular;20" \
		text="Ecm info" transparent="1" />
	<widget name="status" position="360,50" size="320,300" font="Regular;16" \
		halign="left" noWrap="1" />
	<eLabel position="12,358" size="148,2" backgroundColor="#00ff2525" />
	<eLabel position="165,358" size="148,2" backgroundColor="#00389416" />
	<eLabel position="318,358" size="148,2" backgroundColor="#00baa329" />
	<eLabel position="471,358" size="148,2" backgroundColor="#006565ff" />
	<widget name="key_red" position="12,328" zPosition="2" size="148,30" \
		valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget name="key_green" position="165,328" zPosition="2" size="148,30" \
		valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget name="key_yellow" position="318,328" zPosition="2" size="148,30" \
		valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget name="key_blue" position="471,328" zPosition="2" size="148,30" \
		valign="center" halign="center" font="Regular;22" transparent="1" />
	</screen>"""
	
	skin = skin.replace("plugin_title", plugin_def + " - v" + plugin_config.curr_version)
	def __init__(self, session):
		Screen.__init__(self, session)
		self.Console = Console()
		self["key_red"] = Label(_("Stop"))
		self["key_green"] = Label(_("Start"))
		self["key_yellow"] = Label(_("Extra"))
		self["key_blue"] = Label(_("Download"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.ok,
				"green": self.start,
				"red": self.stop,
				"yellow": self.extra,
				"blue": self.StartCamInstall
			}, -1)
		self["status"] = ScrollLabel()
		self["list"] = List([])
		checkconfigdir()
		self.actcam = config.plugins.baseplugin.actcam.value
		self.camstartcmd = ""
		self.CreateInfo()
		self.Timer = eTimer()
		self.Timer.callback.append(self.cronPlugin)
		self.Timer.start(1000*4, False)

	def CreateInfo(self):
		self.iscam = False
		self.StartCreateCamlist()
		self.cronPlugin()

	def cronPlugin(self):
		# Check for changes on installed cams
		if config.plugins.baseplugin.addcam.value != "0":
		        config.plugins.baseplugin.addcam.value = "0" 
                        config.plugins.baseplugin.addcam.save()        
                        self.StartCreateCamlist()
                #update ecm
                listecm = ""
		try:
			ecmfiles = open("/tmp/ecm.info", "r")
			for line in ecmfiles:
				if line[32:]:
					linebreak = line[23:].find(' ') + 23
					listecm += line[0:linebreak]
					listecm += "\n" + line[linebreak + 1:]
				else:
					listecm += line
			self["status"].setText(listecm)
			ecmfiles.close()
		except:
			self["status"].setText("")


	def StartCreateCamlist(self):
		self.Console.ePopen("ls %s" % config.plugins.baseplugin.camdir.value,
			self.CamListStart)

	def CamListStart(self, result, retval, extra_args):
		if result.strip() and not result.startswith('ls: '):
			self.iscam = True
			self.softcamlist = result
			self.Console.ePopen("chmod 755 %s/*" %
				config.plugins.baseplugin.camdir.value)
			if self.actcam != "none" and getcamscript(self.actcam):
				self.CreateCamList()
			else:
				self.Console.ePopen("pidof %s" % self.actcam, self.CamActive)
		else:
			if path.exists("/usr/bin/cam") and not self.iscam and \
				config.plugins.baseplugin.camdir.value != "/usr/bin/cam":
				self.iscam = True
				config.plugins.baseplugin.camdir.value = "/usr/bin/cam"
				self.StartCreateCamlist()
			elif config.plugins.baseplugin.camdir.value != "/usr/CamEmu":
				self.iscam = False
				config.plugins.baseplugin.camdir.value = "/usr/CamEmu"
				self.StartCreateCamlist()
			else:
				self.iscam = False

	def CamActive(self, result, retval, extra_args):
		if result.strip():
			self.CreateCamList()
		else:
			for line in self.softcamlist.splitlines():
				if  line != self.actcam:
					self.Console.ePopen("pidof %s" % line, self.CamActiveFromList, line)
			self.Console.ePopen("echo 1", self.CamActiveFromList, "none")

	def CamActiveFromList(self, result, retval, extra_args):
		if result.strip():
			self.actcam = extra_args
			self.CreateCamList()

	def CreateCamList(self):
		self.list = []
		try:
			test = self.actcam
		except:
			self.actcam = "none"
		if self.actcam != "none":
			softpng = LoadPixmap(cached=True,
				path=resolveFilename(SCOPE_PLUGINS,
				"Extensions/" + plugin + "/images/actcam.png"))
			#self.list.append(( self.actcam.replace("camemu.", ""), softpng, self.checkcam(self.actcam)))
			self.list.append(( self.actcam.replace("camemu.", ""), softpng, ""))
		softpng = LoadPixmap(cached=True,
			path=resolveFilename(SCOPE_PLUGINS,
			"Extensions/" + plugin + "/images/defcam.png"))
#		for line in self.softcamlist.splitlines():
                for line in os.listdir(config.plugins.baseplugin.camdir.value):
			if ( line != self.actcam and line != "camemu.None" and line[:7] == 'camemu.' and line[-1:] != '~'):
				#self.list.append((line.replace("camemu.", ""), softpng, self.checkcam(line)))
				self.list.append((line.replace("camemu.", ""), softpng, ""))
		self["list"].setList(self.list)

	def checkcam (self, cam):
		cam = cam.lower()
		if getcamscript(cam):
			return "Script"
		elif "oscam" in cam:
			return "Oscam"
		elif "mgcamd" in cam:
			return "Mgcamd"
		elif "wicard" in cam:
			return "Wicard"
		elif "camd3" in cam:
			return "Camd3"
		elif "mcas" in cam:
			return "Mcas"
		elif "cccam" in cam:
			return "CCcam"
		elif "gbox" in cam:
			return "Gbox"
		elif "ufs910camd" in cam:
			return "Ufs910"
		elif "incubuscamd" in cam:
			return "Incubus"
		elif "mpcs" in cam:
			return "Mpcs"
		elif "mbox" in cam:
			return "Mbox"
		elif "newcs" in cam:
			return "Newcs"
		elif "vizcam" in cam:
			return "Vizcam"
		elif "sh4cam" in cam:
			return "Sh4CAM"
		elif "rucam" in cam:
			return "Rucam"
		else:
			return cam[0:6]

	def start(self):
		if self.iscam:
			self.camstart = "camemu." + self["list"].getCurrent()[0]
			if self.camstart != self.actcam:
			        # Stop Cam
			        self.stop()
			        # Start Cam
				print plugin_def, _(" Start SoftCam")
				self.camstartcmd = getcamcmd(self.camstart)
				msg = _("Starting %s") % self.camstart
				print msg
				self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO,timeout = 4)
				self.activityTimer = eTimer()
				self.activityTimer.timeout.get().append(self.Starting)
				self.activityTimer.start(1000, False)

	def stop(self):
		if self.iscam and self.actcam != "none":
			stopcam(self.actcam)
			msg  = _("Stopping %s") % self.actcam
			self.actcam = "none"
			self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO,timeout = 4)
			self.activityTimer = eTimer()
			self.activityTimer.timeout.get().append(self.closestop)
			self.activityTimer.start(1000, False)

	def closestop(self):
		self.activityTimer.stop()
		self.mbox.close()
		self.CreateInfo()

	def extra(self):
		self.session.open(LBExtra.installextra)

	def Starting(self):
		self.activityTimer.stop()
		#stopcam(self.actcam)
                config.plugins.baseplugin.actcam.value = self.camstart
                config.plugins.baseplugin.save()
                self.actcam = config.plugins.baseplugin.actcam.value
                cmd = getcamcmd(config.plugins.baseplugin.actcam.value)
                #Console().ePopen(cmd)
                #print plugin_def, "Runing..  ", cmd 

		#self.actcam = self.camstart
		service = self.session.nav.getCurrentlyPlayingServiceReference()
		if service:
			self.session.nav.stopService()
		self.Console.ePopen(self.camstartcmd)
		print plugin_def, " ", self.camstartcmd
		if self.mbox:
			self.mbox.close()
		if service:
			self.session.nav.playService(service)
		self.CreateInfo()

	def ok(self):
		if self.iscam:
			#if "camemu." + self["list"].getCurrent()[0] != self.actcam:
                        self.start()
			#else:
			#	self.restart()

	def cancel(self):
		if config.plugins.baseplugin.actcam.value != self.actcam:
			config.plugins.baseplugin.actcam.value = self.actcam
		config.plugins.baseplugin.save()
		self.close()

	def StartCamInstall(self):
		self.session.open(LBCamEmu.installCam)
		self.StartCreateCamlist()
		
class ConfigEdit(Screen, ConfigListScreen):
	skin = """
<screen name="ConfigEdit" position="center,center" size="500,200" \
	title="SoftCam path configuration">
	<eLabel position="5,0" size="490,2" backgroundColor="#aaaaaa" />
<widget name="config" position="30,20" size="460,50" zPosition="1" \
	scrollbarMode="showOnDemand" />
	<eLabel position="85,180" size="166,2" backgroundColor="#00ff2525" />
	<eLabel position="255,180" size="166,2" backgroundColor="#00389416" />
	<widget name="key_red" position="85,150" zPosition="2" size="170,30" \
		valign="center" halign="center" font="Regular;22" transparent="1" />
	<widget name="key_green" position="255,150" zPosition="2" size="170,30" \
		valign="center" halign="center" font="Regular;22" transparent="1" />
</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Ok"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.close,
				"ok": self.ok,
				"green": self.ok,
				"red": self.close,
			}, -2)
		ConfigListScreen.__init__(self, [], session)
		self.camconfigold = config.plugins.baseplugin.camconfig.value
		self.camdirold = config.plugins.baseplugin.camdir.value
		self.list = []
		self.list.append(getConfigListEntry(_("SoftCam config directory"),
			config.plugins.baseplugin.camconfig))
		self.list.append(getConfigListEntry(_("SoftCam directory"),
			config.plugins.baseplugin.camdir))
		self["config"].list = self.list

	def ok(self):
		if self.camconfigold != config.plugins.baseplugin.camconfig.value \
			or self.camdirold != config.plugins.baseplugin.camdir.value:
			self.session.openWithCallback(self.updateConfig, MessageBox,
				(_("Are you sure you want to save this configuration?\n\n")))
		elif not path.exists(self.camconfigold) or not path.exists(self.camdirold):
			self.updateConfig(True)
		else:
			self.close()

	def updateConfig(self, ret = False):
		if ret == True:
			msg = [ ]
			if not path.exists(config.plugins.baseplugin.camconfig.value):
				msg.append("%s " % config.plugins.baseplugin.camconfig.value)
			if not path.exists(config.plugins.baseplugin.camdir.value):
				msg.append("%s " % config.plugins.baseplugin.camdir.value)
			if msg == [ ]:
				if config.plugins.baseplugin.camconfig.value[-1] == "/":
					config.plugins.baseplugin.camconfig.value = \
						config.plugins.baseplugin.camconfig.value[:-1]
				if config.plugins.baseplugin.camdir.value[-1] == "/":
					config.plugins.baseplugin.camdir.value = \
						config.plugins.baseplugin.camdir.value[:-1]
				self.close()
			else:
				self.mbox = self.session.open(MessageBox,
					_("Directory %s does not exist!\nPlease set the correct directorypath!")
					% msg, MessageBox.TYPE_INFO, timeout = 5 )

def main(session, **kwargs):
	session.open(LBCamManager)

def StartCam(reason, **kwargs):
	if config.plugins.baseplugin.actcam.value != "none":
		if reason == 0: # Enigma start
			sleep(2)
			try:
				cmd = getcamcmd(config.plugins.baseplugin.actcam.value)
				Console().ePopen(cmd)
				print plugin_def, " ", cmd
			except:
				pass
		elif reason == 1: # Enigma stop
			try:
				stopcam(config.plugins.baseplugin.actcam.value)
			except:
				pass

def Plugins(**kwargs):
	return [
	PluginDescriptor(name = plugin,
		description = _("Base plugin emu panel"),
		where = [ PluginDescriptor.WHERE_PLUGINMENU,
		PluginDescriptor.WHERE_EXTENSIONSMENU ],
		icon = "images/softcam.png", fnc = main),
	PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART,
		needsRestart = True, fnc = StartCam)]
  