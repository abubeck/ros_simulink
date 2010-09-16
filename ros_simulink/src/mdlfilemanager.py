#!/usr/bin/env python
import roslib; roslib.load_manifest('ros_simulink')

import sys
import rospy
import re
import string
import pprint
import subprocess
import time
import os
from pyparsing import *
from Cheetah.Template import Template

# A high level grammar of the Simulink mdl file format
SIMULINK_BNF = """
object {
     members
}
members
    variablename  value
    object {
        members
    }
variablename

array
    [ elements ]
matrix
    [elements ; elements]
elements
    value
    elements , value
value
    string
    doublequotedstring
    float
    integer
    object
    array
    matrix
"""

# parse actions
def convertNumbers(s,l,toks):
    """Convert tokens to int or float"""
    # Taken from jsonParser.py
    n = toks[0]
    try:
        return int(n)
    except ValueError, ve:
        return float(n)

def joinStrings(s,l,toks):
    """Join string split over multiple lines"""
    return ["".join(toks)]

# Define grammar

# Parse double quoted strings. Ideally we should have used the simple statement:
#    dblString = dblQuotedString.setParseAction( removeQuotes )
# Unfortunately dblQuotedString does not handle special chars like \n \t,
# so we have to use a custom regex instead.
# See http://pyparsing.wikispaces.com/message/view/home/3778969 for details. 
dblString = Regex(r'\"(?:\\\"|\\\\|[^"])*\"', re.MULTILINE)
dblString.setParseAction( removeQuotes )


mdlNumber = Combine( Optional('-') + ( '0' | Word('123456789',nums) ) +
                    Optional( '.' + Word(nums) ) +
                    Optional( Word('eE',exact=1) + Word(nums+'+-',nums) ) )
mdlObject = Forward()
mdlName = Word('$'+'.'+'_'+alphas+nums)
mdlValue = Forward()
# Strings can be split over multiple lines
mdlString = (dblString + Optional(OneOrMore(Suppress(LineEnd()) + LineStart()
             + dblString)))
mdlElements = delimitedList( mdlValue )
mdlArray = Group(Suppress('[') + Optional(mdlElements) + Suppress(']') )
mdlMatrix =Group(Suppress('[') + (delimitedList(Group(mdlElements),';')) \
              + Suppress(']') )
mdlValue << ( mdlNumber | mdlName| mdlString  | mdlArray | mdlMatrix )
memberDef = Group( mdlName  + mdlValue ) | Group(mdlObject)
mdlMembers = OneOrMore( memberDef)
mdlObject << ( mdlName+Suppress('{') + Optional(mdlMembers) + Suppress('}') )
mdlNumber.setParseAction( convertNumbers )
mdlString.setParseAction(joinStrings)
# Some mdl files from Mathworks start with a comment. Ignore all
# lines that start with a #
singleLineComment = Group("#" + restOfLine)
mdlObject.ignore(singleLineComment)
mdlparser = mdlObject



class mdlfilemanager:
	def __init__(self):
		self.modelname = ""
		self.inputblocks = []
		self.outputblocks = []

	def load(self, filename):
		f = open(filename, 'r')
		testdata = f.read()
		f.close()
		result = mdlparser.parseString(testdata)
		for firstlevel in result:
			if(firstlevel[0] == 'System'):
				for systeminfo in firstlevel:
					if(systeminfo[0] == "Name"):
						self.modelname = systeminfo[1]
					if(systeminfo[0] == "Block"):
						if(string.count(systeminfo[2][1], "ROSLINK" ) > 0):
							if(systeminfo[1][1] == "Outport"):
								self.outputblocks.append(systeminfo[2][1])
							if(systeminfo[1][1] == "Inport"):
								self.inputblocks.append(systeminfo[2][1])
			
	def printout(self):
		print self.modelname
		for block in self.inputblocks:
			print "InBlock: ", block
		for block in self.outputblocks:
			print "OutBlock: ", block

	def generateHeaders(self):
		outstr = ''
		outstr += "#include <ros/ros.h>\n"
		outstr += "#include <rtw/grt_main.h>\n"
		outstr += "#include <std_msgs/Float64MultiArray.h>\n\n\n"
		outstr += "class " + self.modelname + "ROS{\n"
		outstr += "public:\n"
		outstr += "\tros::NodeHandle n;\n"
		for block in self.inputblocks:
			blocknospace = string.replace(block," ", "_")
			outstr += "\tros::Subscriber "+blocknospace+"_sub ;\n"
		for block in self.outputblocks:
			blocknospace = string.replace(block," ", "_")
			outstr += "\tros::Publisher "+blocknospace+"_pub ;\n"
		outstr += "\tdouble inputArgs["+str(len(self.inputblocks))+"];"
		return outstr
	
		

	def generateConstructorCode(self):
		outstr = "\n\n" + self.modelname +'ROS()\n{\n'
		for block in self.inputblocks:
			blocknospace = string.replace(block," ", "_")
			outstr += "\t" + blocknospace+"_sub = n.subscribe(\""+blocknospace+"\", 100, &" + self.modelname + "ROS::"+blocknospace+"_Callback, this);\n"
		for block in self.outputblocks:
			blocknospace = string.replace(block," ", "_")
			outstr += "\t" + blocknospace+"_pub = n.advertise<std_msgs::Float64MultiArray>(\""+blocknospace+"\", 100);\n"
		for i in range(len(self.inputblocks)):
			outstr += "\tinputArgs["+str(i)+"] = 0.0;\n"
		outstr+="}\n"
		return outstr

	def generateCallbackCode(self):
		outstr = ''
		for i in range(len(self.inputblocks)):
			blocknospace = string.replace(self.inputblocks[i]," ", "_")
			outstr += "void "+blocknospace+"_Callback(const std_msgs::Float64MultiArray& msg)\n{\n\t"
			outstr += "inputArgs["+str(i)+"] = msg.data[0];\n\t"
			outstr += "ROS_INFO(\"Received something\");\n}\n\n"
		return outstr

	def generateClassFooter(self):
		return "}; //"+self.modelname+"\n"
	
	def generatePublishFunction(self):
		outstr = "void publishData(int nbrOutputArgs, double* outputArgs)\n{\n"
		outstr += "\tstd_msgs::Float64MultiArray msg;\n\tmsg.data.resize(1);\n"
		for i in range(len(self.outputblocks)):
			blocknospace = string.replace(self.outputblocks[i]," ", "_")
			outstr += "\tmsg.data[0] = outputArgs["+str(i)+"];\n\t"
			outstr += blocknospace+"_pub.publish(msg);\n"
		outstr += "}\n\n"
		return outstr

	def generateMainRoutine(self):
		outstr = "int main(int argc, char** argv)\n{\n"
		outstr += "\tros::init(argc, argv, \""+self.modelname+"\");\n"
		outstr += "\tinitiateController();\n"
		outstr += "\t"+ self.modelname + "ROS "+ self.modelname +"_node;\n"
		outstr += "\tsleep(1);\n"
		outstr += "\tros::Rate loop_rate(5); // Hz\n"
		outstr += "\twhile("+ self.modelname +"_node.n.ok())\n \t{ \n"
		outstr += "\t\tint nbrInputArgs = "+ str(len(self.inputblocks)) +"; \n\t\tint nbrOutputArgs = "+ str(len(self.outputblocks)) +";\n"
		outstr += "\t\tdouble outputArgs["+ str(len(self.outputblocks)) +"] = {"
		for block in range(len(self.outputblocks)-1):
			outstr += "0.0,"
		outstr += "0.0};\n"

		outstr += "\t\tprintf(\"%s\\n\", getControllerOutput(nbrInputArgs, "+ self.modelname + "_node.inputArgs, nbrOutputArgs, outputArgs));\n"
		outstr += "\t\t"+ self.modelname + "_node.publishData(nbrOutputArgs, outputArgs);\n"
	
		outstr += "\t\tros::spinOnce();\n \t\tloop_rate.sleep();\n \t} \n"
	 	outstr += "\tperformCleanup();\n"
		outstr += "\treturn 0; \n} \n"
		return outstr
	
	def writeout(self, writefilename):
		d = os.path.dirname(writefilename)
		if not os.path.exists(d):
			os.makedirs(d)
		f = open(writefilename, 'w')
		f.write(self.generateHeaders())
		f.write(self.generateConstructorCode())
		f.write(self.generateCallbackCode())
		f.write(self.generatePublishFunction())
		f.write(self.generateClassFooter())
		f.write(self.generateMainRoutine())	
		print "==== ROS Wrapper " + writefilename +" generated"
		f.close()

	def genNoSpaceVariables(self):
		self.inputblocks_write = []
		for inp in self.inputblocks:
			self.inputblocks_write.append(string.replace(inp, " ", ""))
		self.outputblocks_write = []
		for inp in self.outputblocks:
			self.outputblocks_write.append(string.replace(inp, " ", ""))

	def genUnderlineVariables(self):
		self.inputblocks_write = []
		for inp in self.inputblocks:
			self.inputblocks_write.append(string.replace(inp, " ", "_"))
		self.outputblocks_write = []
		for inp in self.outputblocks:
			self.outputblocks_write.append(string.replace(inp, " ", "_"))

	def FillAndWriteTemplates(self, templatepath, resultfile):
		d = os.path.dirname(resultfile)
		if not os.path.exists(d):
			os.makedirs(d)
		template_values = { 'inputblocks':self.inputblocks_write, 'numofinputs': len(self.inputblocks_write),'outputblocks':self.outputblocks_write, 'numofoutputs': len(self.outputblocks_write), 'simulinkname':self.modelname}
		tmpl = Template( file = templatepath, searchList = (template_values,) )
		f = open(resultfile, 'w')
		f.write(str(tmpl))
		f.close()


if __name__ == "__main__":
	if(len(sys.argv) >= 2):
		man = mdlfilemanager()
		pkgloc = subprocess.Popen(["rospack", "find", sys.argv[1]], stdout=subprocess.PIPE).communicate()[0]
		if(pkgloc != ""):
			man.load(pkgloc.rstrip()+"/simulink/"+sys.argv[1]+".mdl")
			
			man.printout()
#			man.writeout(pkgloc.rstrip()+"/ros/roswrapper.cpp")
			man.genUnderlineVariables()
			man.FillAndWriteTemplates(roslib.packages.get_pkg_dir("ros_simulink")+"/files/roswrapper.cpp.template", pkgloc.rstrip()+"/ros/roswrapper.cpp")
			if(len(sys.argv) == 3):
				man.FillAndWriteTemplates(roslib.packages.get_pkg_dir("ros_simulink")+"/files/roswrapper.cpp.template", sys.argv[2]+"/ros/roswrapper.cpp")
			print "==== ROS Wrapper " + pkgloc.rstrip()+"/ros/roswrapper.cpp" +" generated"

			man.genNoSpaceVariables()
			man.FillAndWriteTemplates(roslib.packages.get_pkg_dir("ros_simulink")+"/files/grt_main.c.template", pkgloc.rstrip()+"/rtw/grt_main.c")
			if(len(sys.argv) == 3):
				man.FillAndWriteTemplates(roslib.packages.get_pkg_dir("ros_simulink")+"/files/grt_main.c.template", sys.argv[2]+"/rtw/grt_main.c")
			print "Simulink wrapper generated"
			
		
