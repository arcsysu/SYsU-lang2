#pragma once

#include "asg.hpp"
#include <memory>
#include <stack>
#include <unordered_map>

namespace par {

extern Obj::Mgr gMgr;
extern asg::TranslationUnit* gTranslationUnit;
extern asg::FunctionDecl* gCurrentFunction;

/// 符号表，语法树遍历的过程中，Symtbl::g 和 Symtbl::mPrev
/// 隐式地构成了一个单向链表，每一个结点对应一个作用域。
struct Symtbl : std::unordered_map<std::string, asg::Decl*>
{
  static Symtbl* g; ///< 当前符号表

  /// 查找符号表，返回标识符 \p name 对应的声明语义结点
  static asg::Decl* resolve(const std::string& name);

  Symtbl()
    : mPrev(g)
  {
    g = this;
  }

  ~Symtbl() { g = mPrev; }

private:
  Symtbl* mPrev; ///< 上一级符号表
};

using Decls = std::vector<asg::Decl*>;

using Exprs = std::vector<asg::Expr*>;

} // namespace par
