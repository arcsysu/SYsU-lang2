"""从 .tokens 文件生成用于包含的 C++ 头文件

参数：
    - .tokens 文件路径
    - 输出文件路径
    - （可选）命名空间名
"""

import os
from sys import argv

if len(argv) < 3:
    print(__doc__)
    exit(-1)

tokens_path = argv[1]
output_path = os.path.abspath(argv[2])
namespace = argv[3] if len(argv) >= 4 else ""

tokens: list[tuple[str, int]] = []

with open(tokens_path, "r") as f:
    for line in f:
        if line.startswith("#"):
            continue  # 跳过注释
        line = line.strip()
        if not line:
            continue  # 跳过空行

        name, value = line.split("=")
        tokens.append((name, int(value)))

with open(output_path, "w") as f:
    print(
        f"""/**
* 该文件由：{__file__}
* 自动生成自：{tokens_path}
* 请勿手动修改！
*/

#include <cstdint>

namespace {namespace} {'{'}

""",
        file=f,
        end="",
    )

    for name, value in tokens:
        print(f"constexpr size_t k{name} = {value};", file=f)

    print(
        f"""
{'}'} // namespace {namespace}
""",
        file=f,
        end="",
    )
