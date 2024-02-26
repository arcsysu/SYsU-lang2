# 1 antlr 实现

```
-- antlr
   |-- CMakeLists.txt
   |-- README.md
   |-- SYsU_lang.g4
   |-- main.cpp
```

如果你选择 antlr 来进行 task1 的实现，那么你只需要关注`main.cpp`和`SYsU_lang.g4`两个文件。

## 1.1 `SYsU_lang.g4`的介绍

以`g4`作为后缀名的文件`SYsU_lang.g4`是同学们**本次实验主要需要填补**内容的词法分析器规则文件。在文件的开头同学们需要使用以下代码对词法分析器的规则进行定义。

```c++
lexer grammar SYsU_lang;
```

其中`SYsU_lang`可以是同学们取的任意的名字，只要后续在`main.cpp`中使用时保持一致即可。下面对其规则进行简要的介绍。对于`c++`语言中的关键字，数学运算符，以及各种括号等，直接使用以下方法进行定义即可。

```
Auto : 'auto';
LeftParen : '(';
Less : '<';
LessEqual : '<=';
```

其中`:`前面的词相当于是我们为`:`后面的词取的一个别名，词法分析器在扫描到`:`后面这个词的时候，将会输出其别名，以及其所在的文件路径以及行号列号，举个例子，就像下面这段输出一样。

```bash
l_paren '('		Loc=<./1000+/1066_go_upstairs.sysu.c:1:16>
```

那么对于编程语言中更加复杂的组成单元，例如标志符，数字，字符串等，就需要使用正则表达式进行表达，这就需要用到`antlr`中的`fragment`。使用方法也非常简单，大家参照以下对于数字和非数字的定义即可意会。

```c++
fragment
Nondigit
    :   [a-zA-Z_]
    ;

fragment
Digit
    :   [0-9]
    ;
```

多个 fragment 还可以组成一种新的数据结构，示例如下。

```
DigitSequence
    :   Digit+
    ;
```



## 1.2 `main.cpp`的介绍

`main.cpp`是一个`antlr`实现的词法分析器，在处理完输入输出之后，以下代码对一个名为`SYsU_lang`的词法分析器进行初始化。

```c++
  antlr4::ANTLRInputStream input(inFile);
  SYsU_lang lexer(&input);
  antlr4::CommonTokenStream tokens(&lexer);
  tokens.fill();
```

由于我们使用`antlr`实现的词法分析器的输出结果需要与`clang`输出的标准结果进行比较，所以接下来的代码是对词法分析器分析器的输出结果进行格式化，以便和`clang`的输出结果格式一致。

在前面我们对`SYsU_lang.g4`介绍时提到需要使用以下方法对编程语言中的组成部分取一个别名

```
Auto : 'auto';
```

使用下面这一行代码就相当于把我们在`g4`文件中取的所有的别名都放到了`vocabulary`这个数据结构中。

```c++
  const auto& vocabulary = lexer.getVocabulary();
```

接下来进入的`for`循环则是对词法分析器输入的源代码文件中的每一个`token`进行分析。

```c++
for (auto&& token : tokens.getTokens())
```

`for`循环中的下列代码是取出当前`token`的别名的字符串，`antlr`这个工具会根据我们实现好的`g4`文件为我们定义的每一种词法单元的类型一个特定的`ID`，可以通过`token->getType()`获取，然后我们再将其转换为`tokenTypeName`方便打印输出

```c++
    std::string tokenTypeName =
      std::string(vocabulary.getSymbolicName(token->getType()));

    if (tokenTypeName.empty()) {
      tokenTypeName = "<UNKNOWN>"; // 处理可能的空字符串情况
    }
```

接下来的这段代码对`Loc`信息进行提取，这里已经实现了简单的`token`行号以及列号的提取。但是还需要同学们进行进阶的实现，以便正确提取出`token`所在的文件名。

```c++
    std::string locInfo = " Loc=<" + std::to_string(token->getLine()) + ":" +
                          std::to_string(token->getCharPositionInLine() + 1) +
                          ">";
```

`for`循环中剩下的代码用于判断是否输出`[StartOfLine]`和`[LeadingSpace]`以及输出最终结果，这些代码不用同学们进行修改，所以不做更多的介绍。

