file(REAL_PATH ../rtlib _rtlib_dir)
file(REAL_PATH ../task0 _task0_out BASE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

# 生成实验的全部答案
add_custom_target(
  task1-answer
  bash ${CMAKE_CURRENT_SOURCE_DIR}/answer.sh ${CLANG_EXECUTABLE} ${_rtlib_dir}
  ${_task0_out} ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES answer.sh)

# 生成测例权重文件
if(NOT TASK1_CASES_WEIGHT_TXT)
  set(_weight_txt ${CMAKE_CURRENT_BINARY_DIR}/weight.txt)
  string(REPLACE ";" "\n" _lines "${TEST_CASES}")
  file(WRITE ${_weight_txt} "${_lines}")
  set(TASK1_CASES_WEIGHT_TXT ${_weight_txt})
endif()

# 对实验进行评分
add_custom_target(
  task1-score
  COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/score.py
          ${CTEST_COMMAND} ${CMAKE_CURRENT_BINARY_DIR} ${TASK1_CASES_WEIGHT_TXT}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  USES_TERMINAL
  SOURCES score.py)

add_dependencies(task1-score task1 task1-answer task0-answer)

# 为每个测例创建一个测试
foreach(_case ${TEST_CASES})
  set(_output_dir ${CMAKE_CURRENT_BINARY_DIR}/${_case})
  file(MAKE_DIRECTORY ${_output_dir})
  add_test(NAME task1/${_case} COMMAND task1 ${_task0_out}/${_case}
                                       ${_output_dir}/output.txt)
endforeach()

message(AUTHOR_WARNING "请在构建 task0-answer 后再使用 task1 的测试项目。")
