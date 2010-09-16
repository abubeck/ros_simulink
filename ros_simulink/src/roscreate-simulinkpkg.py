#!/usr/bin/python
import sys
import os
import roslib
from ros import roscreate
from roscreate.core import read_template, author_name, on_ros_path
from Cheetah.Template import Template

if __name__ == "__main__":
	packagename = sys.argv[1]
	print "creating ros package"
	depends = ["ros_simulink"]
	roscreate.roscreatepkg.create_package(packagename, author_name(), depends, uses_roscpp=True, uses_rospy=True)
	print "creating folder structure"
	os.mkdir(packagename+"/simulink")
	os.mkdir(packagename+"/ros")
	os.mkdir(packagename+"/rtw")
	print "generating configured mdl file"
	template_values = {'simulinkname': packagename}
	tmpl = Template( file = roslib.packages.get_pkg_dir("ros_simulink")+"/files/configured_mdl_file.template", searchList = (template_values,) )
	filename = packagename+"/simulink/"+packagename+".mdl"
	f = open(filename, 'w')
	f.write(str(tmpl))
	f.close()
	print "finished. Now start a rosmatlab session and use 'rosrun ros_simulink load "+packagename+"' to load the simulink model"
