# 任务 3：中间代码生成

本次任务要求你完成从之前语法分析所得的语法树（ASG）到 LLVM IR 的翻译过程。

## 输入

- 启用复活

  任务 2 的标准答案输出，即 clang 输出的 JSON 格式语法树文件。

- 禁用复活

  任务 0 的标准答案输出，即 clang 预处理后的测例源代码文件。

## 输出

文本格式的 LLVM IR（`.ll` 文件），要求其语义与 clang 的编译结果相同（而代码可以不同）。

## 评测

评测后，每个测例目录下还会生成以下文件：

- `score.txt`

  评测的得分详情。

- `anwser.ll`

  标准答案，即 `clang -S -emit-llvm` 的输出。

- `output.ll`

  你的答案（如果 task3 程序正常运行）。

- `anwser.exe`

  标准答案 `answer.ll` 进一步编译出的可执行文件。

- `output.exe`

  你的 `output.ll` 进一步编译出的可执行文件（如果成功）。

- `answer.compile`

  clang 在编译 `answer.ll` 过程中的输出。

- `output.compile`

  clang 在编译 `output.ll` 过程中的输出。

- `answer.out` 和 `answer.err`

  运行 `answer.exe` 时的标准输出（cout）和标准错误输出（cerr）。

- `output.out` 和 `output.err`

  运行 `output.exe` 时的标准输出（cout）和标准错误输出（cerr）。

## 基础代码

基础代码已经完整实现了从 JSON 文件解析到 ASG 的功能，并且能通过一部分测例。

按照实验设计，你应该只需要修改 `EmitIR.hpp` 与 `EmitIR.cpp` 两个文件就能完成本次任务。然而，我们不保证其它代码没有任何 BUG，如果你在实验中遇到了什么问题，可以自由地修改一切基础代码。

出于简单直白的考量，基础代码采用的翻译策略在性能上可能不是最优的，你可以自由地选择更好的翻译策略，这可能会有助于在接下来的任务 4 中取得高分。

## 一些提示

1. 首先尝试手写 LLVM IR，然后再考虑如何生成

   LLVM IR 也算是一种编程语言，只不过是面向机器编程的：你写 C/C++ 程序让计算机写 LLVM IR。因此在你教会计算机如何生成 LLVM IR 之前，你必须先自己学会 LLVM IR。

   但你不必被“我又要学一门编程语言了”吓到，LLVM IR 在设计上很大程度上参考了 C 语言，因此你应该很快就能上手。而且本实验只涉及到 LLVM IR 的一个子集，你不需要学习 LLVM IR 的全部内容。

   > 《LLVM Language Reference Manual》：https://llvm.org/docs/LangRef.html

2. LLVM 17 的指针没有类型

   只有死语言是一成不变的，LLVM IR 在每个版本都会有一些变化。在 LLVM 17 中，指针类型已经被完全移除，所有指针都是 `ptr` 类型（Opaque Pointers），在你查阅相关 LLVM 的教程和资料时，注意它们所使用的版本和你的区别。

   > 《Opaque Pointers》：https://llvm.org/docs/OpaquePointers.html

3. 大部分语义都有远不止一种翻译方式

   许多高级语言的语义都有多种 LLVM IR 的实现方式，本次任务中你可以自由选择任一种。在实践中应当选择哪一种即属于编译优化问题的讨论范畴，这将是 task4 的任务内容。

4. 逻辑表达式的短路求值

   [短路求值是 C 语言标准明确定义的行为](https://zh.cppreference.com/w/c/language/operator_logical)，所以逻辑表达式可能会翻译为多个基本块。

5. 全局变量初始化

   全局变量的初始化可以通过编译时常量表达式求值或者 `global_ctor` 实现。

6. 局部变量分配

   使用 `alloca` 在栈上分配局部变量，通过 `llvm.stacksave` 和 `llvm.stackrestore` 实现栈空间的局部回收。虽然 C 语言的局部变量可以（也通常是）在函数入口处统一分配，但在语义上每个复合语句都可以有自己的栈帧（例如处理 C++ 中的构造与析构函数调用）。
