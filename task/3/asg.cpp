#include "asg.hpp"

namespace asg {

//==============================================================================
// 类型
//==============================================================================

bool
Type::operator==(const Type& other) const
{
  if (this == &other)
    return true;
  if (spec != other.spec || qual != other.qual)
    return false;
  return *texp == *other.texp;
}

void
Type::__mark__(Mark mark)
{
  mark(texp);
}

const Type*
Type::Cache::operator()(Spec spec, Qual qual, TypeExpr* texp)
{
  for (auto&& i : *this) {
    if (i->spec == spec && i->qual == qual) {
      if (texp == i->texp)
        return i;
      if (texp == nullptr || i->texp == nullptr)
        continue;
      if (*texp == *i->texp)
        return i;
    }
  }
  auto ty = mMgr.make<Type>();
  ty->spec = spec, ty->qual = qual, ty->texp = texp;
  push_back(ty);
  return ty;
}

bool
TypeExpr::__equal__(const TypeExpr& other) const
{
  return *sub == *other.sub;
}

void
TypeExpr::__mark__(Mark mark)
{
  mark(sub);
}

bool
PointerType::__equal__(const TypeExpr& other) const
{
  if (this == &other)
    return true;
  auto p = dynamic_cast<const PointerType*>(&other);
  if (p == nullptr)
    return false;

  if (qual != p->qual)
    return false;
  return *sub == *p->sub;
}

bool
ArrayType::__equal__(const TypeExpr& other) const
{
  if (this == &other)
    return true;
  auto p = dynamic_cast<const ArrayType*>(&other);
  if (p == nullptr)
    return false;

  if (len != p->len)
    return false;
  return *sub == *p->sub;
}

void
FunctionType::__mark__(Mark mark)
{
  for (auto&& i : params)
    mark(const_cast<Type*>(i));
  TypeExpr::__mark__(mark);
}

bool
FunctionType::__equal__(const TypeExpr& other) const
{
  if (this == &other)
    return true;
  auto p = dynamic_cast<const FunctionType*>(&other);
  if (p == nullptr)
    return false;

  if (params.size() != p->params.size())
    return false;
  for (size_t i = 0; i < params.size(); ++i)
    if (*params[i] != *p->params[i])
      return false;
  return true;
}

//==============================================================================
// 表达式
//==============================================================================

void
Expr::__mark__(Mark mark)
{
  mark(const_cast<Type*>(type));
}

void
DeclRefExpr::__mark__(Mark mark)
{
  mark(decl);
  Expr::__mark__(mark);
}

void
ParenExpr::__mark__(Mark mark)
{
  mark(sub);
  Expr::__mark__(mark);
}

void
UnaryExpr::__mark__(Mark mark)
{
  mark(sub);
  Expr::__mark__(mark);
}

void
BinaryExpr::__mark__(Mark mark)
{
  mark(lft), mark(rht);
  Expr::__mark__(mark);
}

void
CallExpr::__mark__(Mark mark)
{
  mark(head);
  for (auto&& i : args)
    mark(i);
  Expr::__mark__(mark);
}

void
InitListExpr::__mark__(Mark mark)
{
  for (auto&& i : list)
    mark(i);
  Expr::__mark__(mark);
}

void
ImplicitCastExpr::__mark__(Mark mark)
{
  mark(sub);
  Expr::__mark__(mark);
}

//==============================================================================
// 语句
//==============================================================================

void
NullStmt::__mark__(Mark)
{
}

void
DeclStmt::__mark__(Mark mark)
{
  for (auto&& i : decls)
    mark(i);
}

void
ExprStmt::__mark__(Mark mark)
{
  mark(expr);
}

void
CompoundStmt::__mark__(Mark mark)
{
  for (auto&& i : subs)
    mark(i);
}

void
IfStmt::__mark__(Mark mark)
{
  mark(cond), mark(then), mark(else_);
}

void
WhileStmt::__mark__(Mark mark)
{
  mark(cond), mark(body);
}

void
DoStmt::__mark__(Mark mark)
{
  mark(body), mark(cond);
}

void
BreakStmt::__mark__(Mark mark)
{
  mark(loop);
}

void
ContinueStmt::__mark__(Mark mark)
{
  mark(loop);
}

void
ReturnStmt::__mark__(Mark mark)
{
  mark(func), mark(expr);
}

//==============================================================================
// 声明
//==============================================================================

void
Decl::__mark__(Mark mark)
{
  mark(const_cast<Type*>(type));
}

void
VarDecl::__mark__(Mark mark)
{
  mark(init);
  Decl::__mark__(mark);
}

void
FunctionDecl::__mark__(Mark mark)
{
  for (auto&& i : params)
    mark(i);
  mark(body);
  Decl::__mark__(mark);
}

//==============================================================================
// 顶层
//==============================================================================

void
TranslationUnit::__mark__(Mark mark)
{
  for (auto&& i : decls)
    mark(i);
}

} // namespace asg
