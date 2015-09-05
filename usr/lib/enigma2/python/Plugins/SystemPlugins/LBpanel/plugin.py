# LBPanel -- Linux-Box Panel.
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
# Author: lucifer
#         iqas
#
# Internet: www.linux-box.es
# Based on original source by epanel for openpli

from enigma import eTimer
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.List import List
from Tools.Directories import crawlDirectory, resolveFilename, SCOPE_CURRENT_SKIN
from Components.Button import Button
from Components.config import config, ConfigElement, ConfigSubsection, ConfigSelection, ConfigSubList, getConfigListEntry, KEY_LEFT, KEY_RIGHT, KEY_OK
#import ExtraActionBox
#import sys
from Screens.Screen import Screen
from Screens.PluginBrowser import PluginBrowser
from Components.PluginComponent import plugins
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
#from Screens.Console import Console
from Components.Label import Label
#
from Components.MenuList import MenuList
from Plugins.Plugin import PluginDescriptor
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Components.config import config, getConfigListEntry, ConfigText, ConfigPassword, ConfigClock, ConfigSelection, ConfigSubsection, ConfigYesNo, configfile, NoSave
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists
#from Components.Harddisk import harddiskmanager
#from Components.NimManager import nimmanager
#from Components.About import about
from os import environ
from OpenSSL import SSL
from enigma import ePicLoad
from enigma import eDVBDB
import os
import gettext
import LBCamEmu
#import LBipk
import LBtools
import LBDaemonsList
from enigma import eEPGCache
#from types import *
#from enigma import *
import sys, traceback
import re
import time
import new
import _enigma
#import enigma
import smtplib
#import commands
import threading
import urllib2
import Screens.Standby
import subprocess, threading
import uuid

global min
min = 0
global cronvar
cronvar = 55

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("lbpanel")
gettext.bindtextdomain("lbpanel", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "SystemPlugins/LBpanel/locale/"))

def _(txt):
	t = gettext.dgettext("lbpanel", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

##################################################################
config.plugins.lbpanel.showmain = ConfigYesNo(default = True)
config.plugins.lbpanel.showepanelmenu = ConfigYesNo(default = True)
config.plugins.lbpanel.showextsoft = ConfigYesNo(default = True)
config.plugins.lbpanel.shownclsw = ConfigYesNo(default = False)
config.plugins.lbpanel.showwcsw = ConfigYesNo(default = False)
config.plugins.lbpanel.showclviewer = ConfigYesNo(default = False)
config.plugins.lbpanel.showscriptex = ConfigYesNo(default = False)
config.plugins.lbpanel.showusbunmt = ConfigYesNo(default = False)
config.plugins.lbpanel.showsetupipk = ConfigYesNo(default = False)
config.plugins.lbpanel.showpbmain = ConfigYesNo(default = False)
config.plugins.lbpanel.filtername = ConfigYesNo(default = False)
config.plugins.lbpanel.update = ConfigYesNo(default = True)
config.plugins.lbpanel.updatesettings = ConfigYesNo(default = True)
config.plugins.lbpanel.lbemail = ConfigYesNo(default = False)
config.plugins.lbpanel.lbiemail = ConfigYesNo(default = False)
config.plugins.lbpanel.lbemailto = ConfigText(default = "mail@gmail.com",fixed_size = False, visible_width=30)
config.plugins.lbpanel.smtpserver = ConfigText(default = "smtp.gmail.com:587",fixed_size = False, visible_width=30)
config.plugins.lbpanel.smtpuser = ConfigText(default = "I@gmail.com",fixed_size = False, visible_width=30)
config.plugins.lbpanel.smtppass = ConfigPassword(default = "mailpass",fixed_size = False, visible_width=15)
config.plugins.lbpanel.lbemailproto =ConfigSelection(default = "tls", choices = [
                ("tls", "tls"),
		("ssl", "ssl"),
		])                                                                
config.plugins.lbpanel.testcam = ConfigYesNo(default = False)
config.plugins.lbpanel.activeemu = ConfigText(default = "No EMU Selecionada")
config.plugins.lbpanel.runeveryhour = ConfigYesNo(default = False)
##################################################################

# Check if feed is active
if not os.path.isfile("/etc/opkg/lbappstore.conf"):
	with open ('/etc/opkg/lbappstore.conf', 'a') as f: f.write ("src/gz lbutils http://appstore.linux-box.es/ficheros" + '\n')
	f.close()

if os.path.isfile("/etc/opkg/extralbappstore.conf"):
        with open ('/etc/opkg/extralbappstore.conf', 'w') as f: f.write ("src/gz extralbutils http://appstore.linux-box.es/ficheros/Emus" + '\n')
        f.close()
        
os.system("sh /usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/script/lbutils.sh init")
# Generic function to send email
def sendemail(from_addr, to_addr, cc_addr,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):

    print "ENVIANDO EMAIL"
    try:
    	proto = config.plugins.lbpanel.lbemailproto.value
    	if config.plugins.lbpanel.lbemail.value == True: 
    		header  = 'From: %s\n' % from_addr
    		header += 'To: %s\n' % to_addr
    		header += 'Cc: %s\n' % cc_addr
    		header += 'Subject: %s\n\n' % subject
    		message = header + message

    		server = smtplib.SMTP(smtpserver)
    		server.ehlo()
    		server.starttls()
    		server.login(login,password)
    		problems = server.sendmail(from_addr, to_addr, message)
    		server.quit()
	if config.plugins.lbpanel.lbiemail.value == True:
		f = { 'from' : from_addr, 'to' : to_addr, 'cc' : '', 'subject' : subject, 'message' : message, 'server' : smtpserver, 'proto' : proto, 'user' : login, 'password' : password}
		url = 'https://appstore.linux-box.es/semail.php?%s' % (urllib.urlencode(f))	
		os.system("wget --no-check-certificate '%s' -O  /tmp/.ilbmail.log" % (url))
    except:
        fo = open("/tmp/.lbemail.error","a+")
        fo.close()
        config.plugins.lbpanel.lbemail.value = False
    	config.plugins.lbpanel.lbemail.save()
    	
def lbversion():
	return ("LBpanel_1.0")

def Test_camemu():

	found = False
	for x in os.listdir('/etc/opkg/'):
				
		if 'extralbappstore.' in x:
			found = True
			break; 													
	return found
																	
def command(comandline, strip=1):
        comandline = comandline + " >/tmp/command.txt"
        os.system(comandline)
        text = ""
        if os.path.exists("/tmp/command.txt") is True:
                file = open("/tmp/command.txt", "r")
                if strip == 1:
                        for line in file:
                                text = text + line.strip() + '\n'
                else:
                        for line in file:
                                text = text + line
                                if text[-1:] != '\n': text = text + "\n"
                file.close()   
        if text[-1:] == '\n': text = text[:-1]
        comandline = text
        os.system("rm /tmp/command.txt")
        return comandline

def search_process(process):
	pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
	for pid in pids:
	    try:
	          name = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
	          if name.find(process) >= 0:
	            return 1
	    except IOError:
		  continue
	return -1
	                                  																	
def opkg_list(filter=""):
 search=0
 list=""

 files = [f for f in os.listdir('/var/lib/opkg/') if os.path.isfile(os.path.join('/var/lib/opkg/', f)) and f != 'status']

 try:
   for file in files:
      fh = open(os.path.join('/var/lib/opkg/', file), "r")
      for line in fh:
            if line[:8] == 'Package:':
                  package = line.split(" ")[1].strip()
                  if (not "-dev"in package) and (not "-dbg" in package):
                        if filter == "":
                              search=1
                        elif filter in package:
                              search=1
            if line[:8] == 'Descript' and search==1:  
                  package = package + " - " + line.split(": ")[1].strip() + "\n"
                  list = list + package
                  search=0
            
      fh.close()
   if list[-1:] == '\n': list = list[:-1]
   return list
 except:
   print "Error loading files"

def ecommand(command=""):
	name=str(uuid.uuid4())
	name=name.replace("-","")
	file = open(("/tmp/.runop%s" % name), "w")
	file.write(command)
	file.write('\n')
	file.close()
	
	output="/tmp/.runop%s.end" % name
	
	cont=0
	while not os.path.exists(output):
		cont+=1
		time.sleep(1)
		if cont > 30:
			if os.path.exists("/tmp/.runop%s" % name) is True:
				os.remove("/tmp/.runop%s" % name)
			return -1		
			break
	os.remove(output)
	return 0

ecommand("nohup /usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/script/lbutils.sh update &")
class LBPanel2(Screen):
	skin = """
<screen name="LBPanel2" position="0,0" size="1280,720">
  <widget source="lb_version" render="Label" position="50,605" zPosition="2" size="450,30" font="Regular;15" halign="center" valign="center" backgroundColor="#d3d3d3" foregroundColor="#000000" transparent="1" />
<widget source="menu" render="Listboxlb" position="591,191" scrollbarMode="showNever" foregroundColor="white" foregroundColorSelected="#ffffff" backgroundColor="#6e6e6e" backgroundColorSelected="#fd6502" transparent="1" size="629,350">
      <convert type="TemplatedMultiContent">
    {"template": [ MultiContentEntryText(pos = (30, 5), size = (460, 50), flags = RT_HALIGN_LEFT, text = 0) ],
    "fonts": [gFont("Regular", 30)],
    "itemHeight": 60
    }
   </convert>
    </widget>
    <widget source="key_menu" render="Label" position="892,650" size="320,32" zPosition="5" font="Regular;20" valign="center" halign="center" backgroundColor="white" foregroundColor="black" transparent="0" />
<!-- colores keys -->
    <!-- rojo -->
    <widget source="key_red" render="Label" position="621,569" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="591,569" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#ee1d11" zPosition="-1" />
    <!-- amarillo -->
    <widget source="key_yellow" render="Label" position="621,604" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="591,604" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#eefb1a" zPosition="-1" />
    <!-- verde -->
    <widget source="key_blue" render="Label" position="912,604" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="882,569" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#11b90a" zPosition="-1" />
    <!-- azul -->
    <widget source="key_green" render="Label" position="912,569" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="882,604" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#1a2cfb" zPosition="-1" />
   <widget source="key_cancel" render="Label" position="335,644" size="500,50" font="Regular; 30" zPosition="2" halign="left" noWrap="1" transparent="1" foregroundColor="white" backgroundColor="#8f8f8f" />
 <!-- fin colores keys -->
    <eLabel text="LBpanel - Red Bee" position="440,34" size="430,65" font="Regular; 42" halign="center" transparent="1" foregroundColor="white" backgroundColor="#140b1" />
    
    <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="80,119" size="600,50" font="Regular; 30" backgroundColor="black" foregroundColor="white" noWrap="1" />
    <widget source="global.CurrentTime" render="Label" position="949,28" size="251,55" backgroundColor="#140b1" foregroundColor="white" transparent="1" zPosition="2" font="Regular;24" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2">
      <convert type="ClockToText">Format:%-H:%M</convert>
    </widget>
    <widget source="global.CurrentTime" render="Label" position="900,50" size="300,55" backgroundColor="#140b1" foregroundColor="white" transparent="1" zPosition="2" font="Regular;16" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2">
      <convert type="ClockToText">Date</convert>
    </widget>
    <widget source="session.VideoPicture" render="Pig" position="64,196" size="375,175" backgroundColor="transparent" zPosition="-1" transparent="0" />
    <widget source="session.CurrentService" render="RunningText" options="movetype=running,startpoint=0,direction=left,steptime=25,repeat=150,startdelay=1500,always=0" position="101,491" size="215,45" font="Regular; 22" transparent="1" valign="center" zPosition="2" backgroundColor="black" foregroundColor="white" noWrap="1" halign="center">
      <convert type="ServiceName">Name</convert>
    </widget>
    <widget source="session.CurrentService" render="Label" zPosition="3" font="Regular; 22" position="66,649" size="215,50" halign="center" backgroundColor="black" transparent="1" noWrap="1" foregroundColor="white">
      <convert type="VtiInfo">TempInfo</convert>
    </widget>
    <eLabel position="192,459" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#ee1d11" zPosition="-1" />
    <eLabel position="251,410" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#1a2cfb" zPosition="-2" />
    <eLabel position="281,449" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#11b90a" zPosition="-6" />
    <eLabel position="233,499" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#eefb1a" zPosition="-5" />
    <eLabel position="60,451" size="65,57" transparent="0" foregroundColor="white" backgroundColor="#ecbc13" zPosition="-6" />
    <eLabel position="96,489" size="229,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="0,0" size="1280,720" transparent="0" zPosition="-15" backgroundColor="#d6d6d6" />
    <ePixmap position="46,180" zPosition="0" size="413,210" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/images/marcotv.png" transparent="0" />
    <eLabel position="60,30" size="1160,68" transparent="0" foregroundColor="white" backgroundColor="#42b3" zPosition="-10" />
    <eLabel position="60,120" size="1160,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="60,640" size="229,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="320,640" size="901,50" transparent="0" foregroundColor="white" backgroundColor="#929292" />
    <eLabel position="591,191" size="629,370" transparent="0" foregroundColor="white" backgroundColor="#6e6e6e" zPosition="-10" />
  </screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("LBpanel"))
		self["key_cancel"] = StaticText(_("PRESS EXIT TO QUIT"))
		self["key_red"] = StaticText(_("Close"))
		if Test_camemu():
			self["key_green"] = StaticText(_("CamEmu"))
		else:
			self["key_green"] = StaticText(chr(9))
		self["key_yellow"] = StaticText(_("Services"))
		self["key_blue"] = StaticText(_("Teambox downloads"))
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions", "CCcamInfoActions", "EPGSelectActions"],
		{
			"ok": self.keyOK,
			"cancel": self.exit,
			"back": self.exit,
			"red": self.exit,
			"green": self.keyGreen,
			"yellow": self.keyYellow,
			"blue": self.keyBlue,
			
		})
		self["lb_version"] = StaticText(_("Version: %s") % lbversion())
		self.list = []
		self["menu"] = List(self.list)
		self.mList()

	def mList(self):
		self.list = []
		zeropng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/softcams.png"))
		onepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/softcams.png"))
		sixpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/cardserver.png"))
		twopng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/tools.png"))
		backuppng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/backup.png"))
		trespng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/seleck.png"))
		treepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/install.png"))
		fourpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/epp2.png"))
		sixpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/system.png"))
		sevenpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/addon.png"))
		cuatropng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/daemons.png"))
		cincopng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/infop.png"))
		settings = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/settings.png"))
		if Test_camemu():
			self.list.append((_("SoftEmus"),"com_one", _("CamEmu start-stop, Test Emu Control, Info Emus"), onepng))
		self.list.append((_("Services "),"com_two", _("Epg,Ntp,scripts,info ..."), twopng ))
		self.list.append((_("System"),"com_six", _("Kernel modules,swap,ftp,samba,crond,usb"), sixpng ))
		self.list.append((_("Teambox downloads"),"com_four", _("Download Teambox Packages"), treepng))
		self.list.append((_("Settings"),"com_settings", _("Settings of LBpanel"), settings))
		self.list.append((_("Add-ons"),"com_seven", _("Plugins"), sevenpng))
		self["menu"].setList(self.list)


	def exit(self):
		self.close()

	def keyOK(self, returnValue = None):
		if returnValue == None:
			returnValue = self["menu"].getCurrent()[1]
			if returnValue is "com_zero":
				self.session.open(LBAbout.About)
			if returnValue is "com_one":
				self.session.open(LBCamEmu.CamEmuPanel)
			elif returnValue is "com_two":
				self.session.open(LBtools.ToolsScreen)
			elif returnValue is "com_tree":
				self.session.open(backup.BackupSuite)
			elif returnValue is "com_four":
				self.session.open(descargasScreen)
			elif returnValue is "com_five":
				self.session.open(ConfigExtentions)
			elif returnValue is "com_six":
				self.session.open(LBtools.SystemScreen)
			elif returnValue is "com_seven":
				self.session.open(PluginBrowser)
			elif returnValue is "com_settings":
				self.session.open(LBsettings)
			else:
				print "\n[LBpanel] cancel\n"
				self.close(None)

				
	def keyYellow (self):
		self.session.open(LBtools.ToolsScreen)

	def keyMenu (self):
		self.session.open(descargasScreen)
		
	def keyGreen (self):
		if Test_camemu():
			self.session.open(LBCamEmu.emuSel2)
		else:
			print "Installing extraappstore"
                        resp=ecommand("/usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/script/lbutils.sh appstore")
			                                                                                                                                                                                                                                                                                                                                	
	def keyBlue (self):		
		self.session.open(descargasScreen)
	
	def infoKey (self):
		self.session.openWithCallback(self.mList,info)
		
##########################################################################################
class descargasScreen(Screen):
	skin = """
	<screen name="descargasScreen" position="0,0" size="1280,720" title="LBpanel Download">
		<widget source="menu" render="Listboxlb" position="591,191" scrollbarMode="showNever" foregroundColor="white" foregroundColorSelected="#ffffff" backgroundColor="#6e6e6e" backgroundColorSelected="#fd6502" transparent="1" size="629,350">
      <convert type="TemplatedMultiContent">
    {"template": [ MultiContentEntryText(pos = (30, 5), size = (460, 50), flags = RT_HALIGN_LEFT, text = 0) ],
    "fonts": [gFont("Regular", 30)],
    "itemHeight": 60
    }
   </convert>
    </widget>
  <!-- colores keys -->
    <!-- rojo -->
    <widget source="key_red" render="Label" position="621,569" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="591,569" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#ee1d11" zPosition="-1" />
    <!-- amarillo -->
    <widget source="key_yellow" render="Label" position="621,604" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="591,604" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#eefb1a" zPosition="-1" />
    <!-- verde -->
    <eLabel render="Label" position="912,604" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="882,569" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#11b90a" zPosition="-1" />
    <!-- azul -->
    <widget source="key_green" render="Label" position="912,569" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="882,604" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#1a2cfb" zPosition="-1" />
   <widget source="key_cancel" render="Label" position="335,644" size="500,50" font="Regular; 30" zPosition="2" halign="left" noWrap="1" transparent="1" foregroundColor="white" backgroundColor="#8f8f8f" />
 <!-- fin colores keys -->
    <eLabel text="LBpanel - Red Bee" position="440,34" size="430,65" font="Regular; 42" halign="center" transparent="1" foregroundColor="white" backgroundColor="#140b1" />
    
    <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="80,119" size="600,50" font="Regular; 30" backgroundColor="black" foregroundColor="white" noWrap="1" />
    <widget source="global.CurrentTime" render="Label" position="949,28" size="251,55" backgroundColor="#140b1" foregroundColor="white" transparent="1" zPosition="2" font="Regular;24" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2">
      <convert type="ClockToText">Format:%-H:%M</convert>
    </widget>
    <widget source="global.CurrentTime" render="Label" position="900,50" size="300,55" backgroundColor="#140b1" foregroundColor="white" transparent="1" zPosition="2" font="Regular;16" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2">
      <convert type="ClockToText">Date</convert>
    </widget>
    <widget source="session.VideoPicture" render="Pig" position="64,196" size="375,175" backgroundColor="transparent" zPosition="-1" transparent="0" />
    <widget source="session.CurrentService" render="RunningText" options="movetype=running,startpoint=0,direction=left,steptime=25,repeat=150,startdelay=1500,always=0" position="101,491" size="215,45" font="Regular; 22" transparent="1" valign="center" zPosition="2" backgroundColor="black" foregroundColor="white" noWrap="1" halign="center">
      <convert type="ServiceName">Name</convert>
    </widget>
    <widget source="session.CurrentService" render="Label" zPosition="3" font="Regular; 22" position="66,649" size="215,50" halign="center" backgroundColor="black" transparent="1" noWrap="1" foregroundColor="white">
      <convert type="VtiInfo">TempInfo</convert>
    </widget>
    <eLabel position="192,459" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#ee1d11" zPosition="-1" />
    <eLabel position="251,410" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#1a2cfb" zPosition="-2" />
    <eLabel position="281,449" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#11b90a" zPosition="-6" />
    <eLabel position="233,499" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#eefb1a" zPosition="-5" />
    <eLabel position="60,451" size="65,57" transparent="0" foregroundColor="white" backgroundColor="#ecbc13" zPosition="-6" />
    <eLabel position="96,489" size="229,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="0,0" size="1280,720" transparent="0" zPosition="-15" backgroundColor="#d6d6d6" />
    <ePixmap position="46,180" zPosition="0" size="413,210" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/images/marcotv.png" transparent="0" />
    <eLabel position="60,30" size="1160,68" transparent="0" foregroundColor="white" backgroundColor="#42b3" zPosition="-10" />
    <eLabel position="60,120" size="1160,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="60,640" size="229,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="320,640" size="901,50" transparent="0" foregroundColor="white" backgroundColor="#929292" />
    <eLabel position="591,191" size="629,370" transparent="0" foregroundColor="white" backgroundColor="#6e6e6e" zPosition="-10" />
   </screen>"""
	 
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("Download Bee"))
		self["key_cancel"] = StaticText(_("PRESS EXIT TO QUIT"))
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Restart GUI"))
		self["key_yellow"] = StaticText(_("Delete"))
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions"],

		{
			"ok": self.OK,
			"cancel": self.exit,
			"back": self.exit,
			"red": self.exit,
			"yellow": self.clear,
			"green": self.restartGUI,
		})
		self.list = []
		self["menu"] = List(self.list)
		self.mList()

	def mList(self):
		self.list = []
		dospng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/ipk.png"))
		cuatropng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/ipk.png"))
		cincopng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/ipk.png"))
		seispng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/ipk.png"))
		sietepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/ipk.png"))
		ochopng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/ipk.png"))
		self.list.append((_("Sorys Channel List"),"dos", _("Download Sorys Channel List"), dospng ))
		self.list.append((_("Download Picon"),"cinco", _("Download Picon"), cincopng ))
		self.list.append((_("Download skinparts"),"seis", _("Download skinparts"), seispng ))
		self.list.append((_("Download default skinparts"),"nueve", _("Download default skinparts"), seispng ))
		self.list.append((_("Download spinner"),"siete", _("Download spinner"), sietepng ))
		self.list.append((_("Download bootlogo"),"ocho", _("Download bootlogo"), ochopng ))
		self.list.append((_("Download bootvideo"),"bootvideo", _("Download bootvideo"), ochopng ))
		self["menu"].setList(self.list)
		
	def exit(self):
		self.close()
		
	def clear(self):
		self.session.open(installremove)
		
	def restartGUI(self):
		self.session.open(TryQuitMainloop, 3)

	def OK(self):
		item = self["menu"].getCurrent()[1]
		if item is "dos":
			self.session.open(installsoftware, "soryslist")
		elif item is "cuatro":
			self.session.open(installsoftware, "configemus")
		elif item is "cinco":
			self.session.open(installsoftware, "picon")
		elif item is "seis":
			self.session.open(installsoftware, "skinparts")
		elif item is "nueve":
			self.session.open(installsoftware, "defaultskinparts")
		elif item is "siete":
			self.session.open(installsoftware, "spinner")
		elif item is "ocho":
			self.session.open(installsoftware, "bootlogo")
		elif item is "bootvideo":
			self.session.open(installsoftware, "bootvideo")		

			
###############################################
class Preview(Pixmap):
	def __init__(self):
		Pixmap.__init__(self)
                self.picload = ePicLoad()
		self.picload.PictureData.get().append(self.paintIconPixmapCB)
                              
	def onShow(self):
		Pixmap.onShow(self)
		self.picload.setPara((self.instance.size().width(), self.instance.size().height(), 1, 1, False, 1, "#00000000"))
                                                    
	def paintIconPixmapCB(self, picInfo=None):
		ptr = self.picload.getData()
		if ptr != None:
			self.instance.setPixmap(ptr.__deref__())
                                                                                      
	def updateIcon(self, filename):
		self.picload.startDecode(filename)
                                                                                                                                                            
class installsoftware(Screen):
	skin = """
<screen name="installsoftware" position="0,0" size="1280,720" title="LBpanel-Download spinner">
    <widget source="menu" render="Listboxlb" position="591,191" size="629,350" scrollbarMode="showNever" foregroundColor="#ffffff" foregroundColorSelected="#ffffff" backgroundColor="#6e6e6e" backgroundColorSelected="#fd6502" transparent="1">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryText(pos = (70, 2), size = (630, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
			MultiContentEntryText(pos = (80, 29), size = (630, 18), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
			MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (50, 40), png = 2), # index 4 is the pixmap
				],
	"fonts": [gFont("Regular", 19),gFont("Regular", 16)],
	"itemHeight": 50
	}
	</convert>
	</widget>
	<ePixmap position="46,180" zPosition="0" size="413,210" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/images/marcotv.png" transparent="0" />
    <widget source="session.VideoPicture" render="Pig" position="64,196" size="375,175" backgroundColor="transparent" zPosition="-1" transparent="0" />
  <eLabel name="" position="60,390" zPosition="2" size="517,244" backgroundColor="black" />
<eLabel name="" position="514,410" zPosition="-11" size="90,20" backgroundColor="#6e6e6e" />
<eLabel name="" position="83,374" zPosition="1" size="20,30" backgroundColor="black" />
<!-- colores keys -->
    <!-- rojo -->
    <widget source="key_red" render="Label" position="621,569" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="591,569" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#ee1d11" zPosition="-1" />
    <!-- amarillo -->
    <eLabel render="Label" position="621,604" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="591,604" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#eefb1a" zPosition="-1" />
    <!-- verde -->
    <eLabel render="Label" position="912,604" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="882,569" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#11b90a" zPosition="-1" />
    <!-- azul -->
    <widget source="key_green" render="Label" position="912,569" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="882,604" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#1a2cfb" zPosition="-1" />
    <!-- fin colores keys -->
    <eLabel text="LBpanel - Red Bee" position="440,34" size="430,65" font="Regular; 42" halign="center" transparent="1" foregroundColor="white" backgroundColor="#140b1" />
    <widget source="key_cancel" render="Label" position="335,644" size="500,50" font="Regular; 30" zPosition="2" halign="left" noWrap="1" transparent="1" foregroundColor="white" backgroundColor="#8f8f8f" />
    <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="80,119" size="600,50" font="Regular; 30" backgroundColor="black" foregroundColor="white" noWrap="1" />
    <widget source="global.CurrentTime" render="Label" position="949,28" size="251,55" backgroundColor="#140b1" foregroundColor="white" transparent="1" zPosition="2" font="Regular;24" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2">
      <convert type="ClockToText">Format:%-H:%M</convert>
    </widget>
    <widget source="global.CurrentTime" render="Label" position="900,50" size="300,55" backgroundColor="#140b1" foregroundColor="white" transparent="1" zPosition="2" font="Regular;16" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2">
      <convert type="ClockToText">Date</convert>
    </widget>
    <widget name="preview" position="66,396" zPosition="3" size="505,232" alphatest="blend" transparent="1" borderWidth="2" borderColor="white" />    
 
    <widget source="session.CurrentService" render="Label" zPosition="3" font="Regular; 22" position="66,649" size="215,50" halign="center" backgroundColor="black" transparent="1" noWrap="1" foregroundColor="white">
      <convert type="VtiInfo">TempInfo</convert>
    </widget>
    
    <eLabel position="center,center" size="1280,720" transparent="0" zPosition="-15" backgroundColor="#d6d6d6" />
    
    <eLabel position="60,30" size="1160,68" transparent="0" foregroundColor="white" backgroundColor="#42b3" zPosition="-10" />
    <eLabel position="60,120" size="1160,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="60,640" size="229,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="320,640" size="901,50" transparent="0" foregroundColor="white" backgroundColor="#929292" />
    <eLabel position="591,191" size="629,370" transparent="0" foregroundColor="white" backgroundColor="#6e6e6e" zPosition="-10" />
  </screen>"""
	  
	def __init__(self, session, type):
		Screen.__init__(self, session)
		if type=="spinner":
			self.setTitle(_("LBpanel-Download spinner"))
			self.plist="spinnerlb"
			self.prev=True
		elif type=="soryslist":
			self.setTitle(_("LBpanel-Download Sorys Settings"))
			self.plist="sorys"
			self.prev=False
		elif type=="configemus":
			self.setTitle(_("LBpanel-Download Config Emus"))
			self.plist="emucfg"
			self.prev=False
		elif type=="picon":
			self.setTitle(_("LBpanel-Download picon"))
			self.plist="piconlb"
			self.prev=True
		elif type=="skinparts":
			self.setTitle(_("LBpanel-Download skinpart"))
			self.plist="skinpartlb"
			self.prev=True
		elif type=="defaultskinparts":
			self.setTitle(_("LBpanel-Download skins default part"))
			self.plist='skinpartlb-openplushd.default.'
			self.prev=True
		elif type=="bootlogo":
			self.setTitle(_("LBpanel-Download bootlogo"))
			self.plist="bootlogolb"
			self.prev=True
		elif type=="bootvideo":
			self.setTitle(_("LBpanel-Download bootvideo"))
			self.plist="bootvideolb"
			self.prev=True
		
		self.session = session
		self.list = []
		self.image="first"
		self["menu"] = List(self.list)
		self["preview"] = Preview()
		self.feedlist()
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Install"))
		self["key_cancel"] = StaticText(_("PRESS EXIT TO QUIT"))
		self.ctimer = eTimer()
		self.ctimer.callback.append(self.__run)
		self.ctimer.start(1000,0)
		                                                
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
			{
				"cancel": self.cancel,
				"ok": self.ok,
				"green": self.setup,
				"red": self.cancel,
				"up": self.Kup,
				"down": self.Kdown,
				"left": self.Kleft,
				"right": self.Kright,
			},-1)

        def __run(self):
        	if len(self.list)==0:
        		image=""
        	elif self.image=="first":
			self.Kup()
                elif self.image!="":
			self.__updateimage()
		
	def __updateimage(self):
		img="/tmp/.lbimg%s" % (self.image)
		eimg="/tmp/.lbimg%s.error" % (self.image)
		print ("Check image: %s" % img)
		if self.prev==False:
			self["preview"].updateIcon(resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/openplus.jpg"))
			self["preview"].show()
			self.image=""
		elif fileExists(img) and os.path.getsize(img)>0:
			self["preview"].updateIcon(img)
			self["preview"].show()
			self.image=""
		elif fileExists(eimg) :
			print "Error downloading %s" % img
			os.remove(eimg)	
			self["preview"].updateIcon(resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/openplus.jpg"))
			self["preview"].show()
			self.image=""
		else:
			print "Preview - wait for finish download"
				
	def feedlist(self):
		self.list = []
		mlist = opkg_list(self.plist)
		softpng = LoadPixmap(cached = True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/emumini.png"))
		ulist=mlist.split('\n')
		ulist.sort()
		mlist=""
		last=""
		for line in ulist:
			try:
				if line.split(' - ')[0] != last:
					self.list.append(("%s" % (line.split(' - ')[0]), line.split(' - ')[1], softpng ))
				last = line.split(' - ')[0]
			except:
				pass
		self["menu"].setList(self.list)
	
	def Kup(self):
		if len(self.list)!=0:
			self["menu"].selectPrevious()
			self.imageDown()		
		
	def Kdown(self):
		if len(self.list)!=0:
			self["menu"].selectNext()
			self.imageDown()
	def Kleft(self):
		if len(self.list)!=0:
			self["menu"].selectPrevious()
			self.imageDown()
	def Kright(self):
		if len(self.list)!=0:
			self["menu"].selectNext()
			self.imageDown()
	
        def runDownloadImg(self, img):
		try:
			index=self["menu"].getIndex()
		except:
			index=0
        	img=self["menu"].getCurrent()[0]
		oimg="http://appstore.linux-box.es/preview/%s.png" % (img)
                timg="/tmp/%s.tmp" % img
                dimg="/tmp/.lbimg%s" % img
                print ("Downloading image  %s to %s") % (oimg, dimg)
                if not fileExists(dimg):
                	try:
                		req = urllib2.Request(oimg)
				u = urllib2.urlopen(req)
				fdest = open(timg, 'wb')
				while True:
					data = u.read(8192) 
					if not data: break
					fdest.write(data)
				fdest.flush()
				fdest.close()
				os.rename(timg, dimg)
				print ("Done download img  %s") % oimg
				
			except: 
				print "Error downloading %s" % oimg
				open("%s.error" % (dimg), 'a').close()
		#run download img cache	
		for x in range(0, self["menu"].count()):
			img=self.list[x][0]
			dimg="/tmp/.lbimg%s" % img
			if ( x==index-1) or  (x==index+1 ) or (x==index):
				if not fileExists(dimg):
					oimg="http://appstore.linux-box.es/preview/%s.png" % (img)
					timg="/tmp/%s.tmp" % img
					print "Downloading %s" % (oimg)
					try:
						req = urllib2.Request(oimg)
						u = urllib2.urlopen(req)
						fdest = open(timg, 'wb')
						while True:
							data = u.read(8192)
							if not data: break
							fdest.write(data)
						fdest.flush()
						fdest.close()
						os.rename(timg, dimg)
						print ("Done download cache img  %s") % oimg
				        except:
				        	print "Error downloading %s" % oimg
				        	open("%s.error" % (dimg), 'a').close()        
			else:
				if fileExists(dimg):
					os.remove(dimg)
			
                        
	def imageDown(self):
		if self.prev==True:
			self.image=self["menu"].getCurrent()[0]
			process = threading.Thread(target=self.runDownloadImg, args=[self.image])
			process.setDaemon(True)
			process.start()
		else:
			self.image="Local"
		
	def ok(self):
		self.setup()
		
	def setup(self):
#		try:
			if len(self.list)>0:
				if self.plist=="sorys":
					resp=ecommand("opkg remove enigma2-plugin-settings-*")
					resp=ecommand("opkg install --force-overwrite %s " % self["menu"].getCurrent()[0])
				else:
					resp=ecommand("opkg install --force-overwrite %s " % self["menu"].getCurrent()[0])
				if resp == 0:
					self.mbox = self.session.open(MessageBox, _("%s is installed" % self["menu"].getCurrent()[0]), MessageBox.TYPE_INFO, timeout = 6 )
				else:
					self.mbox = self.session.open(MessageBox, _("Error in opkg install %s " % self["menu"].getCurrent()[0]), MessageBox.TYPE_INFO, timeout = 6 )
				#self.mbox = self.session.open(MessageBox, _("%s is installed" % self["menu"].getCurrent()[0]), MessageBox.TYPE_INFO, timeout = 6 )	                                        
				#ecommand("nohup /usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/script/lbutils.sh update &")
				self.close()
#		except:
#			self.mbox = self.session.open(MessageBox, _("Error in opkg install %s " % self["menu"].getCurrent()[0]), MessageBox.TYPE_INFO, timeout = 4 )
					
	def cancel(self):
		os.system('rm -f /tmp/.lbimg*')
		self.ctimer.stop()
		self.close()
#################################################
class installremove(Screen):
	skin = """
<screen name="installremove" position="0,0" size="1280,720" title="lb_title">
  <widget source="menu" render="Listboxlb" position="591,191" size="629,350" scrollbarMode="showNever" foregroundColor="#ffffff" foregroundColorSelected="#ffffff" backgroundColor="#6e6e6e" backgroundColorSelected="#fd6502" transparent="1">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryText(pos = (70, 2), size = (630, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
			MultiContentEntryText(pos = (80, 29), size = (630, 18), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
			MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (50, 40), png = 2), # index 4 is the pixmap
				],
	"fonts": [gFont("Regular", 19),gFont("Regular", 13)],
	"itemHeight": 50
	}
	</convert>
	</widget>
	
    
<!-- colores keys -->
    <!-- rojo -->
    <widget source="key_red" render="Label" position="621,569" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="591,569" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#ee1d11" zPosition="-1" />
    <!-- amarillo -->
    <eLabel render="Label" position="621,604" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="591,604" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#eefb1a" zPosition="-1" />
    <!-- verde -->
    <eLabel render="Label" position="912,604" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="882,569" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#11b90a" zPosition="-1" />
    <!-- azul -->
    <widget source="key_green" render="Label" position="912,569" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="882,604" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#1a2cfb" zPosition="-1" />
   <widget source="key_cancel" render="Label" position="335,644" size="500,50" font="Regular; 30" zPosition="2" halign="left" noWrap="1" transparent="1" foregroundColor="white" backgroundColor="#8f8f8f" />
 <!-- fin colores keys -->
    <eLabel text="LBpanel - Red Bee" position="440,34" size="430,65" font="Regular; 42" halign="center" transparent="1" foregroundColor="white" backgroundColor="#140b1" />
    
    <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="80,119" size="600,50" font="Regular; 30" backgroundColor="black" foregroundColor="white" noWrap="1" />
    <widget source="global.CurrentTime" render="Label" position="949,28" size="251,55" backgroundColor="#140b1" foregroundColor="white" transparent="1" zPosition="2" font="Regular;24" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2">
      <convert type="ClockToText">Format:%-H:%M</convert>
    </widget>
    <widget source="global.CurrentTime" render="Label" position="900,50" size="300,55" backgroundColor="#140b1" foregroundColor="white" transparent="1" zPosition="2" font="Regular;16" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2">
      <convert type="ClockToText">Date</convert>
    </widget>
    <widget source="session.VideoPicture" render="Pig" position="64,196" size="375,175" backgroundColor="transparent" zPosition="-1" transparent="0" />
    <widget source="session.CurrentService" render="RunningText" options="movetype=running,startpoint=0,direction=left,steptime=25,repeat=150,startdelay=1500,always=0" position="101,491" size="215,45" font="Regular; 22" transparent="1" valign="center" zPosition="2" backgroundColor="black" foregroundColor="white" noWrap="1" halign="center">
      <convert type="ServiceName">Name</convert>
    </widget>
    <widget source="session.CurrentService" render="Label" zPosition="3" font="Regular; 22" position="66,649" size="215,50" halign="center" backgroundColor="black" transparent="1" noWrap="1" foregroundColor="white">
      <convert type="VtiInfo">TempInfo</convert>
    </widget>
    <eLabel position="192,459" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#ee1d11" zPosition="-1" />
    <eLabel position="251,410" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#1a2cfb" zPosition="-2" />
    <eLabel position="281,449" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#11b90a" zPosition="-6" />
    <eLabel position="233,499" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#eefb1a" zPosition="-5" />
    <eLabel position="60,451" size="65,57" transparent="0" foregroundColor="white" backgroundColor="#ecbc13" zPosition="-6" />
    <eLabel position="96,489" size="229,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="0,0" size="1280,720" transparent="0" zPosition="-15" backgroundColor="#d6d6d6" />
    <ePixmap position="46,180" zPosition="0" size="413,210" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/images/marcotv.png" transparent="0" />
    <eLabel position="60,30" size="1160,68" transparent="0" foregroundColor="white" backgroundColor="#42b3" zPosition="-10" />
    <eLabel position="60,120" size="1160,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="60,640" size="229,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="320,640" size="901,50" transparent="0" foregroundColor="white" backgroundColor="#929292" />
    <eLabel position="591,191" size="629,370" transparent="0" foregroundColor="white" backgroundColor="#6e6e6e" zPosition="-10" />
   </screen>"""
	  
	skin = skin.replace("lb_title", _("LBpanel - Remove Bee installed"))  
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.list = []
		self["menu"] = List(self.list)
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Remove"))
		self["key_cancel"] = StaticText(_("PRESS EXIT TO QUIT"))
		self.feedlist()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.ok,
				"green": self.setup,
				"red": self.cancel,
			},-1)
		self.list = [ ]
		
		
	def feedlist(self):
		self.list = []
		camdlist = command("opkg list-installed | grep -i -e 'sorys' -e 'emucfg' -e 'bootvideolb' -e 'piconlb' -e 'skinpartlb' -e 'spinnerlb' -e 'skindefaultlb' -e 'bootlogolb'")
		softpng = LoadPixmap(cached = True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/LBpanel/images/emumini1.png"))
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
		resp=ecommand("opkg remove %s" % self["menu"].getCurrent()[0])
		self.mbox = self.session.open(MessageBox, _("%s is remove" % self["menu"].getCurrent()[0]), MessageBox.TYPE_INFO, timeout = 4 )
		

	def cancel(self):
		self.close()
#################################################
class LBsettings(ConfigListScreen, Screen):
	skin = """
<screen name="scanhost" position="0,0" size="1280,720" title="LBpanel - Config">
    
  <widget position="591,191" size="629,350" foregroundColor="#ffffff" foregroundColorSelected="#ffffff" backgroundColor="#6e6e6e" backgroundColorSelected="#fd6502" transparent="1" name="config" scrollbarMode="showOnDemand" />
  <!-- colores keys -->
    <!-- rojo -->
    <widget source="key_red" render="Label" position="621,569" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="591,569" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#ee1d11" zPosition="-1" />
    <!-- amarillo -->
    <eLabel render="Label" position="621,604" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="591,604" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#eefb1a" zPosition="-1" />
    <!-- verde -->
    <eLabel render="Label" position="912,604" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="882,569" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#11b90a" zPosition="-1" />
    <!-- azul -->
    <widget source="key_green" render="Label" position="912,569" size="240,30" zPosition="1" font="Regular; 20" backgroundColor="black" transparent="0" foregroundColor="#d6d6d6" halign="center" />
    <eLabel position="882,604" size="30,30" transparent="0" foregroundColor="white" backgroundColor="#1a2cfb" zPosition="-1" />
   <widget source="key_cancel" render="Label" position="335,644" size="500,50" font="Regular; 30" zPosition="2" halign="left" noWrap="1" transparent="1" foregroundColor="white" backgroundColor="#8f8f8f" />
 <!-- fin colores keys -->
    <eLabel text="LBpanel - Red Bee" position="440,34" size="430,65" font="Regular; 42" halign="center" transparent="1" foregroundColor="white" backgroundColor="#140b1" />
    
    <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="80,119" size="600,50" font="Regular; 30" backgroundColor="black" foregroundColor="white" noWrap="1" />
    <widget source="global.CurrentTime" render="Label" position="949,28" size="251,55" backgroundColor="#140b1" foregroundColor="white" transparent="1" zPosition="2" font="Regular;24" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2">
      <convert type="ClockToText">Format:%-H:%M</convert>
    </widget>
    <widget source="global.CurrentTime" render="Label" position="900,50" size="300,55" backgroundColor="#140b1" foregroundColor="white" transparent="1" zPosition="2" font="Regular;16" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2">
      <convert type="ClockToText">Date</convert>
    </widget>
    <widget source="session.VideoPicture" render="Pig" position="64,196" size="375,175" backgroundColor="transparent" zPosition="-1" transparent="0" />
    <widget source="session.CurrentService" render="RunningText" options="movetype=running,startpoint=0,direction=left,steptime=25,repeat=150,startdelay=1500,always=0" position="101,491" size="215,45" font="Regular; 22" transparent="1" valign="center" zPosition="2" backgroundColor="black" foregroundColor="white" noWrap="1" halign="center">
      <convert type="ServiceName">Name</convert>
    </widget>
    <widget source="session.CurrentService" render="Label" zPosition="3" font="Regular; 22" position="66,649" size="215,50" halign="center" backgroundColor="black" transparent="1" noWrap="1" foregroundColor="white">
      <convert type="VtiInfo">TempInfo</convert>
    </widget>
    <eLabel position="192,459" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#ee1d11" zPosition="-1" />
    <eLabel position="251,410" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#1a2cfb" zPosition="-2" />
    <eLabel position="281,449" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#11b90a" zPosition="-6" />
    <eLabel position="233,499" size="165,107" transparent="0" foregroundColor="white" backgroundColor="#eefb1a" zPosition="-5" />
    <eLabel position="60,451" size="65,57" transparent="0" foregroundColor="white" backgroundColor="#ecbc13" zPosition="-6" />
    <eLabel position="96,489" size="229,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="center,center" size="1280,720" transparent="0" zPosition="-15" backgroundColor="#d6d6d6" />
    <ePixmap position="46,180" zPosition="0" size="413,210" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/images/marcotv.png" transparent="0" />
    <eLabel position="60,30" size="1160,68" transparent="0" foregroundColor="white" backgroundColor="#42b3" zPosition="-10" />
    <eLabel position="60,120" size="1160,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="60,640" size="229,50" transparent="0" foregroundColor="white" backgroundColor="black" />
    <eLabel position="320,640" size="901,50" transparent="0" foregroundColor="white" backgroundColor="#929292" />
    <eLabel position="591,191" size="629,370" transparent="0" foregroundColor="white" backgroundColor="#6e6e6e" zPosition="-10" />
   </screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("LBpanel - Configuration"))
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))
		#self["key_yellow"] = StaticText(_("Default Package"))
		self["key_cancel"] = StaticText(_("PRESS EXIT TO QUIT"))
		self.list = []
		self.list.append(getConfigListEntry(_("Auto Update LBpanel"), config.plugins.lbpanel.update))
		self.list.append(getConfigListEntry(_("Auto Update Settings"), config.plugins.lbpanel.updatesettings))
		self.list.append(getConfigListEntry(_("Send email on report by local to user?"), config.plugins.lbpanel.lbemail))
		self.list.append(getConfigListEntry(_("Send email on report by proxy to user?"), config.plugins.lbpanel.lbiemail))
		self.list.append(getConfigListEntry(_("Send errors/reports to: (email)"), config.plugins.lbpanel.lbemailto))
		self.list.append(getConfigListEntry(_("Smtp server"), config.plugins.lbpanel.smtpserver))  
		self.list.append(getConfigListEntry(_("Smtp user"), config.plugins.lbpanel.smtpuser))
		self.list.append(getConfigListEntry(_("Smtp password"), config.plugins.lbpanel.smtppass))
		self.list.append(getConfigListEntry(_("Smtp protocol"), config.plugins.lbpanel.lbemailproto))
		self.list.append(getConfigListEntry(_("Enable Softcam check?"), config.plugins.lbpanel.testcam))                                                                                
		ConfigListScreen.__init__(self, self.list)
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"red": self.cancel,
			"cancel": self.cancel,
			"green": self.save,
			"ok": self.save
		}, -2)
		
		
	def cancel(self):
		for i in self["config"].list:
			i[1].cancel()
		self.close(False)
	
	def save(self):
		config.plugins.lbpanel.update.save()
		config.plugins.lbpanel.updatesettings.save()
                config.plugins.lbpanel.lbemail.save()
                config.plugins.lbpanel.lbiemail.save()  
		config.plugins.lbpanel.lbemailto.save()
		config.plugins.lbpanel.smtpserver.save()
		config.plugins.lbpanel.smtpuser.save()  
		config.plugins.lbpanel.smtppass.save()
		config.plugins.lbpanel.lbemailproto.save()
		config.plugins.lbpanel.testcam.save()
		configfile.save()
		self.mbox = self.session.open(MessageBox,(_("Configuration is saved")), MessageBox.TYPE_INFO, timeout = 4 )

################################################################################################################
## Cron especific function for lbpanel
class lbCron():
	def __init__(self):
		self.dialog = None

	def gotSession(self, session):
		self.session = session
		self.timer = eTimer() 
		self.timer.callback.append(self.update)
		self.timer.start(60000, True)

	def update(self):
		self.timer.stop()
		now = time.localtime(time.time())
		# cron update control, test every hour, execute a script to test.
                global cronvar
		cronvar += 1
		## Check for updates
		print "Executing update LBpanel in %s minutes" % (60 - cronvar)
		if (cronvar == 60 ):
			cronvar = 0
			print "Openplus Panel: Updating packages......"
                        #from Screens.Ipkg import Ipkg
                        #from Components.Ipkg import IpkgComponent
                        #self.ipkg = IpkgComponent()
                        #self.ipkg.startCmd(IpkgComponent.CMD_UPDATE)			                                                                                                                        
			if (config.plugins.lbpanel.updatesettings.value):
				os.system("nohup /usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/script/lbutils.sh testsettings &")
			else:
				os.system("nohup /usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/script/lbutils.sh update &") 
		if (os.path.isfile("/tmp/.lbsettings.update")):
			print "LBpanel settings updated"
			self.mbox = self.session.open(MessageBox,(_("LBpanel settings has been updated, restart Enigma2 to activate your changes.")), MessageBox.TYPE_INFO, timeout = 30 )
			os.remove("/tmp/.lbsettings.update")
		# cron control epg
		if (config.plugins.lbpanel.auto.value == "yes" and config.plugins.lbpanel.epgtime.value[0] == now.tm_hour and config.plugins.lbpanel.epgtime.value[1] == now.tm_min):
			myepg = LBtools.epgdn(self.session)
			myepg.downepg()
		# cron control epg2
		if (config.plugins.lbpanel.auto2.value == "yes" and config.plugins.lbpanel.epgtime2.value[0] == now.tm_hour and config.plugins.lbpanel.epgtime2.value[1] == now.tm_min):
			myepg = LBtools.epgscript(self.session)
			myepg.downepg()
		#epg every hour
		if (config.plugins.lbpanel.runeveryhour.value == True and now.tm_min == 0 and Screens.Standby.inStandby ):
			myepg = LBtools.epgscript(self.session)
			myepg.downepg()
		# reload epg
		if (os.path.isfile("/tmp/.epgreload")):
			os.remove("/tmp/.epgreload")
		# cron control scan peer
		if (config.plugins.lbpanel.checkauto.value == "yes" and config.plugins.lbpanel.checkhour.value[0] == now.tm_hour and config.plugins.lbpanel.checkhour.value[1] == now.tm_min):
			self.scanpeer()
                #cron for send email
                if ((config.plugins.lbpanel.lbemail.value or config.plugins.lbpanel.lbiemail.value) and os.path.isfile("/tmp/.lbscan.end")):
                	os.remove("/tmp/.lbscan.end")
                	msg = ""
                        scaninfo = open("/tmp/.lbscan.log", "r")
                        for line in scaninfo:
                               msg += line  	
			scaninfo.close()
                	sendemail(config.plugins.lbpanel.smtpuser.value, config.plugins.lbpanel.lbemailto.value,"", "Scan report from LBpanel",msg,config.plugins.lbpanel.smtpuser.value,config.plugins.lbpanel.smtppass.value)
                # i-email error test
                if (os.path.isfile("/tmp/.ilbmail.log")):
                	log = open("/tmp/.ilbmail.log", "r")
                	msg = ""
                	for line in log:
                		msg += line
                	if ("Error sending" in msg ):
                		self.mbox = self.session.open(MessageBox,(msg), MessageBox.TYPE_INFO, timeout = 30 )
				
			log.close()
			os.remove("/tmp/.ilbmail.log")
                #cron for testcam
                print "Testing softcam  %s" % (config.plugins.lbpanel.activeemu.value)
                if (config.plugins.lbpanel.testcam.value and config.plugins.lbpanel.activeemu.value != "NotSelected" ):
                	# Test if a cam is live
                	actcam = config.plugins.lbpanel.activeemu.value
                	actcam = actcam.replace("camemu.", "")
                	if (search_process(actcam) != 1):
                		print "Restarting softcam %s" % (config.plugins.lbpanel.activeemu.value)
                		os.system("/usr/CamEmu/%s restart &" % config.plugins.lbpanel.activeemu.value )
				if (config.plugins.lbpanel.lbemail.value or config.plugins.lbpanel.lbiemail.value):
					if os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/templates/errorcam.msg"):
						subj = f.readline()
						msg = f.read()
						f.close
						subj = subj.replace(".cam.",actcam)
						msg = msg.replace(".cam.",actcam)
					else:
						subj = _("Softcam error")
						msg = _('The cam %s appears to malfunction.\nService has been restarted.\nLBpanel\n') % actcam
					sendemail(config.plugins.lbpanel.smtpuser.value, config.plugins.lbpanel.lbemailto.value,"" ,subj ,msg, config.plugins.lbpanel.smtpuser.value,config.plugins.lbpanel.smtppass.value)
		if config.plugins.lbpanel.autosave.value != '0':
			global min
			if min > int(config.plugins.lbpanel.autosave.value) and config.plugins.lbpanel.epgtime.value[1] != now.tm_min:
				min = 0
				self.save_load_epg()
				if config.plugins.lbpanel.autobackup.value:
					self.autobackup()
			else:
				min = min + 1
		# Test errors
		if (os.path.isfile("/tmp/.lbemail.error")):
			print "LBpanel settings updated"
			self.mbox = self.session.open(MessageBox,(_("Email send error:\nYour system not support send local email\nPlease select proxy option to send email")), MessageBox.TYPE_ERROR, timeout = 30 )
			os.remove("/tmp/.lbemail.error")
		self.timer.start(60000, True)
		
	def autobackup(self):
		if fileExists("%sepg.dat.gz.bak" % config.misc.epgcachepath.value):
	        	os.unlink("%sepg.dat.gz.bak" % config.misc.epgcachepath.value)
	                file = gzip.open("%sepg.dat.gz" % config.misc.epgcachepath.value, 'wb')
	                f = open( "%sepg.dat" % (config.misc.epgcachepath.value), "rb")
	                try:
	                	file.write(f.read())
			except:
				print "Error in autobackup epg"
                	f.close()   
	                file.close()
	                if fileExists("%sepg.dat.gz" % config.misc.epgcachepath.value):
	                	os.rename("%sepg.dat.gz" % config.misc.epgcachepath.value, "%sepg.dat.gz.bak" % config.misc.epgcachepath.value)
		
	def save_load_epg(self):
		epgcache = new.instancemethod(_enigma.eEPGCache_save,None,eEPGCache)
		epgcache = eEPGCache.getInstance().save()
		epgcache = new.instancemethod(_enigma.eEPGCache_load,None,eEPGCache)
		epgcache = eEPGCache.getInstance().load()

	def scanpeer(self):
		os.system("/usr/lib/enigma2/python/Plugins/SystemPlugins/LBpanel/lbscan.py %s %s %s %s &" % (config.plugins.lbpanel.checktype.value, config.plugins.lbpanel.autocheck.value, config.plugins.lbpanel.checkoff.value, config.plugins.lbpanel.warnonlyemail.value))
	
#####################################################
def main(session, **kwargs):
	session.open(epgdn2)
##############################################################################
pEmu = lbCron()
##############################################################################
def sessionstart(reason,session=None, **kwargs):
	if reason == 0:
		pEmu.gotSession(session)
##############################################################################
def main(session, **kwargs):
	session.open(LBPanel2)

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("LBpanel"), main, _("Linux_Box_Panel"), 48)]
	return []

def extsoft(session, **kwargs):
	session.open(LBCamEmu.emuSel2)
	
def nclsw(session, **kwargs):
	session.open(LBCamEmu.NCLSwp2)
	
def wcsw(session, **kwargs):
	session.open(LBCamEmu.wicconfsw)
	
def clviewer(session, **kwargs):
	session.open(LBtools.CrashLogScreen)
	
def scriptex(session, **kwargs):
	session.open(LBtools.ScriptScreen)
	
def usbunmt(session, **kwargs):
	session.open(LBtools.UsbScreen)
	
def setupipk(session, **kwargs):
	session.open(LBipk.InstallAll)
	
def Plugins(**kwargs):
	list = [PluginDescriptor(name=_("LBpanel - Red Bee"), description=_("Linux-Box Panel by LBTEAM"), where = [PluginDescriptor.WHERE_PLUGINMENU], icon="images/LBPanel.png", fnc=main)]
	if config.plugins.lbpanel.showepanelmenu.value:
		list.append(PluginDescriptor(name=_("LBpanel"), description=_("Linux-Box Panel"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main))
	if config.plugins.lbpanel.showextsoft.value:
		list.append(PluginDescriptor(name=_("CamEmu Manager"), description=_("Start, Stop, Restart Sofcam/Cardserver"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=extsoft))
	if config.plugins.lbpanel.shownclsw.value:
		list.append(PluginDescriptor(name=_("LB-Newcamd.list switcher"), description=_("Switch newcamd.list with remote conrol"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=nclsw))
	if config.plugins.lbpanel.showwcsw.value:
		list.append(PluginDescriptor(name=_("LB-Wicardd.conf switcher"), description=_("Switch wicardd.conf with remote conrol"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=wcsw))
	if config.plugins.lbpanel.showclviewer.value:
		list.append(PluginDescriptor(name=_("LB-Crashlog viewer"), description=_("Switch newcamd.list with remote conrol"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=clviewer))
	if config.plugins.lbpanel.showscriptex.value:
		list.append(PluginDescriptor(name=_("LB-Script Executer"), description=_("Start scripts from /usr/script"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=scriptex))
	if config.plugins.lbpanel.showusbunmt.value:
		list.append(PluginDescriptor(name=_("LB-Unmount USB"), description=_("Unmount usb devices"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=usbunmt))
	if config.plugins.lbpanel.showsetupipk.value:
		list.append(PluginDescriptor(name=_("LB-Installer"), description=_("install & forced install ipk, bh.tgz, tar.gz, nab.tgz from /tmp"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=setupipk))
	if config.plugins.lbpanel.showmain.value:
		list.append(PluginDescriptor(name=_("LBPanel"), description=_("LBTeam Panel Plugin"), where = [PluginDescriptor.WHERE_MENU], fnc=menu))
	list.append(PluginDescriptor(name=_("LBPanel"), description=_("LBTeam Panel Plugin"), where = [PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART], fnc = sessionstart))
	return list

