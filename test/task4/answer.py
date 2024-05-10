"""搜索指定目录下的所有 .sysu.c 文件，调用 `clang -cc1 -O2 -S -emit-llvm`
获取输出，将输出保存到同名输出目录 answer.ll 文件中。然后再调用 Clang 编译
answer.ll 为 answer.exe，再运行 answer.exe，将输出保存到 answer.out 文件中。
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
    parser = argparse.ArgumentParser("实验四答案生成", description=__doc__)
    parser.add_argument("srcdir", help="测例源码目录")
    parser.add_argument("bindir", help="输出目录")
    parser.add_argument("cases_file", help="测例表路径")
    parser.add_argument("clang_exe", help="Clang 程序路径")
    parser.add_argument("rtlib", help="运行时库源码路径")
    parser.add_argument("rtlib_a", help="运行时库文件路径")
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
        # 生成 LLVM IR
        ll_path = cases_helper.of_case_bindir("answer.ll", case, True)
        print(ll_path, end=" ... ", flush=True)
        try:
            with open(ll_path, "w", encoding="utf-8") as f:
                retn = subps.run(
                    [
                        args.clang_exe,
                        "-cc1",
                        "-O2",
                        "-S",
                        "-emit-llvm",
                        "-isystem",
                        osp.join(args.rtlib, "include"),
                        osp.join(args.srcdir, case.name),
                        "-o",
                        "-",
                    ],
                    stdout=f,
                    timeout=30,
                ).returncode
        except subps.TimeoutExpired:
            print("TIMEOUT")
            continue
        if retn:
            print("FAIL", retn)
            exit(1)
        print("OK")

        # 再将 LLVM IR 编译为二进制程序
        exe_path = cases_helper.of_case_bindir("answer.exe", case, True)
        print(exe_path, end=" ... ", flush=True)
        f = open(
            cases_helper.of_case_bindir("answer.compile", case), "w", encoding="utf-8"
        )
        try:
            with f:
                retn = subps.run(
                    [
                        args.clang_exe,
                        "-o",
                        exe_path,
                        "-O0",
                        args.rtlib_a,
                        ll_path,
                    ],
                    stdout=f,
                    stderr=f,
                    timeout=30,
                ).returncode
        except subps.TimeoutExpired:
            print("TIMEOUT")
            continue
        if retn:
            print("FAIL", retn)
            exit(2)
        print("OK")

        # 运行二进制程序，得到程序输出
        out_path = cases_helper.of_case_bindir("answer.out", case, True)
        err_path = cases_helper.of_case_bindir("answer.err", case, True)
        print(out_path, end=" ... ", flush=True)
        print("OK")
        print(err_path, end=" ... ", flush=True)
        with open(out_path, "w", encoding="utf-8") as f, open(
            err_path, "w", encoding="utf-8"
        ) as ferr:
            try:
                retn = subps.run(
                    [exe_path],
                    stdout=f,
                    stderr=ferr,
                    stdin=cases_helper.open_case_input(case)[1],
                    timeout=20,
                ).returncode
                ferr.write(f"Return Code: {retn}\n")
            except subps.TimeoutExpired:
                print("TIMEOUT")
            else:
                print("OK")

    cache_cases(args.bindir, cache)
