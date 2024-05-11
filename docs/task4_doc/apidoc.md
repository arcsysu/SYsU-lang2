## 常用API

LLVM中几乎所有对象均继承于`llvm::Value`（继承关系见[Value继承关系图](#附录)）。本文档可能无法覆盖实现优化需要的所有API。LLVM中代码即文档，如果不清楚是否存在对应功能的API，可以根据自己的需求查看对应类的头文件。

### 类型

### 指令

LLVM中大部分优化会对指令进行修改，因此对指令操作的函数需要着重了解。

#### 插入、删除、移动指令

插入指令：

* `void insertBefore(Instruction *insertBefore)`：将当前指令插入到指定指令之前
* `void insertAfter(Instruction *insertAfter)`：将当前指令插入到指定指令之后
* `Instruction* getInsertionPointAfterDef()`：返回当前指令定义处的下一个插入点（可能返回空指针）

删除指令：

* `SymbolTableList<Instruction>::iterator eraseFromParent()`：从其父节点（BasicBlock）中移除并删除当前指令，并返回被删除指令的下一条指令（**删除前必须将当前指令的Use替换为其他指令或删除**）
* `void removeFromParent()`：从其父节点（BasicBlock）中移除当前指令但不删除
* `BasicBlock::iterator erase(BasicBlock::iterator FromIt, BasicBlock::iterator ToIt)`：在基本块中使用iterator删除范围内所有指令

移动指令：

* `void moveBefore(Instruction *MovePos)`：将当前指令从父节点（BasicBlock）移除，并移动到指定指令之前
* `void moveBefore(BasicBlock &BB, SymbolTableList<Instruction>::iterator I)`：将当前指令从父节点（BasicBlock）移除，并移动到特定BB的指定指令之前
* `void moveAfter(Instruction *MovePos)`：将当前指令从父节点（BasicBlock）移除，并移动到指定指令之后

#### 修改指令

操作数：

* `void setOperand(unsigned idx, Value *val)`：设置指定索引处的操作数为指定的值

指令修改use的相关操作：

* `void replaceAllUsesWith(Value *V)`：将所有用到当前指令结果的地方替换为V。该函数在进行指令替换时经常会用到，因为删除指令前需要将被删除指令的所有Use替换/删除
* `bool replaceUsesOfWith(Value *From, Value *To)`：将所有用到From的地方替换为To，功能与`replaceAllUsesWith`相同
* `void replaceUsesOutsideBlock(Value *V, BasicBlock *BB)`：将BB之外的Use全部替换为V
* `void replaceUsesWithIf(Value *New, llvm::function_ref<bool(Use &U)> ShouldReplace)`：设置判断条件，满足条件时将当前指令替换为V

```C++
// replaceAllUsesWith用法：
// I0被I2使用，不能删除
I0: %3 = add nsw %1, %2
I1: %4 = add nsw %1, %2
I2: %5 = add nsw %3, %4

// I0.replaceAllUsesWith(I1)：将所有用到%3的地方替换为%4
// 此时I0没有被任何指令使用，可以删除
I0: %3 = add nsw %1, %2
I1: %4 = add nsw %1, %2
I2: %5 = add nsw %4, %4
```

#### 查询指令

操作数：

* `unsigned getOpcode()`：获取指令的操作码（opcode），用于进行指令类型判断
* `unsigned getNumOperands()`：获取指令操作数的数量
* `Value* getOperand(unsigned idx)`：获取指令指定索引处idx的操作数

指令查询use的相关操作：

* `unsigned getNumUses()`：返回当前指令Use的数量（被使用的次数）
* `iterator_range<use_iterator> uses()`：返回当前指令Use的迭代器（Use数量与`getNumUses()`对应）
* `op_range operands()`：返回当前指令Use的迭代器（用于遍历指令的所有操作数）
* `User* getOperandList()`：返回当前指令所有操作数的列表
* `Use& getOperandUse(unsigned idx)`：以`Use`形式返回第idx个操作数

指令所属的位置：

* `Module* getModule()`：获取当前指令所在的模块
* `Function* getFunction()`：获取当前指令所在的函数
* `BasicBlock* getParent()`：获取当前指令所在的基本块

#### Use类

Use类的定义如下，其描述了使用`Val`计算`Parent`的数据依赖关系。例如，在`%3 = add %1, %2`中`%3`存在两个Use，其(`Val`, `Parent`)分别为(`%3`, `%1`)和(`%3`, `%2`)。`Val`相同的多个Use组织成链表的形式，使用`Next`和`Prev`记录链表中前后两个`Use`。

```C++
class Use {
    ...
public:
  friend class Value;
  friend class User;

private:
  Value *Val = nullptr;
  Use *Next = nullptr;
  Use **Prev = nullptr;
  User *Parent = nullptr;

  // 重载后可以直接使用Use调用Use.Val的方法
  Value *operator->() { return Val; }
  const Value *operator->() const { return Val; }
  ...
};
```

相关操作：

* `Value *get()`：返回`Val`
* `User *getUser()`：返回`Parent`
* `unsigned getOperandNo()`：返回当前Use在User的操作数序号
* `Use *getNext()`：返回当前Use在链表中的下一个Use

```C++
// 假设I: %3 = add nsw %1, %2
Instruction *I = ...

// 遍历指令所有的操作数（遍历时使用引用）
// output: 操作数的定义指令
// %1 = ...
// %2 = ...
for (Use& u : I->operands()) {
  // 获取usee对应的指令，此时user为I
  Value* usee = u.get();

  // 下面两条指令等价，因为Use类对->的重载
  usee->print(mOut);
  u->print(mOut);
}

// 遍历指令所有的Use（遍历时使用引用）
// output: 使用到I的结果的指令
// %4 = ... %3, ...
for (Use& u : I->uses()) {
  // 获取user对应的指令，此时usee为I
  Value* user = u.getUser();
  user->print(mOut);
}
```

### 基本块

基本块是LLVM IR控制流的基本组成部分，对基本块的修改需要保证修改后程序的正确性。

#### 插入、删除、移动基本块

插入基本块：

* `BasicBlock *Create(LLVMContext &Context, const Twine &Name = "", Function *Parent = nullptr, BasicBlock *InsertBefore = nullptr)`：创建基本块并插入到指定位置

删除基本块：

* `SymbolTableList<BasicBlock>::iterator eraseFromParent()`：从其父节点（Function）中移除并删除当前基本块，并返回被删除指令的下一个基本块
* `void removeFromParent()`：从其父节点（Function）中移除当前基本块但不删除

移动基本块：

* `void moveBefore(BasicBlock *MovePos)`：将当前基本块从原来的位置移动到MovePos的前面
* `void moveBefore(SymbolTableList<BasicBlock>::iterator MovePos)`：同上
* `void moveAfter(BasicBlock *MovePos)`：将当前基本块从原来的位置移动到MovePos的后面
* `void insertInto(Function *Parent, BasicBlock *InsertBefore = nullptr)`：将当前基本块插入到指定函数的某个基本块InsertBefore前
* `BasicBlock *splitBasicBlock(Instruction *I, const Twine &BBName = "", bool Before = false)`：将基本块从指令I处分裂为两个基本块

#### 查询基本块

查询基本块中的指令：

* `Instruction* getTerminator()`：获取当前基本块的终结指令（跳转、返回指令）
* `iterator getFirstInsertionPt()`：获取当前基本块的第一个插入点
* `Instruction* getFirstNonPHI()`：获取当前基本块的第一个非PHI指令

查询其他基本块：

* `BasicBlock *getSinglePredecessor()`：是否只有一个前驱基本块，且前驱基本块只有一条边指向当前基本块（e.g. switch指令的多个cases指向同一个基本块不满足该条件）
* `BasicBlock *getUniquePredecessor()`：是否只有一个前驱基本块
* `BasicBlock *getSingleSuccessor()`：是否只有一个后驱基本块，且当前基本块只有一条边指向后驱基本块
* `BasicBlock *getUniqueSuccessor()`：是否只有一个后驱基本块
* `pred_range predecessors(BasicBlock *BB)`：返回当前基本块的所有前驱基本块
* `succ_range successors(BasicBlock *BB)`：返回当前基本块的所有后驱基本块
* `unsigned getNumUses()`：返回当前基本块的前驱数量。BasicBlock继承于`llvm::Value`，因此也具有Use属性

查询基本块所属的对象：

* `Module* getModule()`：获取当前基本块所在的模块
* `Function* getParent()`：获取当前基本块所在的函数

### 函数

* `Function* Create(FunctionType* Ty, LinkageTypes Linkage, unsigned AddrSpace, const Twine& N = "", Module* M = nullptr)`：创建函数
* `void eraseFromParent()`：从其父节点（Module）中移除并删除当前函数
* `void removeFromParent()`：从其父节点（Module）中移除当前函数但不删除
* `size_t arg_size()`：获取函数形参数量
* `Argument* getArg(unsigned i)`：获取第i个参数
* `FunctionType* getFunctionType()`：获取函数类型（包括返回类型、参数类型等）
* `Type* getReturnType()`：获取函数的返回类型
* `BasicBlock& getEntryBlock()`：获取函数的入口基本块
* `ValueSymbolTable* getValueSymbolTable()`：获取函数符号表
* `BasicBlockListType &getBasicBlockList()`：获取基本块表

### 分析工具

#### LoopAnalysis

LLVM的循环结构一般如下：

![LLVM循环结构](../images/task4/loop-terminology.svg)

对循环进行优化时，常常需要获取与循环相关的信息，而LLVM为开发者提供了对循环进行分析的Analysis Pass：`LoopAnalysis`。使用该Pass前，需要先进行Analysis Pass的注册（注册方式参考[Analysis Pass注册](./framework.md#注册transform-pass和analysis-pass)）。由于`LoopAnalysis`为Function级别的Analysis Pass，因此需要使用`FunctionAnalysisManager`。`LoopAnalysis`、`FunctionAnalysisManager`和`PassBuilder`的头文件分别为`llvm/Analysis/LoopInfo.h`、`llvm/IR/PassManager.h`、`llvm/Passes/PassBuilder.h`。

```C++
llvm::PreservedAnalyses run(llvm::Module& mod,
                            llvm::ModuleAnalysisManager& mam) {
  // 在FunctionAnalysisManager注册LoopAnalysis
  FunctionAnalysisManager fam;
  PassBuilder pb;
  fam.registerPass( [&]{return LoopAnalysis();} );
  pb.registerFunctionAnalyses(fam);

  for (Function &func : mod) {
    // 跳过函数声明
    if(func.isDeclaration()) continue;

    LoopInfo& LI = fam.getResult<LoopAnalysis>(func);   
    // LI包含了mod中所有循环的信息
    for (Loop* LP : LI) {     
      // 对某个循环LP进行处理
      ...
    }
  } 
}
```

对于LoopInfo有如下函数：

* `SmallVector<LoopT *, 4> getLoopsInPreorder()`：以先序遍历的顺序返回Loop的列表
* `LoopT *getLoopFor(const BlockT *BB)`：返回BB所在的循环
* `unsigned getLoopDepth(const BlockT *BB)`：返回BB所在的循环深度
* `bool isLoopHeader(const BlockT *BB)`：判断BB是否为循环header

对于Loop有如下函数：

* `unsigned getLoopDepth()`：返回循环深度
* `unsigned getNumBlocks()`：返回循环中的基本块数量
* `std::vector<BlockT *> &getBlocksVector()`：返回循环中所有基本块
* `unsigned getNumBackEdges()`：返回back edges的数量
* `const std::vector<LoopT *> &getSubLoops()`：返回内层循环
* `LoopT *getParentLoop()`：返回父循环（若存在）
* `bool contains(const BlockT *BB)`：判断BB是否在当前循环中
* `BlockT *getHeader()`：返回循环的header基本块
* `void getExitingBlocks(SmallVectorImpl<BlockT *> &ExitingBlocks)`：返回所有exiting基本块
* `BlockT *getExitingBlock()`：若只有一个exiting基本块，则返回；否则返回nullptr
* `BlockT *getLoopPreheader()`：返回循环的preheader基本块

#### DominatorTree

支配树（Dominance Tree）是一种用于描述基本块之间支配关系的数据结构。在程序的控制流图中，一个基本块A支配另一个基本块B，意味着无论程序执行路径如何，如果进入B，则一定会先经过A。支配树能够以树状结构表示这种支配关系。支配树有两个主要的概念：

1. 支配关系（Dominance）：在控制流图中，基本块A支配基本块B，如果每条从图的入口节点到B的路径都必须经过A。如果A支配B，那么A被称为B的支配者，B被称为A的被支配者。
2. 支配树（Dominance Tree）：支配树是控制流图中基本块之间支配关系的一种表示。它是一个树状结构，其中每个节点代表一个基本块，节点之间的父子关系表示最近支配关系。最近支配（immediate dominator，记作idom）表示节点的最近支配关系，若a idom b，则a是支配b且离b最近的节点。树的根节点是控制流图的入口基本块。

下面是一个控制流图，其中的节点表示基本块，边表示程序执行基本块的顺序，节点1为入口基本块：

![控制流图](../images/task4/CFG.png)

该控制流图对应的支配树如下：

![支配树](../images/task4/DominatorTree.png)

在LLVM中，支配树使用数据结构`DominatorTree`表示，头文件为`llvm/IR/Dominators.h`。

```C++
llvm::PreservedAnalyses run(llvm::Module& mod,
                            llvm::ModuleAnalysisManager& mam) {
  DominatorTree domTree;

  for (Function &func : mod) {
    // 跳过函数声明
    if(func.isDeclaration()) continue;

    // 计算func的支配关系
    domTree.recalculate(func);
    ...
  } 
}
```

`DominatorTree`的常用API如下：

* `bool dominates(const NodeT *A, const NodeT *B)`：判断节点A是否支配节点B（节点可以是基本块，也可以是指令）
* `bool properlyDominates(const NodeT *A, const NodeT *B)`：判断节点A是否支配节点B且A与B不是同一个节点
* `void getDescendants(NodeT *R, SmallVectorImpl<NodeT *> &Result)`：返回支配节点R的所有节点（包括R）
* `NodeT* getRoot()`：返回支配树的根节点

支配树与支配关系在基本块和代码移动时非常重要，如果我们希望一条指令移动到某个地方后能够影响后续某些基本块或指令，那么就需要将指令放在支配这些基本块或指令的位置。除了普通的支配树，LLVM还提供了后序支配树`PostDominatorTree`，其用法与`DominatorTree`类似，需要使用的同学们可以自行了解。

### 参考资料

* [LLVM 14 Programmers Manual](https://llvm.org/docs/ProgrammersManual.html#the-core-llvm-class-hierarchy-reference)
* [LLVM Loop Terminology](https://llvm.org/docs/LoopTerminology.html)
* [BHU miniSysY文档](https://buaa-se-compiling.github.io/miniSysY-tutorial/)
* [LLVM 中的循环Loop](https://zhuanlan.zhihu.com/p/536765546)


### 附录

![Value继承关系图](../images/task4/Value.png)
 