#! /bin/bash
# 搜索指定目录下的所有 .sysu.c 文件，调用 `clang -cc1 -O3 -S -emit-llvm`
# 获取输出，将输出保存到同名输出目录 answer.ll 文件中。
#
# 参数：
#   $1: clang 路径
#   $2: rtlib 路径
#   $3: 输入目录
#   $4: 输出目录

cd $3
for case in $(find . -name "*.sysu.c")
do
  echo -n $case
  if [ -f $case ]; then
    $1 -cc1 -O3 -S -emit-llvm -isystem $2/include \
      $case -o $4/$case/answer.ll
    # 复制对应名字但后缀为.in.gz的输入文件到输出目录
    input=${case%.sysu.c}.in.gz
    if [ -f $input ]; then
      cp $input $4/$case/answer.in.gz
    fi
    echo ""
  else
    echo " [NOT A FILE]"
  fi
done
