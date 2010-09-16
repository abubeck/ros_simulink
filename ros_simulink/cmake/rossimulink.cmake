#IF(NOT DEFINED $ENV{MATLAB_ROOT_PATH})
#	MESSAGE(ERROR "=========== MATLAB_ROOT_PATH ENV VARIABLE NOT AVAILABLE !!! =========== ")
#  MESSAGE(FATAL_ERROR "=========== Set with: export MATLAB_ROOT_PATH=<path to matlab root>  =========== ")
#ENDIF(NOT DEFINED $ENV{MATLAB_ROOT_PATH})


macro(gen_simulink_bin BIN_NAME MDLFILE)
 ADD_CUSTOM_COMMAND(
 	OUTPUT ${PROJECT_SOURCE_DIR}/ros/roswrapper.cpp ${PROJECT_SOURCE_DIR}/rtw/grt_main.c
 	COMMAND rosrun ros_simulink mdlfilemanager.py ${PROJECT_NAME} ${CMAKE_CURRENT_BINARY_DIR}
 	DEPENDS ${PROJECT_SOURCE_DIR}/${MDLFILE}
 )

 ADD_CUSTOM_COMMAND(
 	OUTPUT ${PROJECT_SOURCE_DIR}/rtw/${PROJECT_NAME}_grt_rtw/${PROJECT_NAME}.cpp ${PROJECT_SOURCE_DIR}/rtw/${PROJECT_NAME}_grt_rtw/${PROJECT_NAME}_capi.cpp ${PROJECT_SOURCE_DIR}/rtw/${PROJECT_NAME}_grt_rtw/${PROJECT_NAME}_data.cpp ${PROJECT_SOURCE_DIR}/rtw/${PROJECT_NAME}_grt_rtw/rtGetInf.cpp  ${PROJECT_SOURCE_DIR}/rtw/${PROJECT_NAME}_grt_rtw/rtGetNaN.cpp ${PROJECT_SOURCE_DIR}/rtw/${PROJECT_NAME}_grt_rtw/rt_nonfinite.cpp 
 	COMMAND rosrun ros_simulink compile  ${PROJECT_NAME}
 	DEPENDS ${PROJECT_SOURCE_DIR}/${MDLFILE}
 )

 INCLUDE_DIRECTORIES($ENV{MATLAB_ROOT_PATH}/rtw/c/src/)
 INCLUDE_DIRECTORIES($ENV{MATLAB_ROOT_PATH}/rtw/c/src/ext_mode/common/)
 INCLUDE_DIRECTORIES($ENV{MATLAB_ROOT_PATH}/extern/include/)
 INCLUDE_DIRECTORIES($ENV{MATLAB_ROOT_PATH}/simulink/include/)

 INCLUDE_DIRECTORIES(${PROJECT_SOURCE_DIR}/rtw/${PROJECT_NAME}_grt_rtw/)

 rosbuild_add_library(simulink_gen
   rtw/${PROJECT_NAME}_grt_rtw/${PROJECT_NAME}.cpp 
   rtw/${PROJECT_NAME}_grt_rtw/${PROJECT_NAME}_capi.cpp 
#   rtw/${PROJECT_NAME}_grt_rtw/${PROJECT_NAME}_data.cpp 
   rtw/${PROJECT_NAME}_grt_rtw/rtGetInf.cpp 
   rtw/${PROJECT_NAME}_grt_rtw/rtGetNaN.cpp 
   rtw/${PROJECT_NAME}_grt_rtw/rt_nonfinite.cpp
   $ENV{MATLAB_ROOT_PATH}/rtw/c/src/rt_logging.c 
   $ENV{MATLAB_ROOT_PATH}/rtw/c/src/rt_logging_mmi.c 
   $ENV{MATLAB_ROOT_PATH}/rtw/c/src/rtw_modelmap_utils.c 
   $ENV{MATLAB_ROOT_PATH}/rtw/c/src/rt_sim.c 
   $ENV{MATLAB_ROOT_PATH}/rtw/c/src/ode3.c
   rtw/grt_main.c
   )

 rosbuild_add_compile_flags(simulink_gen -DUSE_RTMODEL -O0 -ffloat-store -fPIC -m32 -DMODEL=cob_testslinkcontroller -DRT -DNUMST=2 -DTID01EQ=1 -DNCSTATES=1 -DUNIX -DMT=0 -DHAVESTDIO -DUSE_GENERATED_SOLVER -URT_MALLOC)

 rosbuild_add_executable(${BIN_NAME} ros/roswrapper.cpp)
 target_link_libraries(${BIN_NAME} simulink_gen)
endmacro(gen_simulink_bin)


