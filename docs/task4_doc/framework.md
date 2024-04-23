## 框架介绍

本次实验的框架主要分为以下两部分：

* 注册优化pass：在`main.cpp`中注册需要使用的优化pass，并指定优化顺序
* 实现优化pass：在optimizor.hpp中定义需要使用的优化pass类，并在其他文件中实现定义的优化pass的函数

### 注册优化pass和分析pass

注册优化pass的代码主要在`main.cpp`的`opt`函数中：

```C++
void
opt(llvm::Module& mod, llvm::raw_fd_ostream &logFile)
{
  // 定义分析pass的管理器
  LoopAnalysisManager LAM;
  FunctionAnalysisManager FAM;
  CGSCCAnalysisManager CGAM;
  ModuleAnalysisManager MAM;
  ModulePassManager MPM;

  // 注册分析pass的管理器
  PassBuilder PB;
  PB.registerModuleAnalyses(MAM);
  PB.registerCGSCCAnalyses(CGAM);
  PB.registerFunctionAnalyses(FAM);
  PB.registerLoopAnalyses(LAM);
  PB.crossRegisterProxies(LAM, FAM, CGAM, MAM);

  // 添加分析pass到管理器中
  MAM.registerPass([]() { return sysu::StaticCallCounter(); });

  // 添加优化pass到管理器中
  MPM.addPass(sysu::HelloWorldPass(logFile));
  MPM.addPass(sysu::StaticCallCounterPrinter(logFile));

  // 运行优化pass
  MPM.run(mod, MAM);
}
```

以上代码的注释清晰地呈现了LLVM IR优化pass和分析pass的注册过程：

* 优化pass：使用`MPM.addPass(sysu::optPass())`函数添加
* 分析pass：使用`MAM.registerPass([]() { return sysu::analysisPass(); })`函数添加

需要注意的是优化pass的执行顺序与第三部分添加优化pass的顺序相同，因此在优化前需要考虑优化次序对优化结果的影响；而分析pass只会在被使用时执行，因此添加分析pass的顺序不影响执行顺序。实例化优化pass时我们传入了`logFile`变量，该变量能让我们在pass中将中间结果输出到`output.log`文件中，方便同学们进行调试（调试方法见[调试方法](./overview.md#调试方法)一节）。

### 实现优化pass

以常量折叠优化`ConstantFolding`为例，其定义需要添加到`optimizor.hpp`中：

```C++
class ConstantFolding
    : public llvm::PassInfoMixin<ConstantFolding> {
public:
  explicit ConstantFolding(llvm::raw_ostream &OutS) : OS(OutS) {}
  llvm::PreservedAnalyses run(llvm::Module &M,
                              llvm::ModuleAnalysisManager &MAM);

private:
  llvm::raw_ostream &OS;
};
```

由于本实验基于LLVM 17，因此不支持旧版本LLVM提供的基于`ModulePass`、`FunctionPass`等类继承的优化pass实现，新旧版本Pass机制的区别请阅读[Legacy Pass](#legacy-pass)一节。按照上述方式定义的Pass需要继承`PassInfoMixin`类，该类会接受模板参数中优化pass名称为pass进行初始化。每个优化pass都需要实现`run`函数，在该函数内同学们能够对生成的LLVM IR进行分析与变换，最终返回优化后的IR。常量折叠的`run`函数主体代码如下：

```C++
llvm::PreservedAnalyses 
sysu::ConstantFolding::run(llvm::Module &M, llvm::ModuleAnalysisManager &MAM) {
  // 遍历所有函数
  for (auto &Func : M) {
    // 遍历每个函数的基本块
    for (auto &BB : Func) {
      std::vector<Instruction*> InstToErase;
      // 遍历每个基本块的指令
      for (auto& I: BB) {
        ...
      }
      // 从基本块中删除被选中的指令
      for (auto& I:InstToErase) {
        I->eraseFromParent();
      }
    }
  }
  return llvm::PreservedAnalyses::all();
}
```

上述代码展示了如何通过循环遍历`llvm::Module`中所有指令，以上遍历方法可以作为大部分指令优化的框架。使用该框架只需要将算法针对单条指令的处理逻辑填入`...`所处的代码块中，再辅以对指令的操作（例如对操作数的替换、指令的插入移动与删除等）即可完成优化算法的实现。

### 实现分析pass

以分析函数调用次数的`StaticCallCounter`为例，其定义需要添加到`optimizor.hpp`中：

```C++
class StaticCallCounter : public llvm::AnalysisInfoMixin<StaticCallCounter> {
public:
  using Result = llvm::MapVector<const llvm::Function *, unsigned>;
  Result run(llvm::Module &module, llvm::ModuleAnalysisManager &);

private:
  // 分析pass中必须包含"static llvm::AnalysisKey Key"
  static llvm::AnalysisKey Key;
  friend struct llvm::AnalysisInfoMixin<StaticCallCounter>;
};
```

分析pass和优化pass在定义时的区别在于：

* 分析pass的继承对象`AnalysisInfoMixin`继承于优化pass的继承对象`PassInfoMixin`
* 分析pass需要声明`static llvm::AnalysisKey Key`，因为其将作为分析pass区别于其他pass的唯一标识符被`AnalysisInfoMixin::ID()`函数返回
* 分析pass需要声明`friend struct llvm::AnalysisInfoMixin<passName>`，否则`llvm::AnalysisKey Key`会因为是`AnalysisInfoMixin`的私有变量而报错
* 分析pass的run函数返回自定义的结果而非`llvm::PreservedAnalyses`

实现`StaticCallCounter`的主体代码如下：

```C++
sysu::StaticCallCounter::Result
sysu::StaticCallCounter::run(Module &module, ModuleAnalysisManager &) {
  MapVector<const Function *, unsigned> result;

  for (auto &func: module) {
    for (auto &BB: func) {
      for (auto &inst: BB) {
        // 尝试转为CallInst

        // 获取被调用函数

        // 统计函数在源代码中被调用次数
        auto callCount = result.find(directInvoc);
        if (result.end() == callCount) {
          callCount = result.insert({directInvoc, 0}).first;
        }
        ++callCount->second;
      }
    }
  }
  return result;
}

AnalysisKey sysu::StaticCallCounter::Key;
```

注意`static llvm::AnalysisKey Key`是一个静态成员变量，在实现时需要额外声明，否则会出现静态变量未声明的报错。定义和实现分析pass后，我们需要在其他pass中调用该pass。下面的`StaticCallCounterPrinter`调用了定义、实现、注册好的`StaticCallCounter`，将分析结果以表格的形式输出到文件中：

```C++
PreservedAnalyses
sysu::StaticCallCounterPrinter::run(Module &module,
                                    ModuleAnalysisManager &MAM) {
  // 通过MAM执行StaticCallCounter并返回分析结果
  auto directCalls = MAM.getResult<StaticCallCounter>(module);

  OS << "=================================================\n";
  OS << "     sysu-optimizer: static analysis results\n";
  OS << "=================================================\n";
  OS << "       NAME             #N DIRECT CALLS\n";
  OS << "-------------------------------------------------\n";

  for (auto &callCount : directCalls) {
      std::string funcName = callCount.first->getName().str();
      funcName.resize(20, ' ');
      OS << "       " << funcName << "   " << callCount.second << "\n";
  }

  OS << "-------------------------------------------------\n\n";
  return PreservedAnalyses::all();
}
```

需要调用分析pass时，可以通过`run()`函数传入的`ModuleAnalysisManager &MAM`进行调用在`MAM`中注册过的分析pass（注册方法见[注册优化pass和分析pass](#注册优化pass和分析pass)小节），返回类型为分析pass的`run()`函数中自定义的返回类型。通过分析pass和优化pass的灵活组合，同学们可以实现许多代码优化算法。

### Legacy Pass

新旧版本Pass机制对于开发者最明显的区别是代码量的区别，旧Pass机制由于设计问题需要使用不少代码完成一个工作，而重构后的新Pass机制变得非常简洁与高效，开发者能够更方便地为LLVM添加优化。两者的区别如下：

* 继承：旧Pass机制继承`FunctionPass`表示该pass针对单个function优化，当优化对象为module和loop等结构时需要继承对应的类；新版本Pass机制统一继承`PassInfoMixin`类。
* 定义：
	* 旧Pass机制需要声明ID，该ID将作为区分不同pass的唯一标识符，同时ID作为静态成员变量需要在结构体定义外初始化；新Pass机制通过继承`PassInfoMixin`时传入的模板名作为区分pass的标识符。
	* 旧Pass机制需要调用`initialize...`函数进行初始化，该函数需要通过预定义的宏传入参数生成；新Pass机制则不需要额外初始化。
	* 旧Pass机制若需要使用分析pass，需要定义`getAnalysisUsage`函数并手动通过`AU.addRequired<...>()`添加分析pass；新Pass机制只需要在run函数中传入`FunctionAnalysisManager &FAM`即可在函数内使用在FAM注册过的分析pass。
* 实现：旧Pass机制使用`runOnFunction`函数实现优化，该函数返回值表示当前pass是否修改过传入参数的内容；新Pass机制使用`run`函数实现优化，该函数返回值表示当前pass是否会改变某些分析pass的结果。
* 注册：旧Pass机制需要使用预定义的宏生成`initialize...`函数，并定义新的`PassInfo`后注册；新版本Pass机制只需要通过`FPM.addPass()`注册。

以`FlattenCFGPass`为例，两者的pass定义和实现代码如下：

```C++
// Legacy Pass
struct FlattenCFGLegacyPass : public FunctionPass {
  static char ID; // Pass identification, replacement for typeid
public:
  FlattenCFGLegacyPass() : FunctionPass(ID) {
    initializeFlattenCFGLegacyPassPass(*PassRegistry::getPassRegistry());
  }
  bool runOnFunction(Function &F) override;

  void getAnalysisUsage(AnalysisUsage &AU) const override {
    AU.addRequired<AAResultsWrapperPass>();
  }

private:
  AliasAnalysis *AA;
};

bool FlattenCFGLegacyPass::runOnFunction(Function &F) {
  AA = &getAnalysis<AAResultsWrapperPass>().getAAResults();
  bool EverChanged = false;
  // iterativelyFlattenCFG can make some blocks dead.
  while (iterativelyFlattenCFG(F, AA)) {
    removeUnreachableBlocks(F);
    EverChanged = true;
  }
  return EverChanged;
}

// New Pass
struct FlattenCFGPass : PassInfoMixin<FlattenCFGPass> {
  PreservedAnalyses run(Function &F, FunctionAnalysisManager &AM);
};

PreservedAnalyses FlattenCFGPass::run(Function &F,
                                      FunctionAnalysisManager &AM) {
  bool EverChanged = false;
  AliasAnalysis *AA = &AM.getResult<AAManager>(F);
  // iterativelyFlattenCFG can make some blocks dead.
  while (iterativelyFlattenCFG(F, AA)) {
    removeUnreachableBlocks(F);
    EverChanged = true;
  }
  return EverChanged ? PreservedAnalyses::none() : PreservedAnalyses::all();
}
```

两者的pass注册代码如下：

```C++
// Legacy Pass
char FlattenCFGLegacyPass::ID = 0;

INITIALIZE_PASS_BEGIN(FlattenCFGLegacyPass, "flattencfg", "Flatten the CFG",
                      false, false)
INITIALIZE_PASS_DEPENDENCY(AAResultsWrapperPass)
INITIALIZE_PASS_END(FlattenCFGLegacyPass, "flattencfg", "Flatten the CFG",
                    false, false)

#define INITIALIZE_PASS_BEGIN(passName, arg, name, cfg, analysis)              \
  static void *initialize##passName##PassOnce(PassRegistry &Registry) {

#define INITIALIZE_PASS_DEPENDENCY(depName) initialize##depName##Pass(Registry);
#define INITIALIZE_AG_DEPENDENCY(depName)                                      \
  initialize##depName##AnalysisGroup(Registry);

// 上述宏展开后的函数
// static void *initializeFlattenCFGLegacyPassPassOnce(PassRegistry &Registry) {
//   initializeAAResultsWrapperPassPass(Registry);
//   PassInfo *PI =
//       new PassInfo("Flatten the CFG", "flattencfg", &FlattenCFGLegacyPass::ID,
//                    PassInfo::NormalCtor_t(callDefaultCtor<FlattenCFGLegacyPass>),
//                    false, false);
//   Registry.registerPass(*PI, true);
//   return PI;
// }
// static llvm::once_flag InitializeFlattenCFGLegacyPassPassFlag;
// void llvm::initializeFlattenCFGLegacyPassPass(PassRegistry &Registry) {
//   llvm::call_once(InitializeFlattenCFGLegacyPassPassFlag,
//                   initializeFlattenCFGLegacyPassPassOnce, std::ref(Registry));
// }

// New Pass
FunctionPassManager FPM;
FPM.addPass(CREATE_PASS);
```

### 参考资料

* [Writing an LLVM Pass](https://llvm.org/docs/WritingAnLLVMNewPMPass.html)
* [LLVM New Pass Manager](https://llvm.org/docs/NewPassManager.html)
* [LLVM Legacy Pass](https://llvm.org/docs/WritingAnLLVMPass.html)
* [LLVM Pass 其零：新的Pass机制](https://cloud.tencent.com/developer/article/2259875)
* [LLVM Pass 其一：PassManager](https://cloud.tencent.com/developer/article/2259878)
* [LLVM Pass 其二：Analysis与AnalysisManager](https://cloud.tencent.com/developer/article/2259881)
