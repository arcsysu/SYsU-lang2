## 任务描述

恭喜同学们完成了前面两个实验！在实验一中我们实现了一个词法分析器，将源代码文件输入词法分析器后，将会产生 token 流。在实验二中，我们实现了一个语法分析器，读取了词法分析器输出的 token 流，经过了 token 流 -> 抽象语义图ASG -> JSON 格式的抽象语法树的变换。

在本次实验中，大家将要完成一个中间代码生成器，程序的输入是实验二的答案，也就是 JSON 格式的抽象语法树，程序的输出是 LLVM IR（本次实验中为可读的汇编文本格式，文件后缀为 .ll）。同学们在进行实验的过程中，可以参考 task3-answer 输出的答案。从实验三开始，大家将逐渐体会到 LLVM 库的强大。

助教提供的实验三中间代码生成器框架的工作流程如下所示：
![](../images/task3/framework.png)

task3的目录结构如下：

```
-- task3
    |- Obj.hpp
    |- Obj.cpp
    |- asg.hpp
    |- asg.cpp
    |- Json2Asg.hpp
    |- Json2Asg.cpp
    |- EmitIR.hpp
    |- EmitIR.cpp
    `- main.cpp
```

相信大家对 Obj.hpp/cpp 和 asg.hpp/cpp 四个文件已经很熟悉了，它们帮助了大家顺利地完成了实验二，本次实验就不再对它们进行介绍了。

**Json2Asg.hpp/cpp** 实现了 Json2Asg 类，它的功能是读取 llvm::json::Value 格式的抽象语法树，并将其转换为抽象语义图，输出 asg::TranslationUnit。助教们已经实现了这个类，大家不需要对其进行过多的关注。

**EmitIR.hpp/cpp** 用于实现 EmitIR 类，它的功能是读取抽象语义图，即 Json2Asg 输出的 asg::TranslationUnit，然后根据其来生成 LLVM IR。助教们已经已经实现了这个类的基本功能，使目前的实验三代码仅仅能够通过 functional-0/000_main.sysu.c 这个测例。**同学们在实验三中需要做的，就是完善这个类，使得最终实验三的代码能够通过所有测例**。

**main.cpp** 是实验三中间代码生成器的程序入口，负责创建 Json2Asg 实例读取 JSON 格式的抽象语法树，输出 asg::TranslationUnit 传给 EmitIR 实例生成 LLVM IR，输出到文件中。main.cpp 的代码也不需要同学们关注。

**总而言之，同学们在实验三中需要做的，就是完善 EmitIR 类，即补充 EmitIR.hpp 和 EmitIR.cpp 两个文件中的代码，使得实验三的代码最终能够顺利通过所有测例，成为一个完成的中间代码生成器。**

## 评分标准

LLVM IR 是可以通过 LLVM 的工具 lli 被直接执行的，如 `lli output.ll`。

实验三的评分只考虑同学们生成的 LLVM IR 的正确性，对于一个编译器而言，程序的正确性是必然的。对于每个测例，同学们生成的 LLVM IR 不必与标准答案（clang 输出的 LLVM IR，即 task3-answer）相同，只要你生成的 LLVM IR 被执行后，程序的返回值和输出与 clang 生成的 LLVM IR 被执行后的返回值和输出相同，就算通过了该测例。

当所有测例都通过后，那么恭喜同学们拿到了满分！


