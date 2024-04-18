#include "EmitIR.hpp"
#include "Json2Asg.hpp"
#include "asg.hpp"
#include <fstream>
#include <iostream>
#include <llvm/IR/Verifier.h>
#include <llvm/Support/MemoryBuffer.h>

int
main(int argc, char* argv[])
{
  if (argc != 3) {
    std::cout << "Usage: " << argv[0] << " <input> <output>\n";
    return -1;
  }

  auto inFileOrErr = llvm::MemoryBuffer::getFile(argv[1]);
  if (auto err = inFileOrErr.getError()) {
    std::cout << "Error: unable to open input file: " << argv[1] << '\n';
    return -2;
  }
  auto inFile = std::move(inFileOrErr.get());
  std::error_code ec;
  llvm::StringRef outPath(argv[2]);
  llvm::raw_fd_ostream outFile(outPath, ec);
  if (ec) {
    std::cout << "Error: unable to open output file: " << argv[2] << '\n';
    return -3;
  }

  auto json = llvm::json::parse(inFile->getBuffer());
  if (!json) {
    std::cout << "Error: unable to parse input file: " << argv[1] << '\n';
    return 1;
  }

  // 读取 JSON，转换为 ASG
  Obj::Mgr mgr;
  Json2Asg json2asg(mgr);
  auto asg = json2asg(json.get());
  mgr.mRoot = asg;
  mgr.gc();

  // 从 ASG 发射到 LLVM IR
  llvm::LLVMContext ctx;
  EmitIR emitIR(mgr, ctx);
  auto& mod = emitIR(asg);
  mgr.gc();

  // 先把 LLVM IR 写出到文件里，再检查合不合法
  mod.print(outFile, nullptr, false, true);
  if (llvm::verifyModule(mod, &llvm::outs()))
    return 3;
}
