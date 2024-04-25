# 任务 4：中间代码优化

本次任务要求你亲自动手实现一些 LLVM IR 上的优化算法，以提高代码的性能。

## 输入

- 启用复活

  任务 3 的标准答案输出，即 clang 在 O0 优化级别下生成的 LLVM IR 文件。

- 禁用复活

  任务 0 的标准答案输出，即 clang 预处理后的测例源代码文件。

## 输出

文本格式的 LLVM IR（`.ll` 文件），其语义必须与输入相同，但运行性能越高越好。

## 评测

评测后，每个测例目录下会生成以下文件：

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

基础代码演示了 LLVM AnalysisPass 和 TransformPass 的实现以及使用，包括：

- `StaticCallCounter`

  这是一个 AnalysisPass，用于统计每个函数在模块中被调用的次数。

- `StaticCallCounterPrinter`

  这是一个 AnalysisPass，用于打印前述 StaticCallCounter 的结果。

  > 结果被打印到标准错误输出（`llvm::errs()`），CTest 默认会将输出保存到构建目录（`build`）下的 `Testing` 目录中，运行测试后到该目录下寻找后缀为 `.log` 的日志文件查看输出。

- `ConstantFolding`

  这是一个 TransformPass，用于将操作数全部为常数的指令直接替换为结果，以避免在输出程序中重复计算。
