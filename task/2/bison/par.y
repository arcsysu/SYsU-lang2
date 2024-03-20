/* 生成.output文件 */
%verbose

/* 用于调试 (yydebug) */
%define parse.trace

%code top {
int yylex (void);             // 该函数由 Flex 生成
void yyerror (char const *);	// 该函数定义在 par.cpp 中
}

%code requires {
#include "par.hpp"
#include <iostream>
}

%union {
  std::string* RawStr;
  par::Decls* Decls;
  par::Exprs* Exprs;

  asg::TranslationUnit* TranslationUnit;
  asg::Type* Type;
  asg::Expr* Expr;
  asg::Decl* Decl;
  asg::FunctionDecl* FunctionDecl;
  asg::Stmt* Stmt;
  asg::CompoundStmt* CompoundStmt;
  asg::ExprStmt* ExprStmt;
  asg::ReturnStmt* ReturnStmt;
  asg::IfStmt* IfStmt;
  asg::WhileStmt* WhileStmt;
  asg::ContinueStmt* ContinueStmt;
  asg::BreakStmt* BreakStmt;
  asg::NullStmt* NullStmt;
}

/* 在下面说明每个非终结符对应的 union 成员，以便进行编译期类型检查 */
%type <Type> declaration_specifiers type_specifier

%type <Expr> additive_expression multiplicative_expression unary_expression postfix_expression
%type <Expr> expression primary_expression assignment_expression initializer initializer_list
%type <Expr> logical_or_expression logical_and_expression equality_expression relational_expression

%type <Stmt> block_item statement
%type <CompoundStmt> compound_statement block_item_list
%type <ExprStmt> expression_statement
%type <ReturnStmt> jump_statement

%type <Decls> external_declaration declaration init_declarator_list parameter_list
%type <Exprs> argument_expression_list
%type <FunctionDecl> function_definition
%type <Decl> declarator init_declarator parameter_declaration

%type <TranslationUnit> translation_unit

%token <RawStr> IDENTIFIER CONSTANT
%token INT VOID

%token RETURN

%start start

%%

// 起始符号
start
  :	{
      par::Symtbl::g = new par::Symtbl();
    }
    translation_unit
    {
      par::gTranslationUnit = $2;
      delete par::Symtbl::g;
    }
  ;

translation_unit
  : external_declaration
    {
      $$ = par::gMgr.make<asg::TranslationUnit>();
      for (auto&& decl: *$1)
        $$->decls.push_back(decl);
      delete $1;
    }
  | translation_unit external_declaration
    {
      $$ = $1;
      for (auto&& decl: *$2)
        $$->decls.push_back(decl);
      delete $2;
    }
  ;

external_declaration
  : function_definition
    {
      $$ = new par::Decls();
      $$->push_back($1);
    }
  | declaration { $$ = $1; }
  ;

function_definition
  : declaration_specifiers declarator
    {
      auto funcDecl = $2->dcst<asg::FunctionDecl>();
      ASSERT(funcDecl);
      // 设置当前全局的函数作用变量
      par::gCurrentFunction = funcDecl; 
      auto ty = par::gMgr.make<asg::Type>();
      if (funcDecl->type != nullptr)
        ty->texp = funcDecl->type->texp; 
      ty->spec = $1->spec, ty->qual = $1->qual;
      funcDecl->type = ty;

    }
    compound_statement
    {	
      $$ = par::gCurrentFunction;
      $$->name = $2->name;
      $$->body = $4;
    }
  ;

declaration
  : declaration_specifiers init_declarator_list ';'
    {
      for (auto decl: *$2)
      {
        auto ty = par::gMgr.make<asg::Type>();
        if (decl->type != nullptr)
          ty->texp = decl->type->texp; // 保留前面 ArrayType 的texp
        ty->spec = $1->spec, ty->qual = $1->qual;
        decl->type = ty;
        auto varDecl = dynamic_cast<asg::VarDecl*>(decl);
        if (varDecl != nullptr)
        {
          if (varDecl->init != nullptr)
            varDecl->init->type = decl->type;
        }
      }
      $$ = $2;
    }
  ;

declaration_specifiers
  : type_specifier { $$ = $1; }
  | type_specifier declaration_specifiers
    {
      $$ = $2;
      $$->spec = $1->spec;
    }
  ;

type_specifier
  : VOID
    {
      $$ = par::gMgr.make<asg::Type>();
      $$->spec = asg::Type::Spec::kVoid;
    }
  | INT
    {
      $$ = par::gMgr.make<asg::Type>();
      $$->spec = asg::Type::Spec::kInt;
    }
  ;

declarator
  : IDENTIFIER
    {
      $$ = par::gMgr.make<asg::VarDecl>();
      $$->name = std::move(*$1);
      delete $1;

      // 插入符号表
      par::Symtbl::g->insert_or_assign($$->name, $$);
    }
  | declarator '[' ']' // 未知长度数组
    {
      $$ = $1; 
      // 填充Type
      auto ty = par::gMgr.make<asg::Type>();
      if ($$->type != nullptr)
        ty->texp=$$->type->texp;
      auto p = par::gMgr.make<asg::ArrayType>();
      p->len = asg::ArrayType::kUnLen;
      if (ty->texp == nullptr)
      {
        ty->texp = p;
      }
      else
      {
        ty->texp->sub = p;
      }
      $$->type = ty;

      // 插入符号表
      par::Symtbl::g->insert_or_assign($$->name, $$);
    }
  | declarator '[' assignment_expression ']' // 数组定义
    {
      $$ = $1; 
      // 填充Type
      auto ty = par::gMgr.make<asg::Type>();
      if ($$->type != nullptr)
        ty->texp=$$->type->texp;
      auto p = par::gMgr.make<asg::ArrayType>();
      auto integerLiteral = $3->dcst<asg::IntegerLiteral>();
      ASSERT(integerLiteral);
      p->len = integerLiteral->val;
      if (ty->texp == nullptr)
      {
        ty->texp = p;
      }
      else
      {
        ty->texp->sub = p;
      }
      $$->type = ty;

      // 插入符号表
      par::Symtbl::g->insert_or_assign($$->name, $$);
    }
  | declarator '(' ')'
    {
      $$ = par::gMgr.make<asg::FunctionDecl>();
      $$->name = $1->name;
      auto ty = par::gMgr.make<asg::Type>();
      auto p = par::gMgr.make<asg::FunctionType>();
      ty->texp = p;
      $$->type = ty;

      // 插入符号表
      par::Symtbl::g->insert_or_assign($$->name, $$);
    }
  // 函数列表的定义
  | declarator '(' parameter_list ')'
    {
      auto p = par::gMgr.make<asg::FunctionDecl>();
      p->name = $1->name;
      p->params = *$3;
      auto ty = par::gMgr.make<asg::Type>();
      auto functionType = par::gMgr.make<asg::FunctionType>();
      for (auto decl: *$3)
      {
        functionType->params.push_back(decl->type);
      }
      ty->texp = functionType;
      p->type = ty;
      $$ = p;

      // 插入符号表
      par::Symtbl::g->insert_or_assign($$->name, $$);
    }
  ;

parameter_list
  : parameter_declaration
    {
      $$ = new par::Decls();
      $$->push_back($1);
    }
  | parameter_list ',' parameter_declaration
    {
      $$ = $1;
      $$->push_back($3);
    }
  ;

parameter_declaration
  : declaration_specifiers declarator
    {
      // 保留之前定义的 Type
      auto ty = par::gMgr.make<asg::Type>();
      if ($2->type != nullptr)
        ty->texp = $2->type->texp;
      ty->spec = $1->spec, ty->qual = $1->qual;
      $2->type = ty;
      $$ = $2;
    }
  ;

compound_statement
  : {$$ = par::gMgr.make<asg::CompoundStmt>();} // 代码块为空的情况
  |'{' '}' { $$ = par::gMgr.make<asg::CompoundStmt>(); }
  | '{'
    { new par::Symtbl(); } 		// 开启新的符号表作用域
    block_item_list
    '}'
    {
      delete par::Symtbl::g; 	// 结束符号表作用域
      $$ = $block_item_list;
    }
  ;

block_item_list
  : block_item
    {
      $$ = par::gMgr.make<asg::CompoundStmt>();
      $$->subs.push_back($1);
    }
  | block_item_list block_item
    {
      $$ = $1;
      $$->subs.push_back($2);
    }
  ;

block_item
  : declaration
    {
      auto p = par::gMgr.make<asg::DeclStmt>();
      for (auto decl: *$1)
        p->decls.push_back(decl);
      $$ = p;
    }
  | statement { $$ = $1; }
  ;

statement
  : compound_statement { $$ = $1; }
  | expression_statement { $$ = $1; }
  | jump_statement { $$ = $1; }
  ;

expression_statement
  : expression ';'
    {
      $$ = par::gMgr.make<asg::ExprStmt>();
      $$->expr = $1;
    }
  ;

jump_statement
  : RETURN ';'
    {
      $$ = par::gMgr.make<asg::ReturnStmt>();
      $$->func = par::gCurrentFunction;
    }
  | RETURN expression ';'
    {
      $$ = par::gMgr.make<asg::ReturnStmt>();
      $$->func = par::gCurrentFunction;
      $$->expr = $2;
    }

expression
  : assignment_expression { $$ = $1; }
  | expression ',' assignment_expression
    {
      auto p = par::gMgr.make<asg::BinaryExpr>();
      p->op = asg::BinaryExpr::Op::kComma;
      p->lft = $1, p->rht = $3;
      $$ = p;
    }
  ;

assignment_expression
  : logical_or_expression { $$ = $1; }
  | unary_expression '=' assignment_expression
    {
      auto p = par::gMgr.make<asg::BinaryExpr>();
      p->op = asg::BinaryExpr::Op::kAssign;;
      p->lft = $1, p->rht = $3;
      $$ = p;
    }
  ;

logical_or_expression
  : logical_and_expression { $$ = $1; }
  ;

logical_and_expression
  : equality_expression { $$ = $1; }
  ;

equality_expression
  : relational_expression { $$ = $1; }
  ;

relational_expression
  : additive_expression { $$ = $1; }
  ;

additive_expression
  : multiplicative_expression { $$ = $1;}
  | additive_expression '+' multiplicative_expression
    {
      auto p = par::gMgr.make<asg::BinaryExpr>();
      p->op = asg::BinaryExpr::Op::kAdd;
      p->lft = $1, p->rht = $3;
      $$ = p;
    }
  | additive_expression '-' multiplicative_expression
    {
      auto p = par::gMgr.make<asg::BinaryExpr>();
      p->op = asg::BinaryExpr::Op::kSub;
      p->lft = $1, p->rht = $3;
      $$ = p;
    }
  ;

multiplicative_expression
  : unary_expression  { $$ = $1;}
  ;

unary_expression
  : postfix_expression { $$ = $1;}
  | '-' unary_expression
    {
      auto p = par::gMgr.make<asg::UnaryExpr>();
      p->op = asg::UnaryExpr::Op::kNeg;
      p->sub = $2;
      $$ = p;
    }
  ;

postfix_expression
  : primary_expression { $$ = $1; }
  ;

primary_expression
  : IDENTIFIER
    {
      // 查找符号表, 找到对应的Decl
      auto decl = par::Symtbl::resolve(*$1);
      ASSERT(decl);
      delete $1;
      auto p = par::gMgr.make<asg::DeclRefExpr>();
      p->decl = decl;
      $$ = p;
    }
  | CONSTANT
    {
      auto p = par::gMgr.make<asg::IntegerLiteral>();
      p->val = std::stoull(*$1, nullptr, 10);
      delete $1;
      $$ = p;
    }
  ;

argument_expression_list
  : assignment_expression
    {
      $$ = new par::Exprs();
      $$->push_back($1);
    }
  | argument_expression_list ',' assignment_expression
    {
      $$ = $1;
      $$->push_back($3);
    }
  ;

init_declarator_list
  : init_declarator
    {
      $$ = new par::Decls();
      $$->push_back($1);
    }
  | init_declarator_list ',' init_declarator
    {
      $$ = $1;
      $$->push_back($3);
    }
  ;

init_declarator
  : declarator { $$ = $1; }
  | declarator '=' initializer
    {
      auto varDecl = $1->dcst<asg::VarDecl>();
      ASSERT(varDecl);
      $3->type = varDecl->type;
      varDecl->init = $3;
      $$ = varDecl;
    }
  ;

 // 初始化右值
initializer
  : assignment_expression
    {
      auto callExpr = $1->dcst<asg::CallExpr>();
      if (callExpr != nullptr)
      {
        auto implicitCastExpr = dynamic_cast<asg::ImplicitCastExpr*>(callExpr->head);
        auto declRefExpr = dynamic_cast<asg::DeclRefExpr*>(implicitCastExpr->sub);
        $$ = callExpr;
      }
      else
      {
        auto p = par::gMgr.make<asg::InitListExpr>();
        p->list.push_back($1);
        $$ = p;
      }
      $$->type = $1->type;
    }
  | '{' initializer_list '}'
    {
      $$ = $2;
    }
  | '{' '}'
    {
      auto p = par::gMgr.make<asg::InitListExpr>();
      $$ = p;
    }
  ;

// 初始化列表
initializer_list
  : initializer
    {
      $$ = $1;
    }
  | initializer_list ',' initializer
    {
      auto initListExpr3 = $3->dcst<asg::InitListExpr>();
      auto initListExpr1 = $1->dcst<asg::InitListExpr>();
      for(auto exper: initListExpr3->list)
        initListExpr1->list.push_back(exper);
      $$ = initListExpr1;
    }
  ;

%%
