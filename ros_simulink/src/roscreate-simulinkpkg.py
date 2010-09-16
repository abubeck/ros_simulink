import sys



if __name__ == "__main__":
	packagename = argv[0]
	sys.exec("roscreate_pkg packagename roscpp")
	sys.mkdir(packagename/simulink)
	sys.mkdir(packagename/ros)
	sys.mkdir(packagename/rtw)
