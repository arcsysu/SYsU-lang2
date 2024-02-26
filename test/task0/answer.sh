#! /bin/bash
# 搜索指定目录下的所有 .sysu.c 文件，调用 `clang -E` 获取预处理结果，
# 将输出保存到构建目录下的同名文件中。
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
    $1 -E -isystem $2/include $case 1> $4/$case
    echo ""
  else
    echo " [NOT A FILE]"
  fi
done
