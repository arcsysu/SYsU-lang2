#include "par.hpp"
#include "lex.hpp"
#include <fstream>
#include <stack>
#include <unordered_map>

namespace par {

Obj::Mgr gMgr;
asg::TranslationUnit* gTranslationUnit;
asg::FunctionDecl* gCurrentFunction;

Symtbl* Symtbl::g{ nullptr };

asg::Decl*
Symtbl::resolve(const std::string& name)
{
  auto cur = g;
  while (cur) {
    auto iter = cur->find(name);
    if (iter != cur->end())
      return iter->second;
    cur = cur->mPrev;
  }
  return nullptr; // 标识符未定义
}

} // namespace par

void
yyerror(char const* s)
{
  fflush(stdout);
  printf("\n%*s\n%*s\n", lex::g.mLine, "^", lex::g.mColumn, s);
}
