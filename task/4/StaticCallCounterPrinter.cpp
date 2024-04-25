#include "StaticCallCounterPrinter.hpp"
#include "StaticCallCounter.hpp"

using namespace llvm;

PreservedAnalyses
StaticCallCounterPrinter::run(Module& mod, ModuleAnalysisManager& mam)
{
  // 通过MAM执行StaticCallCounter并返回分析结果
  auto directCalls = mam.getResult<StaticCallCounter>(mod);

  mOut << "=================================================\n";
  mOut << "     sysu-optimizer: static analysis results\n";
  mOut << "=================================================\n";
  mOut << "       NAME             #N DIRECT CALLS\n";
  mOut << "-------------------------------------------------\n";

  for (auto& callCount : directCalls) {
    std::string funcName = callCount.first->getName().str();
    funcName.resize(20, ' ');
    mOut << "       " << funcName << "   " << callCount.second << "\n";
  }

  mOut << "-------------------------------------------------\n\n";
  return PreservedAnalyses::all();
}
