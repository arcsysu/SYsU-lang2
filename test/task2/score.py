from io import TextIOWrapper
import sys
import argparse
import subprocess as subps
import os.path as osp
import gc
import json
import yaml
from typing import Any

sys.path.append(osp.abspath(__file__ + "/../.."))
from common import CasesHelper, ScoreReport, print_parsed_args

log_level = 3
key_inner = ["inner"]
kind_initlist = ["InitListExpr"]
key_ignore = ["id"]
level1_kind = ["kind", "name", "value"]
level2_kind = ["type"]


class NodeHelper:
    """节点助手"""

    level1_correct: bool = True
    level2_correct: bool = True
    level3_correct: bool = True
    ast0: dict = None
    ast1: dict = None

    def __init__(
        self,
        level1_correct: bool = True,
        level2_correct: bool = True,
        level3_correct: bool = True,
        ast0: dict = None,
        ast1: dict = None,
    ):
        self.level1_correct = level1_correct
        self.level2_correct = level2_correct
        self.level3_correct = level3_correct
        self.ast0 = ast0
        self.ast1 = ast1

    def to_json_noinner(self, fp: TextIOWrapper) -> None:
        fprint(fp, "\n>---")
        ast0_noinner = self.ast0.copy()
        ast1_noinner = self.ast1.copy()
        for key in ["inner", "id"]:
            if key in ast0_noinner:
                del ast0_noinner[key]
            if key in ast1_noinner:
                del ast1_noinner[key]
        fprint(fp, "\n标准答案节点: \n" + str(ast0_noinner))
        fprint(fp, "\n用户答案节点: \n" + str(ast1_noinner))
        fprint(fp, "\n<---")
        return

    def to_json_inner_n(self, fp: TextIOWrapper, inner_n: int) -> None:
        fprint(fp, "\n>---")
        ast0_copy = self.ast0.copy()
        ast1_copy = self.ast1.copy()
        for key in ["id"]:
            if key in ast0_copy:
                del ast0_copy[key]
            if key in ast1_copy:
                del ast1_copy[key]
        ast0_inner_n = None
        ast1_inner_n = None
        for key in ["inner"]:
            if key in ast0_copy:
                ast0_inner_n = ast0_copy[key][inner_n]
                del ast0_copy[key]
            if key in ast1_copy:
                ast1_inner_n = ast1_copy[key][inner_n]
                del ast1_copy[key]
        fprint(fp, "\n标准答案节点: \n" + str(ast0_copy))
        fprint(fp, "\n标准答案节点inner的第n项: \n" + str(ast0_inner_n))
        fprint(fp, "\n用户答案节点: \n" + str(ast1_copy))
        fprint(fp, "\n用户答案节点inner的第n项: \n" + str(ast1_inner_n))
        fprint(fp, "\n<---")
        return

    def to_yaml(
        self, fp: TextIOWrapper, lv: int, key_to_add: list, inner_err_idx: list
    ) -> None:
        fprint(
            fp, "\n>----------------------------对比开始----------------------------"
        )
        ast0_cp = dict()
        ast1_cp = dict()
        for key in key_to_add:
            ast0_cp[key] = self.ast0.get(key)
            ast1_cp[key] = self.ast1.get(key)
        if len(inner_err_idx) > 0:
            ast0_cp["inner"] = []
            ast1_cp["inner"] = []
        inner_cp_idx = 0
        for i in inner_err_idx:
            for j in range(inner_cp_idx, i):
                ast0_cp["inner"].append("...")
                ast1_cp["inner"].append("...")
            ast0_cp["inner"].append(self.ast0["inner"][i])
            ast1_cp["inner"].append(self.ast1["inner"][i])
            inner_cp_idx = i + 1
        fprint(fp, "\n标准答案节点: \n" + yaml.dump(ast0_cp))
        fprint(fp, "\n用户答案节点: \n" + yaml.dump(ast1_cp))
        fprint(
            fp,
            "\n<----------------------------对比结束----------------------------\n\n",
        )
        return

    def to_dot(self, fp: TextIOWrapper) -> None:
        pass

    def check_key(self, key: str, key_level: int) -> tuple:
        value0 = self.ast0.get(key)
        level_output = ""
        if value0 is None:
            return True, level_output
        value1 = self.get_value1(key, key_level)
        if value1 is None:
            level_output += "\n键 '" + key + "' 在用户答案节点内不存在"
            return False, level_output
        if type(value0) is not type(value1):
            level_output += "\n键 '" + key + "' 对应的值类型错误"
            return False, level_output
        if key == "type":
            qualType0 = value0.get("qualType")
            qualType1 = value1.get("qualType")
            if qualType0 is None:
                return True, level_output
            if qualType1 is None or qualType0 != qualType1:
                level_output += "\n键 '" + key + "' 的qualType对应值错误"
                return False, level_output
            return True, level_output
        if value0 != value1:
            level_output += "\n键 '" + key + "' 错误"
            return False, level_output
        return True, level_output

    def get_value1(self, key: str, key_level: int) -> Any:
        # 如果 key 在 ast1 中存在，直接返回对应的值
        if key in self.ast1:
            return self.ast1.get(key)
        self.level3_correct = False
        if key_level == 2:
            self.level2_correct = False
        if key_level == 1:
            self.level2_correct = False
            self.level1_correct = False
        return None

    @staticmethod
    def filter_value0(value0: list) -> list:
        return list(
            filter(
                lambda x: not x.get("isImplicit", False)
                and not x.get("implicit", False),
                value0,
            )
        )

    @staticmethod
    def filter_ast(ast: dict) -> None:
        if ast_inner := ast.get("inner"):
            for i in ast_inner:
                NodeHelper.filter_ast(i)
            ast["inner"] = NodeHelper.filter_value0(ast_inner)


class AstHelper:
    """语法树助手"""

    all_count: int = 0
    level1_all_count: int = 0
    level1_correct_count: int = 0
    level2_correct_count: int = 0
    level3_correct_count: int = 0

    def __init__(
        self,
        all_count: int = 0,
        level1_all_count: int = 0,
        level1_correct_count: int = 0,
        level2_correct_count: int = 0,
        level3_correct_count: int = 0,
    ):
        self.all_count = all_count
        self.level1_all_count = level1_all_count
        self.level1_correct_count = level1_correct_count
        self.level2_correct_count = level2_correct_count
        self.level3_correct_count = level3_correct_count

    def inc_all_count(self):
        self.all_count += 1

    def inc_l1_all_count(self):
        self.level1_all_count += 1

    def inc_l1_correct_count(self):
        self.level1_correct_count += 1

    def inc_l2_correct_count(self):
        self.level2_correct_count += 1

    def inc_l3_correct_count(self):
        self.level3_correct_count += 1


class Error(Exception):
    pass


def fprint(fp: TextIOWrapper, *args) -> None:
    """输出到fp指向的流

    :param TextIOWrapper fp: 输出流
    :param Any args: 输出的内容
    """
    print(*args, file=fp)


def get_key_level(key: str, kind: str) -> int:
    """获取键值的等级

    :param str key: 键值
    :return int: 返回键值的等级
    """
    if key in level1_kind:
        return 1
    if key in level2_kind:
        return 2
    if key in key_inner:
        if kind in kind_initlist:
            return 2
        return 1
    return 3


def check_ast(
    ast0: Any, ast1: Any, ast_helper: AstHelper, status: int, fp: TextIOWrapper
) -> dict:
    """比较两个 ast 是否相同，采用深度优先遍历

    :param Any ast0: 标准答案的子树
    :param Any ast1: 输出结果的子树
    :param AstHelper ast_helper: 语法树助手
    :param int status: 状态
        0: 正常，未在 InitListExpr 中
        1: 错误，未在 InitListExpr 中
        2: 正常，在 InitListExpr 中
        3: 错误，在 InitListExpr 中
    :param TextIOWrapper fp: 输出文件
    :return NodeHelper node_helper: 节点助手，记录每一个节点不同等级的正确性
    """

    ast_helper.inc_all_count()
    if status == 0 or status == 1:
        ast_helper.inc_l1_all_count()

    # status 为 1 或者 3 时，说明 ast1 在之前已经不匹配了，但还是需要遍历所有节点统计总的节点数
    if status == 1 or status == 3:
        node_helper = NodeHelper(False, False, False, ast0, ast1)
        # 如果有 inner 节点，需要继续遍历
        if value0 := ast0.get("inner"):
            value0 = NodeHelper.filter_value0(value0)
            son_err_status = status
            if get_key_level("inner", ast0.get("kind")) == 2:
                son_err_status = 3
            for i in range(len(value0)):
                # 遍历 inner 的每一项
                check_ast(value0[i], None, ast_helper, son_err_status, fp)
        return node_helper

    # 如果 ast0 和 ast1 的类型不同，直接返回错误
    if type(ast0) is not type(ast1):
        fprint(fp, "\n节点类型错误")
        node_helper = NodeHelper(False, False, False, ast0, None)
        fprint(fp, "\n>------------------------------------------------------------")
        fprint(fp, "\n标准答案节点: \n" + yaml.dump(ast0))
        fprint(fp, "\n<------------------------------------------------------------")
        # 如果有 inner 节点，需要继续遍历
        if value0 := ast0.get("inner"):
            value0 = NodeHelper.filter_value0(value0)
            son_err_status = status
            if get_key_level("inner", ast0.get("kind")) == 2:
                son_err_status = 3
            for i in range(len(value0)):
                # 遍历 inner 的每一项
                check_ast(value0[i], None, ast_helper, son_err_status, fp)
        return node_helper

    node_helper = NodeHelper(True, True, True, ast0, ast1)

    # new--------------------------------------------------------
    # level3 为除了level1和level2之外的键
    level3_kind = [
        key
        for key in ast0.keys()
        if key not in level1_kind
        and key not in key_inner
        and key not in level2_kind
        and key not in key_ignore
    ]

    def check_inner():

        def goon_check_ast():
            for i in range(len(value0)):
                son_node_helper = check_ast(
                    value0[i], None, ast_helper, son_err_status, fp
                )

        nonlocal level_output, key_level, ast_helper, son_err_status, fp
        key = "inner"
        value0 = ast0.get(key)
        value1 = node_helper.get_value1(key, key_level)
        if value1 is None:
            level_output += "\n键 'inner' 在用户答案节点内不存在"
            goon_check_ast()
        else:
            value0 = NodeHelper.filter_value0(value0)
            value1 = NodeHelper.filter_value0(value1)
            if len(value0) != len(value1):
                level_output += "\ninner 长度不匹配"
                level_output += "\n标准答案节点 inner 长度: " + str(len(value0))
                level_output += "\n用户答案节点 inner 长度: " + str(len(value1))
                goon_check_ast()
            else:
                for i in range(len(value0)):
                    son_node_helper = check_ast(
                        value0[i], value1[i], ast_helper, inner_status, fp
                    )
                    if (
                        son_node_helper.level1_correct
                        and son_node_helper.level2_correct
                        and son_node_helper.level3_correct
                    ):
                        continue
                    node_helper.level3_correct = False
                    if inner_status == 0 and not son_node_helper.level1_correct:
                        # 暂时不把level2也置为False
                        # node_helper.level2_correct = False
                        node_helper.level1_correct = False
                        level_output += "\ninner 错误，第" + str(i) + "项"
                    if inner_status == 2 and not son_node_helper.level2_correct:
                        node_helper.level2_correct = False
                        level_output += "\ninner 错误，第" + str(i) + "项"
                    inner_err_idx.append(i)

    level_output = "本节点情况 level 1: "
    key_level = 1
    inner_err_idx = []
    key_err = ["kind", "name", "value", "id"]
    for key in level1_kind:
        key_cor, level_app_output = node_helper.check_key(key, key_level)
        level_output += level_app_output
        if not key_cor:
            node_helper.level1_correct = False
            key_err.append(key)
    if ast0.get("inner") is not None and ast0.get("kind") not in kind_initlist:
        inner_status = 0
        son_err_status = 1
        check_inner()
    # 输出 level_output
    if not node_helper.level1_correct and log_level >= 1:
        fprint(fp, level_output)
        node_helper.to_yaml(fp, key_level, key_err, inner_err_idx)

    level_output = "本节点情况 level 2: "
    key_level = 2
    inner_err_idx = []
    key_err = ["kind", "name", "value", "id"]
    for key in level2_kind:
        key_cor, level_app_output = node_helper.check_key(key, key_level)
        level_output += level_app_output
        if not key_cor:
            node_helper.level2_correct = False
            key_err.append(key)
    if ast0.get("inner") is not None and ast0.get("kind") in kind_initlist:
        inner_status = 2
        son_err_status = 3
        check_inner()
    # 输出 level_output
    if not node_helper.level2_correct and log_level >= 2:
        fprint(fp, level_output)
        node_helper.to_yaml(fp, key_level, key_err, inner_err_idx)

    level_output = "本节点情况 level 3: "
    key_level = 3
    inner_err_idx = []
    key_err = ["kind", "name", "value", "id"]
    for key in level3_kind:
        key_cor, level_app_output = node_helper.check_key(key, key_level)
        level_output += level_app_output
        if not key_cor:
            node_helper.level3_correct = False
            key_err.append(key)
    # 输出 level_output
    if not node_helper.level3_correct and log_level >= 3:
        fprint(fp, level_output)
        node_helper.to_yaml(fp, key_level, key_err, inner_err_idx)
    # new--------------------------------------------------------
    """# old--------------------------------------------------------
    # 遍历 ast0 的每一个键值对
    for key, value0 in ast0.items():
        if key in key_ignore:
            continue

        key_level = get_key_level(key, ast0.get("kind"))
        value1 = node_helper.get_value1(key, key_level)
        # 如果是 inner 节点，需要继续遍历
        if key in key_inner:
            value0 = NodeHelper.filter_value0(value0)
            if value1 is None:
                son_status = 3 if key_level == 2 else 1
                for i in range(len(value0)):
                    son_node_helper = check_ast(
                        value0[i], None, ast_helper, son_status, fp
                    )
                continue
            value1 = list(
                filter(
                    lambda x: not x.get("isImplicit", False)
                    and not x.get("implicit", False),
                    value1,
                )
            )
            # 如果 ast0 和 ast1 的 inner 长度不同，直接返回错误
            if len(value0) != len(value1):
                node_helper.level3_correct = False
                son_status = 3 if key_level == 2 else 1
                if key_level == 2 and log_level >= 2:
                    node_helper.level2_correct = False
                    fprint(fp, "\ninner 长度不匹配")
                    fprint(fp, "标准答案节点 inner 长度: " + str(len(value0)))
                    fprint(fp, "用户答案节点 inner 长度: " + str(len(value1)))
                    node_helper.to_json_noinner(fp)
                if key_level == 1 and log_level >= 1:
                    node_helper.level2_correct = False
                    node_helper.level1_correct = False
                    fprint(fp, "\ninner 长度不匹配")
                    fprint(fp, "标准答案节点 inner 长度: " + str(len(value0)))
                    fprint(fp, "用户答案节点 inner 长度: " + str(len(value1)))
                    node_helper.to_json_noinner(fp)
                for i in range(len(value0)):
                    check_ast(value0[i], None, ast_helper, son_status, fp)
                continue
            # 遍历 inner 的每一项
            for i in range(len(value0)):
                son_status = 2 if key_level == 2 else 0
                son_node_helper = check_ast(
                    value0[i], value1[i], ast_helper, son_status, fp
                )
                # inner 的每一项都正确，直接跳过
                if (
                    son_node_helper.level1_correct
                    and son_node_helper.level2_correct
                    and son_node_helper.level3_correct
                ):
                    continue
                node_helper.level3_correct = False
                if key_level == 2 and log_level >= 2:
                    node_helper.level2_correct = False
                    fprint(fp, "\ninner 错误")
                    node_helper.to_json_inner_n(fp, i)
                if key_level == 1 and log_level >= 1:
                    node_helper.level2_correct = False
                    node_helper.level1_correct = False
                    fprint(fp, "\ninner 错误")
                    node_helper.to_json_inner_n(fp, i)
        else:
            if value1 is None or value1 == value0:
                continue
            if key_level == 3 and log_level >= 3:
                fprint(fp, "\n键值 '" + key + "' 错误")
                node_helper.to_json_noinner(fp)
            node_helper.level3_correct = False
            if key_level == 2:
                node_helper.level2_correct = False
                if log_level >= 2:
                    fprint(fp, "\n键值 '" + key + "' 错误")
                    node_helper.to_json_noinner(fp)
            if key_level == 1:
                node_helper.level2_correct = False
                node_helper.level1_correct = False
                if log_level >= 1:
                    fprint(fp, "\n键值 '" + key + "' 错误")
                    node_helper.to_json_noinner(fp)
    # old--------------------------------------------------------"""
    if node_helper.level1_correct and status == 0:
        ast_helper.inc_l1_correct_count()
    if node_helper.level2_correct:
        ast_helper.inc_l2_correct_count()
    if node_helper.level3_correct:
        ast_helper.inc_l3_correct_count()
    return node_helper


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

    with fp:
        try:
            # 如果没有 answer.json 文件，零分
            std_answer_path = cases_helper.of_case_bindir("answer.json", case)
            if not osp.exists(std_answer_path):
                output = "没有可参考的标准答案"
                fprint(fp, "标准参考答案文件不存在：", std_answer_path)
                raise Error()

            # 如果没有 output.json 文件，零分
            judge_answer_path = cases_helper.of_case_bindir("output.json", case)
            if not osp.exists(judge_answer_path):
                output = "没有输出结果"
                fprint(fp, "输出结果文件不存在：", judge_answer_path)
                raise Error()

            # 读取标准答案
            try:
                with open(std_answer_path, "r") as f:
                    std_answer = json.load(f)
                    gc.collect()
            except Exception as e:
                output = "标准答案文件损坏"
                fprint(fp, "标准答案文件损坏：", std_answer_path)
                raise Error(e)
            # 转化成 yaml 格式输出
            try:
                NodeHelper.filter_ast(std_answer)
                with open(cases_helper.of_case_bindir("answer.yaml", case), "w") as f:
                    f.write(yaml.dump(std_answer))
            except Exception as e:
                output = "转化为yaml失败"
                fprint(fp, "转化为yaml失败")
                raise Error(e)

            # 读取输出结果
            try:
                with open(judge_answer_path, "r") as f:
                    judge_answer = json.load(f)
                    gc.collect()
            except Exception as e:
                output = "输出结果文件损坏"
                fprint(fp, "输出结果文件损坏：", judge_answer_path)
                raise Error(e)
            # 转化成 yaml 格式输出
            try:
                NodeHelper.filter_ast(judge_answer)
                with open(cases_helper.of_case_bindir("output.yaml", case), "w") as f:
                    f.write(yaml.dump(judge_answer))
            except Exception as e:
                output = "转化为yaml失败"
                fprint(fp, "转化为yaml失败")
                raise Error(e)

            ast_helper = AstHelper()
            node_helper = NodeHelper()
            # 比较标准答案和输出结果
            check_ast(std_answer, judge_answer, ast_helper, 0, fp)

            fprint(fp, "")
            fprint(fp, "生成树节点总数:" + f"{ast_helper.all_count}")
            fprint(fp, "生成树中level1节点总数:" + f"{ast_helper.level1_all_count}")
            fprint(
                fp,
                "level1: kind, name, value正确:"
                + f"{ast_helper.level1_correct_count}/{ast_helper.level1_all_count}",
            )
            fprint(
                fp,
                "level2: type, InitListExpr生成树正确:"
                + f"{ast_helper.level2_correct_count}/{ast_helper.all_count}",
            )
            fprint(
                fp,
                "level3: 除id外其他属性全部正确:"
                + f"{ast_helper.level3_correct_count}/{ast_helper.all_count}",
            )
            score = max_score * (
                ast_helper.level1_correct_count * 0.6 / ast_helper.level1_all_count
                + ast_helper.level2_correct_count * 0.4 / ast_helper.all_count
            )
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
    parser = argparse.ArgumentParser("实验二评测脚本")
    parser.add_argument("srcdir", type=str, help="测例目录")
    parser.add_argument("bindir", type=str, help="测评输出目录")
    parser.add_argument("cases_file", type=str, help="测例表路径")
    parser.add_argument("ctest_exe", type=str, help="CTest 程序路径")
    parser.add_argument("log_level", type=int, help="日志等级")
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

    log_level = args.log_level

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
                    "^task2/" + case_name,
                    # 注意这里一定不能写成 test2/，否则会无限递归下去
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
                [args.ctest_exe, "--test-dir", args.bindir, "-R", "^task2/.*"],
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
