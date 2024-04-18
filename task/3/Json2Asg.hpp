#pragma once

#include "asg.hpp"
#include <any>
#include <llvm/Support/JSON.h>
#include <regex>
#include <unordered_map>

class Json2Asg
{
public:
  Obj::Mgr& mMgr;

  Json2Asg(Obj::Mgr& mgr)
    : mMgr(mgr)
  {
  }

  asg::TranslationUnit* operator()(const llvm::json::Value& jval);

private:
  std::unordered_map<std::size_t, Obj*> mIdMap;
  std::unordered_map<std::string, const asg::Type*> mTyMap;

  /**
   * 在遍历函数体时指向当前的函数声明，从而给函数体内返回语句的 ReturnStmt
   * 赋值。
   */
  asg::FunctionDecl* mCurFunc{ nullptr };

  /**
   * 在遍历循环语句体时指向当前的循环语句结点，从而给循环体内的 BreakStmt
   * 和 ContinueStmt 赋值。
   */
  asg::Stmt* mCurLoop{ nullptr };

  template<typename T, typename... Args>
  T* make(Args... args)
  {
    auto obj = mMgr.make<T>(args...);
    return obj;
  }

  template<typename T, typename... Args>
  T* make(std::size_t id, Args... args)
  {
    auto obj = mMgr.make<T>(args...);
    mIdMap.emplace(id, obj);
    return obj;
  }

  //============================================================================
  // 类型
  //============================================================================

  const asg::Type* getty(const llvm::json::Object& jobj);

  //============================================================================
  // 表达式
  //============================================================================

  asg::Expr* expr(const llvm::json::Object& jobj);

  asg::IntegerLiteral* integer_literal(const llvm::json::Object& jobj);

  asg::DeclRefExpr* decl_ref_expr(const llvm::json::Object& jobj);

  asg::ParenExpr* paren_expr(const llvm::json::Object& jobj);

  asg::UnaryExpr* unary_expr(const llvm::json::Object& jobj);

  asg::BinaryExpr* binary_expr(const llvm::json::Object& jobj);

  asg::CallExpr* call_expr(const llvm::json::Object& jobj);

  asg::InitListExpr* init_list_expr(const llvm::json::Object& jobj);

  asg::ImplicitInitExpr* implicit_init_expr(const llvm::json::Object& jobj);

  asg::ImplicitCastExpr* implicit_cast_expr(const llvm::json::Object& jobj);

  //============================================================================
  // 语句
  //============================================================================

  asg::Stmt* stmt(const llvm::json::Object& jobj);

  asg::CompoundStmt* compound_stmt(const llvm::json::Object& jobj);

  asg::NullStmt* null_stmt(const llvm::json::Object& jobj);

  asg::DeclStmt* decl_stmt(const llvm::json::Object& jobj);

  asg::ExprStmt* expr_stmt(const llvm::json::Object& jobj);

  asg::IfStmt* if_stmt(const llvm::json::Object& jobj);

  asg::WhileStmt* while_stmt(const llvm::json::Object& jobj);

  asg::BreakStmt* break_stmt(const llvm::json::Object& jobj);

  asg::ContinueStmt* continue_stmt(const llvm::json::Object& jobj);

  asg::ReturnStmt* return_stmt(const llvm::json::Object& jobj);

  //============================================================================
  // 声明
  //============================================================================

  asg::Decl* decl(const llvm::json::Object& jobj);

  asg::VarDecl* var_decl(const llvm::json::Object& jobj);

  asg::FunctionDecl* function_decl(const llvm::json::Object& jobj);

private:
  /**
   * @brief 尝试解析以 \p s 为起始的字符串，将语义值存入 \p v 。
   * 成功时返回剩余字符串指针，失败时返回 nullptr。
   */
  const char* parse_type(const char* s, const asg::Type*& v);

  /// 解析类型表达式，注意 \p v 在构建后是由外到内的顺序，需要再调用 turn_texp
  /// 将内外翻转。
  const char* parse_texp(const char* s, asg::TypeExpr*& v);
  const char* parse_texp_0(const char* s, asg::TypeExpr*& v);
  const char* parse_texp_1(const char* s, asg::TypeExpr*& v);
  const char* parse_texp_2(const char* s, asg::TypeExpr*& v);

  const char* parse_args(const char* s, std::vector<const asg::Type*>& v);
};
