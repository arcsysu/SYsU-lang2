## EmitIR 介绍


### EmitIR 类的主要职责

EmitIR 类的功能就是读取 Json2Asg 类输出的抽象语义图 asg::TranslationUnit，输出 LLVM IR。

```c++
llvm::Module& operator()(asg::TranslationUnit* tu);
```

EmitIR 类能够为 ASG 中的不同节点（如表达式、语句、函数等）生成其对应的 LLVM IR ，也能够递归处理 ASG 中的复杂结构，如函数内部的语句，复杂表达式中的子表达式等，生成相对应的 LLVM IR。

与实验二中的 Typing 类和 Asg2Json 类的方法相似，EmitIR同样以重载 operator() 的方法，来支持以同样的调用方式，根据不同的参数匹配不同的 operator() 函数，完成对不同的 ASG 节点生成对应的 LLVM IR 的功能。

在此不对 EmitIR 的成员函数和变量继续进行更多地说明，相信大家完成了实验二后，去看 EmitIR 的成员函数，应该可以比较轻易地理解这个函数的功能，换言之，这个函数是为哪个 ASG 节点产生 LLVM IR。

同学们在实验三中的任务，就是完善 EmitIR 类，即补充 EmitIR.hpp 和 EmitIR.cpp 两个文件中的代码，使得实验三的代码最终能够顺利通过所有测例，成为一个完成的中间代码生成器。

### 如何完善 EmitIR 类

本次实验中，助教已经提供了一个基本的 EmitIR 类，使实验三仅仅能通过 functional-0/000_main.sysu.c 这个测例。同时，助教也添加了 TODO 注释，提示同学们需要去做些什么。


大家可以从最基本的处理 asg::TranslationUnit 的函数出发：
```c++
llvm::Module&
EmitIR::operator()(asg::TranslationUnit* tu)
{
  for (auto&& i : tu->decls)
    self(i);
  return mMod;
}
```

然后针对不同的 Decl ，我们需要在这里添加相应的跳转。

```c++
void
EmitIR::operator()(Decl* obj)
{
  // TODO: 添加变量声明处理的跳转

  if (auto p = obj->dcst<FunctionDecl>())
    return self(p);

  ABORT();
}
```

之后大家需要完善处理不同 Decl ，比如 VarDecl 和 FunctionDecl 的节点的函数。
其它类型的实现思路也是类似的，可供参考的实现路线是：  
声明( Decl ) -> 类型( Type ) -> 表达式( Expr ) -> 语句( Stmt )  
在这个过程中，大家需要善用我们提供的测试和调试功能，比对答案及输出结果，不断地进行测试，根据没过的测例一点点查出缺少什么部分、什么功能，逐渐发散,缺啥补啥，逐步完善 EmitIR 类。

<!-- 再到完善处理类型和表达式值的函数，由 FunctionDecl 可以到完善处理语句节点的函数，同时，不断地进行测试，根据没过的测例一点点查出缺少什么部分、什么功能，逐渐发散，缺啥补啥，在 EmitIR.hpp 中添加函数声明，在 EmitIR.cpp 中进行实现。 -->

## 注意点

如果测评机与本地结果不一样，可能是局部变量没有初始化，如 EmitIR 类的成员变量 mCurFunc 没有在构造函数中设置为 nullptr，导致其在被赋值前为野指针。


