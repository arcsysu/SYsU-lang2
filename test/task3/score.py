from io import TextIOWrapper
import re
import sys
import argparse
import subprocess as subps
import os.path as osp
import gc
from typing import NamedTuple

sys.path.append(osp.abspath(__file__ + "/../.."))
from common import CasesHelper, ScoreReport, print_parsed_args

TIME_OUT: int = 10
COMP_PATH: str = None
RTLIB_PATH: str = None


class CompHelper(NamedTuple):
    compiler: str
    rtlib_basedir: str
    rtlib_basename: str
    exe: str
    src: str

    def get_comp_cmd(self):
        return [
            f"{self.compiler}",
            "-O0",
            f"-L{self.rtlib_basedir}",
            "-o",
            f"{self.exe}",
            f"{self.src}",
            f"-l{self.rtlib_basename}",
        ]


class RunHelper(NamedTuple):
    exe: str

    def get_run_cmd(self):
        return [f"{self.exe}"]


class Error(Exception):
    pass


def fprint(fp: TextIOWrapper, *args) -> None:
    """输出到fp指向的流

    :param TextIOWrapper fp: 输出流
    :param Any args: 输出的内容
    :return None
    """
    print(*args, file=fp)


def get_tm(sp):
    val = -1
    matchObj = re.findall(b"TOTAL: (\\d*)H-(\\d*)M-(\\d*)S-(\\d*)us", sp.stderr)
    if len(matchObj) == 0:
        return val
    matchObj = matchObj[-1]
    val = int(matchObj[0])
    val = val * 60 + int(matchObj[1])
    val = val * 60 + int(matchObj[2])
    val = val * 1000000 + int(matchObj[3])
    return val


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

    with fp:
        try:
            # 如果没有 answer.ll 文件，零分
            std_answer_path = cases_helper.of_case_bindir("answer.ll", case)
            if not osp.exists(std_answer_path):
                output = "没有可参考的标准答案"
                fprint(fp, "标准参考答案文件不存在：", std_answer_path)
                raise Error()

            # 如果没有 output.ll 文件，零分
            judge_answer_path = cases_helper.of_case_bindir("output.ll", case)
            if not osp.exists(judge_answer_path):
                output = "没有输出结果"
                fprint(fp, "输出结果文件不存在：", judge_answer_path)
                raise Error()

            # 尝试编译标准答案
            try:
                ac_out_path, ac_out, ac_err_path, ac_err = (
                    cases_helper.open_case_outerr(case, "answer_comp")
                )
                comp_helper = CompHelper(
                    compiler=COMP_PATH,
                    rtlib_basedir=osp.dirname(RTLIB_PATH),
                    rtlib_basename=osp.splitext(osp.basename(RTLIB_PATH))[0][3:],
                    exe=cases_helper.of_case_bindir("answer_exe", case),
                    src=std_answer_path,
                )
                subps.run(
                    comp_helper.get_comp_cmd(),
                    stdout=ac_out,
                    stderr=ac_err,
                    timeout=TIME_OUT,
                )
            except Exception as e:
                output = "编译标准答案时出错"
                fprint(fp, "编译标准答案时出错：", e)
                fprint(fp, "出错行数：", e.__traceback__.tb_lineno)
                raise Error(e)
            # 尝试运行标准答案
            try:
                run_helper = RunHelper(
                    exe=cases_helper.of_case_bindir("answer_exe", case)
                )
                std_run_re = subps.run(
                    run_helper.get_run_cmd(),
                    stdin=input_fp,
                    stdout=subps.PIPE,
                    stderr=subps.PIPE,
                    timeout=TIME_OUT,
                )
            except subps.TimeoutExpired as e:
                output = "运行标准答案超时"
                fprint(fp, "运行标准答案超时：", e)
                raise Error(e)
            except Exception as e:
                output = "运行标准答案时出错"
                fprint(fp, "运行标准答案时出错：", e)
                fprint(fp, "出错行数：", e.__traceback__.tb_lineno)
                raise Error(e)
            # 输出运行结果
            fprint(
                fp,
                f"clang -O0 代码执行用时: {get_tm(std_run_re)}us, 返回值 {std_run_re.returncode}",
            )
            # 写回标准答案的输出
            ar_out_path, ar_out, ar_err_path, ar_err = (
                cases_helper.open_case_outerr(case, "answer_run")
            )
            with ar_out, ar_err:
                ar_out.write(std_run_re.stdout)
                ar_err.write(std_run_re.stderr)

            # 尝试编译用户答案
            try:
                jc_out_path, jc_out, jc_err_path, jc_err = (
                    cases_helper.open_case_outerr(case, "output_comp")
                )
                comp_helper = CompHelper(
                    compiler=COMP_PATH,
                    rtlib_basedir=osp.dirname(RTLIB_PATH),
                    rtlib_basename=osp.splitext(osp.basename(RTLIB_PATH))[0][3:],
                    exe=cases_helper.of_case_bindir("output_exe", case),
                    src=std_answer_path,
                )
                subps.run(
                    comp_helper.get_comp_cmd(),
                    stdout=jc_out,
                    stderr=jc_err,
                    timeout=TIME_OUT,
                )
            except Exception as e:
                output = "编译输出结果时出错"
                fprint(fp, "编译输出结果时出错：", e)
                fprint(fp, "出错行数：", e.__traceback__.tb_lineno)
                raise Error(e)
            # 尝试运行用户答案
            try:
                run_helper = RunHelper(
                    exe=cases_helper.of_case_bindir("output_exe", case)
                )
                judge_run_re = subps.run(
                    run_helper.get_run_cmd(),
                    stdin=input_fp,
                    stdout=subps.PIPE,
                    stderr=subps.PIPE,
                    timeout=TIME_OUT,
                )
            except subps.TimeoutExpired as e:
                output = "运行输出结果超时"
                fprint(fp, "运行输出结果超时：", e)
                raise Error(e)
            except Exception as e:
                output = "运行输出结果时出错"
                fprint(fp, "运行输出结果时出错：", e)
                fprint(fp, "出错行数：", e.__traceback__.tb_lineno)
                raise Error(e)
            # 输出运行结果
            fprint(
                fp,
                f"sysu-lang 代码执行用时: {get_tm(judge_run_re)}us, 返回值 {judge_run_re.returncode}",
            )
            # 写回用户答案的输出
            jr_out_path, jr_out, jr_err_path, jr_err = (
                cases_helper.open_case_outerr(case, "output_run")
            )
            with jr_out, jr_err:
                jr_out.write(judge_run_re.stdout)
                jr_err.write(judge_run_re.stderr)

            # 比较返回值
            if std_run_re.returncode != judge_run_re.returncode:
                fprint(fp, "\n返回值不匹配")
                fprint(fp, ">----")
                fprint(fp, "标准答案返回值: %d" % std_run_re.returncode)
                fprint(fp, "用户答案返回值: %d" % judge_run_re.returncode)
                fprint(fp, "<----")
                output = "返回值不匹配"
                raise Error()
            # 比较输出
            if std_run_re.stdout != judge_run_re.stdout:
                fprint(fp, "\n输出不匹配")
                fprint(fp, ">----")
                fprint(fp, "标准答案输出: %s" % std_run_re.stdout)
                fprint(fp, "用户答案输出: %s" % judge_run_re.stdout)
                fprint(fp, "<----")
                output = "输出不匹配"
                raise Error()

            score = max_score
            fprint(fp, "")
            fprint(fp, f"得分：{score:.2f}/{max_score:.2f}")

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

    score_report = ScoreReport("task2")

    for case in cases_helper.cases:
        test_entry = score_one(cases_helper, case)
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
    parser = argparse.ArgumentParser("实验三评测脚本")
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
                    "^task3/" + case_name,
                    # 注意这里一定不能写成 test3/，否则会无限递归下去
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
                [args.ctest_exe, "--test-dir", args.bindir, "-R", "^task3/.*"],
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
