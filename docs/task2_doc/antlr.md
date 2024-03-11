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
`Ast2Asg` 相关的代码在 `main.cpp` 中是通过如下方法进行调用的。

```c++
  asg::Obj::Mgr mgr;
  asg::Ast2Asg ast2asg(mgr);
  auto asg = ast2asg(ast->translationUnit());
```
上面这段代码发生了从 AST（抽象语法树）到 ASG（抽象语法图）的转换过程。下面是详细的解释：

首先是
```c++
asg::Ast2Asg ast2asg(mgr);
```
这行代码创建了 Ast2Asg 类的一个实例 ast2asg，并将对象管理器 mgr 作为构造函数的参数传递给它。这个对象管理器 mgr 负责在 AST 到 ASG 的转换过程中创建和管理所有 ASG 节点的生命周期。

然后是

```c++
auto asg = ast2asg(ast->translationUnit());
```

这行代码调用了 ast2asg 实例的操作符 `()` 函数，传入了由 `ANTLR` 生成的 `AST` 的根节点 —— 通常是表示整个程序的 `translationUnit` 节点。这个函数的任务是遍历 `AST`，为每个节点创建相应的 `ASG` 节点，并根据 `AST` 节点之间的关系构建 `ASG` 的结构。其中的过程细节是：
1. 遍历AST：函数首先遍历 AST 的每个节点。AST 是根据源代码的语法结构自顶向下递归构建的树形结构，每个节点代表了源代码中的一个语法结构（如表达式、语句、声明等）。
2. 节点转换：对于 AST 的每个节点，Ast2Asg 类中定义的对应的转换方法会被调用。这些方法负责将 AST 节点转换为 ASG 节点。转换过程中可能会创建新的 ASG 节点对象，并利用对象管理器 mgr 进行管理。
3. 构建ASG结构：在转换各个 AST 节点的同时，转换方法还会根据 AST 节点之间的父子关系和兄弟关系来构建 ASG 的图形结构。这一步骤确保了转换后的 ASG 能够准确反映程序的逻辑结构和语法结构。
4. 返回ASG的根节点：整个转换过程完成后，ast2asg(ast->translationUnit()) 会返回转换后的 ASG 的根节点。这个根节点代表了整个程序的抽象语法图，是后续编译过程中进行语义分析、优化和代码生成等操作的基础。

接下来会向大家介绍`Ast2Asg.cpp`相关类和方法的定义。



`Ast2Asg.cpp` 和 `Ast2Asg.hpp` 包含了将 `ANTLR` 生成的抽象语法树（`AST`）转换为另一种形式的抽象语法图（`ASG`）的代码。这一过程涉及遍历 `AST`，然后根据 `AST` 节点的类型和属性创建相应的 `ASG` 节点，并建立它们之间的关系。

### Ast2Asg 类定义
Ast2Asg类负责将由ANTLR解析器生成的AST转换为更方便处理的ASG形式。它包含一个对象管理器（Obj::Mgr）的引用，用于创建和管理AST节点对应的ASG节点。
```c++
class Ast2Asg
{
public:
  Obj::Mgr& mMgr;
  Ast2Asg(Obj::Mgr& mgr) : mMgr(mgr) {}
  // 转换函数等
};
```

### 类型处理
在AST到ASG的转换过程中，需要处理类型声明和符号表。Ast2Asg类包含了多个重载的操作符函数，用于处理不同类型的AST节点，比如类型声明、变量声明、函数声明等。
```c++
// 示例代码段：处理类型说明符
Ast2Asg::SpecQual operator()(ast::DeclarationSpecifiersContext* ctx);
Ast2Asg::SpecQual operator()(ast::DeclarationSpecifiers2Context* ctx)；
```
举个例子，假设有以下C++声明：
```c++
// 对应ast::DeclarationSpecifiersContext的声明示例
int const variable1;

// 对应ast::DeclarationSpecifiers2Context的声明示例
void function(int const parameter);
```
我们要实现的代码需要遍历声明说明符上下文中的所有声明说明符，根据类型说明符和类型限定符设置`SpecQual`结构体的值。`SpecQual`结构体包含了两个成员：一个是类型规格（`Type::Spec`,类似`int`,`float`等），另一个是类型限定（`Type::Qual`，类似`const`等）。

以下两个代码段我们会设计到声明器和直接声明器两个概念，在C语言及其类似的语言中，声明器（`Declarator`）和直接声明器（`Direct Declarator`）是用于定义变量、函数等标识符及其类型信息的语法结构，它们之间的关系可以理解为层次结构中的不同级别。
1. 声明器 (Declarator):
- 声明器用于指定变量名或函数名以及它们的类型信息。它包括直接声明器和可能的修饰符，如指针（`*`）、数组（`[]`）和函数参数列表（`()`）。
- 声明器的作用是将类型信息（通过声明说明符提供）与标识符（通过直接声明器提供）相关联。
- 例如，在声明int `*a[10];`中，`*a[10]`就是声明器，它指明了`a`是一个大小为10的整型指针数组。

1. 直接声明器 (Direct Declarator):
- 直接声明器是声明器的一部分，指定了变量名或函数名本身，不包含任何类型修饰符。
- 直接声明器可以是一个简单的标识符（如变量名或函数名），也可以是包含其他直接声明器的复杂结构，如带有参数列表的函数声明或数组声明。
- 在上面的例子中，`a`就是直接声明器，表明了标识符的名称。
  
接下来向同学们介绍我们有关声明器和直接声明器的两个方法。

```c++
Ast2Asg::operator()(ast::DeclaratorContext* ctx, TypeExpr* sub)
```
以上函数接收一个**声明器上下文**和一个子类型表达式，然后直接将处理委托给`directDeclarator`(`directDeclarator`需要同学们在`g4`文件中进行定义)上下文的处理。这是一个转发函数，主要用于处理具有嵌套结构的声明器。假设我们有一个声明`int *ptr;`，其中`ptr`是指向`int`类型的指针。上述函数会接收到表示指针声明的上下文，然后将其转发给处理直接声明器的函数，以解析出`ptr`的类型为指向`int`的指针。

```c++
Ast2Asg::operator()(ast::DirectDeclaratorContext* ctx, TypeExpr* sub)
```
此函数处理**直接声明器**上下文，可以处理多种声明结构，包括标识符声明、数组类型声明、函数类型声明等。它根据上下文的不同，创建不同的TypeExpr来表示声明的类型，并可能返回标识符名称。
代码示例:
- 对于声明`int arr[10];`，此函数会识别出`arr`是一个数组类型，并且长度为`10`。
- 对于声明`int func(int);`，此函数会识别出`func`是一个函数类型，接收一个`int`类型的参数。


```c++
Ast2Asg::operator()(ast::AbstractDeclaratorContext* ctx, TypeExpr* sub)
```
`Ast2Asg::operator()(ast::AbstractDeclaratorContext* ctx, TypeExpr* sub)`这个函数的作用是处理抽象声明器的上下文，即那些没有直接名称的声明（如类型转换或作为参数的函数类型声明）。举一个简单的例子，

```c++
using FunctionPointerType = void (*)(int);

// 示例：使用该类型声明一个函数指针变量
FunctionPointerType myFunctionPointer;
```
`Ast2Asg::operator()`函数接收一个表示函数指针类型的上下文节点`ctx`（比如，包含参数类型的信息）和一个表示函数返回类型的`sub`（在这个例子中是`void`），然后构造出一个`FunctionType`的实例，它表示了整个函数指针类型。这个过程涉及到从`AST`节点中提取信息，并根据这些信息构建出`ASG`（抽象语法图）中的节点。


```c++
Ast2Asg::operator()(ast::DirectAbstractDeclaratorContext* ctx, TypeExpr* sub)
```
此函数处理更具体的抽象声明器上下文，可以处理数组和函数类型的声明，但不涉及标识符名称。它主要用于解析没有名称的类型表达式，如函数参数列表中的类型或者作为其他类型声明的一部分。举个例子，对于声明`void func(int [])`中的`int []`，此函数会识别出参数类型为一个未指定长度的整型数组。对于声明`void (*func)(int, float)`中的`(*func)(int, float)`，此函数会构造一个表示函数指针类型的`TypeExpr`，该函数接收`int`和`float`类型的参数。


### 表达式处理
这段代码实现了将抽象语法树（AST）转换为另一种中间表示形式，称为抽象语义图（ASG），专注于表达式的处理。它涉及多个不同类型的表达式，每种表达式的处理方法都有其对应的函数。输入通常是AST中的节点，每个节点代表一个特定的语言构造，如表达式、声明等。返回值是经过转换后的ASG节点，表示相应的语言构造。
```c++
  Expr* operator()(ast::ExpressionContext* ctx);
  // 输入：一个或多个逗号分隔的表达式。
  // 返回值：最后一个表达式的ASG节点。

  Expr* operator()(ast::AssignmentExpressionContext* ctx);
  // 输入：一个赋值表达式
  // 返回值：赋值操作的ASG节点。

  Expr* operator()(ast::LogicalOrExpressionContext* ctx);
  // 输入：包含逻辑“或”操作的表达式。
  // 返回值：逻辑“或”操作的ASG节点。

  Expr* operator()(ast::LogicalAndExpressionContext* ctx);
  // 输入：包含逻辑“与”操作的表达式。
  // 返回值：逻辑“与”操作的ASG节点。

  Expr* operator()(ast::EqualityExpressionContext* ctx);
  // 输入：包含等于或不等于操作的表达式。
  // 返回值：等于或不等于操作的ASG节点。

  Expr* operator()(ast::RelationalExpressionContext* ctx);
  // 输入：包含关系操作（大于、小于、大于等于、小于等于）的表达式。
  // 返回值：关系操作的ASG节点。

  Expr* operator()(ast::AdditiveExpressionContext* ctx);
  // 输入：包含加法或减法操作的表达式。
  // 返回值：加法或减法操作的ASG节点。

  Expr* operator()(ast::MultiplicativeExpressionContext* ctx);
  // 输入：包含乘法、除法、取模操作的表达式。
  // 返回值：乘法、除法、取模操作的ASG节点。

  Expr* operator()(ast::UnaryExpressionContext* ctx);
  // 输入：包含单个操作数的操作（如取反、逻辑非）的表达式。
  // 返回值：单个操作数操作的ASG节点。

  Expr* operator()(ast::PostfixExpressionContext* ctx);
  // 输入：包含后缀表达式的操作（如数组访问、函数调用）的表达式。
  // 返回值：后缀操作的ASG节点。

  Expr* operator()(ast::PrimaryExpressionContext* ctx);
  // 输入：基础表达式，如标识符、常量。
  // 返回值：基础表达式的ASG节点。

  Expr* operator()(ast::InitializerContext* ctx);
  // 输入：用于变量初始化的单个值或值列表。
  // 返回值：初始化操作的ASG节点。
```

### 语句处理
在这一部分的代码中，每个返回的对象都是`ASG`的一部分，它们相互关联形成了程序逻辑的图形表示。这种表示便于进行优化、分析和最终的代码生成。例如，`CompoundStmt`在`ASG`中可能是一个有多个分支的节点，每个分支代表一个子语句；`IfStmt`在`ASG`中是一个有三个分支的节点，分别对应条件、`then`分支和`else`分支（如果存在）。这样的结构使得编译器能够清晰地理解和处理高级语言中的复杂结构。


```c++
  Stmt* operator()(ast::StatementContext* ctx);

  CompoundStmt* operator()(ast::CompoundStatementContext* ctx);
  // 处理复合语句
  // 输入是由花括号包围的一系列语句，示例：{ int x = 0; x += 1; } 这表示一个作用域内的语句块。
  // 返回值：CompoundStmt对象，它包含一组子语句（声明语句和其他语句）的列表。在ASG中，这个对象可以表示为一个节点，其子节点是由它包含的声明和语句转换成的ASG节点。

  Stmt* operator()(ast::ExpressionStatementContext* ctx);
  // 处理表达式语句
  // 输入：单独的表达式作为语句。
  // 返回值：ExprStmt对象，它持有一个表达式。在ASG中，这个对象对应一个节点，其子节点是表达式转换成的ASG节点。

  Stmt* operator()(ast::SelectionStatementContext* ctx);
  // 处理选择语句
  // 输入：if或else语句。
  // 返回值：IfStmt对象，包含条件表达式、then分支和可选的else分支。在ASG中，这个对象对应一个分支节点，其子节点分别是条件表达式、then分支语句和else分支语句（如果有）的ASG表示。

  Stmt* operator()(ast::IterationStatementContext* ctx);
  // 处理迭代语句
  // 输入：while、do-while循环。
  // 返回值：对于while循环，返回WhileStmt对象；对于do-while循环，返回DoStmt对象。这些对象持有循环条件和循环体。在ASG中，这些对象对应循环节点，其子节点是条件表达式和循环体的ASG表示。

  Stmt* operator()(ast::JumpStatementContext* ctx);
  // 处理跳转语句
  // 输入：continue、break或return语句。
  // 返回值：对于continue和break，分别返回ContinueStmt和BreakStmt对象，这些对象可以链接到对应的循环节点。对于return，返回ReturnStmt对象，它可以持有一个可选的返回值表达式。在ASG中，这些对象对应控制流更改的节点，如循环退出或函数返回，其中ReturnStmt的子节点是返回值表达式的ASG表示（如果存在）。
```



### 符号表和作用域管理
```c++
struct Ast2Asg::Symtbl : public std::unordered_map<std::string, Decl*>
{
  Ast2Asg& m;
  Symtbl* mPrev;
  // 构造函数和析构函数用于管理作用域
  Symtbl(Ast2Asg& m) : m(m), mPrev(m.mSymtbl) { m.mSymtbl = this; }
  ~Symtbl() { m.mSymtbl = mPrev; }
  // 解析名称
  Decl* resolve(const std::string& name);
};

```
`Ast2Asg` 相关代码实现了编译过程中一个关键步骤：将ANTLR生成的AST转换为ASG。这一过程涉及到对不同类型节点的处理，包括类型定义、变量和函数声明、表达式和语句的转换。此外，通过对符号表和作用域的管理，实现了对变量作用域和生命周期的控制。这些转换和处理为后续的编译步骤（如类型检查、代码优化和生成）打下了基础。