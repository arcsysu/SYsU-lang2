%{
#include "lex.hpp"
/* 所有代码全部抽离出来，放到 lex.hpp 和 lex.cpp 里 */

using namespace lex;

#define ADDCOL() g.mColumn += yyleng;
#define COME(id) return come(id, yytext, yyleng, yylineno)
#define COME_LINE() return come_line(yytext, yyleng, yylineno)
%}

%option 8bit warn noyywrap yylineno


%%

^#[^\n]*                /* 屏蔽以#开头的行 */
<<EOF>> {return YYEOF;}

.*\n { COME_LINE(); }   /* 匹配每一行*/

. {COME(YYUNDEF);}

%%

/* about symbols avaliable (yytext, yyleng etc.) in the context of Flex:
 * https://ftp.gnu.org/old-gnu/Manuals/flex-2.5.4/html_node/flex_14.html
 * https://ftp.gnu.org/old-gnu/Manuals/flex-2.5.4/html_node/flex_15.html
*/
