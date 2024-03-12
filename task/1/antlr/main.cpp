#include "SYsU_lang.h" // 确保这里的头文件名与您生成的词法分析器匹配
#include <fstream>
#include <iostream>
#include <string>
#include <unordered_map>

// 映射定义，将ANTLR的tokenTypeName映射到clang的格式
std::unordered_map<std::string, std::string> tokenTypeMapping = {
  { "Int", "int" },//
  { "Identifier", "identifier" },//
  { "LeftParen", "l_paren" },//
  { "RightParen", "r_paren" },//
  { "RightBrace", "r_brace" },//
  { "LeftBrace", "l_brace" },//
  { "LeftBracket", "l_square" },//
  { "RightBracket", "r_square" },//
  { "Constant", "numeric_constant" },//
  { "Return", "return" },//
  { "Semi", "semi" },//
  { "EOF", "eof" },
  { "Equal", "equal" },//
  { "Plus", "plus" },//
  { "Comma", "comma" },//
  { "Const", "const" },
  { "NumericConstant", "numeric_constant"},
  { "Minus", "minus"},
  { "Star", "star"},
  { "Slash", "slash"},
  { "Percent", "percent"},
  { "Greater", "greater"},
  { "If", "if"},
  { "EqualEqual", "equalequal"},
  { "AmpAmp", "ampamp"},
  { "Else", "else"},
  { "Void", "void"},
  { "PipePipe", "pipepipe"},
  { "While", "while"},
  { "Break", "break"},
  { "Continue", "continue"},
  { "For", "for"},
  { "Less", "less"},
  { "LessEqual", "lessequal"},
  { "GreaterEqual", "greaterequal"},
  { "Exclaim", "exclaim"},
  { "ExclaimEqual", "exclaimequal"},


  // 在这里继续添加其他映射
};

static std::string filename="";
static bool changeline=false;
static bool leadspace=false;
static int lastline=0;
static int lastpos=0;
static int startline=0;

void
print_token(const antlr4::Token* token,
            const antlr4::CommonTokenStream& tokens,
            std::ofstream& outFile,
            const antlr4::Lexer& lexer)
{
  auto& vocabulary = lexer.getVocabulary();

  auto tokenTypeName =
    std::string(vocabulary.getSymbolicName(token->getType()));
  if(tokenTypeName=="LineAfterPreprocessing"){
    std::string text=token->getText();
    std::string line="";
    for(int i=0;i<text.length();i++){
      if(text[i]!=' '&&line=="")continue;
      for(i=i+1;i<text.length();i++){
        if(text[i]==' ')break;
        line+=text[i];
      }
    }
    startline=std::stoi(line);
  }
  if(tokenTypeName=="LineAfterPreprocessing"){
    std::string text=token->getText();
    std::string name="";
    for(int i=0;i<text.length();i++){
      if(text[i]!='"')continue;
      for(i=i+1;i<text.length();i++){
        if(text[i]=='"')break;
        name+=text[i];
      }
    }
    filename=name;
    return;
  }

  if(tokenTypeName=="Newline"){
    changeline=true;
    startline++;
    return;
  }

  if(tokenTypeName=="Whitespace"){
    leadspace=true;
    return;
  }
  if (tokenTypeName.empty())
    tokenTypeName = "<UNKNOWN>"; // 处理可能的空字符串情况

  if (tokenTypeMapping.find(tokenTypeName) != tokenTypeMapping.end()) {
    tokenTypeName = tokenTypeMapping[tokenTypeName];
  }

  std::string locInfo="";
  if(tokenTypeName=="eof"){
    changeline=false;
    leadspace=false;
    locInfo = "Loc=<" +filename+":"+ std::to_string(lastline) + ":" +
                          std::to_string(lastpos) + 
                          ">";
  }
  else
    locInfo = "Loc=<" +filename+":"+ std::to_string(startline-1) + ":" +
                          std::to_string(token->getCharPositionInLine() + 1) + 
                          ">";

  bool startOfLine = changeline;
  bool leadingSpace = leadspace;
  changeline=false;
  leadspace=false;
  lastline=startline-1;
  lastpos=token->getCharPositionInLine()+2;

  if (token->getText() != "<EOF>")
    outFile << tokenTypeName << " '" << token->getText() << "'";
  else
    outFile << tokenTypeName << " '"
            << "'";
  if(startOfLine&&leadingSpace)
    outFile <<"\t [StartOfLine] [LeadingSpace]";
  else if(startOfLine)
    outFile <<"\t [StartOfLine]";
  else if(leadingSpace)
    outFile <<"\t [LeadingSpace]";
  else
    outFile <<"\t";
  outFile << "\t"+locInfo << std::endl;
}

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

  std::ofstream outFile(argv[2]);
  if (!outFile) {
    std::cout << "Error: unable to open output file: " << argv[2] << '\n';
    return -3;
  }

  std::cout << "程序 '" << argv[0] << std::endl;
  std::cout << "输入 '" << argv[1] << std::endl;
  std::cout << "输出 '" << argv[2] << std::endl;

  antlr4::ANTLRInputStream input(inFile);
  SYsU_lang lexer(&input);

  antlr4::CommonTokenStream tokens(&lexer);
  tokens.fill();

  for (auto&& token : tokens.getTokens()) {
    print_token(token, tokens, outFile, lexer);
  }
}
