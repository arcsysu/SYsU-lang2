"""对给定的测例表调用 `clang -cc1 -dump-tokens` 获取输出，
将输出保存到同名输出目录下的 answer.txt 文件中。
"""

import sys
import os.path as osp
import argparse
import subprocess as subps

sys.path.append(osp.abspath(__file__ + "/../.."))
from common import (
    CasesHelper,
    print_parsed_args,
    exit_if_cases_cached,
    cache_cases,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("实验一答案生成", description=__doc__)
    parser.add_argument("srcdir", help="测例源码目录")
    parser.add_argument("bindir", help="输出目录")
    parser.add_argument("cases_file", help="测例表路径")
    parser.add_argument("clang_exe", help="Clang 程序路径")
    parser.add_argument("rtlib", help="运行时库路径")
    args = parser.parse_args()
    print_parsed_args(parser, args)

    cache = exit_if_cases_cached(args.bindir, args.cases_file)

    print("加载测例表...", end="", flush=True)
    cases_helper = CasesHelper.load_file(
        args.srcdir,
        args.bindir,
        args.cases_file,
    )
    print("完成")

    for case in cases_helper.cases:
        path = cases_helper.of_bindir(case.name + "/answer.txt", True)
        print(path, end=" ... ", flush=True)
        with open(path, "w", encoding="utf-8") as f:
            subps.run(
                [
                    args.clang_exe,
                    "-cc1",
                    "-dump-tokens",
                    osp.join(args.srcdir, case.name),
                ],
                stderr=f,
            )
        print("OK")

    cache_cases(args.bindir, cache)
