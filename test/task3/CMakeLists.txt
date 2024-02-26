file(REAL_PATH ../rtlib _rtlib_dir)
file(REAL_PATH ../task0 _task0_out BASE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
file(REAL_PATH ../task2 _task2_out BASE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

# 生成实验的全部答案
add_custom_target(
  task3-answer
  bash ${CMAKE_CURRENT_SOURCE_DIR}/answer.sh ${CLANG_EXECUTABLE} ${_rtlib_dir}
  ${TEST_CASES_DIR} ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES answer.sh)

# 生成测例权重文件
if(NOT TASK3_CASES_WEIGHT_TXT)
  set(_weight_txt ${CMAKE_CURRENT_BINARY_DIR}/weight.txt)
  string(REPLACE ";" "\n" _lines "${TEST_CASES}")
  file(WRITE ${_weight_txt} "${_lines}")
  set(TASK3_CASES_WEIGHT_TXT ${_weight_txt})
endif()

# 对实验进行评分
add_custom_target(
  task3-score
  COMMAND
    ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py ${CTEST_COMMAND}
    ${CMAKE_CURRENT_BINARY_DIR} ${TASK3_CASES_WEIGHT_TXT}
    ${CLANG_PLUS_EXECUTABLE} ${_rtlib_path} 10
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES score.py)

add_dependencies(task3-score task3 task3-answer test-rtlib)

# 为每个测例创建一个测试
if(TASK3_REVIVE)
  # 如果启用复活，则将前一个实验的标准答案作为输入
  add_dependencies(task3-score task2-answer)

  foreach(_case ${TEST_CASES})
    set(_output_dir ${CMAKE_CURRENT_BINARY_DIR}/${_case})
    file(MAKE_DIRECTORY ${_output_dir})
    add_test(NAME task3/${_case}
             COMMAND task3 ${_task2_out}/${_case}/answer.json
                     ${_output_dir}/output.ll)
  endforeach()

  message(AUTHOR_WARNING "在实验三复活：请在构建 task2-answer 后再使用 task3 的测试项目。")

else()
  # 否则以实验零的标准答案作为输入
  add_dependencies(task3-score task0-answer)

  foreach(_case ${TEST_CASES})
    set(_output_dir ${CMAKE_CURRENT_BINARY_DIR}/${_case})
    file(MAKE_DIRECTORY ${_output_dir})
    add_test(NAME task3/${_case} COMMAND task3 ${_task0_out}/${_case}
                                         ${_output_dir}/output.ll)
  endforeach()

  message(AUTHOR_WARNING "实验三复活已禁用，请在构建 task0-answer 后再使用 task3 的测试项目。")

endif()
