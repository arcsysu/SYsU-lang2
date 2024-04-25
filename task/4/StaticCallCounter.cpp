#include "StaticCallCounter.hpp"

using namespace llvm;

StaticCallCounter::Result
StaticCallCounter::run(Module& mod, ModuleAnalysisManager&)
{
  MapVector<const Function*, unsigned> result;

  for (auto& func : mod) {
    for (auto& bb : func) {
      for (auto& inst : bb) {
        // 尝试转为CallInst
        auto* callInst = dyn_cast<CallInst>(&inst);
        if (callInst == nullptr) {
          continue;
        }

        // 获取被调用函数
        auto directInvoc = callInst->getCalledFunction();
        if (directInvoc == nullptr) {
          continue;
        }

        // 统计函数在源代码中被调用次数
        auto callCount = result.find(directInvoc);
        if (result.end() == callCount) {
          callCount = result.insert({ directInvoc, 0 }).first;
        }
        ++callCount->second;
      }
    }
  }

  return result;
}

AnalysisKey StaticCallCounter::Key;
