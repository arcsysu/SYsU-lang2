cmake_minimum_required(VERSION 3.20)

include(config.cmake)
project(SYsU-lang VERSION 2.0.0.0)
include(CTest)

# 语言标准
set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED TRUE)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

# 任务
add_subdirectory(task)

# 评测
add_subdirectory(test)
