#include "Asg2Json.hpp"
#include "Ast2Asg.hpp"
#include "SYsULexer.hpp"
#include "Typing.hpp"
#include "asg.hpp"
#include <fstream>
#include <iostream>

int
main(int argc, char* argv[])
{
  if (argc != 3) {
    std::cout << "Usage: " << argv[0] << " <input> <output>\n";
    return -1;
  }

  std::ifstream inFile(argv[1]);
  if (!inFile) {
    std::cout << "Error: unable to open input file: " << argv[1] << '\n';
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

  antlr4::ANTLRInputStream input(inFile);
  SYsULexer lexer(&input);

  antlr4::CommonTokenStream tokens(&lexer);
  SYsUParser parser(&tokens);

  auto ast = parser.compilationUnit();
  Obj::Mgr mgr;

  asg::Ast2Asg ast2asg(mgr);
  auto asg = ast2asg(ast->translationUnit());
  mgr.mRoot = asg;
  mgr.gc();

  asg::Typing inferType(mgr);
  inferType(asg);
  mgr.gc();

  asg::Asg2Json asg2json;
  llvm::json::Value json = asg2json(asg);

  outFile << json << '\n';
}
