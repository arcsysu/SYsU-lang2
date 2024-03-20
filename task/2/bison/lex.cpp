#include "lex.hpp"
#include <cstring>
#include <iostream>
#include <unordered_map>

namespace lex {

G g;

int
come_line(const char* yytext, int yyleng, int yylineno)
{
  char name[64];
  char value[64];
  sscanf(yytext, "%s '%[^']'", name, value);

  static const std::unordered_map<std::string, int> kTokenId = {
    { "identifier", IDENTIFIER },
    { "numeric_constant", CONSTANT },
    { "int", INT },
    { "void", VOID },
    { "return", RETURN },
    { "l_paren", '(' },
    { "r_paren", ')' },
    { "l_brace", '{' },
    { "r_brace", '}' },
    { "semi", ';' },
    { "equal", '=' },
    { "l_square", '[' },
    { "r_square", ']' },
    { "comma", ',' },
    { "minus", '-' },
    { "plus", '+' },
    { "eof", YYEOF },
    // TODO 添加其他的 token
  };

  auto iter = kTokenId.find(name);
  assert(iter != kTokenId.end());

  yylval.RawStr = new std::string(value, strlen(value));
  return iter->second;
}

int
come(int tokenId, const char* yytext, int yyleng, int yylineno)
{
  g.mId = tokenId;
  g.mText = { yytext, std::size_t(yyleng) };
  g.mLine = yylineno;

  g.mStartOfLine = false;
  g.mLeadingSpace = false;

  return tokenId;
}

} // namespace lex
