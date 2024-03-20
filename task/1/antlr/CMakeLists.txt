if(NOT antlr4-runtime_FOUND OR NOT antlr4-generator_FOUND)
  message(FATAL_ERROR "未找到 ANTLR4 ！")
endif()

antlr4_generate(
  task1-antlr # 唯一标识名
  ${CMAKE_CURRENT_SOURCE_DIR}/SYsULexer.g4 # 输入文件
  LEXER # 生成类型：LEXER/PARSER/BOTH
  FALSE # 是否生成 listener
  FALSE # 是否生成 visitor
  "" # C++ 命名空间
)

file(GLOB _src *.cpp *.hpp *.c *.h)
add_executable(task1 ${_src} ${ANTLR4_SRC_FILES_task1-antlr})

target_include_directories(task1 PRIVATE . ${ANTLR4_INCLUDE_DIR_task1-antlr})
target_include_directories(task1 SYSTEM PRIVATE ${ANTLR4_INCLUDE_DIR})

target_link_libraries(task1 antlr4_static)
