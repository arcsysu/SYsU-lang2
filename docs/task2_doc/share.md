# 两种实现方式的共有代码

在 `COMMON` 文件夹下存在如下几个代码文件，这几个文件是无论使用 `ANTLR` 还是使用 `BISON` 进行实验二的实现都会用到的代码，在这里对这几个文件进行统一的解读。

```bash
-- common
   |-- Asg2Json.cpp
   |-- Asg2Json.hpp
   |-- Typing.cpp
   |-- Typing.hpp
   `-- asg.hpp
```


## asg.hpp 代码介绍

`asg.hpp` 文件定义了一个用于表示抽象语法图（`Abstract Syntax Graph`，简称 `ASG`）的数据结构，这是在编译器设计中用于表示源代码结构的一种高级表示形式。这个文件中定义的结构和类用于表示编程语言的不同构件，如类型、表达式、语句等。


## 基础类Obj

首先是基础类 `Obj` 的定义，

- **Obj** : 表示 ASG 中所有节点的基类，提供了类型转换的方法 (`dcst`, `scst`, `rcst`) 和一个 `std::any` 类型的成员 `any`，用于存储任意类型的附加数据。后面的类型系统类，表达式类，语句类，声明类等都由 `Obj` 类派生出来。
- **Mgr** : `Obj` 的嵌套类，用于管理 `Obj` 对象的生命周期，包括创建和销毁对象。这是一个包含 `std::unique_ptr<Obj>` 的向量，提供了 `make` 模板方法用于创建新对象。
- **Walked** : 用于防止在遍历 ASG 时发生循环引用，通过在构造时标记节点，在析构时清除标记。
- **Ptr** : 一个模板类，用于表示对 ASG 节点的类型安全的指针，支持有限的泛型。

```cpp
struct Obj
{
  std::any any; /// 留给遍历器存放任意数据

  virtual ~Obj() = default;

  template<typename T>
  T* dcst()
  {
    return dynamic_cast<T*>(this);
  }

  template<typename T>
  T* scst()
  {
    return static_cast<T*>(this);
  }

  template<typename T>
  T& rcst()
  {
    return *reinterpret_cast<T*>(this);
  }

  struct Mgr : public std::vector<std::unique_ptr<Obj>>
  {
    template<typename T, typename... Args>
    T& make(Args... args)
    {
      auto ptr = std::make_unique<T>(args...);
      auto& obj = *ptr;
      emplace_back(std::move(ptr));
      return obj;
    }
  };

  /// 检查循环引用，防止无限递归。
  struct Walked
  {
    Obj* mObj;

    Walked(Obj* obj)
      : mObj(obj)
    {
      ASSERT(!mObj->any.has_value());
      mObj->any = nullptr;
    }

    ~Walked() { mObj->any.reset(); }
  };

  /// 有限泛型的指针模板类
  template<typename... Ts>
  struct Ptr
  {
    static_assert(all_true<std::is_convertible_v<Ts*, Obj*>...>::value);

    Obj* mObj{ nullptr };

    Ptr() {}

    Ptr(std::nullptr_t) {}

    template<typename T,
             typename = std::enable_if_t<is_one_of<T, Ts...>::value>>
    Ptr(T* p)
      : mObj(p)
    {
    }

    operator bool() { return mObj != nullptr; }

    template<typename T,
             typename = std::enable_if_t<is_one_of<T, Ts...>::value>>
    T* dcst()
    {
      return dynamic_cast<T*>(mObj);
    }

    template<typename T,
             typename = std::enable_if_t<is_one_of<T, Ts...>::value>>
    T& rcst()
    {
      return *reinterpret_cast<T>(mObj);
    }
  };
};
```



## 类型系统

然后是**类型系统类**的定义,下面的代码首先定义了一套类型系统，用于在编译器中表示和处理变量、表达式和函数的类型信息。基本类型信息(`Type`)提供了对简单数据类型的描述，而类型表达式(`TypeExpr` 及其派生类)则用于表示更复杂的类型结构，如指针、数组和函数类型。这套类型系统是编译器实现类型检查、类型推断和代码生成等任务的基础。

```cpp
struct TypeExpr;
struct Expr;
struct Decl;

struct Type
{
  /// 说明（Specifier）
  enum class Spec : std::uint8_t
  {
    kINVALID,
    kVoid,
    kChar,
    kInt,
    kLong,
    kLongLong,
  };

  /// 限定（Qualifier）
  enum class Qual : std::uint8_t
  {
    kNone,
    kConst,
    // kVolatile,
  };

  Spec spec{ Spec::kINVALID };
  Qual qual{ Qual::kNone };

  TypeExpr* texp{ nullptr };
};

struct TypeExpr : public Obj
{
  TypeExpr* sub{ nullptr };
};

struct PointerType : public TypeExpr
{
  Type::Qual qual{ Type::Qual::kNone };
};

struct ArrayType : public TypeExpr
{
  std::uint32_t len{ 0 }; /// 数组长度，kUnLen 表示未知
  static constexpr std::uint32_t kUnLen = UINT32_MAX;
};

struct FunctionType : public TypeExpr
```

 **Type 结构体 :**

* Spec : 枚举类型，定义了基本的数据类型（如 `void`, `char`, `int`, `long`, `long long`），用于表示变量或表达式的数据类型。
* Qual : 枚举类型，定义了类型限定符（如 `const`），用于增加类型的限定信息。
* texp : 指向 `TypeExpr` 的指针，用于表示更复杂的类型结构，比如指针、数组或函数类型。

 **TypeExpr 结构体及其派生 :**

* 它是一个从 `Obj` 派生的基类，表示所有类型表达式的基础。`TypeExpr` 通过继承 `Obj`，成为抽象语法图（ASG）的一部分，允许在 ASG 中以统一的方式处理类型信息。
* sub : 表示类型表达式的子类型，用于构建嵌套的类型表达式，如指针的指向类型或数组元素的类型。

 **派生自 TypeExpr 的几种类型 :**

* PointerType : 表示指针类型，增加了 `qual` 成员来表示指针所指向的类型的限定符（如 `const`）。
* ArrayType : 表示数组类型，增加了 `len` 成员来表示数组的长度，其中 `kUnLen` 表示长度未知的情况。
* FunctionType : 表示函数类型，通过 `params` 成员来表示函数参数的类型列表。


## 表达式

以下代码定义了抽象语法树（`AST`）中表达式节点的结构和类型，是编译器前端在语法分析和语义分析阶段使用的。每种表达式类型都继承自基类 `Expr `，它本身继承自 `Obj`，意味着所有表达式节点都是抽象语法图（`ASG`）的一部分。

```cpp
struct Decl;

struct Expr : public Obj
{
  enum class Cate : std::uint8_t
  {
    kINVALID,
    kRValue,
    kLValue,
  };

  Type type;
  Cate cate{ Cate::kINVALID };
};

struct IntegerLiteral : public Expr
{
  std::uint64_t val{ 0 };
};

struct StringLiteral : public Expr
{
  std::string val;
};

struct DeclRefExpr : public Expr
{
  Decl* decl{ nullptr };
};

struct ParenExpr : public Expr
{
  Expr* sub{ nullptr };
};

struct UnaryExpr : public Expr
{
  enum Op
  {
    kINVALID,
    kPos,
    kNeg,
    kNot
  };

  Op op{ kINVALID };
  Expr* sub{ nullptr };
};

struct BinaryExpr : public Expr
{
  enum Op
  {
    kINVALID,
    kMul,
    kDiv,
    kMod,
    kAdd,
    kSub,
    kGt,
    kLt,
    kGe,
    kLe,
    kEq,
    kNe,
    kAnd,
    kOr,
    kAssign,
    kComma,
    kIndex,
  };

  Op op{ kINVALID };
  Expr *lft{ nullptr }, *rht{ nullptr };
};

struct CallExpr : public Expr
{
  Expr* head{ nullptr };
  std::vector<Expr*> args;
};

struct InitListExpr : public Expr
{
  std::vector<Expr*> list;
};

struct ImplicitInitExpr : public Expr
{};

struct ImplicitCastExpr : public Expr
```

其中，

 **Expr 结构体** : 作为所有表达式类型的基类，包含了共同的属性：

* `Cate`: 表示表达式的类别，即是左值（可以出现在赋值运算符的左侧）还是右值（通常表示临时值或字面量）。
* `Type`: 表示表达式的类型信息，包括基本类型（如 `int`、`float`）和更复杂的类型（如指针、数组）。

 **具体的表达式类型** :

* **IntegerLiteral** : 表示整数字面量的表达式。
* **StringLiteral** : 表示字符串字面量的表达式。
* **DeclRefExpr** : 表示对声明的引用，如变量名或函数名。
* **ParenExpr** : 表示括号表达式，用于改变运算顺序或仅仅为了清晰。
* **UnaryExpr** : 表示一元运算表达式，如取反、逻辑非等。
* **BinaryExpr** : 表示二元运算表达式，如加减乘除、逻辑与或等。
* **CallExpr** : 表示函数调用表达式。
* **InitListExpr** : 表示初始化列表表达式，用于数组或结构体的初始化。
* **ImplicitInitExpr** : 表示隐式初始化表达式，可能用于默认初始化。
* **ImplicitCastExpr** : 表示隐式类型转换表达式，如自动类型提升或类型转换。

每种表达式类型通过特有的成员变量来表示其独特的语义和结构。例如，`UnaryExpr` 包含一个操作符和一个子表达式，`BinaryExpr` 包含一个操作符和两个子表达式（左右），而 `CallExpr` 包含一个表示被调用函数的表达式和一个参数表达式列表。


## 语句

以下代码定义了在抽象语法树（`AST`）或抽象语法图（`ASG`）中表示程序语句的结构和类型，是编译器前端在构建 `AST`或 `ASG`时使用的。每种语句类型都继承自基类 `Stmt `，它本身继承自 `Obj`，意味着所有语句节点都是 `ASG`的一部分。

```cpp
struct FunctionDecl;

struct Stmt : public Obj
{};

struct NullStmt : public Stmt
{};

struct DeclStmt : public Stmt
{
  std::vector<Decl*> decls;
};

struct ExprStmt : public Stmt
{
  Expr* expr{ nullptr };
};

struct CompoundStmt : public Stmt
{
  std::vector<Stmt*> subs;
};

struct IfStmt : public Stmt
{
  Expr* cond{ nullptr };
  Stmt *then{ nullptr }, *else_{ nullptr };
};

struct WhileStmt : public Stmt
{
  Expr* cond{ nullptr };
  Stmt* body{ nullptr };
};

struct DoStmt : public Stmt
{
  Stmt* body{ nullptr };
  Expr* cond{ nullptr };
};

struct BreakStmt : public Stmt
{
  Stmt* loop{ nullptr };
};

struct ContinueStmt : public Stmt
{
  Stmt* loop{ nullptr };
};

struct ReturnStmt : public Stmt
{
  FunctionDecl* func{ nullptr };
  Expr* expr{ nullptr };
};
```

其中，

**Stmt 结构体** : 作为所有语句类型的基类，没有包含具体的成员变量，主要用于多态地处理不同类型的语句。

**具体的语句类型** :

* **NullStmt** : 空语句，通常表示一个占位或无操作的语句（如单独的分号 `;`）。
* **DeclStmt** : 声明语句，包含一组声明，如变量或函数的声明。
* **ExprStmt** : 表达式语句，包含一个表达式，通常是一个操作的执行，如函数调用或赋值操作。
* **CompoundStmt** : 复合语句（或块语句），包含一系列其他语句，通常用花括号 `{}` 包裹。
* **IfStmt** : 条件语句，包含一个条件表达式和两个分支（then和else），根据条件表达式的值执行其中一个分支。
* **WhileStmt** : while循环语句，包含一个条件表达式和一个循环体，只要条件为真，就循环执行循环体。
* **DoStmt** : do-while循环语句，类似于while循环，但保证循环体至少执行一次，之后再检查条件。
* **BreakStmt** : 跳出循环语句，用于立即退出最近的包围循环。
* **ContinueStmt** : 继续下一次循环语句，用于立即跳至最近的包围循环的下一个迭代。
* **ReturnStmt** : 返回语句，用于从函数返回值或结束函数的执行。包含一个可选的返回值表达式。

这些语句类型覆盖了编程语言中的基本语句结构，允许编译器解析源代码并构建表示程序逻辑的AST或ASG。通过这些结构，编译器能够进行语法检查、语义分析，并为后续的优化和代码生成阶段准备数据结构。


## 声明

以下代码定义了抽象语法树（`AST`）中用于表示程序中的声明（`declarations`）的结构和类型，是编译器前端在解析和处理程序源代码时使用的。

```cpp
struct Decl : public Obj
{
  Type type;
  std::string name;
};

struct VarDecl : public Decl
{
  Expr* init{ nullptr };
};

struct FunctionDecl : public Decl
{
  std::vector<Decl*> params;
  CompoundStmt* body{ nullptr };
};

using TranslationUnit = std::vector<Decl*>;
```

其中，

 **Decl 结构体** : 作为所有声明类型的基类，包含了每个声明共有的属性：

* `Type`: 声明的类型，用于描述变量的数据类型或函数返回类型等。
* `name`: 声明的名称，例如变量名或函数名。

 **具体的声明类型** :

* **VarDecl** : 变量声明，继承自 `Decl`。除了基类的 `type` 和 `name` 属性外，还包含一个可选的 `init` 表达式用于初始化变量。
* **FunctionDecl** : 函数声明，也继承自 `Decl`。除了 `type` 和 `name`，还包含参数列表 `params`（每个参数也是一个 `Decl` 类型的对象）和函数体 `body`（一个复合语句，由多个其他语句组成）。

**TranslationUnit** : 是一个 `Decl` 类型的对象的向量（`vector`），用于表示一个翻译单元（通常是一个源文件）。翻译单元包含了该源文件中的所有顶层声明，如全局变量声明和函数定义。

总体来说，这段代码为编译器提供了一种方式来表示和处理程序中的各种声明。通过这些声明的结构，编译器能够解析源代码中的变量声明和函数定义，构建相应的AST或ASG，以便进行后续的语义分析、优化和代码生成等任务。
