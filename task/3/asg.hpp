#pragma once

#include "Obj.hpp"
#include <string>
#include <cstdint>

namespace asg {

//==============================================================================
// 类型
//==============================================================================

struct TypeExpr;
struct Expr;
struct Decl;

struct Type : Obj
{
  /// 说明（Specifier）
  enum struct Spec : std::uint8_t
  {
    kINVALID,
    kVoid,
    kChar,
    kInt,
    kLong,
    kLongLong,
  };

  /// 限定（Qualifier）
  struct Qual
  {
    bool const_{ false };
    // bool volatile_{ false };

    bool operator==(const Qual& other) const { return const_ == other.const_; }
    bool operator!=(const Qual& other) const { return !operator==(other); }
  };

  Spec spec{ Spec::kINVALID };
  Qual qual;

  TypeExpr* texp{ nullptr };

  /**
   * @brief 类型等价性判断，等价性是类型系统最重要的性质，我们在这里而不是
   * 在 Typing 中实现。
   */
  bool operator==(const Type& other) const;
  bool operator!=(const Type& other) const { return !operator==(other); }

private:
  void __mark__(Mark mark) override;

public:
  /**
   * @brief 类型缓存
   *
   * 编译过程中，尤其是语法分析和类型推导阶段，会有大量的语义节点包含相同的
   * 类型或子类型，重复创建这些类型节点会导致无谓的内存占用，因此使用这个类
   * 型缓存器。考虑到我们测例中不会包含太多的类型种类，这里的实现采用了简单
   * 的线性查找算法，更高级的做法是设计有唯一性的类型编码方法，然后使用哈希
   * 表来映射和查找。
   */
  struct Cache : std::vector<const Type*>
  {
    Obj::Mgr& mMgr;

    Cache(Obj::Mgr& mgr)
      : mMgr(mgr)
    {
    }

    const Type* operator()(Spec spec, Qual qual, TypeExpr* texp);
  };
};

struct TypeExpr : Obj
{
  TypeExpr* sub{ nullptr };

  bool operator==(const TypeExpr& other) const
  {
    if (this == &other)
      return true;
    if (this == nullptr || &other == nullptr)
      return false;
    return __equal__(other);
  }

  bool operator!=(const TypeExpr& other) const { return !operator==(other); }

protected:
  void __mark__(Mark mark) override;

private:
  virtual bool __equal__(const TypeExpr& other) const = 0;
};

struct PointerType : TypeExpr
{
  Type::Qual qual;

private:
  bool __equal__(const TypeExpr& other) const override;
};

struct ArrayType : TypeExpr
{
  std::uint32_t len{ 0 }; /// 数组长度，kUnLen 表示未知
  static constexpr std::uint32_t kUnLen = UINT32_MAX;

private:
  bool __equal__(const TypeExpr& other) const override;
};

struct FunctionType : TypeExpr
{
  std::vector<const Type*> params;

private:
  void __mark__(Mark mark) override;
  bool __equal__(const TypeExpr& other) const override;
};

//==============================================================================
// 表达式
//==============================================================================

struct Decl;

struct Expr : Obj
{
  enum struct Cate : std::uint8_t
  {
    kINVALID,
    kRValue,
    kLValue,
  };

  const Type* type;
  Cate cate{ Cate::kINVALID };

protected:
  void __mark__(Mark mark) override;
};

struct IntegerLiteral : Expr
{
  std::uint64_t val{ 0 };
};

struct StringLiteral : Expr
{
  std::string val;
};

struct DeclRefExpr : Expr
{
  Decl* decl{ nullptr };

private:
  void __mark__(Mark mark) override;
};

struct ParenExpr : Expr
{
  Expr* sub{ nullptr };

private:
  void __mark__(Mark mark) override;
};

struct UnaryExpr : Expr
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

private:
  void __mark__(Mark mark) override;
};

struct BinaryExpr : Expr
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

private:
  void __mark__(Mark mark) override;
};

struct CallExpr : Expr
{
  Expr* head{ nullptr };
  std::vector<Expr*> args;

private:
  void __mark__(Mark mark) override;
};

struct InitListExpr : Expr
{
  std::vector<Expr*> list;

private:
  void __mark__(Mark mark) override;
};

struct ImplicitInitExpr : Expr
{};

struct ImplicitCastExpr : Expr
{
  enum
  {
    kINVALID,
    kLValueToRValue,
    kIntegralCast,
    kArrayToPointerDecay,
    kFunctionToPointerDecay,
    kNoOp,
  } kind{ kINVALID };
  Expr* sub{ nullptr };

private:
  void __mark__(Mark mark) override;
};

//==============================================================================
// 语句
//==============================================================================

struct FunctionDecl;

struct Stmt : Obj
{};

struct NullStmt : Stmt
{
protected:
  void __mark__(Mark mark) override;
};

struct DeclStmt : Stmt
{
  std::vector<Decl*> decls;

private:
  void __mark__(Mark mark) override;
};

struct ExprStmt : Stmt
{
  Expr* expr{ nullptr };

private:
  void __mark__(Mark mark) override;
};

struct CompoundStmt : Stmt
{
  std::vector<Stmt*> subs;

private:
  void __mark__(Mark mark) override;
};

struct IfStmt : Stmt
{
  Expr* cond{ nullptr };
  Stmt *then{ nullptr }, *else_{ nullptr };

private:
  void __mark__(Mark mark) override;
};

struct WhileStmt : Stmt
{
  Expr* cond{ nullptr };
  Stmt* body{ nullptr };

private:
  void __mark__(Mark mark) override;
};

struct DoStmt : Stmt
{
  Stmt* body{ nullptr };
  Expr* cond{ nullptr };

private:
  void __mark__(Mark mark) override;
};

struct BreakStmt : Stmt
{
  Stmt* loop{ nullptr };

private:
  void __mark__(Mark mark) override;
};

struct ContinueStmt : Stmt
{
  Stmt* loop{ nullptr };

private:
  void __mark__(Mark mark) override;
};

struct ReturnStmt : Stmt
{
  FunctionDecl* func{ nullptr };
  Expr* expr{ nullptr };

private:
  void __mark__(Mark mark) override;
};

//==============================================================================
// 声明
//==============================================================================

struct Decl : Obj
{
  const Type* type;
  std::string name;

protected:
  void __mark__(Mark mark) override;
};

struct VarDecl : Decl
{
  Expr* init{ nullptr };

private:
  void __mark__(Mark mark) override;
};

struct FunctionDecl : Decl
{
  std::vector<Decl*> params;
  CompoundStmt* body{ nullptr };

private:
  void __mark__(Mark mark) override;
};

//==============================================================================
// 顶层
//==============================================================================

struct TranslationUnit : Obj
{
  std::vector<Decl*> decls;

private:
  void __mark__(Mark mark) override;
};

} // namespace asg
