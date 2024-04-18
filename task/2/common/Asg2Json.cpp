#include "Asg2Json.hpp"

#define self (*this)

namespace asg {

json::Object
Asg2Json::operator()(TranslationUnit* tu)
{
  json::Object ret;

  ret["kind"] = "TranslationUnitDecl";

  json::Array inner;
  for (auto&& i : tu->decls)
    inner.push_back(self(i));
  ret["inner"] = std::move(inner);

  return ret;
}

//==============================================================================
// 类型
//==============================================================================

std::string
Asg2Json::operator()(const Type* type)
{
  std::string ret;

  if (type->qual.const_)
    ret += "const ";

  switch (type->spec) {
    case Type::Spec::kINVALID:
      ret += "INVALID";
      break;

    case Type::Spec::kVoid:
      ret += "void";
      break;

    case Type::Spec::kChar:
      ret += "char";
      break;

    case Type::Spec::kInt:
      ret += "int";
      break;

    case Type::Spec::kLong:
      ret += "long";
      break;

    case Type::Spec::kLongLong:
      ret += "long long";
      break;

    default:
      ABORT();
  }

  if (type->texp)
    ret += self(type->texp);

  return ret;
}

std::string
Asg2Json::operator()(TypeExpr* texp)
{
  Obj::Walked guard(texp);

  if (auto p = texp->dcst<ArrayType>()) {
    std::string ret = "[";

    if (p->len != ArrayType::kUnLen)
      ret += std::to_string(p->len);
    ret.push_back(']');

    if (texp->sub != nullptr)
      ret += self(texp->sub);

    return ret;
  }

  if (auto p = texp->dcst<FunctionType>()) {
    std::string ret;

    if (texp->sub != nullptr)
      ret = std::string("(") + self(texp->sub) + ")";

    ret += " (";
    if (!p->params.empty()) {
      auto it = p->params.begin(), end = p->params.end();
      while (true) {
        ret += self(*it);
        if (++it == end)
          break;
        ret += ", ";
      }
    }
    ret.push_back(')');

    return ret;
  }

  if (auto p = texp->dcst<PointerType>()) {
    if (auto arrayType = texp->sub->dcst<ArrayType>()) {
      std::string ret;
      if (arrayType->sub != nullptr) {
        ret = " (*)";
        ret += self(arrayType->sub);
      } else {
        ret = " *";
      }

      return ret;
    }

    if (auto functionType = texp->sub->dcst<FunctionType>()) {
      std::string ret;
      ret = " (*)";
      ret += "(";
      if (!functionType->params.empty()) {
        auto it = functionType->params.begin(),
             end = functionType->params.end();
        while (true) {
          ret += self(*it);
          if (++it == end)
            break;
          ret += ", ";
        }
      }
      ret.push_back(')');

      return ret;
    }
  }

  ABORT();
}

//==============================================================================
// 表达式
//==============================================================================

json::Object
Asg2Json::operator()(Expr* obj)
{
  json::Object ret;

  if (auto p = obj->dcst<IntegerLiteral>())
    ret = std::move(self(p));

  else if (auto p = obj->dcst<StringLiteral>())
    ret = std::move(self(p));

  else if (auto p = obj->dcst<DeclRefExpr>())
    ret = std::move(self(p));

  else if (auto p = obj->dcst<ParenExpr>())
    ret = std::move(self(p));

  else if (auto p = obj->dcst<UnaryExpr>())
    ret = std::move(self(p));

  else if (auto p = obj->dcst<BinaryExpr>())
    ret = std::move(self(p));

  else if (auto p = obj->dcst<CallExpr>())
    ret = std::move(self(p));

  else if (auto p = obj->dcst<InitListExpr>())
    ret = std::move(self(p));

  else if (auto p = obj->dcst<ImplicitInitExpr>())
    ret = std::move(self(p));

  else if (auto p = obj->dcst<ImplicitCastExpr>())
    ret = std::move(self(p));

  else
    ABORT();

  ret["type"] = json::Object({ { "qualType", self(obj->type) } });

  switch (obj->cate) {
    case Expr::Cate::kINVALID:
      ret["valueCategory"] = "INVALID";
      break;

    case Expr::Cate::kLValue:
      ret["valueCategory"] = "lvalue";
      break;

    case Expr::Cate::kRValue:
      ret["valueCategory"] = "prvalue";
      break;

    default:
      ABORT();
  }

  return ret;
}

json::Object
Asg2Json::operator()(IntegerLiteral* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "IntegerLiteral";
  ret["value"] = std::to_string(obj->val);

  return ret;
}

json::Object
Asg2Json::operator()(StringLiteral* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "StringLiteral";

  std::string value;
  value.push_back('"');
  for (auto&& c : obj->val) {
    switch (c) {
      case '\'':
        value += "\\'";
        break;

      case '"':
        value += "\\\"";
        break;

      case '\?':
        value += "\\?";
        break;

      case '\\':
        value += "\\\\";
        break;

      case '\a':
        value += "\\a";
        break;

      case '\b':
        value += "\\b";
        break;

      case '\f':
        value += "\\f";
        break;

      case '\n':
        value += "\\n";
        break;

      case '\r':
        value += "\\r";
        break;

      case '\t':
        value += "\\t";
        break;

      case '\v':
        value += "\\v";
        break;

      default:
        value.push_back(c);
    }
  }
  value.push_back('"');
  ret["value"] = std::move(value);

  return ret;
}

json::Object
Asg2Json::operator()(DeclRefExpr* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "DeclRefExpr";

  return ret;
}

json::Object
Asg2Json::operator()(ParenExpr* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "ParenExpr";

  json::Array inner;
  inner.push_back(self(obj->sub));
  ret["inner"] = std::move(inner);

  return ret;
}

json::Object
Asg2Json::operator()(UnaryExpr* obj)
{
  assert(obj->sub);

  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "UnaryOperator";

  switch (obj->op) {
    case UnaryExpr::kPos:
      ret["opcode"] = "+";
      break;

    case UnaryExpr::kNeg:
      ret["opcode"] = "-";
      break;

    case UnaryExpr::kNot:
      ret["opcode"] = "!";
      break;

    default:
      ABORT();
  }

  json::Array inner;
  inner.push_back(self(obj->sub));
  ret["inner"] = std::move(inner);

  return ret;
}

json::Object
Asg2Json::operator()(BinaryExpr* obj)
{
  assert(obj->lft && obj->rht);

  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "BinaryOperator";

  switch (obj->op) {
    case BinaryExpr::kMul:
      ret["opcode"] = "*";
      break;

    case BinaryExpr::kDiv:
      ret["opcode"] = "/";
      break;

    case BinaryExpr::kMod:
      ret["opcode"] = "%";
      break;

    case BinaryExpr::kAdd:
      ret["opcode"] = "+";
      break;

    case BinaryExpr::kSub:
      ret["opcode"] = "-";
      break;

    case BinaryExpr::kGt:
      ret["opcode"] = ">";
      break;

    case BinaryExpr::kLt:
      ret["opcode"] = "<";
      break;

    case BinaryExpr::kGe:
      ret["opcode"] = ">=";
      break;

    case BinaryExpr::kLe:
      ret["opcode"] = "<=";
      break;

    case BinaryExpr::kEq:
      ret["opcode"] = "==";
      break;

    case BinaryExpr::kNe:
      ret["opcode"] = "!=";
      break;

    case BinaryExpr::kAnd:
      ret["opcode"] = "&&";
      break;

    case BinaryExpr::kOr:
      ret["opcode"] = "||";
      break;

    case BinaryExpr::kAssign:
      ret["opcode"] = "=";
      break;

    case BinaryExpr::kComma:
      ret["opcode"] = ",";
      break;

    case BinaryExpr::kIndex:
      ret["kind"] = "ArraySubscriptExpr";
      break;

    default:
      ABORT();
  }

  json::Array inner;
  inner.push_back(self(obj->lft));
  inner.push_back(self(obj->rht));
  ret["inner"] = std::move(inner);

  return ret;
}

json::Object
Asg2Json::operator()(CallExpr* obj)
{
  assert(obj->head);

  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "CallExpr";

  json::Array inner;
  inner.push_back(self(obj->head));
  for (auto&& i : obj->args)
    inner.push_back(self(i));
  ret["inner"] = std::move(inner);

  return ret;
}

json::Object
Asg2Json::operator()(InitListExpr* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "InitListExpr";

  json::Array inner;
  for (auto&& i : obj->list)
    inner.push_back(self(i));
  ret["inner"] = std::move(inner);

  return ret;
}

json::Object
Asg2Json::operator()(ImplicitInitExpr* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "InitListExpr";

  return ret;
}

json::Object
Asg2Json::operator()(ImplicitCastExpr* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "ImplicitCastExpr";

  json::Array inner;
  inner.push_back(self(obj->sub));
  ret["inner"] = std::move(inner);

  return ret;
}

//==============================================================================
// 语句
//==============================================================================

json::Object
Asg2Json::operator()(Stmt* obj)
{
  if (auto p = obj->dcst<DeclStmt>())
    return self(p);

  if (auto p = obj->dcst<ExprStmt>())
    return self(p);

  if (auto p = obj->dcst<CompoundStmt>())
    return self(p);

  if (auto p = obj->dcst<IfStmt>())
    return self(p);

  if (auto p = obj->dcst<WhileStmt>())
    return self(p);

  if (auto p = obj->dcst<DoStmt>())
    return self(p);

  if (auto p = obj->dcst<BreakStmt>())
    return self(p);

  if (auto p = obj->dcst<ContinueStmt>())
    return self(p);

  if (auto p = obj->dcst<ReturnStmt>())
    return self(p);

  if (auto p = obj->dcst<NullStmt>()) {
    json::Object ret;
    ret["kind"] = "NullStmt";
    return ret;
  }

  ABORT();
}

json::Object
Asg2Json::operator()(DeclStmt* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "DeclStmt";

  json::Array inner;
  for (auto&& i : obj->decls)
    inner.push_back(self(i));
  ret["inner"] = std::move(inner);

  return ret;
}

json::Object
Asg2Json::operator()(ExprStmt* obj)
{
  assert(obj->expr);
  return self(obj->expr);
}

json::Object
Asg2Json::operator()(CompoundStmt* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "CompoundStmt";

  json::Array inner;
  for (auto&& i : obj->subs)
    inner.push_back(self(i));
  ret["inner"] = std::move(inner);

  return ret;
}

json::Object
Asg2Json::operator()(IfStmt* obj)
{
  assert(obj->cond && obj->then);

  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "IfStmt";

  json::Array inner;
  inner.push_back(self(obj->cond));
  inner.push_back(self(obj->then));
  if (obj->else_)
    inner.push_back(self(obj->else_));
  ret["inner"] = std::move(inner);

  return ret;
}

json::Object
Asg2Json::operator()(WhileStmt* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "WhileStmt";

  json::Array inner;
  inner.push_back(self(obj->cond));
  inner.push_back(self(obj->body));
  ret["inner"] = std::move(inner);

  return ret;
}

json::Object
Asg2Json::operator()(DoStmt* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "DoStmt";

  json::Array inner;
  inner.push_back(self(obj->body));
  inner.push_back(self(obj->cond));
  ret["inner"] = std::move(inner);

  return ret;
}

json::Object
Asg2Json::operator()(BreakStmt* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "BreakStmt";

  return ret;
}

json::Object
Asg2Json::operator()(ContinueStmt* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "ContinueStmt";

  return ret;
}

json::Object
Asg2Json::operator()(ReturnStmt* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "ReturnStmt";

  json::Array inner;
  if (obj->expr)
    inner.push_back(self(obj->expr));
  ret["inner"] = std::move(inner);

  return ret;
}

//==============================================================================
// 声明
//==============================================================================

json::Object
Asg2Json::operator()(Decl* obj)
{
  json::Object ret;

  if (auto p = obj->dcst<VarDecl>())
    ret = std::move(self(p));

  else if (auto p = obj->dcst<FunctionDecl>())
    ret = std::move(self(p));

  else
    ABORT();

  ret["type"] = json::Object({ { "qualType", self(obj->type) } });

  return ret;
}

json::Object
Asg2Json::operator()(VarDecl* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "VarDecl";

  ret["name"] = obj->name;

  json::Array inner;
  if (obj->init)
    inner.push_back(self(obj->init));
  ret["inner"] = std::move(inner);

  return ret;
}

json::Object
Asg2Json::operator()(FunctionDecl* obj)
{
  json::Object ret;
  Obj::Walked guard(obj);

  ret["kind"] = "FunctionDecl";

  ret["name"] = obj->name;

  json::Array inner;
  for (auto&& i : obj->params) {
    json::Object pobj;
    pobj["kind"] = "ParmVarDecl";
    pobj["name"] = i->name;
    pobj["type"] = json::Object({ { "qualType", self(i->type) } });

    inner.push_back(std::move(pobj));
  }

  if (obj->body)
    inner.push_back(self(obj->body));

  ret["inner"] = std::move(inner);

  return ret;
}

} // namespace asg
