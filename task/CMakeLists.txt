find_package(FLEX 2.6)
find_package(BISON 3.8)

find_package(antlr4-runtime 4.13)
find_package(antlr4-generator 4.13)

find_package(LLVM 17 REQUIRED)
llvm_map_components_to_libnames(LLVM_LIBS core support transformutils irreader
                                passes)
# 如何列出所有的component：`llvm-config --components`

macro(add_task task)
  if(NOT STUDENT_ID STREQUAL "" OR NOT STUDENT_NAME STREQUAL "")
    configure_file(config-${task}.cmake.in
                   ${CMAKE_CURRENT_SOURCE_DIR}/${task}/config.cmake @ONLY)
  endif()
  add_subdirectory(${task})

  set(_student "${STUDENT_ID}-${STUDENT_NAME}")
  set(_out "${CMAKE_CURRENT_BINARY_DIR}/task${task}.${_student}.tar.xz")
  set(_msg "作业已打包，请提交 '${_out}' 到评测服务器。")

  add_custom_target(
    task${task}-pack
    COMMAND ${CMAKE_COMMAND} -E tar cvfJ ${_out}
            ${CMAKE_CURRENT_SOURCE_DIR}/${task}
    COMMAND echo ${_msg}
    COMMAND echo ${_msg}
    COMMAND echo ${_msg}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
endmacro()

add_task(0)
add_task(1)
add_task(2)
add_task(3)
add_task(4)
