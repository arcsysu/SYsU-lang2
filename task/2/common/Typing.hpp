#include "asg.hpp"

namespace asg {

/**
 * @brief 在抽象语法图上推导并补全类型
 */
class Typing
{
public:
  Obj::Mgr& mMgr;
  Type::Cache mTypeCache;

  Typing(Obj::Mgr& mgr)
    : mMgr(mgr)
    , mTypeCache(mgr)
  {
  }

  TranslationUnit* operator()(TranslationUnit* tu);

private:
  template<typename T, typename... Args>
  T* make(Args... args)
  {
    return mMgr.make<T>(args...);
  }

  //============================================================================
  // 表达式
  //============================================================================

  Expr* operator()(Expr* obj);

  Expr* operator()(IntegerLiteral* obj);

  Expr* operator()(StringLiteral* obj);

  Expr* operator()(DeclRefExpr* obj);

  Expr* operator()(ParenExpr* obj);

  Expr* operator()(UnaryExpr* obj);

  Expr* operator()(BinaryExpr* obj);

  Expr* operator()(CallExpr* obj);

  //============================================================================
  // 语句
  //============================================================================

  void operator()(Stmt* obj);

  void operator()(DeclStmt* obj);

  void operator()(ExprStmt* obj);

  void operator()(CompoundStmt* obj);

  void operator()(IfStmt* obj);

  void operator()(WhileStmt* obj);

  void operator()(DoStmt* obj);

  void operator()(BreakStmt* obj);

  void operator()(ContinueStmt* obj);

  void operator()(ReturnStmt* obj);

  //============================================================================
  // 声明
  //============================================================================

  void operator()(Decl* obj);

  void operator()(VarDecl* obj);

  void operator()(FunctionDecl* obj);

  //============================================================================
  // 其它
  //============================================================================

  Expr* ensure_rvalue(Expr* exp);

  /// 整数提升：https://zh.cppreference.com/w/c/language/conversion#%E6%95%B4%E6%95%B0%E6%8F%90%E5%8D%87
  Expr* promote_integer(Expr* exp, Type::Spec to = Type::Spec::kInt);

  /// 对于 \p lft = \p rht 的等式，转换 \p rht 的类型以适应 \p lft
  Expr* assignment_cast(Expr* lft, Expr* rht);

  /// 由被赋值类型 \p to 倒推初始化表达式 \p init 的类型
  Expr* infer_init(Expr* init, const Type* to);

  /// 倒退列表初始化的类型，返回构造的初始化表达式和用到了第几个初始化元素
  std::pair<Expr*, std::size_t> infer_initlist(const std::vector<Expr*>& list,
                                               std::size_t begin,
                                               const Type* to);
};

} // namespace asg
