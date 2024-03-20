file(REAL_PATH ../rtlib _rtlib_dir)
file(REAL_PATH ../task0 _task0_out BASE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

# 生成测例表
if(NOT TASK1_CASES_TXT)
  set(_task1_cases "")
  foreach(_case ${TEST_CASES})
    if(NOT _case MATCHES ${TASK1_EXCLUDE_REGEX})
      list(APPEND _task1_cases ${_case})
    endif()
  endforeach()
  set(TASK1_CASES_TXT ${CMAKE_CURRENT_BINARY_DIR}/cases.txt)
  string(REPLACE ";" "\n" _lines "${_task1_cases}")
  file(WRITE ${TASK1_CASES_TXT} "${_lines}")
else()
  exec_program(
    ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/..
    ARGS common.py ${TEST_CASES_DIR} ${CMAKE_CURRENT_BINARY_DIR}
         ${TASK1_CASES_TXT}
    OUTPUT_VARIABLE _task1_cases)
endif()

# 生成全部答案
add_custom_target(
  task1-answer
  ${Python3_EXECUTABLE}
  ${CMAKE_CURRENT_SOURCE_DIR}/answer.py
  ${_task0_out} # 传入 task0 的输出目录，而不是 TEST_CASES_DIR
  ${CMAKE_CURRENT_BINARY_DIR}
  ${TASK1_CASES_TXT}
  ${CLANG_EXECUTABLE}
  ${_rtlib_dir}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES answer.py)

add_dependencies(task1-answer task0-answer)

# 对实验进行评分
add_custom_target(
  task1-score
  COMMAND
    ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py ${TEST_CASES_DIR}
    ${CMAKE_CURRENT_BINARY_DIR} ${TASK1_CASES_TXT} ${CTEST_COMMAND}
    ${TASK1_LOG_LEVEL}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES score.py)

add_dependencies(task1-score task1 task1-answer)

# 为每个测例创建一个测试和评分
foreach(_case ${_task1_cases})
  set(_output_dir ${CMAKE_CURRENT_BINARY_DIR}/${_case})
  file(MAKE_DIRECTORY ${_output_dir})
  add_test(NAME task1/${_case} COMMAND task1 ${_task0_out}/${_case}
                                       ${_output_dir}/output.txt)
  add_test(
    NAME test1/${_case}
    COMMAND
      ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py
      ${TEST_CASES_DIR} ${CMAKE_CURRENT_BINARY_DIR} ${TASK1_CASES_TXT}
      ${CTEST_COMMAND} ${TASK1_LOG_LEVEL} --single ${_case})
endforeach()

message(AUTHOR_WARNING "请在构建 task0-answer 后再使用 task1 的测试项目。")
