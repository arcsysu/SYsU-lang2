#include "Json2Asg.hpp"

using namespace asg;

TranslationUnit*
Json2Asg::operator()(const llvm::json::Value& jval)
{
  auto jobj = jval.getAsObject();
  ASSERT(jobj);
  ASSERT(jobj->getString("kind") == "TranslationUnitDecl");

  auto inner = jobj->getArray("inner");
  ASSERT(inner);

  auto ret = make<TranslationUnit>();
  for (auto& jval : *inner) {
    auto jobj = jval.getAsObject();
    ASSERT(jobj);
    if (auto p = decl(*jobj))
      ret->decls.push_back(p);
  }

  return ret;
}

namespace {

std::size_t
jobj_id(const llvm::json::Object& jobj)
{
  auto id = jobj.getString("id");
  ASSERT(id);
  ASSERT(id->starts_with("0x"));
  auto hexStr = id->substr(2).str();
  return std::stoull(hexStr, nullptr, 16);
}

} // namespace

//==============================================================================
// 类型
//==============================================================================

const Type*
Json2Asg::getty(const llvm::json::Object& jobj)
{
  auto a = jobj.getObject("type");
  ASSERT(a);
  auto b = a->getString("qualType");
  ASSERT(b);
  auto texpStr = b->str();

  auto iter = mTyMap.find(texpStr);
  if (iter != mTyMap.end())
    return iter->second;

  const Type* ty;
  auto s = parse_type(texpStr.c_str(), ty);
  ASSERT(s && *s == '\0');
  mTyMap.emplace(texpStr, ty);
  return ty;
}

//==============================================================================
// 表达式
//==============================================================================

Expr*
Json2Asg::expr(const llvm::json::Object& jobj)
{
  auto kind = jobj.getString("kind");
  ASSERT(kind);

  Expr* ret;

  if (kind == "IntegerLiteral")
    ret = integer_literal(jobj);

  else if (kind == "BinaryOperator")
    ret = binary_expr(jobj);

  else if (kind == "UnaryOperator")
    ret = unary_expr(jobj);

  else if (kind == "DeclRefExpr")
    ret = decl_ref_expr(jobj);

  else if (kind == "ImplicitCastExpr")
    ret = implicit_cast_expr(jobj);

  else if (kind == "ParenExpr")
    ret = paren_expr(jobj);

  else if (kind == "InitListExpr")
    ret = init_list_expr(jobj);

  else if (kind == "ImplicitValueInitExpr")
    ret = implicit_init_expr(jobj);

  else if (kind == "ArraySubscriptExpr")
    ret = binary_expr(jobj);

  else if (kind == "CallExpr")
    ret = call_expr(jobj);

  else
    ABORT();

  auto cateVal = jobj.get("valueCategory");
  ASSERT(cateVal);
  auto cate = cateVal->getAsString();
  ASSERT(cate);
  if (cate == "lvalue")
    ret->cate = Expr::Cate::kLValue;
  else if (cate == "prvalue")
    ret->cate = Expr::Cate::kRValue;
  else
    ABORT();

  return ret;
}

IntegerLiteral*
Json2Asg::integer_literal(const llvm::json::Object& jobj)
{
  auto integerLiteral = make<IntegerLiteral>();

  integerLiteral->type = getty(jobj);

  auto value = jobj.getString("value");
  ASSERT(value);

  integerLiteral->val = std::stoull(value->str());

  return integerLiteral;
}

DeclRefExpr*
Json2Asg::decl_ref_expr(const llvm::json::Object& jobj)
{
  auto declRefExpr = make<DeclRefExpr>();

  declRefExpr->type = getty(jobj);

  auto ref = jobj.getObject("referencedDecl");
  ASSERT(ref);
  std::size_t id = jobj_id(*ref);
  auto refObj = mIdMap[id]->dcst<Decl>();
  ASSERT(refObj);
  declRefExpr->decl = refObj;

  return declRefExpr;
}

ParenExpr*
Json2Asg::paren_expr(const llvm::json::Object& jobj)
{
  auto parenExpr = make<ParenExpr>();

  parenExpr->type = getty(jobj);

  auto inner = jobj.getArray("inner");
  ASSERT(inner);

  parenExpr->sub = expr(*inner->front().getAsObject());
  return parenExpr;
}

UnaryExpr*
Json2Asg::unary_expr(const llvm::json::Object& jobj)
{
  auto unaryExpr = make<UnaryExpr>();

  unaryExpr->type = getty(jobj);

  auto opCode = jobj.getString("opcode");
  ASSERT(opCode);
  if (opCode == "-") {
    unaryExpr->op = UnaryExpr::Op::kNeg;
  } else if (opCode == "!") {
    unaryExpr->op = UnaryExpr::Op::kNot;
  } else if (opCode == "+") {
    unaryExpr->op = UnaryExpr::Op::kPos;
  } else {
    ABORT();
  }

  auto inner = jobj.getArray("inner");
  ASSERT(inner);

  unaryExpr->sub = expr(*(inner->front().getAsObject()));

  return unaryExpr;
}

BinaryExpr*
Json2Asg::binary_expr(const llvm::json::Object& jobj)
{
  auto kind = jobj.getString("kind");
  ASSERT(kind);

  auto binaryExpr = make<BinaryExpr>();
  binaryExpr->type = getty(jobj);

  if (kind == "ArraySubscriptExpr")
    binaryExpr->op = BinaryExpr::Op::kIndex;
  else {
    auto opCode = jobj.getString("opcode");
    ASSERT(opCode);

    if (opCode == "*")
      binaryExpr->op = BinaryExpr::Op::kMul;
    else if (opCode == "/")
      binaryExpr->op = BinaryExpr::Op::kDiv;
    else if (opCode == "%")
      binaryExpr->op = BinaryExpr::Op::kMod;
    else if (opCode == "+")
      binaryExpr->op = BinaryExpr::Op::kAdd;
    else if (opCode == "-")
      binaryExpr->op = BinaryExpr::Op::kSub;
    else if (opCode == ">")
      binaryExpr->op = BinaryExpr::Op::kGt;
    else if (opCode == "<")
      binaryExpr->op = BinaryExpr::Op::kLt;
    else if (opCode == ">=")
      binaryExpr->op = BinaryExpr::Op::kGe;
    else if (opCode == "<=")
      binaryExpr->op = BinaryExpr::Op::kLe;
    else if (opCode == "==")
      binaryExpr->op = BinaryExpr::Op::kEq;
    else if (opCode == "!=")
      binaryExpr->op = BinaryExpr::Op::kNe;
    else if (opCode == "&&")
      binaryExpr->op = BinaryExpr::Op::kAnd;
    else if (opCode == "||")
      binaryExpr->op = BinaryExpr::Op::kOr;
    else if (opCode == "=")
      binaryExpr->op = BinaryExpr::Op::kAssign;
    else {
      ABORT();
    }
  }

  auto inner = jobj.getArray("inner");
  ASSERT(inner);

  binaryExpr->lft = expr(*inner->front().getAsObject());
  binaryExpr->rht = expr(*(*inner)[1].getAsObject());

  return binaryExpr;
}

CallExpr*
Json2Asg::call_expr(const llvm::json::Object& jobj)
{
  auto callExpr = make<CallExpr>();
  callExpr->type = getty(jobj);

  auto inner = jobj.getArray("inner");
  ASSERT(inner);

  callExpr->head = expr(*inner->front().getAsObject());

  for (std::uint32_t i = 1; i < inner->size(); ++i) {
    callExpr->args.push_back(expr(*(*inner)[i].getAsObject()));
  }

  return callExpr;
}

InitListExpr*
Json2Asg::init_list_expr(const llvm::json::Object& jobj)
{
  auto initListExpr = make<InitListExpr>();

  initListExpr->type = getty(jobj);

  auto initList = jobj.getArray("inner");
  if (!initList) {
    initList = jobj.getArray("array_filler");
  }
  ASSERT(initList);

  for (auto& value : *initList) {
    auto object = value.getAsObject();
    ASSERT(object);

    if (auto pExpr = expr(*object))
      initListExpr->list.push_back(pExpr);
  }

  return initListExpr;
}

ImplicitInitExpr*
Json2Asg::implicit_init_expr(const llvm::json::Object& jobj)
{
  auto implicitInitExpr = make<ImplicitInitExpr>();
  implicitInitExpr->type = getty(jobj);
  return implicitInitExpr;
}

ImplicitCastExpr*
Json2Asg::implicit_cast_expr(const llvm::json::Object& jobj)
{
  auto implicitCastExpr = make<ImplicitCastExpr>();
  implicitCastExpr->type = getty(jobj);

  auto castKind = jobj.getString("castKind");
  ASSERT(castKind);

  if (castKind == "LValueToRValue")
    implicitCastExpr->kind = ImplicitCastExpr::kLValueToRValue;
  else if (castKind == "ArrayToPointerDecay")
    implicitCastExpr->kind = ImplicitCastExpr::kArrayToPointerDecay;
  else if (castKind == "FunctionToPointerDecay")
    implicitCastExpr->kind = ImplicitCastExpr::kFunctionToPointerDecay;
  else
    ABORT();

  auto inner = jobj.getArray("inner");
  ASSERT(inner);

  implicitCastExpr->sub = expr(*inner->front().getAsObject());

  return implicitCastExpr;
}

//==============================================================================
// 声明
//==============================================================================

Decl*
Json2Asg::decl(const llvm::json::Object& jobj)
{
  auto kind = jobj.getString("kind");
  ASSERT(kind);

  if (kind == "VarDecl")
    return var_decl(jobj);

  if (kind == "FunctionDecl")
    return function_decl(jobj);

  if (kind == "ParmVarDecl")
    return var_decl(jobj);

  if (kind == "TypedefDecl")
    return nullptr;

  ABORT();
}

VarDecl*
Json2Asg::var_decl(const llvm::json::Object& jobj)
{
  auto varDecl = make<VarDecl>(jobj_id(jobj));

  auto name = jobj.getString("name");
  ASSERT(name);
  varDecl->name = name->str();

  varDecl->type = getty(jobj);

  auto inner = jobj.getArray("inner");
  if (inner)
    varDecl->init = expr(*inner->front().getAsObject());
  else
    varDecl->init = nullptr;

  return varDecl;
}

FunctionDecl*
Json2Asg::function_decl(const llvm::json::Object& jobj)
{
  if (jobj.getBoolean("isImplicit") && jobj.getBoolean("isImplicit") == true)
    return nullptr;

  auto funcDecl = make<FunctionDecl>(jobj_id(jobj));

  auto name = jobj.getString("name");
  funcDecl->name = name->str();

  funcDecl->type = getty(jobj);

  auto inner = jobj.getArray("inner");
  if (!inner) {
    funcDecl->body = nullptr;
    return funcDecl;
  }

  mCurFunc = funcDecl;
  for (auto& value : *inner) {
    auto object = value.getAsObject();
    ASSERT(object);

    auto kind = object->getString("kind");
    ASSERT(kind);

    if (kind == "ParmVarDecl") {
      funcDecl->params.push_back(decl(*object));
      continue;
    }

    if (kind == "CompoundStmt") {
      ASSERT(funcDecl->body == nullptr);
      funcDecl->body = compound_stmt(*object);
      continue;
    }
    ABORT();
  }

  return funcDecl;
}

//==============================================================================
// 语句
//==============================================================================

Stmt*
Json2Asg::stmt(const llvm::json::Object& jobj)
{
  auto kind = jobj.getString("kind");
  ASSERT(kind);

  if (kind == "DeclStmt")
    return decl_stmt(jobj);

  if (kind == "ReturnStmt")
    return return_stmt(jobj);

  if (kind == "BinaryOperator")
    return expr_stmt(jobj);

  if (kind == "UnaryOperator")
    return expr_stmt(jobj);

  if (kind == "CallExpr")
    return expr_stmt(jobj);

  if (kind == "IfStmt")
    return if_stmt(jobj);

  if (kind == "WhileStmt")
    return while_stmt(jobj);

  if (kind == "NullStmt")
    return null_stmt(jobj);

  if (kind == "CompoundStmt")
    return compound_stmt(jobj);

  if (kind == "ContinueStmt")
    return continue_stmt(jobj);

  if (kind == "BreakStmt")
    return break_stmt(jobj);

  ABORT();
}

CompoundStmt*
Json2Asg::compound_stmt(const llvm::json::Object& jobj)
{
  auto compoundStmt = make<CompoundStmt>();

  auto inner = jobj.getArray("inner");
  if (!inner)
    return compoundStmt;

  for (auto& value : *inner) {
    auto object = value.getAsObject();
    ASSERT(object);

    compoundStmt->subs.push_back(stmt(*object));
  }
  return compoundStmt;
}

DeclStmt*
Json2Asg::decl_stmt(const llvm::json::Object& jobj)
{
  auto declStmt = make<DeclStmt>();
  auto inner = jobj.getArray("inner");
  ASSERT(inner);

  for (auto& value : *inner) {
    auto object = value.getAsObject();
    ASSERT(object);
    if (auto pDecl = decl(*object))
      declStmt->decls.push_back(pDecl);
  }

  return declStmt;
}

ReturnStmt*
Json2Asg::return_stmt(const llvm::json::Object& jobj)
{
  auto returnStmt = make<ReturnStmt>();

  returnStmt->func = mCurFunc;

  auto inner = jobj.getArray("inner");
  if (inner)
    returnStmt->expr = expr(*inner->front().getAsObject());

  return returnStmt;
}

IfStmt*
Json2Asg::if_stmt(const llvm::json::Object& jobj)
{
  auto ifStmt = make<IfStmt>();

  auto inner = jobj.getArray("inner");
  ASSERT(inner);

  ifStmt->cond = expr(*(inner->front().getAsObject()));
  ifStmt->then = stmt(*((*inner)[1].getAsObject()));
  if (inner->size() == 3)
    ifStmt->else_ = stmt(*((*inner)[2].getAsObject()));

  return ifStmt;
}

WhileStmt*
Json2Asg::while_stmt(const llvm::json::Object& jobj)
{
  auto whileStmt = make<WhileStmt>();
  mCurLoop = whileStmt;

  auto inner = jobj.getArray("inner");
  ASSERT(inner);

  whileStmt->cond = expr(*(inner->front().getAsObject()));
  whileStmt->body = stmt(*((*inner)[1].getAsObject()));

  return whileStmt;
}

NullStmt*
Json2Asg::null_stmt(const llvm::json::Object& jobj)
{
  return make<NullStmt>();
}

BreakStmt*
Json2Asg::break_stmt(const llvm::json::Object& jobj)
{
  auto ret = make<BreakStmt>();
  ret->loop = mCurLoop;
  return ret;
}

ContinueStmt*
Json2Asg::continue_stmt(const llvm::json::Object& jobj)
{
  auto ret = make<ContinueStmt>();
  ret->loop = mCurLoop;
  return ret;
}

ExprStmt*
Json2Asg::expr_stmt(const llvm::json::Object& jobj)
{
  auto exprStmt = make<ExprStmt>();
  exprStmt->expr = expr(jobj);
  return exprStmt;
}

// ========================================================================== //
// 类型字符串解析
// ========================================================================== //

/**
 * 本实验中 `clang -cc1 -ast-dump=json` 输出的类型字符串语法：
 *
 *  type
 *    : base+ texp '\0'
 *    ;
 *  base
 *    : 'void' | 'char' | 'int' | 'long' | 'const'
 *    ;
 *  texp
 *    : texp_2
 *    ;
 *  texp_0
 *    : %empty
 *    | '[' oct ']'
 *    | '(' args ')'
 *    | '(' texp ')'
 *    ;
 *  texp_1
 *    ; texp_0+
 *    ;
 *  texp_2
 *    : '*' texp_2
 *    | texp_1
 *    ;
 *  args
 *    : %empty
 *    | type (',' type)*
 *    ;
 *  oct
 *    : [0-9]+
 *    ;
 *
 * 以下是对应上述文法的手工实现的 LL(1) 递归下降解析器，在学完编译
 * 原理课程后，所有同学都应当掌握手写 LL(1) 递归下降解析器的能力。
 *
 * 容易看出以下的函数在签名上都有相似的模式，例如：
 *   1. 所有函数的第一个参数都是一个字符串指针，指向待解析的字符串开头；
 *   2. 所有函数的返回值都是一个字符串指针，指向解析成功后的剩余字符串开头；
 *   3. 如果解析失败，返回 nullptr；
 *   4. 解析过程的语义值通过额外的引用参数传出。
 * 这些都是实现 LL(1) 递归下降解析器的常规编码范式，遵循范式去实现代码
 * 可以避免常见的误区，极大地提升编码质量。
 */

namespace {

const char*
match(const char* s, const char* p)
{
  while (*p) {
    if (*s != *p)
      return nullptr;
    ++s, ++p;
  }
  return s;
}

const char*
skip_spaces(const char* s)
{
  while (*s == ' ')
    ++s;
  return s;
}

const char*
parse_base(const char* s, Type& v)
{
  if (auto p = match(s, "void")) {
    ASSERT(v.spec == Type::Spec::kINVALID);
    v.spec = Type::Spec::kVoid;
    return p;
  }
  if (auto p = match(s, "char")) {
    ASSERT(v.spec == Type::Spec::kINVALID);
    v.spec = Type::Spec::kChar;
    return p;
  }
  if (auto p = match(s, "int")) {
    ASSERT(v.spec == Type::Spec::kINVALID);
    v.spec = Type::Spec::kInt;
    return p;
  }
  if (auto p = match(s, "long")) {
    if (v.spec == Type::Spec::kINVALID)
      v.spec = Type::Spec::kLong;
    else if (v.spec == Type::Spec::kLong)
      v.spec = Type::Spec::kLongLong;
    else
      ABORT();
    return p;
  }
  if (auto p = match(s, "const")) {
    v.qual.const_ = true;
    return p;
  }
  return nullptr;
}

const char*
parse_oct(const char* s, std::uint32_t& v)
{
  if (*s < '0' || *s > '9')
    return nullptr;
  std::uint32_t num = 0;
  while ('0' <= *s && *s <= '9') {
    num = num * 10 + (*s - '0');
    ++s;
  }
  v = num;
  return s;
}

/// 把 \p texp 的里面翻出来，因为 C 的类型表达式与表达式内外顺序是相反的。
TypeExpr*
turn_texp(TypeExpr* texp)
{
  if (texp->sub == nullptr)
    return texp;
  auto innerMost = turn_texp(texp->sub);
  innerMost->sub = texp;
  texp->sub = nullptr;
  return innerMost;
}

} // namespace

const char*
Json2Asg::parse_type(const char* s, const Type*& v)
{
  auto ty = make<Type>();
  s = parse_base(s, *ty);
  if (!s)
    return nullptr;

  while (true) {
    auto p = parse_base(skip_spaces(s), *ty);
    if (!p)
      break;
    s = p;
  }

  s = parse_texp(skip_spaces(s), ty->texp);
  if (ty->texp)
    ty->texp = turn_texp(ty->texp); // 将类型表达式内外翻转

  v = ty;
  return s;
}

const char*
Json2Asg::parse_texp(const char* s, TypeExpr*& v)
{
  return parse_texp_2(s, v);
}

const char*
Json2Asg::parse_texp_0(const char* s, TypeExpr*& v)
{
RULE_1:
  if (auto p = match(s, "[")) {
    std::uint32_t len;
    p = parse_oct(skip_spaces(p), len);
    if (!p)
      goto RULE_2;
    p = match(skip_spaces(p), "]");
    if (!p)
      goto RULE_2;
    auto arrTy = make<ArrayType>();
    arrTy->len = len;
    v = arrTy;
    return p;
  }

RULE_2:
  if (auto p = match(s, "(")) {
    std::vector<const Type*> params;
    p = parse_args(skip_spaces(p), params);
    if (!p)
      goto RULE_3;
    p = match(skip_spaces(p), ")");
    if (!p)
      goto RULE_3;
    auto funTy = make<FunctionType>();
    funTy->params = std::move(params);
    v = funTy;
    return p;
  }

RULE_3:
  if (auto p = match(s, "(")) {
    p = parse_texp(skip_spaces(p), v);
    if (!p)
      goto EMPTY;
    p = match(skip_spaces(p), ")");
    if (!p)
      goto EMPTY;
    return p;
  }

EMPTY:
  v = nullptr;
  return s;
}

const char*
Json2Asg::parse_texp_1(const char* s, TypeExpr*& v)
{
  TypeExpr* texp;
  auto p = parse_texp_0(s, texp);
  if (!p)
    return nullptr;
  if (s != p) {
    while (true) {
      s = p;
      TypeExpr* sup;
      p = parse_texp_0(skip_spaces(p), sup);
      if (!p)
        return nullptr;
      if (s == p)
        break;
      sup->sub = texp;
      texp = sup;
    }
  }
  v = texp;
  return s;
}

const char*
Json2Asg::parse_texp_2(const char* s, TypeExpr*& v)
{
RULE_1:
  if (auto p = match(s, "*")) {
    TypeExpr* texp;
    p = parse_texp_2(skip_spaces(p), texp);
    if (!p)
      goto EMPTY;
    v = make<PointerType>();
    v->sub = texp;
    return p;
  }

RULE_2:
  if (auto p = parse_texp_1(s, v))
    return p;

EMPTY:
  return nullptr;
}

const char*
Json2Asg::parse_args(const char* s, std::vector<const Type*>& v)
{
  const Type* ty;
  auto p = parse_type(s, ty);
  if (!p)
    return s; // 没有参数的情况也是合法的
  s = p;

  std::vector<const Type*> params;
  params.push_back(ty);

  while (true) {
    p = match(skip_spaces(s), ",");
    if (!p)
      break;

    p = parse_type(skip_spaces(p), ty);
    if (!p)
      return nullptr;

    params.push_back(ty);
    s = p;
  }

  v = std::move(params);
  return s;
}
