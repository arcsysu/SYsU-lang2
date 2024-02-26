# 1 flex 实现

在这里我们会向同学们介绍我们基于`flex`实现的残缺词法分析器的代码结构与关键代码的含义，方便同学们快速上手。以下是其代码结构

```
-- flex
    |-- CMakeLists.txt
    |-- README.md
    |-- lex.cpp
    |-- lex.hpp
    |-- lex.l
    |-- main.cpp
```

## 1.1 lex相关代码介绍

文件名字中与`lex`相关的代码有三个，其中`lex.l`代码是本次实验中同学们主要需要填写代码的地方。当我们使用Flex处理一个`.l`文件时，Flex会编译这个文件并根据其中的规则生成一个C源文件（通常是`lex.yy.c`），这个源文件中包含了`yylex`函数的定义。如何编译`task1`这个工程文件已经在实验环境配置部分进行了介绍，所以同学们只需要学会如何在`.l`文件中编写规则即可。

在`lex.l`代码的头部存在着以下这段代码。在`ADDCOL()`这个宏定义中，`yyleng`代表当前匹配到的字符串的长度，`ADDCOL()`这个宏定义用于更新词法分析过程中的列信息。`COME(id)`宏封装了对`come()`函数的调用，用于处理和记录识别到的每个词法单元，并最终返回该单元的类型。在`come()`函数的输入参数中，`yytext`代表当前识别到的文本内容，例如`auto`,`{`这样的词法单元，`yylineno`代表`	yytext`出现的行号。`id`代表一个枚举值，这些枚举值在`lex.hpp`中的`enum Id`中被定义。

```c++
%{
#include "lex.hpp"
#include <cstring>
/* 所有代码全部抽离出来，放到 lex.hpp 和 lex.cpp 里 */

using namespace lex;

#define ADDCOL() g.mColumn += yyleng;
#define COME(id) return come(id, yytext, yyleng, yylineno)
%}
```

在`lex.l`中你可以定义一系列正则表达式为自己所用，例如你可以使用以下方法为正则表达式取一个别名，方便后续对这些正则表达式进行组合使用

```c++
D     [0-9]
L     [a-zA-Z_]
H     [a-fA-F0-9]
E     ([Ee][+-]?{D}+)
P     ([Pp][+-]?{D}+)
FS    (f|F|l|L)
IS    ((u|U)|(u|U)?(l|L|ll|LL)|(l|L|ll|LL)(u|U))
```

在`lex.l`中对关键字和数学符号等进行规则的编写十分简单，方法如下。

```
"auto"        { ADDCOL(); COME(AUTO); }
"_Bool"       { ADDCOL(); COME(BOOL); }
```

上面代码中的,`auto`是一个词法单元，`COME(AUTO)`中的`AUTO`是我们在前面提到过的`lex.hpp`中的`enum Id`中被定义的枚举值。但`AUTO`并非我们在最终文件中输出的字符串，最终文件中`AUTO`对应输出的字符串需要到`lex.cpp`文件的`kTokenNames`数组的**对应位置**进行修改。

所以最终进行总结，同学们的任务即是在`lex.l`中编写词法分析规则之后，到`enum Id`中去添加对应的枚举值，并且在`kTokenNames`的正确位置添加对应的输出字符串即可。



## 1.2 main.cpp代码介绍

`main.cpp`中的 `main` 函数有三个输入参数，分别是程序名称`argv[0]`,输入文件路径`argv[1]`,输出文件路径`argv[2]`。其中 `argv[1]`在`main` 函数定义 `yyin` 时候使用，`yyin`是`flex`词法分析器的默认输入流指针，指向文件输入源，从而使词法分析器从指定文件读取输入。

`outFile`是一个`std::ofstream`类型的对象，用于向一个文件写入输出。在`main.cpp`中，它被用来打开并写入词法分析的结果, 它利用`argv[2]`进行初始化。

在 `main` 函数处理完输入输出时候就进入了`while`循环，在`while` 循环的循环条件判定中存在一个名为`yylex()`的函数。同学们可能会非常疑惑在`main.cpp`中找不到`yylex()`这个函数的定义。其实在上一小节我们提到了`yylex`函数是由Flex根据`.l`文件中定义的规则自动生成的。当你使用Flex处理一个`.l`文件时，Flex会编译这个文件并生成一个C源文件（通常是`lex.yy.c`），其中包含了`yylex`函数的定义。