#pragma once

#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/PassManager.h>
#include <llvm/Support/raw_ostream.h>

class StaticCallCounter : public llvm::AnalysisInfoMixin<StaticCallCounter>
{
public:
  using Result = llvm::MapVector<const llvm::Function*, unsigned>;
  Result run(llvm::Module& mod, llvm::ModuleAnalysisManager&);

private:
  // A special type used by analysis passes to provide an address that
  // identifies that particular analysis pass type.
  static llvm::AnalysisKey Key;
  friend struct llvm::AnalysisInfoMixin<StaticCallCounter>;
};
