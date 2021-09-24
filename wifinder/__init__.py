import os, io, sys, subprocess, gi, threading
import time
import re

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio, GLib

class WiFinder(Gtk.Window):
	APList = []
	container = None
	scroller = None
	scrollbox = None
	
	def __init__(self):
		Gtk.Window.__init__(self)
		self.set_title("WiFinder")
		self.set_border_width(10)
		self.set_default_size(360, 720)
		#self.maximize()
		
		self.scroller = Gtk.ScrolledWindow()
		self.scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		
		self.scrollbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
		
		self.scroller.add(self.scrollbox)
		
		self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
		self.add(self.container)
		

		macbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		
		self.macentry = Gtk.SearchEntry()
		self.macentry.set_text("")
		#self.macentry.connect("activate", self.OnSetMac)
		#self.macentry.get_style_context().add_class('app-theme')
		macbox.pack_start(self.macentry, True, True, 0)

		self.container.pack_end(self.scroller, True, True, 0)
		self.container.add(macbox)
		
		self.show_all()
		
		x = threading.Thread(target=self.DoScan, args=(None, True))
		x.start()
		
	def LaunchScan(self):
		x = threading.Thread(target=self.DoScan, args=(None, True))
		x.start()

	def DoScan(self, sort, clear):
		if sort is None:
			sort = "ssid"
		
		nmcliparams = [
			'nmcli',
			'dev',
			'wifi',
			'list'
		]
                    
		self.nmcli = subprocess.Popen(nmcliparams, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		out, err = self.nmcli.communicate()
		
		print("Output: \n" + out.decode('UTF-8'))
		
		aplist = out.decode('UTF-8').split("\n")
		outaplist = []
		
		for eap in range(1, len(aplist)):
			if aplist[eap][0: 1] == "*":
				aplist[eap] = aplist[eap][1:]
				
			aplist[eap] = aplist[eap].strip()
			
			apinfos = re.findall(r'\S+', aplist[eap])
			
			"""tmac = aplist[eap][0:17]
			tssid = aplist[eap][19:41].strip()
			tmode = aplist[eap][41:49].strip()
			tchan = aplist[eap][49:55].strip()
			trate = aplist[eap][55:67].strip()
			tsignal = aplist[eap][67:75].strip()
			tsec = aplist[eap][81:].strip()"""
			
			tmac = apinfos[0]
			tssid = apinfos[1]
			tmode = apinfos[2]
			tchan = apinfos[3]
			trate = apinfos[4]
			tsignal = apinfos[5]
			tsec = apinfos[7]
			
			if tmac != "":
				apdict = {
					"mac": tmac,
					"ssid": tssid,
					"mode": tmode,
					"chan": tchan,
					"rate": trate,
					"signal": tsignal if tsignal != "" else "0",
					"sec": tsec
				}
				
				outaplist.append(apdict)
		
		#print(outaplist)
		GLib.idle_add(self.DoUpdateApList, outaplist)
		
	def DoUpdateApList(self, newaplist):
		#	First, update the APList global
		for eap in range(0, len(newaplist)):
			apid = self.FindAPID(newaplist[eap]["mac"])
			
			if apid < 0:
				apentry = {
					"mac": newaplist[eap]["mac"].replace(":", "").strip(),
					"data": newaplist[eap],
					"lastupdate": time.time(),
					"ui": {}
				}
				
				self.APList.append(apentry)
				apid = self.FindAPID(newaplist[eap]["mac"])
				
				self.BuildUIElement(apid)
			else:
				self.APList[apid]["data"] = newaplist[eap]
				self.APList[apid]["lastupdate"] = time.time()
				
			self.UpdateUIElement(apid)
		
		#print(self.APList)
		#GObject.timeout_add(1000, self.LaunchScan)
		GLib.timeout_add(1000, self.LaunchScan)
	
	def FindAPID(self, mac):
		if len(self.APList) == 0:
			return -1
		
		prettymac = mac.replace(":", "").strip()
		
		for eap in range(0, len(self.APList)):
			if self.APList[eap]["mac"] == prettymac:
				return eap
				
		return -1
		
	def BuildUIElement(self, apid):
		#fullbox
		#	SSID
		#	MAC | CHANNEL
		#	SIGNAL METER
		self.APList[apid]["ui"]["fullbox"] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
		self.APList[apid]["ui"]["ssidlbl"] = Gtk.Label()
		self.APList[apid]["ui"]["ssidlbl"].set_markup("<big><big><b>" + self.APList[apid]["data"]["ssid"] + "</b></big></big>")
		self.APList[apid]["ui"]["ssidlbl"].set_alignment(0.0, 0.5)
		self.APList[apid]["ui"]["ssidlbl"].set_justify(Gtk.Justification.FILL)
		self.APList[apid]["ui"]["ssidlbl"].set_line_wrap(False)
		
		self.APList[apid]["ui"]["fullbox"].add(self.APList[apid]["ui"]["ssidlbl"])
		
		self.APList[apid]["ui"]["macchanbox"] = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
		self.APList[apid]["ui"]["maclbl"] = Gtk.Label()
		self.APList[apid]["ui"]["maclbl"].set_markup("<big>" + self.APList[apid]["data"]["mac"] + "</big>")
		self.APList[apid]["ui"]["maclbl"].set_alignment(0.0, 0.5)
		self.APList[apid]["ui"]["maclbl"].set_justify(Gtk.Justification.LEFT)
		
		self.APList[apid]["ui"]["chanlbl"] = Gtk.Label()
		self.APList[apid]["ui"]["chanlbl"].set_markup(self.APList[apid]["data"]["chan"])
		self.APList[apid]["ui"]["chanlbl"].set_alignment(1.0, 0.5)
		self.APList[apid]["ui"]["chanlbl"].set_justify(Gtk.Justification.RIGHT)
		
		self.APList[apid]["ui"]["macchanbox"].pack_start(self.APList[apid]["ui"]["maclbl"], True, True, 0)
		self.APList[apid]["ui"]["macchanbox"].add(self.APList[apid]["ui"]["chanlbl"])
		
		self.APList[apid]["ui"]["fullbox"].add(self.APList[apid]["ui"]["macchanbox"])
		
		self.APList[apid]["ui"]["signallevel"] = Gtk.LevelBar()
		self.APList[apid]["ui"]["signallevel"].set_value(int(self.APList[apid]["data"]["signal"]) / 100)
		self.APList[apid]["ui"]["fullbox"].add(self.APList[apid]["ui"]["signallevel"])
		
		#	And a nice little separator
		self.APList[apid]["ui"]["separator"] = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
		self.APList[apid]["ui"]["fullbox"].add(self.APList[apid]["ui"]["separator"])
		
		self.scrollbox.add(self.APList[apid]["ui"]["fullbox"])
		
		self.show_all()
		
	def UpdateUIElement(self, apid):
		
		self.APList[apid]["ui"]["ssidlbl"].set_markup("<big><big><b>" + self.APList[apid]["data"]["ssid"] + "</b></big></big>")
		self.APList[apid]["ui"]["maclbl"].set_markup("<big>" + self.APList[apid]["data"]["mac"] + "</big>")
		self.APList[apid]["ui"]["chanlbl"].set_markup(self.APList[apid]["data"]["chan"])
		self.APList[apid]["ui"]["signallevel"].set_value(int(self.APList[apid]["data"]["signal"]) / 100)
		
		self.show_all()
		

app = WiFinder()
app.connect("destroy", Gtk.main_quit)
app.show_all()
Gtk.main()
