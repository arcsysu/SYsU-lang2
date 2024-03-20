#include "Asg2Json.hpp"
#include "Typing.hpp"
#include "lex.l.hh"
#include "par.y.hh"
#include <fstream>
#include <iostream>

extern int yydebug;

int
main(int argc, char* argv[])
{
  if (argc != 3) {
    std::cout << "Usage: " << argv[0] << " <input> <output>\n";
    return -1;
  }

  yyin = fopen(argv[1], "r");
  if (!yyin) {
    std::cerr << "Failed to open " << argv[1] << '\n';
    return -2;
  }

  std::error_code ec;
  llvm::StringRef outPath(argv[2]);
  llvm::raw_fd_ostream outFile(outPath, ec);
  if (ec) {
    std::cout << "Error: unable to open output file: " << argv[2] << '\n';
    return -3;
  }

  std::cout << "程序 " << argv[0] << std::endl;
  std::cout << "输入 " << argv[1] << std::endl;
  std::cout << "输出 " << argv[2] << std::endl;

  // 从源代码生成抽象语义图
  yydebug = 1; // 启用 Bison 的调试输出
  if (auto e = yyparse())
    return e;
  par::gMgr.mRoot = par::gTranslationUnit;
  par::gMgr.gc();

  // 执行类型检查
  asg::Typing typing(par::gMgr);
  typing(par::gTranslationUnit);
  typing.mTypeCache.clear();
  par::gMgr.gc();

  // 将抽象语义图转换为 JSON 并输出
  asg::Asg2Json asg2json;
  llvm::json::Value json = asg2json(par::gTranslationUnit);
  outFile << json << '\n';

  fclose(yyin);
}
