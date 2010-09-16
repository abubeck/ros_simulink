#!/usr/bin/env python

import sys
import subprocess
import time
import os
import xmlrpclib

class rosmatlabclient:
	def __init__(self):
		self.server = xmlrpclib.ServerProxy("http://localhost:14441")
	def load(self, pkgname):
		pkgloc = subprocess.Popen(["rospack", "find", pkgname], stdout=subprocess.PIPE).communicate()[0]
		if(pkgloc != ""):
			print type(pkgloc)
			print "==="
			print pkgloc
			print "==="
		        resp1 = self.server.matlab.eval("cd "+ pkgloc.rstrip() + "/simulink")
			time.sleep(0.5)
		        resp1 = self.server.matlab.eval("open_system('" + pkgname + "')")
			
		
		
	def compile(self, pkgname):
		pkgloc = subprocess.Popen(["rospack", "find", pkgname], stdout=subprocess.PIPE).communicate()[0]
		if(pkgloc != ""):
			print type(pkgloc)
			print "==="
			print pkgloc
			print "==="
		        resp1 = self.server.matlab.eval("cd "+ pkgloc.rstrip() + "/simulink")
			time.sleep(0.5)
		        resp1 = self.server.matlab.eval("rtwbuild('" + pkgname + "')")
			time.sleep(0.5)
			if os.path.exists(pkgloc.rstrip()+"/rtw/slprj"):
				subprocess.Popen(["rm", "-r" ,pkgloc.rstrip()+"/rtw/slprj"])
			subprocess.Popen(["mv", pkgloc.rstrip()+"/simulink/slprj", pkgloc.rstrip()+"/rtw/slprj"], stdout=subprocess.PIPE)
			time.sleep(0.5)
			if os.path.exists(pkgloc.rstrip()+"/rtw/"+pkgname+"_grt_rtw"):
				subprocess.Popen(["rm", "-r" ,pkgloc.rstrip()+"/rtw/"+pkgname+"_grt_rtw"])
			subprocess.Popen(["mv", pkgloc.rstrip()+"/simulink/"+pkgname+"_grt_rtw", pkgloc.rstrip()+"/rtw/"+pkgname+"_grt_rtw"], stdout=subprocess.PIPE)
			d = pkgloc.rstrip()+"/build/rtw/"
			if not os.path.exists(d):
				os.makedirs(d)
			subprocess.Popen(["cp", "-r", pkgloc.rstrip()+"/rtw/"+pkgname+"_grt_rtw", pkgloc.rstrip()+"/build/rtw/"+pkgname+"_grt_rtw"], stdout=subprocess.PIPE)

	def generate(self, pkgname):
		pass

if __name__ == "__main__":
	client = rosmatlabclient()	
	if len(sys.argv) == 3:
		if(sys.argv[1] == "load"):
			client.load(sys.argv[2])
		if(sys.argv[1] == "compile"):
			client.compile(sys.argv[2])
		if(sys.argv[1] == "generate"):
			client.generate(sys.argv[2])
	else:
		print "Usage: rosmlabcmd [load | compile | generate] pkgname"


