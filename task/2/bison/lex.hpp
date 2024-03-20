#pragma once

#include "par.y.hh"
#include <string>
#include <string_view>
#include <cstdio>

namespace lex {

struct G
{
  int mId{ YYEOF };             // 词号
  std::string_view mText;       // 对应文本
  std::string mFile;            // 文件路径
  int mLine{ 0 }, mColumn{ 0 }; // 行号、列号
  bool mStartOfLine{ true };    // 是否是行首
  bool mLeadingSpace{ false };  // 是否有前导空格
};

extern G g;

int
come_line(const char* yytext, int yyleng, int yylineno);

int
come(int tokenId, const char* yytext, int yyleng, int yylineno);

} // namespace lex
