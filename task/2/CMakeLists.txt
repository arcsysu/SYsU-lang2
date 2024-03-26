include(config.cmake)

if(TASK2_WITH STREQUAL "bison")
  message(AUTHOR_WARNING "使用 Bison 完成实验二")
  add_subdirectory(bison)

elseif(TASK2_WITH STREQUAL "antlr")
  message(AUTHOR_WARNING "使用 ANTLR 完成实验二")
  add_subdirectory(antlr)

else()
  message(FATAL_ERROR "Unknown task1 completion way: ${TASK2_WITH}")

endif()
