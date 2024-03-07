import sys
import subprocess as subps
import argparse
import os.path as osp

sys.path.append(osp.abspath(__file__ + "/../.."))
from common import ScoreReport, print_parsed_args

if __name__ == "__main__":
    parser = argparse.ArgumentParser("实验零评测脚本")
    parser.add_argument("bindir", help="输出目录")
    parser.add_argument("exe", help="task0 程序路径")
    args = parser.parse_args()
    print_parsed_args(parser, args)

    report = ScoreReport("task0")

    result = subps.run([args.exe], stdout=subps.PIPE, stderr=subps.PIPE)
    if result.returncode != 0:
        report.tests.append(
            ScoreReport.TestEntry(
                name="程序正常退出",
                score=0,
                max_score=100,
                output=f"程序返回码 {result.returncode}",
            )
        )
    else:
        report.tests.append(
            ScoreReport.TestEntry(
                name="程序正常退出",
                score=100,
                max_score=100,
                output=result.stdout.decode("utf-8"),
            )
        )

    report.print()

    score_json = osp.join(args.bindir, "score.json")
    with open(score_json, "w", encoding="utf-8") as f:
        report.dump_autograder(f)

    score_txt = osp.join(args.bindir, "score.txt")
    with open(score_txt, "w", encoding="utf-8") as f:
        report.dump_human_text(f)

    print("成绩单已保存：", score_txt)
    print("JSON 格式：", score_json)
