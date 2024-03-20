file(REAL_PATH ../rtlib _rtlib_dir)
file(REAL_PATH ../task0 _task0_out BASE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
file(REAL_PATH ../task1 _task1_out BASE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

# 生成测例表
if(NOT TASK2_CASES_TXT)
  set(_task2_cases "")
  foreach(_case ${TEST_CASES})
    if(NOT _case MATCHES ${TASK2_EXCLUDE_REGEX})
      list(APPEND _task2_cases ${_case})
    endif()
  endforeach()
  set(TASK2_CASES_TXT ${CMAKE_CURRENT_BINARY_DIR}/cases.txt)
  string(REPLACE ";" "\n" _lines "${_task2_cases}")
  file(WRITE ${TASK2_CASES_TXT} "${_lines}")
else()
  exec_program(
    ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/..
    ARGS common.py ${TEST_CASES_DIR} ${CMAKE_CURRENT_BINARY_DIR}
         ${TASK2_CASES_TXT}
    OUTPUT_VARIABLE _task2_cases)
endif()

# 生成全部答案
add_custom_target(
  task2-answer
  ${Python3_EXECUTABLE}
  ${CMAKE_CURRENT_SOURCE_DIR}/answer.py
  ${_task0_out}
  ${CMAKE_CURRENT_BINARY_DIR}
  ${TASK2_CASES_TXT}
  ${CLANG_EXECUTABLE}
  ${_rtlib_dir}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES answer.py)

add_dependencies(task2-answer task0-answer)

# 对实验进行评分
add_custom_target(
  task2-score
  COMMAND
    ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py ${TEST_CASES_DIR}
    ${CMAKE_CURRENT_BINARY_DIR} ${TASK2_CASES_TXT} ${CTEST_COMMAND}
    ${TASK2_LOG_LEVEL}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES score.py)

add_dependencies(task2-score task2 task2-answer)

# 为每个测例创建一个测试和评分
if(TASK2_REVIVE)
  # 如果启用复活，则将前一个实验的标准答案作为输入
  add_dependencies(task2-score task1-answer)

  foreach(_case ${_task2_cases})
    set(_output_dir ${CMAKE_CURRENT_BINARY_DIR}/${_case})
    file(MAKE_DIRECTORY ${_output_dir})
    add_test(NAME task2/${_case}
             COMMAND task2 ${_task1_out}/${_case}/answer.txt
                     ${_output_dir}/output.json)
    add_test(
      NAME test2/${_case}
      COMMAND
        ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py
        ${TEST_CASES_DIR} ${CMAKE_CURRENT_BINARY_DIR} ${TASK2_CASES_TXT}
        ${CTEST_COMMAND} ${TASK2_LOG_LEVEL} --single ${_case})
  endforeach()

  message(AUTHOR_WARNING "在实验二复活：请在构建 task1-answer 后再使用 task2 的测试项目。")

else()
  # 否则以实验零的标准答案作为输入
  add_dependencies(task2-score task0-answer)

  foreach(_case ${_task2_cases})
    set(_output_dir ${CMAKE_CURRENT_BINARY_DIR}/${_case})
    file(MAKE_DIRECTORY ${_output_dir})
    add_test(NAME task2/${_case} COMMAND task2 ${_task0_out}/${_case}
                                         ${_output_dir}/output.json)
    add_test(
      NAME test2/${_case}
      COMMAND
        ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py
        ${TEST_CASES_DIR} ${CMAKE_CURRENT_BINARY_DIR} ${TASK2_CASES_TXT}
        ${CTEST_COMMAND} ${TASK2_LOG_LEVEL} --single ${_case})
  endforeach()

  message(AUTHOR_WARNING "实验二复活已禁用，请在构建 task0-answer 后再使用 task2 的测试项目。")

endif()
