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

from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from xml.dom import Node
from xml.dom import minidom
import os
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from enigma import *
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from twisted.web.client import downloadPage
from twisted.web.client import getPage
import urllib
from Components.Label import Label
from Components.Language import language
from os import environ
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from inspect import getsourcefile
from os.path import abspath
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
                                         

class installextra(Screen):

    skin = """
    <screen name="installCam" position="center,160" size="1150,500" title="plugin_title">
    <ePixmap position="715,10" zPosition="1" size="440,480" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/plugin_name/images/fondo10.png" alphatest="blend" transparent="1" />
    <ePixmap name="red" position="20,488" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/plugin_name/images/red.png" transparent="1" alphatest="on" />
    <widget name="key_red" position="20,458" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
    <widget name="list" position="50,10" size="540,350" scrollbarMode="showOnDemand" />
    <eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />
    <widget name="info" position="150,50" zPosition="4" size="300,300" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />
    <widget name="fspace" position="0,320" zPosition="4" size="600,80" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />
    </screen>"""
    skin = skin.replace("plugin_title", plugin_def + _("-Extra Downloads"))
    skin = skin.replace("plugin_name", plugin)

    def __init__(self, session):
        self.skin = installextra.skin
        Screen.__init__(self, session)
        self['key_red'] = Button(_('Exit'))
        self.list = []
        self['list'] = MenuList([])
        self['info'] = Label()
        self['fspace'] = Label()
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['info'].setText(_("Downloading plugins groups, please wait"))
        self.timer = eTimer()
        self.timer.callback.append(self.downloadxmlpage)
        self.timer.start(100, 1)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'cancel': self.close,
         'red': self.close}, -2)

    def updateable(self):
        try:
            selection = str(self.names[0])
            lwords = selection.split('_')
            lv = lwords[1]
            self.lastversion = lv
            if float(lv) == float(plugin_config.curr_version):
                return False
            if float(lv) > float(plugin_config.curr_version):
                return True
            return False
        except:
            return False

    def downloadxmlpage(self):
        url = plugin_config.url_xml_repo 
        getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print str(error)
        self['info'].setText(_("Error on download of plugings groups!"))
        self.downloading = False

    def _gotPageLoad(self, data):
        self.xml = data
        try:
            if self.xml:
                xmlstr = minidom.parseString(self.xml)
                self.data = []
                self.names = []
                icount = 0
                list = []
                xmlparse = xmlstr
                self.xmlparse = xmlstr
                for plugins in xmlstr.getElementsByTagName('plugins'):
                    self.names.append(plugins.getAttribute('cont').encode('utf8'))

                self.list = list
                self['info'].setText('')
                self['list'].setList(self.names)
                self.downloading = True
            else:
                self.downloading = False
                self['info'].setText(_("Error on Download on plugin list!"))
                return
        except:
            self.downloading = False
            self['info'].setText(_("Server data error"))

    def okClicked(self):
        if self.downloading == True:
            try:
                self.downloading = True
                selection = str(self['list'].getCurrent())
                self.session.open(SelectIpk, self.xmlparse, selection)
            except:
                return


class SelectIpk(Screen):

    skin = """
    <screen name="installCam" position="center,160" size="1150,500" title="plugin_title">
    <ePixmap position="715,10" zPosition="1" size="440,480" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/plugin_name/images/fondo10.png" alphatest="blend" transparent="1" />
    <ePixmap name="red" position="20,488" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/plugin_name/images/red.png" transparent="1" alphatest="on" />
    <widget name="key_red" position="20,458" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
    <widget name="list" position="50,10" size="540,350" scrollbarMode="showOnDemand" />
    <eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />
    <widget name="info" position="150,50" zPosition="4" size="300,300" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />
    <widget name="fspace" position="0,320" zPosition="4" size="600,80" font="Regular;24" foregroundColor="#ffffff" transparent="1" halign="left" valign="center" />
    <widget name="countrymenu" position="10,0" zPosition="1" size="590,373" scrollbarMode="showOnDemand" />
    </screen>
    """
    skin = skin.replace("plugin_title", plugin_def + _("-Extra Downloads"))
    skin = skin.replace("plugin_name", plugin )
    
    def __init__(self, session, xmlparse, selection):
        self.skin = SelectIpk.skin
        Screen.__init__(self, session)
        self['key_red'] = Button(_('Exit'))
        self.list = []
        self['list'] = MenuList([])
        self['info'] = Label()
        self['fspace'] = Label()
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['info'].setText(_("Downloading plugin list, please wait"))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.selClicked,
         'cancel': self.close,
         'red': self.close}, -2)

        self.xmlparse = xmlparse
        self.selection = selection
        list = []
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    list.append(plugin.getAttribute('name').encode('utf8'))
                continue

        list.sort()
        self['info'].setText('')
        self['countrymenu'] = MenuList(list)
    
    def selClicked(self):
        try:
            selection_country = self['countrymenu'].getCurrent()
        except:
            return
            
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombt(urlserver, pluginname)
                        continue
                    else:
                        continue

                continue
        return

    def prombt(self, com, dom):
        self.com = com
        self.dom = dom
        if self.selection == 'Skins':
            self.session.openWithCallback(self.callMyMsg, MessageBox, _('Mising compatible skin!'), MessageBox.TYPE_YESNO)
            
        else:
            self.session.open(Console, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com])
        self.close()

    def callMyMsg(self, result):
        if result:
            dom = self.dom
            com = self.com
            self.session.open(Console, _('downloading-installing: %s') % dom, ['ipkg install -force-overwrite %s' % com])
