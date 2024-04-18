#include "asg.hpp"
#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>

class EmitIR
{
public:
  Obj::Mgr& mMgr;
  llvm::Module mMod;

  EmitIR(Obj::Mgr& mgr, llvm::LLVMContext& ctx, llvm::StringRef mid = "-");

  llvm::Module& operator()(asg::TranslationUnit* tu);

private:
  llvm::LLVMContext& mCtx;

  llvm::Type* mIntTy;
  llvm::FunctionType* mCtorTy;

  llvm::Function* mCurFunc;
  std::unique_ptr<llvm::IRBuilder<>> mCurIrb;

  //============================================================================
  // 类型
  //============================================================================

  llvm::Type* operator()(const asg::Type* type);

  //============================================================================
  // 表达式
  //============================================================================

  llvm::Value* operator()(asg::Expr* obj);

  llvm::Constant* operator()(asg::IntegerLiteral* obj);

  // TODO: 添加表达式处理相关声明

  //============================================================================
  // 语句
  //============================================================================

  void operator()(asg::Stmt* obj);

  void operator()(asg::CompoundStmt* obj);

  void operator()(asg::ReturnStmt* obj);

  // TODO: 添加语句处理相关声明

  //============================================================================
  // 声明
  //============================================================================

  void operator()(asg::Decl* obj);

  void operator()(asg::FunctionDecl* obj);

  // TODO: 添加声明处理相关声明
};
