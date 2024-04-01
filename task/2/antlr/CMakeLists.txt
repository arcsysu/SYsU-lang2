if(NOT antlr4-runtime_FOUND OR NOT antlr4-generator_FOUND)
  message(FATAL_ERROR "未找到 ANTLR4 ！")
endif()

antlr4_generate(
  task2-antlr # 唯一标识名
  ${CMAKE_CURRENT_SOURCE_DIR}/SYsUParser.g4 # 输入文件
  PARSER # 生成类型：LEXER/PARSER/BOTH
  FALSE # 是否生成 listener
  FALSE # 是否生成 visitor
  "" # C++ 命名空间
)

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/SYsULexer.tokens.hpp
  COMMAND
    ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/SYsULexer.py
    ${CMAKE_CURRENT_SOURCE_DIR}/SYsULexer.tokens
    ${CMAKE_CURRENT_BINARY_DIR}/SYsULexer.tokens.hpp SYsULexerTokens
  MAIN_DEPENDENCY ${CMAKE_CURRENT_SOURCE_DIR}/SYsULexer.py
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/SYsULexer.tokens
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

file(GLOB _common_src ../common/*)
file(GLOB _src *.cpp *.hpp *.c *.h)
add_executable(task2 ${_common_src} ${_src} ${ANTLR4_SRC_FILES_task2-antlr}
                     ${CMAKE_CURRENT_BINARY_DIR}/SYsULexer.tokens.hpp)

target_include_directories(
  task2 PRIVATE . ../common ${ANTLR4_INCLUDE_DIR_task2-antlr}
                ${CMAKE_CURRENT_BINARY_DIR})
target_include_directories(task2 SYSTEM PRIVATE ${ANTLR4_INCLUDE_DIR}
                                                ${LLVM_INCLUDE_DIRS})

target_link_libraries(task2 antlr4_static ${LLVM_LIBS})
