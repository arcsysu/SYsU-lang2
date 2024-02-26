file(REAL_PATH ../rtlib _rtlib_dir)
file(REAL_PATH ../task0 _task0_out BASE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
file(REAL_PATH ../task3 _task3_out BASE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

# 生成实验的全部答案
add_custom_target(
  task4-answer
  bash ${CMAKE_CURRENT_SOURCE_DIR}/answer.sh ${CLANG_EXECUTABLE} ${_rtlib_dir}
  ${TEST_CASES_DIR} ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES answer.sh)

# 生成测例权重文件
if(NOT TASK4_CASES_WEIGHT_TXT)
  set(_weight_txt ${CMAKE_CURRENT_BINARY_DIR}/weight.txt)
  string(REPLACE ";" "\n" _lines "${TEST_CASES}")
  file(WRITE ${_weight_txt} "${_lines}")
  set(TASK4_CASES_WEIGHT_TXT ${_weight_txt})
endif()

# 对实验进行评分
add_custom_target(
  task4-score
  COMMAND
    ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py ${CTEST_COMMAND}
    ${CMAKE_CURRENT_BINARY_DIR} ${TASK4_CASES_WEIGHT_TXT}
    ${CLANG_PLUS_EXECUTABLE} ${_rtlib_path} 10
  USES_TERMINAL
  SOURCES score.py)

add_dependencies(task4-score task4 task4-answer test-rtlib)

# 为每个测例创建一个测试
if(TASK4_REVIVE)
  # 如果启用复活，则将前一个实验的标准答案作为输入
  add_dependencies(task4-score task3-answer)

  foreach(_case ${TEST_CASES})
    set(_output_dir ${CMAKE_CURRENT_BINARY_DIR}/${_case})
    file(MAKE_DIRECTORY ${_output_dir})
    add_test(NAME task4/${_case} COMMAND task4 ${_task3_out}/${_case}/answer.ll
                                         ${_output_dir}/output.ll)
  endforeach()

  message(AUTHOR_WARNING "在实验四复活：请在构建 task3-answer 后再使用 task4 的测试项目。")

else()
  # 否则以实验零的标准答案作为输入
  add_dependencies(task4-score task0-answer)

  foreach(_case ${TEST_CASES})
    set(_output_dir ${CMAKE_CURRENT_BINARY_DIR}/${_case})
    file(MAKE_DIRECTORY ${_output_dir})
    add_test(NAME task4/${_case} COMMAND task3 ${_task0_out}/${_case}
                                         ${_output_dir}/output.ll)
  endforeach()

  message(AUTHOR_WARNING "实验四复活已禁用，请在构建 task0-answer 后再使用 task4 的测试项目。")

endif()
