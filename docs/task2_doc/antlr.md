# 使用antlr完成实验二
使用`antlr`完成实验时所需要用到的文件如下所示，其中`common`文件夹内的内容是不管使用`antlr`还是`bison`进行实现都需要用到的代码。
```bash
-- antlr
   |-- Ast2Asg.cpp
   |-- Ast2Asg.hpp
   |-- CMakeLists.txt
   |-- README.md
   |-- SYsU_lang.g4
   `-- main.cpp
-- common
   |-- Asg2Json.cpp
   |-- Asg2Json.hpp
   |-- Typing.cpp
   |-- Typing.hpp
   `-- asg.hpp
```

这些代码使用 `antlr` 实现了一个简单的语法分析器，用于将 `SYsU_lang` 语言的源代码转换为抽象语法树（`AST`），再进一步转换为抽象语法图（`ASG`），最后再将 `ASG` 转换为 `JSON` 格式进行输出（将 `ASG` 转换为 `JSON` 格式输出的原因是 `ASG` 是存在于内存中的不便于阅读的数据结构，输出为 `JSON` 格式方便同学们与实验标准答案对应的输出进行对比差错）。下面是对主要代码文件的结构和关键功能的分析，以便同学们对代码的整体架构有一定的了解，方便后续进行编码。

`main.cpp`
包含主函数 `main`，用于整个程序的入口。
检查命令行参数，确保有输入和输出文件。
使用 `antlr4::ANTLRInputStream` 处理输入文件，生成词法分析器（`lexer`）和语法分析器（`parser`）。
从语法分析器中获取 `AST`，并使用 `asg::Ast2Asg` 类将 `AST` 转换为 `ASG`。
利用 `asg::Typing` 类进行类型推断，填充 `ASG` 中缺失的类型信息。
最后，使用 `asg::Asg2Json` 类将 `ASG` 转换为 `JSON` 格式并输出到文件。

`SYsU_lang.g4`
定义了 `SYsU_lang` 语言的语法规则。
包含了表达式、语句、声明等语法规则的定义。

`Ast2Asg.cpp` 和 `Ast2Asg.hpp` 中
`Ast2Asg` 类负责将 `AST` 转换为 `ASG`。
包括对各种语法结构（如表达式、语句、声明等）的处理方法。
使用了访问者模式来遍历 `AST` 并构建 `ASG`。

`asg.hpp`
定义了 `ASG` 的结构，包括各种节点类型（如表达式节点、语句节点、声明节点等）。
提供了用于管理 `AST` 和 `ASG` 节点生命周期的 `Obj::Mgr` 类。

`Asg2Json.cpp` 和 `Asg2Json.hpp`
`Asg2Json` 类负责将 `ASG` 转换为 `JSON` 格式。
包括对 `ASG` 中各种节点的处理方法，以生成相应的 `JSON` 对象。

`Typing.cpp` 和 `Typing.hpp`
`Typing` 类用于在 `ASG` 中推导和补全类型信息。
对 `ASG` 进行遍历，根据变量声明、表达式等的上下文来推断类型。
整体来说，这个语法分析器的实现涉及了从源代码文本到 `AST`，再到 `ASG`，最后可能的输出为 `JSON` 的完整流程。每个步骤都使用了专门的类和方法来处理特定的任务，如语法分析、`AST` 到 `ASG` 的转换、类型推断和 `ASG` 到 `JSON` 的转换。

## SYsU_lang.g4 介绍
以 `g4` 为后缀名的文件是 `antlr` 中用于定义词法规则和语法规则的文件。其中 `ANTLR` 规定以大写字母开头定义的语句用于定义词法规则，以小写字母开头定义的语句用于定义语法规则。在本小节中我们默认同学都开启`复活`，即本小节直接把 `clang` 输出的词法分析结果输入到我们自己实现的语法分析器中。其中词法分析相关处理助教团队已经提前为同学们写好，所以大家的精力只需要放在语法分析部分即可。









## Ast2Asg 相关代码介绍
`Ast2Asg.cpp` 和 `Ast2Asg.hpp` 包含了将 `ANTLR` 生成的抽象语法树（`AST`）转换为另一种形式的抽象语法图（`ASG`）的代码。这一过程涉及遍历 `AST`，然后根据 `AST` 节点的类型和属性创建相应的 `ASG` 节点，并建立它们之间的关系。
