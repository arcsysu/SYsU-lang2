find_package(
  Python3
  COMPONENTS Interpreter
  REQUIRED)

file(
  GLOB_RECURSE
  _rtlib_src
  rtlib/*.cc
  rtlib/*.cpp
  rtlib/*.c
  rtlib/*.hh
  rtlib*.hpp
  rtlib/*.h)
add_library(test-rtlib STATIC ${_rtlib_src})
target_include_directories(test-rtlib PUBLIC rtlib/include)
set(_rtlib_path ${CMAKE_CURRENT_BINARY_DIR})

file(REAL_PATH ${CMAKE_COMMAND}/../ctest CTEST_COMMAND)
if(NOT EXISTS ${CTEST_COMMAND})
  message(FATAL_ERROR "未找到 CTest 命令，请检查 CMake 是否正确安装。")
endif()

# 搜索所有测例
set(TEST_CASES_DIR ${CMAKE_CURRENT_SOURCE_DIR}/cases)
file(
  GLOB_RECURSE TEST_CASES
  RELATIVE ${TEST_CASES_DIR}
  "${TEST_CASES_DIR}/*.sysu.c")

add_subdirectory(task0)
add_subdirectory(task1)
add_subdirectory(task2)
add_subdirectory(task3)
add_subdirectory(task4)
