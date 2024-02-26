#!/bin/sh
ANTLRDIR=$1
TARGETPLATFORM=$2
ANTLRDIR=$(realpath $ANTLRDIR)
# download the source
wget -c https://www.antlr.org/download/antlr-4.13.1-complete.jar -P $ANTLRDIR
wget -c https://www.antlr.org/download/antlr4-cpp-runtime-4.13.1-source.zip -P $ANTLRDIR
# clear
rm -rf $ANTLRDIR/source $ANTLRDIR/build $ANTLRDIR/install

unzip $ANTLRDIR/antlr4-cpp-runtime-4.13.1-source.zip -d $ANTLRDIR/source
mkdir $ANTLRDIR/build $ANTLRDIR/install

cmake $ANTLRDIR/source -B $ANTLRDIR/build -G Ninja \
  -DCMAKE_INSTALL_PREFIX=$ANTLRDIR/install \
  -DANTLR4_INSTALL=ON \
  -DCMAKE_BUILD_TYPE=Release
cmake --build $ANTLRDIR/build --target install -j $(nproc)

# clear
rm -rf $ANTLRDIR/source $ANTLRDIR/build $ANTLRDIR/antlr4-cpp-runtime-4.13.1-source.zip
