file(
  GLOB_RECURSE
  _rtlib_src
  rtlib/*.cc
  rtlib/*.cpp
  rtlib/*.c)
set(TEST_RTLIB_SO ${CMAKE_CURRENT_BINARY_DIR}/libtest-rtlib.so)
add_custom_target(
  test-rtlib
  ${CLANG_PLUS_EXECUTABLE}
  -shared
  -fPIC
  -o
  ${TEST_RTLIB_SO}
  -I
  ${CMAKE_CURRENT_SOURCE_DIR}/rtlib/include
  ${_rtlib_src}
  SOURCES ${_rtlib_src})

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

# 生成全测例表
set(TEST_CASES_TXT ${CMAKE_CURRENT_BINARY_DIR}/cases.txt)
string(REPLACE ";" "\n" _lines "${TEST_CASES}")
file(WRITE ${TEST_CASES_TXT} "${_lines}")

add_subdirectory(task0)
add_subdirectory(task1)
add_subdirectory(task2)
add_subdirectory(task3)
add_subdirectory(task4)
