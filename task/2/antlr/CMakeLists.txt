if(NOT antlr4-runtime_FOUND OR NOT antlr4-generator_FOUND)
  message(FATAL_ERROR "未找到 ANTLR4 ！")
endif()

antlr4_generate(
  task2-antlr # 唯一标识名
  ${CMAKE_CURRENT_SOURCE_DIR}/SYsU_lang.g4 # 输入文件
  BOTH # 生成类型：LEXER/PARSER/BOTH
  TRUE # 是否生成 listener
  TRUE # 是否生成 visitor
  "" # C++ 命名空间
)

file(GLOB _common_src ../common/*)
file(GLOB _src *.cpp *.hpp *.c *.h)
add_executable(task2 ${_common_src} ${_src} ${ANTLR4_SRC_FILES_task2-antlr})

target_include_directories(task2 PRIVATE . ../common
                                         ${ANTLR4_INCLUDE_DIR_task2-antlr})
target_include_directories(task2 SYSTEM PRIVATE ${ANTLR4_INCLUDE_DIR}
                                                ${LLVM_INCLUDE_DIRS})

target_link_libraries(task2 antlr4_static ${LLVM_LIBS})
