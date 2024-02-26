#include "lex.hpp"
#include "lex.l.hh"
#include <fstream>
#include <iostream>

static std::ofstream outFile;

static std::string
escape(std::string_view sv)
{
  std::string result;
  for (char c : sv) {
    switch (c) {
      case '\n':
        result += "\\n";
        break;
      case '\t':
        result += "\\t";
        break;
      case '\r':
        result += "\\r";
        break;
      case '\v':
        result += "\\v";
        break;
      case '\f':
        result += "\\f";
        break;
      case '\a':
        result += "\\a";
        break;
      case '\b':
        result += "\\b";
        break;
      case '\\':
        result += "\\\\";
        break;
      case '\'':
        result += "\\\'";
        break;
      case '\0':
        break;
      default:
        result += c;
        break;
    }
  }
  return result;
}

void
print_token()
{
  outFile << lex::id2str(lex::g.mId) << " \'" << escape(lex::g.mText) << "\'";
  if (lex::g.mStartOfLine)
    outFile << "\t[StartOfLine]";
  if (lex::g.mLeadingSpace)
    outFile << "\t[LeadingSpace]";
  outFile << "\tLoc=<0:0>\n";
  outFile << std::flush;
}

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

  outFile = std::ofstream(argv[2]);
  if (!outFile) {
    std::cerr << "Failed to open " << argv[2] << '\n';
    return -3;
  }

  std::cout << "程序 '" << argv[0] << std::endl;
  std::cout << "输入 '" << argv[1] << std::endl;
  std::cout << "输出 '" << argv[2] << std::endl;

  // 这个循环完成词法分析，yylex()中会调用print_token()，从而向
  // 输出文件中写入词法分析结果。
  while (yylex())
    ;

  fclose(yyin);
}
