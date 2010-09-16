cmake_minimum_required(VERSION 2.4.6)
include($ENV{ROS_ROOT}/core/rosbuild/rosbuild.cmake)

# Set the build type.  Options are:
#  Coverage       : w/ debug symbols, w/o optimization, w/ code-coverage
#  Debug          : w/ debug symbols, w/o optimization
#  Release        : w/o debug symbols, w/ optimization
#  RelWithDebInfo : w/ debug symbols, w/ optimization
#  MinSizeRel     : w/o debug symbols, w/ optimization, stripped binaries
#set(ROS_BUILD_TYPE RelWithDebInfo)

rosbuild_init()

#set the default path for built executables to the "bin" directory
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
#set the default path for built libraries to the "lib" directory
set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)

#INCLUDE_DIRECTORIES(/media/Daten/matlab2008/extern/include/)
#LINK_DIRECTORIES(/media/Daten/matlab2008/bin/glnx86/)

add_jar_dir(lib)
add_jar_dir("/usr/share/java/")
add_java_source_dir(${PROJECT_SOURCE_DIR}/src)
rospack_add_java_executable(rosmatlab rosmatlab matlabinterface MatlabRequestProcessorFactoryFactory)
#javac -classpath lib/matlabcontrol-3.1.0.jar:/usr/share/java/* -d bin/ src/MatlabRequestProcessorFactoryFactory.java src/matlabinterface.java src/rosmatlab.java

#uncomment if you have defined messages
rosbuild_genmsg()
#uncomment if you have defined services
rosbuild_gensrv()



#common commands for building c++ executables and libraries
#rosbuild_add_library(${PROJECT_NAME} src/example.cpp)
#target_link_libraries(${PROJECT_NAME} another_library)
#rosbuild_add_boost_directories()
#rosbuild_link_boost(${PROJECT_NAME} thread)
#rosbuild_add_executable(rosmatlab src/rosmatlab.cpp)
#target_link_libraries(rosmatlab eng)
