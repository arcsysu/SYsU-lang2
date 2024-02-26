if(NOT FLEX_FOUND)
  message(FATAL_ERROR "没有找到 Flex ！")
endif()
if(NOT BISON_FOUND)
  message(FATAL_ERROR "没有找到 Bison ！")
endif()

flex_target(
  task2 ${CMAKE_CURRENT_SOURCE_DIR}/lex.l ${CMAKE_CURRENT_BINARY_DIR}/lex.l.cc
  COMPILE_FLAGS ""
  DEFINES_FILE ${CMAKE_CURRENT_BINARY_DIR}/lex.l.hh)

bison_target(
  task2 ${CMAKE_CURRENT_SOURCE_DIR}/par.y ${CMAKE_CURRENT_BINARY_DIR}/par.y.cc
  DEFINES_FILE ${CMAKE_CURRENT_BINARY_DIR}/par.y.hh)

file(GLOB _common_src ../common/*)
file(GLOB _src *.cpp *.hpp *.c *.h)
add_executable(task2 ${_common_src} ${_src} ${FLEX_task2_OUTPUTS}
                     ${FLEX_task2_OUTPUT_HEADER} ${BISON_task2_OUTPUTS})

target_include_directories(task2 PRIVATE . ../common
                                         ${CMAKE_CURRENT_BINARY_DIR})
target_include_directories(task2 SYSTEM PRIVATE ${LLVM_INCLUDE_DIRS})

target_link_libraries(task2 antlr4_static ${LLVM_LIBS})
