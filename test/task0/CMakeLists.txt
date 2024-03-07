file(REAL_PATH ../cases _cases_dir)
file(REAL_PATH ../rtlib _rtlib_dir)

# 生成测例表
set(TASK0_CASES_TXT ${CMAKE_CURRENT_BINARY_DIR}/cases.txt)
string(REPLACE ";" "\n" _lines "${TEST_CASES}")
file(WRITE ${TASK0_CASES_TXT} "${_lines}")

# 生成实验零的全部答案（预处理的结果）
add_custom_target(
  task0-answer
  ${Python3_EXECUTABLE}
  ${CMAKE_CURRENT_SOURCE_DIR}/answer.py
  ${TEST_CASES_DIR}
  ${CMAKE_CURRENT_BINARY_DIR}
  ${TASK0_CASES_TXT}
  ${CLANG_EXECUTABLE}
  ${_rtlib_dir}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES answer.py)

# 对实验进行评分
add_custom_target(
  task0-score
  ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py
  ${CMAKE_CURRENT_BINARY_DIR} $<TARGET_FILE:task0>
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES score.py)

add_dependencies(task0-score task0)
