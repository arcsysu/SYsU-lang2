%{
#include "lex.hpp"
/* 所有代码全部抽离出来，放到 lex.hpp 和 lex.cpp 里 */

using namespace lex;

#define ADDCOL() g.mColumn += yyleng;
#define COME(id) return come(id, yytext, yyleng, yylineno)
%}

%option 8bit warn noyywrap yylineno

D     [0-9]
L     [a-zA-Z_]
IS    ((u|U)|(u|U)?(l|L|ll|LL)|(l|L|ll|LL)(u|U))

%%

"int"       { ADDCOL(); COME(INT); }
"return"    { ADDCOL(); COME(RETURN); }

"("         { ADDCOL(); COME(L_PAREN); }
")"         { ADDCOL(); COME(R_PAREN); }
"["         { ADDCOL(); COME(L_SQUARE); }
"]"         { ADDCOL(); COME(R_SQUARE); }
"{"         { ADDCOL(); COME(L_BRACE); }
"}"         { ADDCOL(); COME(R_BRACE); }

"+"         { ADDCOL(); COME(PLUS); }

";"         { ADDCOL(); COME(SEMI); }
","         { ADDCOL(); COME(COMMA); }

"="         { ADDCOL(); COME(EQUAL); }

{L}({L}|{D})*         { ADDCOL(); COME(IDENTIFIER); }

L?\"(\\.|[^\\"\n])*\" { ADDCOL(); COME(STRING_LITERAL); }

0[0-7]*{IS}?          { ADDCOL(); COME(CONSTANT); }
[1-9]{D}*{IS}?        { ADDCOL(); COME(CONSTANT); }

^#[^\n]*              { return ~YYEOF; } /* 预处理信息处理，可以从预处理信息中获得文件名以及行号 */

[ \t\v\n\f]           { return ~YYEOF; } /* 需要处理行号和列号信息 */

<<EOF>>     { ADDCOL(); COME(YYEOF); }

%%

/* about symbols avaliable (yytext, yyleng etc.) in the context of Flex:
 * https://ftp.gnu.org/old-gnu/Manuals/flex-2.5.4/html_node/flex_14.html
 * https://ftp.gnu.org/old-gnu/Manuals/flex-2.5.4/html_node/flex_15.html
*/
