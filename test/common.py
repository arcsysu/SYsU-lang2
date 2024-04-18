import json
import os
import sys
import math
from typing import NamedTuple, Optional
import argparse


class CasesHelper(NamedTuple):
    """评分测例助手"""

    class Case(NamedTuple):
        name: str
        weight: float
        input: Optional[str]

    srcdir: str
    """测例源目录"""

    bindir: str
    """测例输出目录"""

    cases: list[Case] = []
    """测例表"""

    @staticmethod
    def load_file(srcdir: str, bindir: str, path: str) -> "CasesHelper":
        """从文件加载测例表

        :param str srcdir: 测例源目录
        :param str bindir: 测例输出目录
        :param str path: 测例表文件路径
        """

        ret = CasesHelper(srcdir, bindir)

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    continue  # 跳过注释行

                splits = line.split()
                if not splits:
                    continue

                assert len(splits) <= 2, "权重文件格式错误：每行至多两列"
                if len(splits) == 1:
                    (name,) = splits
                    weight = 1.0
                else:
                    name, weight = splits
                    weight = float(weight)

                assert name.endswith(".sysu.c")

                input_path = os.path.join(
                    srcdir,
                    name.rstrip(".sysu.c") + ".in",
                )
                if not os.path.exists(input_path):
                    input_path = None

                ret.cases.append(
                    CasesHelper.Case(name=name, weight=weight, input=input_path)
                )

        return ret

    def of_srcdir(self, relpath: str) -> str:
        """返回源目录下的文件路径

        :param str relpath: 相对路径
        :return str: 绝对路径
        """
        return os.path.abspath(os.path.join(self.srcdir, relpath))

    def of_bindir(self, relpath: str, mkdir=False) -> str:
        """返回输出目录下的文件路径

        :param str relpath: 相对路径
        :param bool mkdir: 是否创建父目录
        :return str: 绝对路径
        """
        path = os.path.abspath(os.path.join(self.bindir, relpath))
        if mkdir:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def of_case_bindir(self, relpath: str, case: Case, mkdir=False) -> str:
        """返回测例输出目录下的文件路径

        :param str relpath: 相对路径
        :param Case case: 测例
        :param bool mkdir: 是否创建父目录
        :return str: 绝对路径
        """
        return self.of_bindir(os.path.join(case.name, relpath), mkdir)

    def open_autograder_json(self):
        """打开 Autograder 使用的 JSON 文件"""
        path = self.of_bindir("score.json", True)
        return path, open(path, "w", encoding="utf-8")

    def open_root_report(self):
        """打开总评分报告文件"""
        path = self.of_bindir("score.txt", True)
        return path, open(path, "w", encoding="utf-8")

    def open_case_report(self, case: Case):
        """打开单测例评分报告文件"""
        path = self.of_case_bindir("score.txt", case)
        return path, open(path, "w", encoding="utf-8")

    def open_outerr(self, name: str):
        """打开用于重定向子进程 stdout 和 stderr 的两个文件"""
        path_out = self.of_bindir(f"{name}.stdout", True)
        path_err = self.of_bindir(f"{name}.stderr", True)
        return (path_out, open(path_out, "wb"), path_err, open(path_err, "wb"))

    def open_case_outerr(self, case: Case, name: str):
        """打开测例目录中用于重定向子进程 stdout 和 stderr 的两个文件"""
        path_out = self.of_case_bindir(f"{name}.stdout", case, True)
        path_err = self.of_case_bindir(f"{name}.stderr", case, True)
        return (path_out, open(path_out, "wb"), path_err, open(path_err, "wb"))

    def open_case_input(self, case: Case):
        """打开测例输入文件"""
        path = case.input
        if path is None:
            return None, None
        return (path, open(path, "rb"))


class ScoreReport(NamedTuple):
    """评分报告"""

    class TestEntry(NamedTuple):
        name: str  # 为测例的相对路径
        score: int
        max_score: int
        output: str = ""
        output_path: str = ""
        weight: float = 1.0

    class LeaderBoardEntry(NamedTuple):
        name: str
        value: float
        order: int
        is_desc: bool
        suffix: str = ""

    title: str
    tests: list[TestEntry] = []
    leader_board: list[LeaderBoardEntry] = []

    def final_score(self) -> float:
        """计算最终得分（总分）

        :return float: 最终得分
        """

        return sum(i.score * i.weight / len(self.tests) for i in self.tests)

    def final_max_score(self) -> float:
        """计算最终满分

        :return float: 最终满分
        """

        return sum(i.max_score * i.weight / len(self.tests) for i in self.tests)

    def dump_autograder(self, fp, output_prefix="") -> None:
        """转储 Autograder 使用的 JSON 文件

        https://autograder-docs.howardlau.me/user-guide/docker-image-specification/

        :param str fp: 输出文件
        :param str output_prefix: output_path 的前缀
        """

        jobj = {
            "tests": [
                {
                    "name": i.name,
                    "score": math.ceil(i.score),
                    "max_score": math.ceil(i.max_score),
                    "output": i.output,
                    "output_path": os.path.join(output_prefix, i.output_path),
                }
                for i in self.tests
            ],
            "leaderboard": [
                {
                    "name": i.name,
                    "value": '{:.2f}'.format(i.value),
                    "order": i.order,
                    "is_desc": i.is_desc,
                    "suffix": i.suffix,
                }
                for i in self.leader_board
            ],
        }
        json.dump(jobj, fp, ensure_ascii=False, indent=2)

    def dump_human_text(self, fp):
        """转储供人直接阅读的文本文件

        :param str fp: 输出文件
        """

        print(
            f"{self.title}\n总分（加权）："
            + f"{self.final_score():.2f}/{self.final_max_score():.2f}\n",
            file=fp,
        )

        # 计算首列宽
        name_col_len = max(len(i.name) for i in self.tests) + 2

        for i in self.tests:
            print(
                f"{i.name:<{name_col_len}}"
                + f"{i.score:>6.2f}/{i.max_score:<6.2f} "
                + i.output,
                file=fp,
            )

    def print(self, fp=sys.stdout):
        """打印成绩单

        与 dump_text 的区别在于限制了最大列宽，避免显示在屏幕上乱掉。

        :param fp: 输出文件
        """

        for i in self.tests:
            col1 = i.name
            if len(col1) > 60:
                col1 = "... " + col1[-55:]
            col1 = f"{col1 + ' ':.<60}"

            col2 = f" {i.score:.2f}"
            col2 = f"{col2:.>6}/{i.max_score:.2f}"

            print(col1, col2, file=fp, sep="...")

        print(
            f"\n{self.title}\n总分（加权）："
            + f"{self.final_score():.2f}/{self.final_max_score():.2f}",
            file=fp,
        )


def print_parsed_args(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
):
    """打印程序解析到的参数"""

    for action in parser._actions:
        if action.dest == "help":
            continue
        print(
            action.help,
            getattr(args, action.dest),
        )
    print()


def exit_if_cases_cached(bindir: str, cases_file: str) -> bytes:
    """如果测例表已缓存，退出程序

    :param str bindir: 测例输出目录
    :param str cases_file: 测例表路径
    :param str cache_name: 缓存文件名
    :return bytes: 新的缓存文件内容
    """

    cases_cache = os.path.join(bindir, "cases.cache")
    with open(cases_file, "rb") as f:
        new = f.read()
    if os.path.exists(cases_cache):
        with open(cases_cache, "rb") as f:
            old = f.read()
        if new == old:
            print("测例表已缓存，什么都不用做")
            sys.exit(0)
    return new


def cache_cases(bindir: str, content: bytes):
    cases_cache = os.path.join(bindir, "cases.cache")
    with open(cases_cache, "wb") as f:
        f.write(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("提取测例表首列为 CMake 列表")
    parser.add_argument("srcdir", type=str, help="测例源码目录")
    parser.add_argument("bindir", type=str, help="测例输出目录")
    parser.add_argument("cases_file", type=str, help="测例表路径")
    args = parser.parse_args()

    cases_helper = CasesHelper.load_file(
        args.srcdir,
        args.bindir,
        args.cases_file,
    )
    print(";".join(i.name for i in cases_helper.cases))
