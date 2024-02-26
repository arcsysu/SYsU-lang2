file(REAL_PATH ../cases _cases_dir)
file(REAL_PATH ../rtlib _rtlib_dir)

# 生成实验零的全部答案（预处理的结果）
add_custom_target(
  task0-answer
  bash ${CMAKE_CURRENT_SOURCE_DIR}/answer.sh ${CLANG_EXECUTABLE} ${_rtlib_dir}
  ${_cases_dir} ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES answer.sh)

# 创建输出目录
file(
  GLOB_RECURSE _cases
  RELATIVE ${_cases_dir}
  ${_cases_dir}/*.sysu.c)
foreach(_case ${_cases})
  set(_output_dir ${CMAKE_CURRENT_BINARY_DIR}/${_case})
  cmake_path(GET _output_dir PARENT_PATH _parent_dir)
  file(MAKE_DIRECTORY ${_parent_dir})
endforeach()

# 对实验进行评分
add_custom_target(
  task0-score
  ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py
  ${CMAKE_CURRENT_BINARY_DIR} $<TARGET_FILE:task0>
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES score.py)

add_dependencies(task0-score task0)
