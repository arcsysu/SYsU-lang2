## 框架介绍

本次实验的框架主要分为以下两部分：

* 注册优化pass：在`main.cpp`中注册需要使用的优化pass，并指定优化顺序
* 实现优化pass：在optimizor.hpp中定义需要使用的优化pass类，并在其他文件中实现定义的优化pass的函数

### 注册优化pass

注册优化pass的代码主要在`main.cpp`的`opt`函数中：

```C++
void
opt(llvm::Module& mod)
{
  // 定义分析pass的管理器
  LoopAnalysisManager LAM;
  FunctionAnalysisManager FAM;
  CGSCCAnalysisManager CGAM;
  ModuleAnalysisManager MAM;

  // 注册分析pass的管理器
  PassBuilder PB;
  PB.registerModuleAnalyses(MAM);
  PB.registerCGSCCAnalyses(CGAM);
  PB.registerFunctionAnalyses(FAM);
  PB.registerLoopAnalyses(LAM);
  PB.crossRegisterProxies(LAM, FAM, CGAM, MAM);

  // 定义优化pass的管理器
  ModulePassManager MPM;

  // 添加优化pass到管理器中
  MPM.addPass(sysu::HelloWorldPass(llvm::errs()));
  MPM.addPass(sysu::ConstantFolding(llvm::errs()));

  // 运行优化pass
  MPM.run(mod, MAM);
}
```

以上代码的注释清晰地呈现了LLVM IR优化pass的注册过程。同学们只需要将定义好的优化pass按照上述方式实例化后使用`MPM.addPass()`函数添加即可。需要注意的是优化pass的执行顺序与第三部分添加优化pass的顺序相同，因此在优化前需要考虑优化次序对优化结果的影响。

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

### 注册分析pass

待补充

### 实现分析pass

待补充

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
* [LLVM Pass其零：新的Pass机制](https://cloud.tencent.com/developer/article/2259875)
