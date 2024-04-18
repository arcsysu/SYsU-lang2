file(REAL_PATH ../rtlib _rtlib_dir)
file(REAL_PATH ../task0 _task0_out BASE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
file(REAL_PATH ../task2 _task2_out BASE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

# 生成测例表
if(NOT TASK3_CASES_TXT)
  set(_task3_cases "")
  foreach(_case ${TEST_CASES})
    if(NOT _case MATCHES ${TASK3_EXCLUDE_REGEX})
      list(APPEND _task3_cases ${_case})
    endif()
  endforeach()
  set(TASK3_CASES_TXT ${CMAKE_CURRENT_BINARY_DIR}/cases.txt)
  string(REPLACE ";" "\n" _lines "${_task3_cases}")
  file(WRITE ${TASK3_CASES_TXT} "${_lines}")
else()
  exec_program(
    ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/..
    ARGS common.py ${TEST_CASES_DIR} ${CMAKE_CURRENT_BINARY_DIR}
         ${TASK3_CASES_TXT}
    OUTPUT_VARIABLE _task3_cases)
endif()

# 生成全部答案
add_custom_target(
  task3-answer
  ${Python3_EXECUTABLE}
  ${CMAKE_CURRENT_SOURCE_DIR}/answer.py
  ${TEST_CASES_DIR}
  ${CMAKE_CURRENT_BINARY_DIR}
  ${TASK3_CASES_TXT}
  ${CLANG_EXECUTABLE}
  ${_rtlib_dir}
  ${TEST_RTLIB_SO}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES answer.py)

add_dependencies(task3-answer task0-answer test-rtlib)

# 对实验进行评分
add_custom_target(
  task3-score
  COMMAND
    ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py ${TEST_CASES_DIR}
    ${CMAKE_CURRENT_BINARY_DIR} ${TASK3_CASES_TXT} ${CTEST_COMMAND}
    ${CLANG_PLUS_EXECUTABLE} ${TEST_RTLIB_SO}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES score.py)

add_dependencies(task3-score task3 task3-answer test-rtlib)

# 为每个测例创建一个测试
if(TASK3_REVIVE)
  # 如果启用复活，则将前一个实验的标准答案作为输入
  add_dependencies(task3-score task2-answer)

  foreach(_case ${_task3_cases})
    set(_output_dir ${CMAKE_CURRENT_BINARY_DIR}/${_case})
    file(MAKE_DIRECTORY ${_output_dir})
    add_test(NAME task3/${_case}
             COMMAND task3 ${_task2_out}/${_case}/answer.json
                     ${_output_dir}/output.ll)
    add_test(
      NAME test3/${_case}
      COMMAND
        ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py
        ${TEST_CASES_DIR} ${CMAKE_CURRENT_BINARY_DIR} ${TASK3_CASES_TXT}
        ${CTEST_COMMAND} ${CLANG_PLUS_EXECUTABLE} ${TEST_RTLIB_SO} --single
        ${_case})
  endforeach()

  message(AUTHOR_WARNING "在实验三复活：请在构建 task2-answer 后再使用 task3 的测试项目。")

else()
  # 否则以实验零的标准答案作为输入
  add_dependencies(task3-score task0-answer)

  foreach(_case ${_task3_cases})
    set(_output_dir ${CMAKE_CURRENT_BINARY_DIR}/${_case})
    file(MAKE_DIRECTORY ${_output_dir})
    add_test(NAME task3/${_case} COMMAND task3 ${_task0_out}/${_case}
                                         ${_output_dir}/output.ll)
    add_test(
      NAME test3/${_case}
      COMMAND
        ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py
        ${TEST_CASES_DIR} ${CMAKE_CURRENT_BINARY_DIR} ${TASK3_CASES_TXT}
        ${CTEST_COMMAND} ${CLANG_PLUS_EXECUTABLE} ${TEST_RTLIB_SO} --single
        ${_case})
  endforeach()

  message(AUTHOR_WARNING "实验三复活已禁用，请在构建 task0-answer 后再使用 task3 的测试项目。")

endif()
