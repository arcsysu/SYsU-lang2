import sys
import argparse
import subprocess as subps
import os.path as osp
import gc

sys.path.append(osp.abspath(__file__ + "/../.."))
from common import CasesHelper, ScoreReport, print_parsed_args


class Error(Exception):
    pass


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
    print(output_path, end=" ... ", flush=True)

    def fprint(*args):
        print(*args, file=fp)

    with fp:
        try:
            # 如果没有 answer.txt 文件，零分
            answer_path = cases_helper.of_case_bindir("answer.txt", case)
            if not osp.exists(answer_path):
                output = "没有可参考的标准答案"
                fprint("标准参考答案文件不存在：", answer_path)
                raise Error()

            # 如果没有 output.txt 文件，零分
            output_path = cases_helper.of_case_bindir("output.txt", case)
            if not osp.exists(output_path):
                output = "没有输出结果"
                fprint("输出结果文件不存在：", output_path)
                raise Error()

            # 读取 answer.txt 和 output.txt 文件
            with open(answer_path, "r", encoding="utf-8") as f:
                answers = f.readlines()
            with open(output_path, "r", encoding="utf-8") as f:
                outputs = f.readlines()

            def split_tokens(t):
                tmp = str(t)
                k1 = tmp.find("'")
                k2 = tmp.rfind("'")
                k3 = tmp.rfind("Loc=<")
                flag0 = 1
                if k1 == -1 or k2 == -1 or k3 == -1:
                    flag0 = 0
                if k1 != -1 and k2 != -1:
                    flag0 = 1
                tok0 = tmp.split()[0].strip()
                str0 = tmp[k1 + 1 : k2].strip()
                mid0 = str(tmp[k2 + 1 : k3].strip().split())
                loc0 = tmp[k3:].strip()
                return [tok0, str0, mid0, loc0, flag0]

            # 如果词法单元数量不一致，零分
            tokens_count = len(answers)
            output_tokens_count = len(outputs)
            if tokens_count != output_tokens_count:
                output = "词法单元数量不一致"
                fprint(
                    "词法单元数量与标准答案不一致："
                    + f"{tokens_count} != {output_tokens_count}"
                )
                fprint("请检查是否有遗漏或多余的词法单元")
                raise Error()

            # 逐个比较词法单元，计算评分
            tokens_kind_correct_count = 0
            tokens_location_correct_count = 0
            tokens_unrelated_correct_count = 0
            for i in range(tokens_count):
                tok0, str0, mid0, loc0, flag0 = split_tokens(answers[i])
                tok1, str1, mid1, loc1, flag1 = split_tokens(outputs[i])

                if flag1 != 1:
                    fprint("\n词法单元 " + str(i + 1) + " 输出格式错误")
                    fprint("< " + answers[i])
                    fprint("---")
                    fprint("> " + outputs[i])
                    continue

                if i == tokens_count - 1:
                    if tok1 == "eof" and str1 == "":
                        tokens_kind_correct_count += 1
                        tokens_location_correct_count += 1
                        tokens_unrelated_correct_count += 1
                        break
                    else:
                        fprint("\n词法单元 " + str(i + 1) + " 类型错误")
                        fprint("< " + tok0)
                        fprint("---")
                        fprint("> " + tok1)
                        continue

                if tok0 != tok1:
                    fprint("\n词法单元 " + str(i + 1) + " 类型错误")
                    fprint("< " + tok0)
                    fprint("---")
                    fprint("> " + tok1)
                    continue

                if str0 != str1:
                    fprint("\n词法单元 " + str(i + 1) + " 值错误")
                    fprint("< " + str0)
                    fprint("---")
                    fprint("> " + str1)
                    continue

                tokens_kind_correct_count += 1

                if loc0 != loc1:
                    fprint("\n词法单元 " + str(i + 1) + " 位置错误")
                    fprint("< " + loc0)
                    fprint("---")
                    fprint("> " + loc1)
                    continue

                tokens_location_correct_count += 1

                if mid0 != mid1:
                    fprint("\n词法单元 " + str(i + 1) + " 识别无关字符错误")
                    fprint("< " + mid0)
                    fprint("---")
                    fprint("> " + mid1)
                    continue

                tokens_unrelated_correct_count += 1

            fprint()
            fprint(
                "类型及值正确的词法单元数目："
                + f"{tokens_kind_correct_count}/{tokens_count}"
            )
            fprint(
                "位置正确的词法单元数目："
                + f"{tokens_location_correct_count}/{tokens_count}"
            )
            fprint(
                "识别无关字符正确的词法单元数目："
                + f"{tokens_unrelated_correct_count}/{tokens_count}"
            )

            score = max_score * (
                tokens_kind_correct_count / tokens_count * 0.6
                + tokens_location_correct_count / tokens_count * 0.3
                + tokens_unrelated_correct_count / tokens_count * 0.1
            )

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

    score_report = ScoreReport("task1")

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
    parser = argparse.ArgumentParser("实验一评测脚本")
    parser.add_argument("srcdir", type=str, help="测例目录")
    parser.add_argument("bindir", type=str, help="测评输出目录")
    parser.add_argument("cases_file", type=str, help="测例表路径")
    parser.add_argument("ctest_exe", type=str, help="CTest 程序路径")
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
        print("运行 CTest 获取结果...")
        print("CTest 运行输出：", out_path, err_path)
        with out, err:
            subps.run(
                [
                    args.ctest_exe,
                    "--test-dir",
                    args.bindir,
                    "-R",
                    "task1/" + case_name,
                    # 注意这里一定不能写成 test1/，否则会无限递归下去
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
        print("运行 CTest 获取结果...")
        print("CTest 运行输出：", out_path, err_path)
        with out, err:
            subps.run(
                [args.ctest_exe, "--test-dir", args.bindir],
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
        print("=" * 80, end="\n\n")

        # 保存成绩单
        txt_path, f = cases_helper.open_root_report()
        with f:
            score_report.dump_human_text(f)
        print("成绩单已保存：", txt_path)

        json_path, f = cases_helper.open_autograder_json()
        with f:
            score_report.dump_autograder(f)
        print("JSON 格式：", json_path)
