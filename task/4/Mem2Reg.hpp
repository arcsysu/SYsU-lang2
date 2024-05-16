#pragma once

#include <llvm/Analysis/AssumptionCache.h>
#include <llvm/Analysis/IteratedDominanceFrontier.h>
#include <llvm/Analysis/InstructionSimplify.h>
#include <llvm/IR/BasicBlock.h>
#include <llvm/IR/Dominators.h>
#include <llvm/IR/Function.h>
#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/Instructions.h>
#include <llvm/IR/PassManager.h>
#include <llvm/Passes/PassBuilder.h>

class Mem2Reg : public llvm::PassInfoMixin<Mem2Reg>
{
public:
  Mem2Reg() {}

  llvm::PreservedAnalyses run(llvm::Module& mod,
                              llvm::ModuleAnalysisManager& mam);
};
