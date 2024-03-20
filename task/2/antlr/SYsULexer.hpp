#pragma once

#include <antlr4-runtime.h>
#include <deque>
#include <memory>
#include <stack>
#include <string>

class SYsULexer : public antlr4::TokenSource
{
public:
  SYsULexer(antlr4::CharStream* input);

  std::unique_ptr<antlr4::Token> nextToken() override;

  size_t getLine() const override;

  size_t getCharPositionInLine() override;

  antlr4::CharStream* getInputStream() override;

  std::string getSourceName() override;

  template<typename T1>
  void setTokenFactory(antlr4::TokenFactory<T1>* tokenFactory)
  {
    mFactory = tokenFactory;
  }

  antlr4::TokenFactory<antlr4::CommonToken>* getTokenFactory() override;

private:
  antlr4::CharStream* mInput;
  std::pair<TokenSource*, antlr4::CharStream*> mSource;
  antlr4::TokenFactory<antlr4::CommonToken>* mFactory;

  std::string mSourceName;
  size_t mLine = 1, mColumn = 0;

  std::unique_ptr<antlr4::CommonToken> common_token(size_t type,
                                                    size_t start,
                                                    size_t stop,
                                                    std::string text = {})
  {
    return mFactory->create(mSource,
                            type,
                            std::move(text),
                            antlr4::Token::DEFAULT_CHANNEL,
                            start,
                            stop,
                            mLine,
                            mColumn);
  }
};
