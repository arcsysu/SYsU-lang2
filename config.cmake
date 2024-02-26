# 你的学号
set(STUDENT_ID "0123456789")
# 你的姓名
set(STUDENT_NAME "某某某")

# 实验一的完成方式："flex"或"antlr"
set(TASK1_WITH "flex")

# 实验二的完成方式："bison"或"antlr"
set(TASK2_WITH "bison")
# 是否在实验二复活，ON或OFF
set(TASK2_REVIVE OFF)

# 是否在实验三复活，ON或OFF
set(TASK3_REVIVE OFF)

# 是否在实验四复活，ON或OFF
set(TASK4_REVIVE OFF)

################################################################################
## 以下内容为内部环境配置，一般情况下不需要学生修改，学生本地的修改对实验评测无影响。
################################################################################

# ANTLR4
if(DEFINED ENV{ANTLR_DIR})
    message("ANTLR目录为 $ENV{ANTLR_DIR}")
    set(antlr4-runtime_DIR
        "$ENV{ANTLR_DIR}/install/lib/cmake/antlr4-runtime")
    set(antlr4-generator_DIR
        "$ENV{ANTLR_DIR}/install/lib/cmake/antlr4-generator")
    set(ANTLR4_JAR_LOCATION "$ENV{ANTLR_DIR}/antlr-4.13.1-complete.jar")
else()
    message("ANTLR目录为 ${CMAKE_SOURCE_DIR}/antlr")
    set(antlr4-runtime_DIR
        "${CMAKE_SOURCE_DIR}/antlr/install/lib/cmake/antlr4-runtime")
    set(antlr4-generator_DIR
        "${CMAKE_SOURCE_DIR}/antlr/install/lib/cmake/antlr4-generator")
    set(ANTLR4_JAR_LOCATION "${CMAKE_SOURCE_DIR}/antlr/antlr-4.13.1-complete.jar")
endif()

# llvm clang
if(DEFINED ENV{LLVM_DIR})
    message("LLVM目录为 $ENV{LLVM_DIR}")
    set(LLVM_DIR "$ENV{LLVM_DIR}/install/lib/cmake/llvm")
    set(CLANG_EXECUTABLE "$ENV{LLVM_DIR}/install/bin/clang")
    set(CLANG_PLUS_EXECUTABLE "$ENV{LLVM_DIR}/install/bin/clang++")
else()
    message("LLVM目录为 ${CMAKE_SOURCE_DIR}/llvm")
    set(LLVM_DIR "${CMAKE_SOURCE_DIR}/llvm/install/lib/cmake/llvm")
    set(CLANG_EXECUTABLE "${CMAKE_SOURCE_DIR}/llvm/install/bin/clang")
    set(CLANG_PLUS_EXECUTABLE "${CMAKE_SOURCE_DIR}/llvm/install/bin/clang++")
endif()

# 测试运行时限（秒）
set(CTEST_TEST_TIMEOUT 3)

# 实验一测例权重文件
set(TASK1_CASES_WEIGHT_TXT "")

# 实验二测例权重文件
set(TASK2_CASES_WEIGHT_TXT "")

# 实验三测例权重文件
set(TASK3_CASES_WEIGHT_TXT "")

# 实验四测例权重文件
set(TASK4_CASES_WEIGHT_TXT "")
