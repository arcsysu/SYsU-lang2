import re
import sys
import argparse
import subprocess as subps
import os.path as osp
import gc
import math

sys.path.append(osp.abspath(__file__ + "/../.."))
from common import CasesHelper, ScoreReport, print_parsed_args

TIME_OUT: int = 10
COMP_PATH: str = None
RTLIB_PATH: str = None


class Error(Exception):
    pass


def get_tm(sp):
    val = -1
    ret = -1
    matchTimerObj = re.findall("Timer@(\\d*)-(\\d*): (\\d*)H-(\\d*)M-(\\d*)S-(\\d*)us", sp)
    matchTotalObj = re.findall("TOTAL: (\\d*)H-(\\d*)M-(\\d*)S-(\\d*)us", sp)
    matchRetObj = re.findall("Return Code: (\\d*)", sp)
    if len(matchRetObj) == 0 or len(matchTotalObj) == 0:
        # 没有计时区且没有总计时区，说明格式错误
        val = -2
        ret = -2
        return val, ret
    matchTotalObj = matchTotalObj[-1]
    val = int(matchTotalObj[0])
    val = val * 60 + int(matchTotalObj[1])
    val = val * 60 + int(matchTotalObj[2])
    val = val * 1000000 + int(matchTotalObj[3])
    matchRetObj = matchRetObj[-1]
    ret = int(matchRetObj)
    if len(matchTimerObj) == 0:
        # 没有计时区，说明为功能检测测例
        val = -1
    return val, ret


def score_one(
    cases_helper: CasesHelper, case: CasesHelper.Case
) -> ScoreReport.TestEntry:
    """评测单个测例，打印出一行评测结果"""

    name = case.name
    score = 0.0
    max_score = 100.0
    output = "[PASS]"
    weight = case.weight
    output_path, fp = cases_helper.open_case_report(case)
    input_path, input_fp = cases_helper.open_case_input(case)
    print(output_path, end=" ... ", flush=True)

    def fprint(*args):
        print(*args, file=fp)

    with fp:
        try:
            # 如果没有标准答案的相关文件，零分
            answer_out_path = cases_helper.of_case_bindir("answer.out", case)
            answer_err_path = cases_helper.of_case_bindir("answer.err", case)
            if not osp.exists(answer_out_path):
                output = "没有可参考的标准答案"
                fprint("标准参考答案文件不存在：", answer_out_path)
                raise Error()
            if not osp.exists(answer_err_path):
                output = "没有可参考的标准答案"
                fprint("标准参考答案文件不存在：", answer_err_path)
                raise Error()

            # 如果没有 output.ll 文件，零分
            judge_answer_path = cases_helper.of_case_bindir("output.ll", case)
            if not osp.exists(judge_answer_path):
                output = "没有输出结果"
                fprint("输出结果文件不存在：", judge_answer_path)
                raise Error()

            # 如果runtime library不存在，零分
            if not osp.exists(RTLIB_PATH):
                output = "运行时库不存在, 点击test-rtlib生成"
                fprint("运行时库不存在， 点击test-rtlib生成：", RTLIB_PATH)
                raise Error()

            # 尝试编译学生答案
            output_exe_path = cases_helper.of_case_bindir("output.exe", case)
            try:
                with open(
                    cases_helper.of_case_bindir("output.compile", case),
                    "w",
                    encoding="utf-8",
                ) as f:
                    subps.run(
                        [
                            COMP_PATH,
                            "-o",
                            output_exe_path,
                            "-O0",
                            RTLIB_PATH,
                            judge_answer_path,
                        ],
                        stdout=f,
                        stderr=f,
                        timeout=TIME_OUT,
                    )
            except Exception as e:
                output = "编译输出结果时出错"
                fprint("编译输出结果时出错：", e)
                fprint("出错行数：", e.__traceback__.tb_lineno)
                raise Error(e)

            # 尝试运行用户答案
            try:
                output_out_path = cases_helper.of_case_bindir("output.out", case)
                output_err_path = cases_helper.of_case_bindir("output.err", case)
                with open(output_out_path, "w", encoding="utf-8") as f, open(
                    output_err_path, "w", encoding="utf-8"
                ) as ferr:
                    retn = subps.run(
                        [output_exe_path],
                        stdin=input_fp,
                        stdout=f,
                        stderr=ferr,
                        timeout=TIME_OUT,
                    ).returncode
                    ferr.write(f"Return Code: {retn}\n")
            except subps.TimeoutExpired as e:
                output = "运行输出结果超时"
                fprint("运行输出结果超时：", e)
                raise Error(e)
            except Exception as e:
                output = "运行输出结果时出错"
                fprint("运行输出结果时出错：", e)
                fprint("出错行数：", e.__traceback__.tb_lineno)
                raise Error(e)

            # 比较输出
            with open(answer_out_path, "r", encoding="utf-8") as f:
                answer_out = f.read()
            with open(output_out_path, "r", encoding="utf-8") as f:
                output_out = f.read()
            with open(answer_err_path, "r", encoding="utf-8") as f:
                answer_err = f.read()
            with open(output_err_path, "r", encoding="utf-8") as f:
                output_err = f.read()

            answer_time, answer_ret = get_tm(answer_err)
            output_time, output_ret = get_tm(output_err)
            if answer_time == -2 and answer_ret == -2:
                output = "标准答案运行输出格式有误，应增大运行时间限制"
                raise Error()
            if output_time == -2 and output_ret == -2:
                output = "用户答案运行输出格式有误，检查生成的代码是否有误"
                raise Error()
            
            if answer_time == -1:
                max_score = 1.0

            fprint(f"O2 代码执行用时: {answer_time} us")
            fprint(f"sysu-lang 代码执行用时: {output_time} us")
            if answer_out != output_out:
                fprint("\n输出不匹配")
                fprint(">----")
                fprint("标准答案: %s" % answer_out)
                fprint("用户答案: %s" % output_out)
                fprint("<----")
                output = "输出不匹配"
                raise Error()

            if answer_ret != output_ret:
                fprint("\n返回值不匹配")
                fprint(">----")
                fprint("标准答案: %d" % answer_ret)
                fprint("用户答案: %d" % output_ret)
                fprint("<----")
                output = "返回值不匹配"
                raise Error()

            if answer_time == -1:
                output = "功能检测通过"
                score = max_score
                raise Error()
            if output_time == -1:
                output = "用户答案计时错误"
                raise Error()
            if output_time == 0:
                score = max_score
            elif answer_time == 0:
                score = 0.0
            else:
                score = max_score * math.sqrt((answer_time / output_time))
            # 超出分数则取最大分
            if score > max_score:
                score = max_score
            fprint("")
            fprint(f"得分：{score:.2f}/{max_score:.2f}")

        except Error:
            pass

    print(output)
    return ScoreReport.TestEntry(
        name=name,
        score=score,
        max_score=max_score,
        output=output,
        output_path=output_path,
        weight=weight,
    )


def score_all(cases_helper: CasesHelper) -> ScoreReport:
    """评测所有测例，生成成绩单"""

    score_report = ScoreReport("task4")

    for case in cases_helper.cases:
        test_entry = score_one(cases_helper, case)
        if test_entry.weight == 0:
            if test_entry.score != test_entry.max_score:
                break
        else:
            score_report.tests.append(test_entry)
        gc.collect()

    score_report.leader_board.append(
        ScoreReport.LeaderBoardEntry(
            "总分",
            score_report.final_score(),
            0,
            True,
            "",
        )
    )

    return score_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser("实验四评测脚本")
    parser.add_argument("srcdir", type=str, help="测例目录")
    parser.add_argument("bindir", type=str, help="测评输出目录")
    parser.add_argument("cases_file", type=str, help="测例表路径")
    parser.add_argument("ctest_exe", type=str, help="CTest 程序路径")
    parser.add_argument("comp_path", type=str, help="编译器路径")
    parser.add_argument("rtlib_path", type=str, help="运行时库路径")
    parser.add_argument("--single", type=str, help="运行单个测例")
    args = parser.parse_args()
    print_parsed_args(parser, args)

    print("加载测例表...", end="", flush=True)
    cases_helper = CasesHelper.load_file(
        args.srcdir,
        args.bindir,
        args.cases_file,
    )
    print("完成")

    COMP_PATH = args.comp_path
    RTLIB_PATH = args.rtlib_path

    if case_name := args.single:
        for case in cases_helper.cases:
            if case.name == case_name:
                break
        else:
            print("没有找到指定的测例：", case_name)
            sys.exit(1)

        # 通过 CTest 运行同学们的代码
        case_outerr = cases_helper.open_case_outerr(case, "ctest")
        out_path, out, err_path, err = case_outerr
        print("CTest 运行日志：", out_path, err_path)
        print("运行 CTest 以得到结果...", end="", flush=True)
        with out, err:
            subps.run(
                [
                    args.ctest_exe,
                    "--test-dir",
                    args.bindir,
                    "-R",
                    "^task4/" + case_name,
                    # 注意这里一定不能写成 test4/，否则会无限递归下去
                ],
                stdout=out,
                stderr=err,
            )
        print("完成")

        score_one(cases_helper, case)
        print("评测结果已保存：", cases_helper.of_case_bindir("score.txt", case))

    else:
        # 通过 CTest 运行同学们的代码
        out_path, out, err_path, err = cases_helper.open_outerr("ctest")
        print("CTest 运行日志：", out_path, err_path)
        print("运行 CTest 以得到结果...", end="", flush=True)
        with out, err:
            subps.run(
                [args.ctest_exe, "--test-dir", args.bindir, "-R", "^task4/.*"],
                stdout=out,
                stderr=err,
            )
        print("完成")

        # 评分，生成成绩单
        print()
        score_report = score_all(cases_helper)
        print()

        print("=" * 80)
        score_report.print()
        print("=" * 80)

        # 保存成绩单
        txt_path, f = cases_helper.open_root_report()
        with f:
            score_report.dump_human_text(f)
        print("成绩单已保存：", cases_helper.of_bindir("score.txt"))

        json_path, f = cases_helper.open_autograder_json()
        with f:
            score_report.dump_autograder(f)
        print("JSON 格式：", cases_helper.of_bindir("score.json"))
