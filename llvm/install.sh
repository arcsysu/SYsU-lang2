#!/bin/bash

if [ ! -f llvm-17.0.6.src.tar.xz ]; then
  wget https://github.com/llvm/llvm-project/releases/download/llvmorg-17.0.6/llvm-17.0.6.src.tar.xz
fi
if [ ! -f clang-17.0.6.src.tar.xz ]; then
  wget https://github.com/llvm/llvm-project/releases/download/llvmorg-17.0.6/clang-17.0.6.src.tar.xz
fi
if [ ! -f cmake-17.0.6.src.tar.xz ]; then
  wget https://github.com/llvm/llvm-project/releases/download/llvmorg-17.0.6/cmake-17.0.6.src.tar.xz
fi
rm -rf llvm clang cmake build install

tar -xJvf llvm-17.0.6.src.tar.xz
tar -xJvf clang-17.0.6.src.tar.xz
tar -xJvf cmake-17.0.6.src.tar.xz
mv llvm-17.0.6.src llvm
mv clang-17.0.6.src clang
mv cmake-17.0.6.src cmake

mkdir build install
cmake llvm -B build -G Ninja\
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=$(realpath install) \
  -DLLVM_ENABLE_PROJECTS="clang" \
  -DLLVM_TARGETS_TO_BUILD="X86" \
  -DLLVM_USE_LINKER=lld \
  -DLLVM_INCLUDE_BENCHMARKS=OFF \
  -DLLVM_INCLUDE_EXAMPLES=OFF \
  -DLLVM_INCLUDE_TESTS=OFF
cmake --build build --target install
