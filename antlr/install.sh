#!/bin/bash

if [ ! -f antlr-4.13.1-complete.jar ]; then
  wget https://www.antlr.org/download/antlr-4.13.1-complete.jar
fi
if [ ! -f antlr4-cpp-runtime-4.13.1-source.zip ]; then
  wget https://www.antlr.org/download/antlr4-cpp-runtime-4.13.1-source.zip
fi
rm -rf source build install

unzip antlr4-cpp-runtime-4.13.1-source.zip -d source
mkdir build install

cmake source -B build -G Ninja \
  -DCMAKE_INSTALL_PREFIX=$(realpath install) \
  -DANTLR4_INSTALL=ON
cmake --build build --target install
