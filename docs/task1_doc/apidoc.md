# API速查

## antlr 的 API 文档

### Lexer（词法分析器基础类）
Lexer类是所有由ANTLR生成的词法分析器的基类。它负责将输入的字符流（CharStream）转换成一个个的词法单元（Token）。
```
主要方法和用法：
- nextToken()：从输入流中获取下一个词法单元。这是进行词法分析的主要方法。
- reset()：重置词法分析器的状态，通常在开始新的分析前调用。
- skip()：跳过当前正在考虑的字符或词法单元。
- getCharStream()：返回当前词法分析器正在使用的字符流。
```

### Token（词法单元接口）
Token接口表示由词法分析器生成的一个词法单元，包含了关于该词法单元的所有信息，如类型、文本和在输入文本中的位置。
```
主要属性：
- getType()：获取词法单元的类型，类型通常由词法分析器的规则定义。
- getText()：获取词法单元的文本内容。
- getLine()：获取词法单元出现的行号。
- getCharPositionInLine()：获取词法单元在其所在行的位置（字符偏移量）。
```

### Vocabulary（词法符号名称访问）
Vocabulary接口提供了一种方式来访问由词法分析器使用的词法符号的名称。这对于打印调试信息或者在解析时生成更可读的输出非常有用。

```
主要方法：
- getSymbolicName(int tokenType)：根据词法单元的类型（tokenType）返回其符号名称。
- getLiteralName(int tokenType)：根据词法单元的类型返回其字面值名称（如果有的话）。
- getDisplayName(int tokenType)：根据词法单元的类型返回最适合显示的名称。
```

### CharStream（字符流接口）
CharStream是一个接口，定义了ANTLR词法分析器从中读取输入文本的字符流的方法。这个接口允许ANTLR以统一的方式处理不同来源的文本输入。

```
主要方法和用法：
- consume()：消费（读取）当前的字符，并将指针移动到下一个字符。
- LA(int i)：查看向前第i个字符，但不从流中消费它。LA(1)表示查看下一个字符。
- mark()：标记当前流的状态，以便之后可以调用release()回到这个状态。
- release(int marker)：回到由mark()方法标记的状态。
- seek(int index)：将字符流的当前位置设置为index。
- getText(Interval interval)：获取指定区间内的文本。
```



## flex 的 API 文档
在使用 Flex 构建词法分析器时，同学主要会与 Flex 的宏定义、函数和配置选项打交道。Flex 是一个为了快速生成词法分析器的工具，它不像 ANTLR 那样有一个面向对象的 API 集合，而是基于一系列的宏定义和函数来工作。以下是在使用 Flex 构建词法分析器过程中最可能用到的关键概念和组件：

###  宏定义和特殊规则
```
- %{ 和 %}：在这对大括号之间的代码会被直接复制到生成的源文件中。
- %option：设置不同的 Flex 选项，如noyywrap, case-insensitive等。
- %union：定义一个联合体，用于yylval可以返回的不同数据类型。
- YY_DECL：用于定义yylex函数的原型，可以被重定义以适应特定的用户需求。
- YY_BUF_SIZE：定义了 Flex 内部缓冲区的默认大小。
- YY_USER_ACTION：在每个匹配的规则执行动作前执行的代码。
- %x, %s：用于声明开始条件，控制匹配的上下文。
```

###  函数和全局变量
```
- yylex()：词法分析器的主要入口点，每次调用返回下一个词法单元。
- yy_scan_string(const char *str)：使词法分析器从一个字符串而不是标准输入或文件中读取输入。
- yy_switch_to_buffer(YY_BUFFER_STATE new_buffer)：切换当前的输入缓冲区。
- yy_create_buffer(FILE *file, int size)：为给定的文件创建一个新的输入缓冲区。
- yy_delete_buffer(YY_BUFFER_STATE b)：删除一个输入缓冲区。
- yyrestart(FILE *file)：重置词法分析器的状态并从新的文件开始读取输入。
- YY_BUFFER_STATE：表示输入缓冲区的状态的类型。
- yylval：在与 yacc/bison 配合使用时，用于传递词法单元的值。
- yytext：包含当前匹配的文本。
- yyleng：包含yytext的长度。
- yylineno：跟踪当前的行号（如果%option yylineno被使用）。
```

###  规则和模式
```
- 规则部分由一个模式和随后的 C 代码块组成，模式匹配后执行代码块。
- 规则可以使用正则表达式来定义。
- “.”匹配任何单个字符，除了换行符。
- "*"、"+"和"?"分别表示前面的元素出现0次或多次、1次或多次、0次或1次。
- "|"用于分隔选择项，表示或的关系。
```


