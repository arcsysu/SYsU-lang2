# syntax=docker/dockerfile:1.4
ARG BASE_IMAGE=ubuntu
ARG BASE_TAG=22.04
FROM --platform=$TARGETPLATFORM ${BASE_IMAGE}:${BASE_TAG}
ARG TARGETPLATFORM
COPY antlr/ /opt/SYsU-lang/antlr/
COPY llvm/ /opt/SYsU-lang/llvm/
# Run to install the required packages and clean up
RUN <<EOF
apt-get update -y
apt-get upgrade -y
apt-get install -y --no-install-recommends \
    libantlr4-runtime-dev default-jre-headless pkg-config uuid-dev flex bison \
    clang llvm-dev zlib1g-dev libzstd-dev lld python3 cmake ninja-build git \
    wget curl zip unzip ca-certificates build-essential vim gdb
apt-get autoremove -y
apt-get clean -y
EOF
# Install ANTLR and LLVM
RUN <<EOF
chmod +x /opt/SYsU-lang/antlr/image-install.sh
bash /opt/SYsU-lang/antlr/image-install.sh /opt/SYsU-lang/antlr
chmod +x /opt/SYsU-lang/llvm/image-install.sh
bash /opt/SYsU-lang/llvm/image-install.sh /opt/SYsU-lang/llvm $TARGETPLATFORM
EOF
ENV ANTLR_DIR=/opt/SYsU-lang/antlr/ \
    LLVM_DIR=/opt/SYsU-lang/llvm/
