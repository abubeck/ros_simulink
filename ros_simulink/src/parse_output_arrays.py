#!/usr/bin/env python
import re

def getNumOfArray(modelname, topicname):
	f = open("simulink/"+modelname+"_grt_rtw/"+modelname+".h", 'r')
	fstr = f.read()
	regexstring = "real_T " + topicname + '\[\d\]'
	m = re.search(regexstring,fstr)	
	if(m):
		return m.group(0).split('[')[1].split(']')[0]
	else:
		return 0

if __name__ == "__main__":
	print getNumOfArray("cob_testslinkcontroller","ROSLINKTopic2")
	print getNumOfArray("cob_testslinkcontroller","ROSLINKTopic1")
