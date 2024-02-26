if(NOT FLEX_FOUND)
  message(FATAL_ERROR "没有找到 Flex ！")
endif()

flex_target(
  task1 ${CMAKE_CURRENT_SOURCE_DIR}/lex.l ${CMAKE_CURRENT_BINARY_DIR}/lex.l.cc
  COMPILE_FLAGS ""
  DEFINES_FILE ${CMAKE_CURRENT_BINARY_DIR}/lex.l.hh)

file(GLOB _src *.cpp *.hpp *.c *.h)
add_executable(task1 ${_src} ${FLEX_task1_OUTPUTS} ${FLEX_task1_OUTPUT_HEADER})

target_include_directories(task1 PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
                                         ${CMAKE_CURRENT_BINARY_DIR})
