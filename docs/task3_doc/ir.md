下面的资料对大家了解 LLVM IR 可能会提供不错的帮助\~\~\~

[LLVM Lanaguage Reference Manual](https://llvm.org/docs/LangRef.html)

[LLVM Programmers Manual](https://llvm.org/docs/ProgrammersManual.html)

[The Core LLVM Class Hierarchy Reference](https://www.llvm.org/docs/ProgrammersManual.html#id128)

[LLVM IR 快速上手](https://buaa-se-compiling.github.io/miniSysY-tutorial/pre/llvm_ir_quick_primer.html) [强烈推荐]

[LLVM 中的 SSA](https://buaa-se-compiling.github.io/miniSysY-tutorial/pre/llvm_ir_ssa.html) [强烈推荐]

[LLVM 架构中最为重要的概念](https://buaa-se-compiling.github.io/miniSysY-tutorial/pre/design_hints.html) [强烈推荐]


### LLVM IR 结构

对于下述源代码，假设文件名为 test.c：
```c
const int a = 10;
int b = 5;

int main() {
  if(b < a)
    return 1;
  return 0;
}
```

使用 `clang -cc1 -S -emit-llvm test.c` 生成的 LLVM IR 如下：

```
; ModuleID = 'test.c'
source_filename = "test.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@a = constant i32 10, align 4
@b = global i32 5, align 4

; Function Attrs: noinline nounwind optnone
define dso_local i32 @main() #0 {
entry:
  %retval = alloca i32, align 4
  store i32 0, i32* %retval, align 4
  %0 = load i32, i32* @b, align 4
  %cmp = icmp slt i32 %0, 10
  br i1 %cmp, label %if.then, label %if.end

if.then:                                          ; preds = %entry
  store i32 1, i32* %retval, align 4
  br label %return

if.end:                                           ; preds = %entry
  store i32 0, i32* %retval, align 4
  br label %return

return:                                           ; preds = %if.end, %if.then
  %1 = load i32, i32* %retval, align 4
  ret i32 %1
}

attributes #0 = { noinline nounwind optnone "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-features"="+cx8,+mmx,+sse,+sse2,+x87" }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{!"clang version 14.0.6"}
```

LLVM IR 文件的基本单元为 Module，一个 Module 对应于一个完整的编译单元（Translation Unit），一般来说，一个 Module 就是一个源码文件，如一个以 .c 为后缀的 c 语言文件，不过也可以将多个 Module 合并为一个 Module（通过 llvm-link 工具），本次实验中均为单文件编译，因此不涉及 Module 合并，均为单 Module。

一个 Module 就是 LLVM IR 的顶层容器，其中包含了:

- 注释。LLVM IR 中，所有的注释均以分号;开头，如`; ModuleID = 'test.c'`即为一句注释，表示模块 ID，编译器据此来区分不同的模块。
- 源文件名，如`source_filename = "test.c"`。
- 目标平台信息。`target datalayout` 表示数据布局如大小端存储、对齐方式、整数类型有哪些等等；`target triple `为描述目标平台信息的三元组，一般形式为 `<architecture>-<vendor>-<system>[-extra-info]`。
- 元数据。以感叹号!开头，可以附加到 LLVM IR 的指令和全局对象上，为优化器和代码生成器提供关于代码的额外信息。
- 全局标识符，以 @ 开头
  - 全局变量 GlobalVariable。如在上述IR中，`@a = constant i32 10, align 4` 和 `@b = global i32 5, align 4`，`align 4` 表示4字节对齐。
  - 函数 Function。定义了的函数以 define 开头，如在上述IR中，`define dso_local i32 @main()`，i32 表示函数的返回值为 int 类型。函数若只是声明而没有函数体，则以 declare 开头，如 `declare i32 f()`。函数也可以有参数列表，如`define i32 f(i32 %a, i32 %b)`。
    每个定义了的函数均由若干个基本块 BasicBlock 构成。
    - 每一个基本块都有一个属于自己的，在当前函数中唯一的标签，**每个函数执行的第一个基本块一定是标签为 entry 的基本块**，它是函数的入口基本块。在上述IR中，main() 函数总共有4个基本块，其标签分别为 entry，if.then，if.end 和 return，在开始执行 main() 函数时，一定是从 entry 基本块开始执行。
    - 每一个基本块中都有若干条指令以及局部变量，且最后一条指令一定是一条 [终结指令](https://llvm.org/docs/LangRef.html#terminator-instructions)，如上述IR中 return 基本块的`ret i32 %1`，以及分支跳转指令，分支跳转指令又分为有条件跳转，如`br i1 %cmp, label %if.then, label %if.end`，如果 %cmp 为真，则跳转到 if.then 基本块，否则跳转到 if.end 基本块，和无条件跳转，如`br label %return`，直接跳转到 return 基本块。
      一个基本块中的指令一定是从上往下顺序执行的，且一个基本块中的指令要么全都执行，要么全都不执行。
    - 基本块中的局部变量以百分号%开头，如上述 LLVM IR 中的 %cmp，如果没有为局部变量或者基本块标签命名，则 LLVM 会自动以无符号数字，按顺序为每个局部变量和基本块标签编号，如 %1，%2。

### 三个最为重要的类

#### llvm::LLVMContext

[llvm::LLVMContext Class Reference](https://llvm.org/doxygen/classllvm_1_1LLVMContext.html)

llvm::LLVMConext 是一个不透明的对象，它拥有和管理许多核心LLVM数据结构，例如类型和常量值表。我们不需要详细了解它，我们只需要将一个该类型的实例来传递给需要它的API即可。

创建LLVMContext的实例也非常简单，[构造函数](https://llvm.org/doxygen/classllvm_1_1LLVMContext.html#a4eb1cb06b47255ef63fa4212866849e1)：

```c++
#include <llvm/IR/LLVMContext.h>

/// 构造函数：LLVMContext();
llvm::LLVMContext TheContext;	
```

#### llvm::Module

[llvm::Module Class Reference](https://llvm.org/doxygen/classllvm_1_1Module.html)

llvm::Module 是所有其他 LLVM IR 对象的顶层容器，包含了全局变量、函数、该模块所依赖的库/其他模块、符号表和有关目标平台的各种数据。我们生成的所有 IR 都会储存在这里。

为了创建 LLVM Module的实例，我们需要表示 Module ID 的字符串以及 LLVMContext 的引用，[构造函数](https://llvm.org/doxygen/classllvm_1_1Module.html#a378f93ece2ac999e500f07056cfe6528)：

```c++
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>

llvm::LLVMContext TheContext;	

/// 构造函数：Module(StringRef ModuleID, LLVMContext &C)；
llvm::Module TheModule("Module ID", TheContext);
```

#### llvm::IRBuilder

[llvm::IRbuilder Class Reference](https://llvm.org/doxygen/classllvm_1_1IRBuilder.html)

既然 llvm::Module 包含了生成的所有的 LLVM IR，那么该如何生成 LLVM IR 呢？或者说如何向 llvm::Module 中插入 LLVM IR 呢？这就需要用到 llvm::IRBuilder 了。

LLVM::IRBuilder 用于生成 LLVM IR，其提供了统一的 API 来创建和插入指令到基本块（BasicBlock）中。我们可以使用 llvm::IRBuilder 的[构造函数](https://llvm.org/doxygen/classllvm_1_1IRBuilder.html#aa1e284a3ff6e4e6662223ed0b0cdd201)来指定 IR 的插入位置，也可以使用[ SetInsertPoint 方法](https://llvm.org/doxygen/classllvm_1_1IRBuilderBase.html#ace45cae6925c65e9d6916e09dd5b17cc)来修改 IR 的插入位置。

```c++
#include <llvm/IR/IRbuilder.h>

// ====================================================================
// 利用构造函数
// ====================================================================
llvm::BasicBlock *Block = /* 获得 BasicBlock 实例的指针 */;
/// 指定当前IR插入点为 Block 的末尾
llvm::IRBuilder<> TheBuilder(Block);

/// 或者

llvm::Instruction *Inst = /* 获得 IR 指令实例的指针 */;
/// 指定当前IR插入点为指令 Inst 之前
llvm::IRBuilder<> TheBuilder(Inst);

// ====================================================================
// 利用 SetInsertPoint 方法
// ====================================================================
/// 假设我们已经有了 llvm::IRBuilder 的实例TheBuilder
llvm::BasicBlock *Block = /* 获得 BasicBlock 实例的指针 */;
/// 指定当前IR插入点为 Block 的末尾
TheBuilder.SetInsertPoint(Block);

/// 或者

llvm::Instruction *Inst = /* 获得 IR 指令实例的指针 */;
/// 指定当前IR插入点为指令 Inst 之前
TheBuilder.SetInsertPoint(Inst);
```

创建 llvm::IRBuilder 的实例时，也可以不在一开始就指定 IR 插入点，直接将 LLVMContext 的引用作为参数传入即可，在想要设置 IR 插入点时，可以利用 SetInsertPoint 方法：

```c++
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/IRBuilder.h>

llvm::LLVMContext TheContext;	

llvm::Module TheModule("Module ID", TheContext);

llvm::IRBuilder<> TheBuilder(TheContext);
```

llvm::IRBuilder 创建 LLVM IR 的接口可以在 [llvm::IRbuilder Class Reference](https://llvm.org/doxygen/classllvm_1_1IRBuilder.html) 中找到，不过 llvm::IRBuilder 插入 LLVM IR 的接口基本都继承自 [llvm::IRBuilderBase](https://llvm.org/doxygen/classllvm_1_1IRBuilderBase.html) ，查看 llvm::IRBuilderBase 的接口也是可以的。本文接下来也会介绍一些本次实验中常用的接口。

### LLVM IR 类型系统

[llvm::Type Class Reference](https://llvm.org/doxygen/classllvm_1_1Type.html)

[llvm::IntegerType Class Reference](https://llvm.org/doxygen/classllvm_1_1IntegerType.html)

[llvm::ArrayType Class Referece](https://llvm.org/doxygen/classllvm_1_1ArrayType.html)

[llvm::FunctionType Class Reference](https://llvm.org/doxygen/classllvm_1_1FunctionType.html)

[llvm::PointerType Class Reference](https://llvm.org/doxygen/classllvm_1_1PointerType.html)

[LLVM Type System](https://llvm.org/docs/LangRef.html#type-system)

LLVM IR 是强类型的，类型系统是 LLVM IR 中最为重要的一部分。就像我们在 c 语言中创建变量时要指定数据类型一样，当我们调用 llvm::IRBuilder 的接口进行各种 IR 的生成时，如创建变量和函数，类型都是不可或缺的一部分。

llvm::Type 是 LLVM IR 类型系统中的基类，其和其派生类提供了许多静态方法来创建类型实例，部分类型也可以通过 llvm::IRBuilder 的接口来创建。
![](https://llvm.org/doxygen/classllvm_1_1Type__inherit__graph.png)



#### Void类型

LLVM IR 中显示为：void 

```c++
#include <llvm/IR/Type.h>

/// 省略TheContext, TheModule, TheBuilder实例的创建

/// static Type *llvm::Type::getVoidTy(LLVMContext &C);
llvm::Type *type = llvm::Type::getVoidTy(TheContext);

/// 或者

llvm::Type *type = TheBuilder.getVoidType();
```

#### 1位整数（bool）类型

LLVM IR 中显示为：i1

```c++
/// static IntegerType *llvm::Type::getInt1Ty(LLVMContext &C);
llvm::Type *type = llvm::Type::getInt1Ty(TheContext);

/// 或者

llvm::Type *type = TheBuilder.getInt1Ty();
```

#### 32位整数类型

LLVM IR 中显示为：i32

```C++
/// static IntegerType *llvm::Type::getInt32Ty(LLVMContext &C);
llvm::Type *type = llvm::Type::getInt32Ty(TheContext);

/// 或者

llvm::Type *type = TheBuilder.getInt32Ty();
```

#### 特定位数的整数类型

LLVM IR 中显示为：iN，其中 N 为我们自己指定的位数

```c++
#include <llvm/IR/DerivedTypes.h>

unsigned N = /* 指定位数 */;

/// NumBits：整数位数
/// static IntegerType *llvm::IntegerType::get(LLVMContext &C, unsigned NumBits);
llvm::Type *type = llvm::IntegerType::get(TheContext, N);

/// 或者

llvm::Type *type = TheBuild.getIntNTy(N);
```

#### 函数类型

```c++
#include <llvm/IR/DerivedTypes.h>

/// Result：  函数返回值类型
/// Params：  函数的参数列表中各个参数的类型
/// isVarArg：True表示函数为可变参数函数，即函数的最后一个参数为...
/// static FunctionType *llvm::FunctionType::get(Type *Result, ArrayRef<Type *> Params, bool isVarArg);

/// 例如：void (int, int)
llvm::FunctionType *funcType = llvm::FunctionType::get(
    llvm::Type::getVoidTy(TheContext),
    {llvm::Type::getInt32Ty(TheContext), llvm::Type::getInt32Ty(TheContext)},
    false);
```

若函数没有参数时，也可以省去 Params 形参：

```c++
/// static FunctionType *llvm::FunctionType::get(Type *Result, bool isVarArg);
/// 例如：int ()
llvm::FunctionType *funcType =
    llvm::FunctionType::get(llvm::Type::getVoidTy(TheContext), false);
```

有了 llvm::FunctionType 实例后，可以：

```c++
llvm::FunctionType *funcType = /* 获得函数类型实例指针 */;

/// True表示为可变参数函数
bool isVarArg = funcType->isVarArg(); 

/// 获得函数返回值类型
llvm::Type *retType = funcType->getReturnType();

/// 获得函数参数数量，不包括可变参数
unsigned num = funcType->getNumParams();

/// 获得函数第 I 个参数的类型
unsigned I = /* 第 I 个参数 */;
llvm::Type *ithParamType = funcType->getParamType(I);

/// 遍历函数参数类型
auto begin = funcType->param_begin();
    while(begin != funcType->param_end()) {
		/* Do something */
        begin ++;
	}
}
```

#### 数组类型

```c++
#include <llvm/IR/DerivedTypes.h>

/// ElementType：数组元素的类型
/// NumElements：数组元素的个数
/// static ArrayType *llvm::ArrayType::get(Type *ElementType, uint64_t NumElements);

/// 例如数组：int [5][10]
/// LLVM IR 中显示为[5 x [10 x i32]]
llvm::ArrayType *arrType1D = llvm::ArrayType::get(Type::getInt32Ty(TheContext), 10);
llvm::ArrayType *arrType2D = llvm::ArrayType::get(arrType1D, 5);
```

有了 llvm::ArrayType 实例后，可以：

```c++
llvm::ArrayType *arrType = /* 获得数组实例指针 */;

/// 获得数组元素个数
uint64_t len = arrType->getNumElements();

/// 获得数组元素类型
llvm::Type *elementType = arrType->getElementType();
```

#### 指针类型

```c++
#include <llvm/IR/DerivedTypes.h>

/// ElementType： 指针指向的元素类型
/// AddressSpace：地址空间，0表示默认地址空间
/// static PointerType *llvm::PointerType::get(Type *ElementType, unsigned AddressSpace);

/// 例如：int *
llvm::Type *pointee = llvm::Type::getInt32Ty(TheContext);
llvm::Type *pointer = llvm::PointerType::get(pointee, 0);

/// 或者

/// 我们也可以通过被指向的类型的成员函数来获得指针类型
llvm::Type *pointer = pointee->getPointerTo();
```

在 LLVM 17 中，所有的指针类型都是不透明指针 [Opaque Pointers](https://llvm.org/docs/OpaquePointers.html)，即对于一个指针类型，我们无法知道其指向的类型，不管是查看生成的 LLVM IR，还是调用 llvm::Type/PointerType 的接口（ LLVM 17 中已经移除了 llvm::Type/PointerType 获得指针指向类型的接口）。

例如，对于上述例子，int * 在传统 LLVM 指针类型中，在 LLVM IR 中的表示为 i32*，但是在 LLVM 17 的 LLVM IR 中，则表示为 ptr。

#### 判断是否为特定类型

当我们有了一个 llvm::Type 的实例时，可以通过下述方法判断其是否是特定类型，返回值均为 bool 类型：

```C++
llvm::Type *type = /* 获得 llvm::Type 实例指针 */

/// True 表示是整数类型
bool isIntTy = type->isIntegerTy();

unsigned N = /* 整数位数 */
// True 表示是 N 位整数类型
bool isNBitsIntTy = type->isIntegerTy(N);

// True 表示是void类型
bool isVoidTy = type->isVoidTy();

// True 表示是FunctionType
bool isFunctionTy = type->isFunctionTy();

// True 表示是数组类型
bool isArrayTy = type->isArrayTy();

// True 表示是指针类型
bool isPointerTy = type->isPointerTy();
```

### 常量

[llvm::Constant Class Reference](https://llvm.org/doxygen/classllvm_1_1Constant.html)

[llvm::ConstantInt Class Reference](https://llvm.org/doxygen/classllvm_1_1ConstantInt.html)

[llvm::ConstantArray Class Reference](https://llvm.org/doxygen/classllvm_1_1ConstantArray.html)

![](https://llvm.org/doxygen/classllvm_1_1Constant__inherit__graph.png)

LLVM IR 中，对于常量的创建，与 llvm::Type 相同，llvm::Constant 和其派生类提供了许多静态方法，以工厂模式来非常容易地创建我们需要的常量。

#### 创建整数常量

```c++
#include <llvm/IR/Constants.h>

/// 返回给定整数值 V 和整数类型 Ty 的整数常量
/// 如果 Ty 的位宽大于64位：
///		如果 IsSigned=false，则对 V 进行零扩展（无符号扩展）
/// 	否则，V 将被解释为64位有符号整数，并且进行有符号扩展来适应 Ty
/// Ty：		 整数类型
/// V：		 整数值
/// IsSigned：True 表示当 Ty 的位宽大于64位时，对 V 进行有符号扩展，否则为无符号扩展
/// static ConstantInt *llvm::ConstantInt::get(IntegerType *Ty, uint64_t V, bool IsSigned = false)

/// 例如：i32 10
llvm::ConstantInt *constantInt = llvm::ConstantInt::get(llvm::Type::getInt32Ty(TheContext), 10);

/// 或者

/// 利用 llvm::IRBuilder
llvm::ConstantInt *constantInt = TheBuilder.getInt32(10);
```

#### 创建数组常量

```c++
#include <llvm/IR/Constants.h>

/// Ty：数组类型
/// V： 数组的元素的值，均为常量
/// static Constant *llvm::ConstantArray::get(ArrayType *Ty, ArrayRef<Constant*> V)

/// 例如：{1, 2, 3}
llvm::Constant *constantArray = llvm::ConstantArray::get(
      llvm::ArrayType::get(llvm::Type::getInt32Ty(TheContext), 3),
      {
          llvm::ConstantInt::get(llvm::Type::getInt32Ty(TheContext), 1),
          llvm::ConstantInt::get(llvm::Type::getInt32Ty(TheContext), 2),
          llvm::ConstantInt::get(llvm::Type::getInt32Ty(TheContext), 3),
      });
```

#### 对任意类型创建0常量

常用于对变量进行默认的零初始化。

```c++
#include <llvm/IR/Constants.h>

/// Ty：类型
static Constant *llvm::Constant::getNullValue(Type *Ty);
```

### 全局变量

[llvm::GlobalVariable Class Reference](https://llvm.org/doxygen/classllvm_1_1GlobalVariable.html)

#### 创建全局变量

创建全局变量可以直接使用 llvm::GlobalVariable 的构造函数

```c++
#include <llvm/IR/GlobalVariable.h>

/// M：			llvm::Module实例，包含所有 LLVM IR 的顶层容器
///		 		 全局变量创建完成后将会自动插入 M 的符号表中
/// Ty：			全局变量的类型
/// isConstant：	是否是常量
/// Linkage：	全局变量的链接类型，如是否被外部函数可见
/// Initializer：初始值
/// Name：		全局变量的名字
/// 其他参数在本次实验中可以不用关注
GlobalVariable(Module &M, Type *Ty, 
               bool isConstant, LinkageTypes Linkage, 
               Constant *Initializer, const Twine &Name="", 
               GlobalVariable *InsertBefore=nullptr, 
               ThreadLocalMode=NotThreadLocal, 
               std::optional< unsigned > AddressSpace=std::nullopt, 
               bool isExternallyInitialized=false);
```

全局变量在创建时就必须被初始化，有两种初始化的方式：

1. 创建全局变量前求得其初始值，创建时即利用求得的值初始化

2. 利用全局构造函数，其在 llvm::Module 被加载的时候（程序真正的代码被执行之前）自动被执行，从而对全局变量进行初始化

   [Global constructors](https://llvm.org/docs/LangRef.html#the-llvm-global-ctors-global-variable)

##### 第一种方法

在创建全局变量前，我们已经求得了其的初始值，那么只需要调用 llvm::GlobalVariable 的构造函数创建全局变量就可以了

```c++
// 例如：int a = 20

llvm::Type *ty = llvm::Type::getInt32Ty(TheContext);
llvm::Constant *initVal =
    llvm::ConstantInt::get(llvm::Type::getInt32Ty(TheContext), 10);

llvm::GlobalVariable *gloVar = new llvm::GlobalVariable(
    TheModule, ty, false, /* Not constant */
    llvm::GlobalValue::ExternalLinkage, initVal, "glolVar");
```

生成的 LLVM IR 如下：

```
@glolVar = global i32 10
```

##### 第二种方法

有时候全局变量的初始值比较难以直接求解成一个 llvm::Constant 的实例，比如数组的初始化、值为表达式，此时我们可以使用全局构造函数来为全局变量进行初始化。

这个方法可以分成三步来完成：

1. 创建全局变量，并为全局变量暂时先指定零初始化；

2. 创建函数（创建函数的具体细节可见[函数](#函数)），完成为全局变量进行初始化的逻辑；

   基本块创建可见[基本块](#基本块)，store 指令可见[store](#store 指令)

3. 将函数添加至模块的全局构造函数数组中。

```c++
/// 举个简单的例子，例如：int a = 20

/// 1. 创建全局变量，并为全局变量暂时先指定零初始化
llvm::Type *ty = llvm::Type::getInt32Ty(TheContext);
llvm::GlobalVariable *gloVar =
    new llvm::GlobalVariable(TheModule, ty, false, /* Not constant */
                             llvm::GlobalValue::ExternalLinkage,
                             nullptr /* 初始值为 nullptr */, "glolVar");
/// 零初始化
gloVar->setInitializer(llvm::Constant::getNullValue(ty));

/// 2. 创建函数，完成为全局变量进行初始化的逻辑
/// 函数返回值为 void，无参数
/// 函数名字为 ctor
llvm::Function *ctorFunc = llvm::Function::Create(
    llvm::FunctionType::get(llvm::Type::getVoidTy(TheContext), false),
    llvm::GlobalValue::PrivateLinkage, "ctor", &TheModule);
/// 为函数 ctorFunc 创建 entry 基本块
llvm::BasicBlock *entryBlock = llvm::BasicBlock::Create(TheContext, "entry", ctorFunc);
/// 设置 LLVM IR 插入点为 entry 基本块
TheBuilder.SetInsertPoint(entryBlock);
/// 创建 store 指令将常量1存入全局变量 gloVar
TheBuilder.CreateStore(llvm::ConstantInt::get(llvm::Type::getInt32Ty(TheContext), 10), gloVar);

/// 3. 将函数添加至模块 TheModule 的全局构造函数数组中,65535为优先级
///    优先级数值越大执行时间越靠后，优先级数值最大值为65535
///    模块被加载时，全局构造函数数组中的全局构造函数将按照优先级依次执行
llvm::appendToGlobalCtors(TheModule, ctorFunc, 65535);
```

生成的 LLVM IR 如下：

```
@glolVar = global i32 0
@llvm.global_ctors = appending global [1 x { i32, ptr, ptr }] [{ i32, ptr, ptr } { i32 65535, ptr @ctor, ptr null }]

define private void @ctor() {
entry:
  store i32 10, ptr @glolVar, align 4
}
```

#### 在模块符号表中查找全局变量

```c++
/// gloVarName 表示全局变量的名字
llvm::GlobalVariable *gloVar = TheModule.getGlobalVariable(gloVarName);
```

### 局部变量

LLVM IR 中的的局部变量仅出现在基本块中，且均以百分号%开头。局部变量在 LLVM IR 中的分配方式有两种：

1. 分配给虚拟寄存器。这种局部变量多采用`%1=some operation`的形式来进行赋值，存储的是指令返回的结果，如整数加法指令：

   ```
   ; 将寄存器 %4 和寄存器 %5 的值相加，它们的值均为 i32 类型，结果存储在寄存器 %6 中
   %6 = add i32 %4, %5
   ```

   每一条有返回结果的指令，其指令的结果都将直接存储在寄存器中。

2. 使用 alloca 指令在函数栈上进行内存分配。比如`%2=alloca i32`，表示动态分配一个能够存储 i32 整数的内存空间，地址存储在寄存器 %2 中，因此 %2 寄存器中存储的其实是一个指针。访问 %2 指向的内容或者向 %2 指向的地址存储数据时，需要分别用到 load 和 store 指令，而取虚拟寄存器中的值不需要使用 load 指令，直接使用即可。

#### alloca 指令

```c++
// Ty：要分配的内存空间的类型
// Name：局部变量的名字，若未取名，则 LLVM 自动分配
AllocaInst *CreateAlloca(Type *Ty, Value *ArraySize=nullptr, const Twine &Name="");
```

例如，对于 int a：

```C++
TheBuilder.CreateAlloca(TheBuilder.getInt32Ty(), nullptr, "a");
```

结果如下：

```c++
%a = alloca i32
```

局部变量 a 是通过 alloca 指令通过内存分配得到的，其类型其实为指针，也就是 i32 *，指向 i32 类型的数据，不过在 LLVM IR 中，其类型显示为 ptr。

又如，对于 int a\[10\]\[5\]：

```c++
/// int [5]
llvm::ArrayType *arrType1D = llvm::ArrayType::get(TheBuilder.getInt32Ty(), 5);  
/// int [10][5]
llvm::ArrayType *arrType2D =llvm::ArrayType::get(arrType1D, 10);  

TheBuilder.CreateAlloca(arrType2D, nullptr, "a");
```

结果如下：

```
%a = alloca [10 x [5 x i32]]
```

%a 存储的其实是指向 [10 x [10 x i32]] 类型的数组的指针。

##### alloca 可能会引起的问题

在 C 语言中，当一个花括号 { ... \} 中（CompoundStmt 中）的程序语句被执行完成后，会自动释放花括号中的局部变量。但是，在 LLVM IR 中，是不会自动释放由 alloca 指令分配内存的局部变量的，因此，当程序中的 alloca 指令执行许多次后，尤其是循环中的 alloca 指令，可能会造成函数栈空间不足的问题，造成程序崩溃。

例如，对于下述代码：

```c
/* Do something */

while(i < 10000) {
    int tmp = /* 创建局部变量 */;
    
    /* Do something */
}

/* Do something */
```

对应的 LLVM IR 如下：

```
while.cond:                                       ; preds = %while.body, %entry
  ; 计算 i < 10000
  %0 = load i32, ptr %i
  %cmp = icmp slt i32 %0, 10000
  br i1 %cmp, label %while.body, label %while.end

while.body:                                       ; preds = %while.cond
  ; alloca 创建 tmp 变量
  %tmp = alloca i32
  ; Do something
  br label %while.cond

while.end:                                        ; preds = %while.cond
  ; Do something
```

1. 每次循环结束后，tmp 变量所占的内存空间都不会被释放；
2. 每次循环开始时，又通过 alloca 指令继续在栈上分配空间，创建变量 tmp

循环次数过多时，最终可能会导致函数的栈空间不足，程序崩溃。

###### 第一种解决方法

将 LLVM IR [函数](#函数)中所有的 alloca 指令都放到函数的 entry [基本块](#基本块)中，使得在一开始就为之后函数中会用到的局部变量在栈上分配内存空间，这也是 clang 的做法。

###### 第二种解决方法

使用 LLVM 的内建（intrinsics）函数 llvm.stacksave 和 llvm.stackrestore，在每次解析 CompoundStmt，生成 LLVM IR 时，在 LLVM IR 的开头调用 llvm.stacksave 记录当前函数的栈高度，在为 CompoundStmt 生成 LLVM IR 结束后，在 LLVM IR 的末尾调用 llvm.stackrestore 将函数的栈高度回到之前记录的高度，这有效地释放了在 CompundStmt 中通过 alloca 指令分配内存创建的任何变量。

使用方法如下：

```c++
/// 创建调用 llvm.stacksave 的指令
auto sp = TheBuilder.CreateIntrinsic(llvm::Intrinsic::stacksave, {}, {},
                                     nullptr, "sp");
/* 解析 CompoundStmt，生成 LLVM IR */

/// 创建调用 llvm.stackrestore 的指令
TheBuilder.CreateIntrinsic(llvm::Intrinsic::stackrestore, {}, {sp});
```



#### store 指令

要想将数据存储在：

1. 使用 alloca 指令得到的局部变量中时；
2. 某指针类型的变量指向的地址中时（其实这一点包括了第一点，因为使用 alloca 指令得到的变量，其类型也为指针）。

需要用到 store 指令：

```c++
/// 将数据存储在某指针类型的变量指向的地址中
/// Val：要存储的数据
/// Ptr：指针类型的变量，指向数据要存放的地址
StoreInst *CreateStore(Value *Val, Value *Ptr, bool isVolatile=false);
```

例如，对于`int a = 10`，要将常量10存入局部变量 a 中：

```c++
/// 1. 使用 alloca 指令创建局部变量 a 
llvm::AllocaInst *a = TheBuilder.CreateAlloca(TheBuilder.getInt32Ty(), nullptr, "a");

// 2. 使用 store 指令将常量10存储到局部变量 a 中
TheBuilder.CreateStore(TheBuilder.getInt32(10), a);
```

生成的 LLVM IR 如下：

```
%a = alloca i32
store i32 10, ptr %a
```

在本例中就可以发现，对于 %a ，LLVM IR 使用的是类型 ptr，也就是说明 %a 的数据类型其实是指针，指向数据存放的地址。

#### load 指令

当我们想要取出：

1. 使用 alloca 指令得到的局部变量中的值
2. 某指针类型的变量指向的地址中的数据（其实这一点包括了第一点，因为使用 alloca 指令得到的变量，其类型也为指针）

可以使用 load 指令：

```c++
/// 取出某指针类型的变量指向的地址中的数据
/// Ty：	 取出的值的类型
/// Ptr： 指针类型的变量，指向数据存放的地址
LoadInst *CreateLoad(Type *Ty, Value *Ptr, const Twine &Name = "");
```

如，对于`int a = 10; int b = a`：

```c++
/// 1. 使用 alloca 创建局部变量 a
llvm::AllocaInst *a = TheBuilder.CreateAlloca(TheBuilder.getInt32Ty(), nullptr, "a");

/// 2. 将常量10存入局部变量 a
TheBuilder.CreateStore(TheBuilder.getInt32(10), a);

/// 3. 使用 load 将局部变量 a 的值取出来，也即取出常量10
///    我们已经知道要取出的数据类型是 i32 了，Ty 参数的值为 i32
llvm::Value *aVal = TheBuilder.CreateLoad(llvm::Type::getInt32Ty(TheContext), a);

/// 4. 使用 alloca 创建局部变量 b
llvm::AllocaInst *b = TheBuilder.CreateAlloca(TheBuilder.getInt32Ty(), nullptr, "b");

/// 5. 将常量10存入 b 中
TheBuilder.CreateStore(aVal, b);
```

生成的 LLVM IR 如下：

```
%a = alloca i32
store i32 10, ptr %a
%0 = load i32, ptr %a ; 使用寄存器分配的局部变量，存储常量10
%b = alloca i32
store i32 %0, ptr %b
```

对于寄存器分配的局部变量，使用其值时不需要使用 load 指令，指令的结果已经直接存储在该局部变量中了，使用时直接传给需要它的接口即可。

如上例中的：

```c++
Value *aVal = TheBuilder.CreateLoad(a->getAllocatedType(), a);
```

该 load 指令的结果直接存储在寄存器 %0 中：`%0 = load i32, ptr %a`，使用时直接传给需要它的接口即可：

```c++
/// store i32 %0, ptr %b
TheBuilder.CreateStore(aVal, b);
```

#### 全局变量的取值和赋值

全局变量的存储也是需要分配内存空间的，而不是直接存储在寄存器中。因此实际上，全局变量也是指针类型。

例如 `@globalVar = global i32 10`，全局变量 @globalVar 为 i32 * 类型（LLVM IR 中显示为 ptr），指向 i32 类型的数据，该数据为 i32 10。

根据 [store](#store 指令) 和 [load](# load 指令) 两节可知：全局变量的赋值（非使用 llvm::Constant 的常量数据进行初始化）和取值也是分别使用 store 指令和 load 指令。 

例如：

```c++
/// 全局变量 a 的声明和定义
int a = 10;  

int main() {
    /* do something */
    
    /// 全局变量的取值
    int b = a;
    
    /// 全局变量的赋值
    a = 20;  
    
    /* do something */
}
```

生成 LLVM IR 的部分 C++ 参考代码如下：

```c++
/// 1. 创建全局变量 a，赋初始值常量10
auto a = llvm::GlobalVariable(TheModule, TheBuilder.getInt32Ty(), false,
                              llvm::GlobalVariable::ExternalLinkage,
                              TheBuilder.getInt32(10), "a");
/* Do something */

/// 在 main 函数中
/// 2. 创建局部变量 b
llvm::AllocaInst *b =
    TheBuilder.CreateAlloca(llvm::Type::getInt32Ty(TheContext), nullptr, "b");

/// 3. 在模块的符号表中查找全局变量 a
auto GloVarA = TheModule.getGlobalVariable("a");

/// 3. 使用 load 指令取出全局变量 a 的值
///    全局变量的存储也是需要分配内存空间的，因此全局变量 a 本身其实是指针类型
///    我们已经知道了要取出 i32 类型的数据了，Ty 参数的值为 i32
llvm::Value *valA =
    TheBuilder.CreateLoad(llvm::Type::getInt32Ty(TheContext), GloVarA);

/// 4. 使用 store 指令将全局变量 a 的值存入局部变量 b 中
TheBuilder.CreateStore(valA, b);

/// 5. 将常量20存入全局变量 a 中
TheBuilder.CreateStore(TheBuilder.getInt32(20), GloVarA);

/* Do something */
```

生成的部分 LLVM IR 如下：

```
@a = global i32 10  			; 创建全局变量 a

; do something
; 在 main 函数中

%b = alloca i32					; 创建局部变量 b
%0 = load i32, ptr @a			; 取出全局变量 a 的值
store i32 %0, ptr %b			; 将全局变量 a 的值存入 b 中
store i32 20, ptr @a    		; 将常量20存入全局变量 a 中

; do something
```

#### 在函数符号表中查找局部变量

了解 LLVM IR 中的函数，可见 [函数](#函数)

```c++
#include <llvm/IR/ValueSymbolTable.h>

llvm::Function *func = /* 获得 llvm::Function 实例指针 */;

// 以 varName 表示局部变量的名字，未找到则返回 nullptr
llvm::Value* var = func->getValueSymbolTable()->lookup(VarName);
```

### 数组

数组的创建可以参考 [创建全局变量](#创建全局变量) 和 [局部变量](#局部变量) 两节。

[创建数组常量](#创建数组常量) 和 [对任意类型创建0常量](#对任意类型创建0常量) 两节对于全局数组的初始化或许会有帮助。

使用全局构造函数来初始化全局数组和局部数组的初始化可以参考下面 [数组元素的访问](#数组元素的访问) 一节，通过 GEP 指令、[load](#load 指令) 指令和 [store](#store 指令) 指令来进行逐数组元素初始化。

#### 数组元素的访问

访问数组的元素需要用到 GEP（GetElementPtr，获取元素指针）指令，这个指令用于获取聚合数据结构的子元素的**地址**，在本实验中，即为获得数组元素的**地址**。GEP 指令**仅进行地址计算**，**而不进行内存访问**，其实质是将**指针偏移量**应用于**基指针**并返回**结果指针**。

在本次实验中，对于数组元素的访问，可以使用 llvm::IRBuilder 的 CreateInBoundsGEP()。

```c++
/// 根据索引列表，将指针偏移量应用于基指针，获得结果指针
/// Ty：		基指针 Ptr 指向的数据的类型
/// Ptr：	基指针
/// IdxList：索引列表
Value *CreateInBoundsGEP(Type *Ty, Value *Ptr, ArrayRef<Value *> IdxList, const Twine &Name="");
```

例如，对于int arr\[10\]\[5\]，如果我们想要访问 arr\[2\]\[1\]：

```C++
/// 数组的创建：
/// llvm::ArrayType *arrTy1D =
///     llvm::ArrayType::get(llvm::Type::getInt32Ty(TheContext), 5);
/// llvm::ArrayType *arrTy2D =
///     llvm::ArrayType::get(arrTy1D, 10);
/// auto arr = TheBuilder.CreateAlloca(arrTy2D, nullptr, "arr");
/// 省略对于数组 arr 的赋值

/// 索引
std::vector<llvm::Value *> idxList{
    TheBuilder.getInt64(0), TheBuilder.getInt64(2), TheBuilder.getInt64(1)};

/// GEP 指令访问 arr[2][1]
llvm::Value *val = TheBuilder.CreateInBoundsGEP(arrTy2D, arr, idxList);
```

产生的LLVM IR如下：

```
%0 = getelementptr inbounds [10 x [5 x i32]], ptr %arr, i64 0, i64 2, i64 1
```

llvm::IRBuilder 的 CreateInBoundsGEP() 产生的 LLVM IR 的基本语法如下：

```
<result> = getelementptr inbounds <ty>, ptr <ptrval> {, <ty> <idx>}
```

第一个`<ty>`：表示第一个索引指向的数据的类型，也即基指针指向的数据类型。在上述例子中，即为数组类型。

`<ptrval>`：表示基指针。

`<ty> <idx>`：表示一组索引的类型和索引值，`{...}`花括号表示一组或者多组索引，索引的类型`<ty>`一般为`i32`或者`i64`，索引值`<idx>`为具体的数字。索引指向的数据类型决定了增加索引值时，指针的偏移量为多少。每一组索引指向的数据类型都是不一样的，其索引值变化时，对应的指针偏移量的变化也不同。

细心的同学可能已经发现，我们想要访问 arr\[2\]\[1\]，为什么索引的第一位是0呢，为什么使用0、2、1的索引列表而不是直接2、1？

**全局数组和使用 alloca 指令分配内存得到的局部数组，其变量本质都是指针类型，指向对应的数组**。第一个索引0指向的数据类型即为 %arr 指向的数据类型，也就是 [10 x [5 x i32]] 的数组，索引值每变化1，对应的指针偏移量就为 10 * 5 * 32 位，而整个数组 %arr 的大小也正好就这么大。

通过第一个索引0可以取出 [10 x [5 x i32]] 的数组，该数组也可以看作 [5 x i32]* 类型的指针。对于该指针来说，第二个索引2就成为了其 getelementptr inbounds 指令的第一个索引，索引2指向的数据类型为 [5 x i32] 的数组。索引值每变化1，对应的指针偏移量就为 5 * 32 位。

通过第二个索引2就取出了 [5 x i32] 的数组，该数组可以看作 i32 *类型的指针。对于该指针来说，第三个索引1就成为了其 getelementptr inbounds 指令的第一个索引，索引1指向的数据类型为 i32 类型的整数。索引值每变化1，对应的指针偏移量就为32位。

我们想要访问 arr\[2\]\[1\]，口头计算加上我们的经验便可以知道：

我们是要访问 (arr的基地址 + 2\*5\*32 位+ 1\*32 位) 这个地址处开始的32位的数据。通过上述分析可知，GEP 指令以 %arr 的值为基地址，指针偏移量为 0\*10\*5\*32 + 2\*5\*32 + 1\*32，最终确实返回的是我们想要的 a\[2\]\[1\]处数据的指针，注意，**GEP 指令返回的是元素的指针**，也就是说，上例中 %result 其实是 i32 *，指向我们想要的 a\[2\]\[1\]。

对于数组元素的赋值和取值，因为我们通过 GEP 指令得到的是元素指针，是指针类型，那么我们便可以使用 [store](#store 指令) 和 [load](#load 指令) 指令。

例如，令 arr\[2\]\[1\]=2 并取出该值：

```C++
/// 索引
std::vector<llvm::Value *> idxList{
    TheBuilder.getInt64(0), TheBuilder.getInt64(2), TheBuilder.getInt64(1)};

/// GEP 指令访问 arr[2][1]
llvm::Value *element = TheBuilder.CreateInBoundsGEP(arrTy2D, arr, idxList);

/// store 指令赋值
TheBuilder.CreateStore(TheBuilder.getInt32(2), element);

/// load 指令取值
TheBuilder.CreateLoad(llvm::Type::getInt32Ty(TheContext), element);
```

生成的LLVM IR 如下：

```
; 取出元素指针
%0 = getelementptr inbounds [10 x [5 x i32]], ptr %arr, i64 0, i64 2, i64 1
; 赋值
store i32 2, ptr %0
; 取值
%1 = load i32, ptr %0
```

对 GEP 指令还有疑惑的，可以查看：

[GEP FAQ](https://llvm.org/docs/GetElementPtr.html)

[理解 getElementPtr](https://buaa-se-compiling.github.io/miniSysY-tutorial/lab7/help.html)

[LLVM's getelementptr, by example](https://blog.yossarian.net/2020/09/19/LLVMs-getelementptr-by-example)

### 函数

[llvm::Function Class Reference](https://llvm.org/doxygen/classllvm_1_1Function.html)

#### 函数声明/创建

```c++
#include <llvm/IR/Function.h>

// Ty：函数类型
// Linkage：函数的链接属性
// N：函数名字
// M：函数属于的模块
static Function *llvm::Function::Create(FunctionType *Ty, LinkageTypes Linkage, const Twine &N, Module *M);
```

例如，对于函数 void f(int a, int b)：

```c++
/// 函数类型：void(int, int)
llvm::FunctionType *funcType = llvm::FunctionType::get(
    llvm::Type::getVoidTy(TheContext),
    {llvm::Type::getInt32Ty(TheContext), llvm::Type::getInt32Ty(TheContext)},
    false);

/// 创建函数
llvm::Function *func = llvm::Function::Create(
    funcType, llvm::GlobalValue::ExternalLinkage, "f", &TheModule);
```

对应 LLVM IR 如下：

```
declare void @f(i32 %0, i32 %1)
```

此时函数并没有包含 [基本块 BasicBlock](#基本块)，我们仅仅是对函数进行了声明。

细心的同学可能会发现，LLVM IR 中，函数 f 的参数为 %0 和 %1，并不是源码中的 a 和 b，我们可以通过迭代器遍历函数 f 的参数列表，为每个参数设置名字：

```c++
auto argIter = func->arg_begin();

/// 设置第一个参数的名字为 a，并使 argIter ++
argIter++->setName("a"); 
/// 设置第二个参数的名字为 b
argIter->setName("b");
```

此时 LLVM IR 如下：

```
declare void @f(i32 %a, i32 %b)
```

#### 函数定义

在函数有了 [基本块](#基本块) 后，其便成了定义了的函数，在 LLVM IR 中， declare 关键字将自动变成 define。

#### 在模块符号表中查找函数

```c++
/// llvm::Module 的成员函数
/// 通过函数名字，在 llvm::Module 的符号表找到对应的函数
/// Name：要调用的函数的名字
Function *getFunction(StringRef Name) const;
```

例如，想找到名字为 f 的函数：

```c++
llvm::Function *func = TheModule.getFunction("f");
```

#### 调用函数

```c++
/// llvm::IRBuilder的成员函数
/// 创建 call 指令
/// Callee：	要调用的函数
/// Args：	调用函数时传入的实参列表，可不传参
CallInst *CreateCall(FunctionCallee Callee, ArrayRef<Value *> Args = None,
                       const Twine &Name = "", MDNode *FPMathTag = nullptr);
```

例如，想要调用函数 void f(int a, int b)，并传入参数常量1和2作为参数：

```c++
/// 通过 llvm::Module 的符号表找到对应的函数
llvm::Function *func = TheModule.getFunction("f");

/// 利用 llvm::IRBuilder 创建 call 指令
TheBuilder.CreateCall(
    func, {llvm::ConstantInt::get(llvm::Type::getInt32Ty(TheContext), 1),
        llvm::ConstantInt::get(llvm::Type::getInt32Ty(TheContext), 2)});
```

生成的 LLVM IR 如下：

```
call void @f(i32 1, i32 2)
```

如果想要调用函数 void f()，没有参数传入：

```c++
/// 通过 llvm::Module 的符号表找到对应的函数
Function *func = TheModule.getFunction("f");

// 利用 llvm::IRBuilder 创建 call 指令
TheBuilder.CreateCall(func);
```

结果如下：

```
call void @f()
```

#### 获得函数基本块

```c++
llvm::Function *func = /* 获得 llvm::Function 实例指针 */;

/// 遍历基本块列表
for(auto &Block : *func) {
    /* Do something */
}

/// 获得 entry 基本块
llvm::BasicBlock *entryBlock = func->getEntryBlock();
```

#### 获得当前函数所属Module

```C++
llvm::Function *func = /* 获得 llvm::Function 实例指针 */;

llvm::Module *module = func->getParent();
```

### 基本块

每一个定义了的函数都有若干个基本块，并且第一个基本块的标签（label）一定为 entry ，这是函数的入口基本块，函数执行时的第一个基本块。

#### 创建基本块

```c++
/// Name：	基本块的标签名，不取名则 LLVM 自动分配
/// Parent：	基本块所属的函数
static BasicBlock *llvm::BasicBlock::Create(LLVMContext &Context, 
                               const Twine &Name="", 
                               Function *Parent=nullptr, 
                               BasicBlock *InsertBefore=nullptr);
```

例如，在函数 func 中创建标签为 entry 基本块：

```c++
llvm::BasicBlock *block = llvm::BasicBlock::Create(TheContext, "entry", func);
```

#### 获得当前基本块所属的函数

```c++
llvm::Function *func = block->getParent();
```

#### 获得基本块的终结指令

在 LLVM IR 正确组织的情况下，每一个基本块的最后一条指令都应该是一条终结指令 [Terminator instructions](https://llvm.org/docs/LangRef.html#terminator-instructions)。

```c++
/// 如果Block没有终结指令，则inst = nullptr
/// 也可据此来判断该基本块是否有终结指令
llvm::Instruction *inst = Block->getTerminator();
```

#### 获得当前 llvm::IRBuilder 正在插入 LLVM IR 的基本块

```
llvm::BasicBlock *curBlock = TheBuilder.GetInsertBlock();
```

#### 基本块间跳转与变量传递

参见 [二元表达式->与&&](#条件跳转指令) 中短路求值的实现方法

### 二元表达式

#### 整数加法+

```C++
/// LHS + RHS

/// LHS：			加号左边操作数
/// RHS：			加号右边操作数
/// Name：			结果分配的寄存器的名字
/// NUW和NSW标志位：	 NUW表示No Unsigned Wrap，NSW表示No Signed Wrap
/// 				 如果设置了NUW和/或NSW，则分别保证了指令操作不会发生无符号/有符号溢出，
/// 				 如果有溢出发生，则指令的结果为poison value，
/// 				 如果没设置NUW和/或NSW，则LLVM会分别对无符号/有符号的溢出情况进行处理。
Value *CreateAdd (Value *LHS, Value *RHS, 
                  const Twine &Name="", 
                  bool HasNUW=false, bool HasNSW=false);
```

例如，对于 a+b：

```C++
/// 在函数符号表中查找局部变量 a 和 b
llvm::Value *a = func->getValueSymbolTable()->lookup("a");
llvm::Value *b = func->getValueSymbolTable()->lookup("b");

/// load 指令取出 a 和 b 的值
llvm::Value *valA = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), a);
llvm::Value *valB = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), b);

/// 进行加法
TheBuilder.CreateAdd(valA, valB);
```

生成的 LLVM IR 如下：

```
%0 = load i32, ptr %a
%1 = load i32, ptr %b
%2 = add i32 %0, %1
```

#### 整数减法-

```c
/// LHS - RHS
Value *CreateSub(Value *LHS, Value *RHS, 
                 const Twine &Name = "",
                 bool HasNUW = false, bool HasNSW = false);
```

例如，a-b：

```C++
/// load 指令取出 a 和 b 的值
llvm::Value *valA = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), a);
llvm::Value *valB = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), b);

TheBuilder.CreateSub(valA, valB);
```

生成的 LLVM IR 如下：

```
%0 = load i32, ptr %a
%1 = load i32, ptr %b
%2 = sub i32 %0, %1
```

#### 整数乘法*

```C++
/// LHS * RHS
Value *CreateMul(Value *LHS, Value *RHS, 
                 const Twine &Name="", 
                 bool HasNUW=false, bool HasNSW=false);
```

例如，a*b：

```C++
/// load 指令取出 a 和 b 的值
llvm::Value *valA = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), a);
llvm::Value *valB = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), b);

TheBuilder.CreateMul(valA, valB);
```

生成的 LLVM IR 如下：

```
%0 = load i32, ptr %a
%1 = load i32, ptr %b
%2 = mul i32 %0, %1
```

#### 整数除法/

```C++
/// 有符号整数除法
/// LHS / RHS
Value *CreateSDiv(Value *LHS, Value *RHS, 
                  const Twine &Name="", 
                  bool isExact=false);
```

例如， a/b：

```C++
/// load 指令取出 a 和 b 的值
llvm::Value *valA = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), a);
llvm::Value *valB = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), b);

TheBuilder.CreateSDIV(valA, valB);
```

生成的 LLVM IR 如下：

```
%0 = load i32, ptr %a
%1 = load i32, ptr %b
%2 = sdiv i32 %0, %1
```

#### 整数取余%

```C++
// 有符号整数取余
// LHS % RHS
Value *createSRem(Value *LHS, Value *RHS, const Twine &Name="");
```

例如，a%b：

```C++
/// load 指令取出 a 和 b 的值
llvm::Value *valA = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), a);
llvm::Value *valB = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), b);

TheBuilder.CreateSRem(valA, valB);
```

生成的 LLVM IR 如下：

```
%0 = load i32, ptr %a
%1 = load i32, ptr %b
%2 = srem i32 %0, %1
```

#### 整数比较

比较操作的返回值均为 i1 类型，也即 bool 类型。

##### 大于>

```C++
/// 有符号大于
/// LHS > RHS
Value *CreateICmpSGT(Value *LHS, Value *RHS, const Twine &Name="");
```

##### 大于等于>=

```C++
/// 有符号大于等于
/// LHS >= RHS
Value *CreateICmpSGE (Value *LHS, Value *RHS, const Twine &Name="");
```

##### 小于<

```C++
/// 有符号小于
/// LHS < RHS
Value *CreateICmpSLT(Value *LHS, Value *RHS, const Twine &Name="");
```

##### 小于等于<=

```C++
/// 有符号小于等于
/// LHS <= RHS
Value *CreateICmpSLE (Value *LHS, Value *RHS, const Twine &Name="")
```

##### 相等==

```C++
/// 相等
/// LHS == RHS
Value *CreateICmpEQ (Value *LHS, Value *RHS, const Twine &Name="");
```

##### 不相等!=

````C++
/// 不相等
/// LHS != RHS
Value *CreateICmpNE(Value *LHS, Value *RHS, const Twine &Name="");
````

#### 与&&

##### 短路求值思路参考

对于形如 exp_1 && exp_2 这样的与的表达式，其中 exp_1 和 exp_2 为具有真值的表达式，当 exp_1 和 exp_2 均为 true 时，整个表达式的值才为 true。换句话说，exp_1 或者 exp_2 为 false 时，整个表达式的值就为 false。

因此，在处理这个表达式的时候：

- 若 exp_1=true，则继续处理 exp_2：
  - 若 exp_2=true，整个表达式值为 true
  - 若 exp_2=false，整个表达式值为 false
- 若 exp_1=false，不必继续处理 exp_2 ，因为此时整个表达式的真值已经为 false

在生成这段表达式的 LLVM IR 时，可以参考采用下述基本块控制流：

将这个表达式的处理分为三个部分：

1. 处理 exp_1 的部分：

   在当前基本块中处理 exp_1，获得处理完 exp_1 后当前正在插入的基本块（因为处理 exp_1 可能需要创建多个基本块），在该基本块末尾创建条件跳转指令 br，如果 exp_1=true，跳转到标签为 land.rhs 的基本块，否则，跳转到标签为 land.end的基本块。

2. exp_1=true 接着处理 exp_2 的部分：

   在 land.rhs 基本块中，处理 exp_2，此基本块中已经确定 exp_1=true。获得处理完 exp_2 后当前正在插入的基本块，在该基本块的末尾创建无条件跳转指令，无条件跳转到 land.end 基本块。

3. 最后获得表达式的值的部分：

   在 land.end 基本块中，为了确定表达式的值，需要使用 phi 指令：

   - 如果是从处理 exp_1 的基本块跳转过来的，则表达式的值为 false，因为跳过了处理 exp_2；
   - 如果是从处理 exp_2 的基本块跳转过来的，则表达式的值与 exp_2 的值一样。

   之后利用该表达式的值进行后续的操作，如处理 if 或者 while。

注意，land.rhs 和 land.end 这些标签均可以自己取名。由于 exp_1 和 exp_2 可能不是原子逻辑表达式，即其可能嵌套了 && 或者 ||，因此处理 exp_1 或者 exp_2 时可能会涉及到多个基本块，不过子表达式基本块的控制流结构基本上也是一样的，都是对表达式处理三部分的嵌套。

##### 条件跳转指令

```C++
/// 如果 Cond=True，则跳转到 True 基本块，否则，跳转到 False 基本块
/// Cond：	条件，i1类型
/// True：	如果 Cond 为真，则跳转到 True 基本块
/// False：	如果 Cond 为假，则跳转到 False 基本块
BranchInst *CreateCondBr(Value *Cond, 
                         BasicBlock *True, 
                         BasicBlock *False, 
                         MDNode *BranchWeights=nullptr, MDNode *Unpredictable=nullptr);
```

例如 a==b && exp_2：

```C++
Value *eq = TheBuilder.CreateICmpEQ(valA, valB); /// 判断是否 a == b
BasicBlock *lhsTrueBlock = BasicBlock::Create(TheContext, "land.rhs", func);
BasicBlock *landEndBlock = BasicBlock::Create(TheContext, "land.end", func);
TheBuilder.CreateCondBr(eq, lhsTrueBlock, landEndBlock);
```

生成的 LLVM IR 如下：

```
br i1 %4, label %land.rhs, label %land.end  ; %4=true 则跳转到 %land.rhs，否则跳转到 %land.end
```

##### 无条件跳转指令

```C++
/// 无条件跳转到目标基本块
/// Dest：目标基本块
BranchInst *CreateBr(BasicBlock *Dest);
```

例如：

```C++
TheBuilder.CreateBr(landEndBlock);
```

生成的 LLVM IR 如下：

```
br label %land.end
```

##### phi 指令

phi 指令（Phi Instruction）是在 LLVM IR 中用于处理基本块间值传递的指令。它用于合并不同的路径上的值，通常出现在基本块的开头，用于指定从不同的前驱基本块传递过来的值。

在 LLVM IR 中，phi 指令的语法为：

```
%result = phi <ty> [ %value1, %block1 ], [ %value2, %block2 ], ...
```

- `%result`： phi 指令的结果，表示从前驱基本块传递过来的值存放在该寄存器中。
- `<ty>`：结果值的类型。
- `[%value1, %block1], [%value2, %block2], ...`：每个方括号表示一个前驱基本块和从基本块传递过来的值，`%value1`、`%value2` 等是前驱基本块传递过来的值，`%block1`、`%block2` 等是对应的前驱基本块。

如果当前基本块是从`%blockn`基本块跳转过来的，则`%result`的值等于`%valuen`。

要想使用 phi 指令，首先需要创建 phi 节点：

```C++
/// Ty：：				指定创建的 PHINode 的结果的类型，即上述语法中的 <ty>
/// NumReservedValues：	 表示 PHINode 要处理多少前驱基本块，有多少候选值，即上述语法中 [%value %block] 对的数量
PHINode *CreatePHI(Type *Ty, unsigned NumReservedValues, const Twine &Name="");
```

之后，使用 addIncoming() 函数来为 PHINode 添加前驱基本块和值，即添加 `[%value %block] `对。

```C++
/// PHINode成员函数
/// V：	前驱基本块传过来的值
/// BB：	前驱基本块
void addIncoming(Value *V, BasicBlock *BB)
```

例如：

```C++
PHINode *phi = TheBuilder.CreatePHI(Type::getInt1Ty(TheContext), 2, "merge");
phi->addIncoming(eq, Block);
phi->addIncoming(gt, lhsTrueBlock);
```

生成的IR如下：

```
%merge = phi i1 [ %4, %entry ], [ %5, %land.rhs ]
```

##### 与的例子

例如，对于表达式 a > b && b > c，三者均为 i32 类型。

```C++
/// 在函数符号表中查找局部变量 a、b、c
llvm::Value *varA = func->getValueSymbolTable()->lookup("a");
llvm::Value *varB = func->getValueSymbolTable()->lookup("b");
llvm::Value *varC = func->getValueSymbolTable()->lookup("c");

/// load 指令取出 a、b、c 的值
llvm::Value *valA = TheBuilder.CreateLoad(llvm::Type::getInt32Ty(TheContext), varA);
llvm::Value *valB = TheBuilder.CreateLoad(llvm::Type::getInt32Ty(TheContext), varB);
llvm::Value *valC = TheBuilder.CreateLoad(llvm::Type::getInt32Ty(TheContext), varC);

/// a > b
llvm::Value *aGTb = TheBuilder.CreateICmpEQ(valA, valB);

llvm::BasicBlock *lhsTrueBlock = llvm::BasicBlock::Create(TheContext, "land.rhs", func);
llvm::BasicBlock *landEndBlock = llvm::BasicBlock::Create(TheContext, "land.end", func);
/// a > b为真，则跳转到 land.rhs，否则，跳转到 land.end
TheBuilder.CreateCondBr(aGTb, lhsTrueBlock, landEndBlock);

/// 将当前 IR 插入点设置为 land.rhs，因为要处理 exp_2，即 b > c
TheBuilder.SetInsertPoint(lhsTrueBlock);
/// b > c
llvm::Value *bGTc = TheBuilder.CreateICmpSGT(valB, valB);
// 无条件跳转到 land.end
TheBuilder.CreateBr(landEndBlock);

TheBuilder.SetInsertPoint(landEndBlock);
/// phi指令
llvm::PHINode *phi = TheBuilder.CreatePHI(llvm::Type::getInt1Ty(TheContext), 2, "merge");
phi->addIncoming(TheBuilder.getInt1(false), Block);
phi->addIncoming(bGTc, lhsTrueBlock);
```

生成的 LLVM IR 如下：

```
; ........................................
	%0 = load i32, ptr %a, align 4
    %1 = load i32, ptr %b, align 4
    %2 = load i32, ptr %c, align 4
    %3 = icmp eq i32 %0, %1
    br i1 %3, label %land.rhs, label %land.end

land.rhs:                                         ; preds = %entry
    %4 = icmp sgt i32 %1, %1
    br label %land.end

land.end:                                         ; preds = %land.rhs, %entry
    %merge = phi i1 [ false, %entry ], [ %4, %land.rhs ]
```

#### 或||

##### 短路求值思路参考

和 [与&&](#与&&) 类似。

对于形如 exp_1 || exp_2 这样的或的表达式，其中 exp_1 和 exp_2 为具有真值的表达式，当 exp_1 或者 exp_2 为 true 时，整个表达式的值就为 true。

因此，在处理这个表达式的时候：

- 若 exp_1=false，则继续处理 exp_2：
  - 若 exp_2=true，整个表达式值为 true
  - 若 exp_2=false，整个表达式值为 false
- 若 exp_1=true，不必继续处理 exp_2 ，因为此时整个表达式的真值已经为 false

在生成这段表达式的 LLVM IR 时，可以参考采用下述基本块控制流：

将这个表达式的处理分为三个部分：

1. 处理 exp_1 的部分：

   在当前基本块中处理 exp_1，获得处理完 exp_1 后当前正在插入的基本块（因为处理 exp_1 可能需要创建多个基本块），在该基本块末尾创建条件跳转指令 br，如果 exp_1=true，跳转到标签为 lor.end 的基本块，表达式的值已经为 true，不需要 计算 exp_2，否则，跳转到标签为 lor.rhs 的基本块。

2. exp_1=false 接着处理 exp_2 的部分：

   在 lor.rhs 基本块中处理 exp_2，此基本块中已经确定 exp_1=false，表达式的值等于 exp_2 的值，获得处理完 exp_2 后当前正在插入的基本块，在该基本块的末尾创建无条件跳转指令，无条件跳转到 lor.end 基本块。

3. 最后获得表达式的值的部分：

   在 lor.end 基本块中，为了确定表达式的值，需要使用 phi 指令：

   - 如果是从处理 exp_1 的基本块跳转过来的，则表达式的值为 true，因为跳过了处理 exp_2；
   - 如果是从处理 exp_2 的基本块跳转过来的，则表达式的值与 exp_2 的值一样。

   之后利用该表达式的值进行后续的操作，如处理 if 或者 while。

##### 或的例子

例如，对于表达式 a > b || b > c，三者均为 i32 类型：

```c++
/// 在函数符号表中查找局部变量 a、b、c
llvm::Value *varA = func->getValueSymbolTable()->lookup("a");
llvm::Value *varB = func->getValueSymbolTable()->lookup("b");
llvm::Value *varC = func->getValueSymbolTable()->lookup("c");

/// load 指令取出 a、b、c 的值
llvm::Value *valA = TheBuilder.CreateLoad(llvm::Type::getInt32Ty(TheContext), varA);
llvm::Value *valB = TheBuilder.CreateLoad(llvm::Type::getInt32Ty(TheContext), varB);
llvm::Value *valC = TheBuilder.CreateLoad(llvm::Type::getInt32Ty(TheContext), varC);

/// a > b
llvm::Value *aGTb = TheBuilder.CreateICmpEQ(valA, valB);

llvm::BasicBlock *lhsFalseBlock = llvm::BasicBlock::Create(TheContext, "lor.rhs", func);
llvm::BasicBlock *lorEndBlock = llvm::BasicBlock::Create(TheContext, "lor.end", func);
/// a > b为真，则跳转到 lor.end，否则，跳转到 lor.rhs
TheBuilder.CreateCondBr(aGTb, lorEndBlock, lhsFalseBlock);

/// 将当前 IR 插入点设置为 lor.rhs，因为要处理 exp_2，即 b > c
TheBuilder.SetInsertPoint(lhsFalseBlock);
/// b > c
llvm::Value *bGTc = TheBuilder.CreateICmpSGT(valB, valC);
// 无条件跳转到 lor.end
TheBuilder.CreateBr(lorEndBlock);

TheBuilder.SetInsertPoint(lorEndBlock);
/// phi指令
llvm::PHINode *phi = TheBuilder.CreatePHI(llvm::Type::getInt1Ty(TheContext), 2, "merge");
phi->addIncoming(TheBuilder.getInt1(true), Block);
phi->addIncoming(bGTc, lhsFalseBlock);
```

生成的 LLVM IR 如下：

```
; ........................................
  %0 = load i32, ptr %a, align 4
  %1 = load i32, ptr %b, align 4
  %2 = load i32, ptr %c, align 4
  %3 = icmp eq i32 %0, %1
  br i1 %3, label %lor.end, label %lor.rhs

lor.rhs:                                          ; preds = %entry
  %4 = icmp sgt i32 %1, %2
  br label %lor.end

lor.end:                                          ; preds = %lor.rhs, %entry
  %merge = phi i1 [ true, %entry ], [ %4, %lor.rhs ]
```

### 一元表达式

#### 非!

```c++
/// 将对 V 进行按位取反操作
Value *CreateNot(Value *V, const Twine &Name="");
```

例如 !(a>b)，两个遍历均为 i32 类型：

```C++
/// load 指令取出 a 和 b 的值
llvm::Value *valA = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), varA);
llvm::Value *valB = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), varB);

// a > b
llvm::Value *cmp = TheBuilder.CreateICmpSGT(valA, valB);

// 非
TheBuilder.CreateNot(cmp);
```

生成的 LLVM IR 如下：

```
%0 = load i32, ptr %a
%1 = load i32, ptr %b
%2 = icmp sgt i32 %0, %1	; a > b
%3 = xor i1 %2, true		; !(a > b)
```

#### 取负-

```C++
/// 用于创建整数的取负操作
/// 对 V 进行取负
Value *CreateNeg (Value *V, const Twine &Name="", bool HasNUW=false, bool HasNSW=false);
```

例如 b=-a：

```C++
/// load指令取出 a 的值
llvm::Value *valA = TheBuilder.CreateLoad(TheBuilder.getInt32Ty(), varA);

/// 取负，-a
llvm::Value *negValA = TheBuilder.CreateNeg(valA);

/// b = -a
TheBuilder.CreateStore(negValA, varB);
```

生成的 LLVM IR 如下：

```
%0 = load i32, ptr %a
%1 = sub i32 0, %0      ; -a
store i32 %1, ptr %b	; b = -a
```
