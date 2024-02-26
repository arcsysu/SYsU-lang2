import os
import sys
import json
import gc
import argparse
import logging
import os.path as osp


class Test_Report:

    def __init__(self, name, score, max_score, output, output_path=None):
        self.name = name
        self.score = score
        self.max_score = max_score
        self.output = output
        self.output_path = output_path


class LeaderBoard_Report:

    def __init__(self, name, value, order, is_desc=False, suffix=None):
        self.name = name
        self.value = value
        self.order = order
        self.is_desc = is_desc
        self.suffix = suffix


class ReportsManager:

    def __init__(self, task_name='task'):
        self.tests = []
        self.testsleaderboard = []
        self.tests_name_max_len = 0
        self.testsleaderboard_name_max_len = 0
        self.task_name = task_name

    def add_test_report(self,
                        name,
                        score,
                        max_score,
                        output,
                        output_path=None):
        self.tests.append(
            Test_Report(name, score, max_score, output, output_path))
        self.tests_name_max_len = max(self.tests_name_max_len, len(name))

    def add_test_report_instance(self, Test_Report):
        self.tests.append(Test_Report)
        self.tests_name_max_len = max(self.tests_name_max_len,
                                      len(Test_Report.name))

    def add_leaderboard_report(self,
                               name,
                               value,
                               order=0,
                               is_desc=False,
                               suffix=None):
        self.testsleaderboard.append(
            LeaderBoard_Report(name, value, order, is_desc, suffix))
        self.testsleaderboard_name_max_len = max(
            self.testsleaderboard_name_max_len, len(name))

    def add_leaderboard_report_instance(self, LeaderBoard_Report):
        self.testsleaderboard.append(LeaderBoard_Report)
        self.testsleaderboard_name_max_len = max(
            self.testsleaderboard_name_max_len, len(LeaderBoard_Report.name))

    def to_json(self):
        # 返回一个 json 字符串，它有两个属性，一个是 test_reports，一个是 leaderboard_reports
        # test_reports 是一个列表，每一个元素是一个字典，包含了一个测试报告的信息
        # leaderboard_reports 是一个列表，每一个元素是一个字典，包含了一个排行榜报告的信息
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def to_txt(self):
        # 返回一个字符串，它包含了所有的测试报告和排行榜报告的信息
        txt = u''
        for leaderboard in self.testsleaderboard:
            if leaderboard.name == '总分':
                txt += f'{self.task_name} 总分:'.encode('utf-8').decode('utf-8')
                txt += f'{leaderboard.value:.2f}'.encode('utf-8').decode(
                    'utf-8')
                if leaderboard.suffix:
                    txt += f' {leaderboard.suffix}'.encode('utf-8').decode(
                        'utf-8')
                txt += '\n\n'.encode('utf-8').decode('utf-8')
        for test in self.tests:
            txt += f'{test.name}'.ljust(self.tests_name_max_len +
                                        2).encode('utf-8').decode('utf-8')
            txt += f'{test.score:.2f}'.rjust(8).encode('utf-8').decode('utf-8')
            txt += '/'.encode('utf-8').decode('utf-8')
            txt += f'{test.max_score:.2f}'.ljust(8).encode('utf-8').decode(
                'utf-8')
            txt += f'{test.output}'.ljust(20).encode('utf-8').decode('utf-8')
            txt += '\n'.encode('utf-8').decode('utf-8')
        return txt


class CustomFilter(logging.Filter):

    def __init__(self,
                 name: str = "",
                 condition_dict: dict = {},
                 condition: str = None) -> None:
        super().__init__(name)
        self.condition_dict = condition_dict
        self.condition = condition

    def filter(self, record):
        return self.condition_dict[self.condition]


def check_and_get_case(task2_logger, condition_dict, task2_test_dir,
                       task2_test_weight):
    # 判断 task2_test_dir 是否存在
    task2_test_dir = osp.abspath(task2_test_dir)
    if not osp.exists(task2_test_dir):
        task2_logger.error('task2_test_dir: %s does not exist.' %
                           task2_test_dir)
        return 0, {}
    # 判断 task2_test_weight 是否存在
    if not osp.exists(task2_test_weight):
        task2_logger.error('task2_test_weight: %s does not exist.' %
                           task2_test_weight)
        return 0, {}

    task2_test_weight_dict = {}
    try:
        with open(task2_test_weight, 'r') as f:
            for line in f:
                case_line = line.strip().split()
                if len(case_line) == 2:
                    case = case_line[0]
                    weight = case_line[1]
                    task2_test_weight_dict[case] = float(weight)
                elif len(case_line) == 1:
                    case = case_line[0]
                    task2_test_weight_dict[case] = 1.0
    except Exception as e:
        task2_logger.error('task2_test_weight: %s format error.' %
                           task2_test_weight)
        task2_logger.error(e)
        return 0, {}

    return 1, task2_test_weight_dict


def make_weighted_averge(now_weighted_averge, now_weights_sum, new_value,
                         new_weight):
    new_weights_sum = now_weights_sum + new_weight
    new_weighted_averge = now_weighted_averge + (
        new_value - now_weighted_averge) * new_weight * 1.0 / new_weights_sum
    return new_weighted_averge, new_weights_sum


def output_node(n, ast0, ast1, task2_logger: logging.Logger):
    task2_logger.error('\n>---')
    ast0_noinner = ast0.copy()
    ast1_noinner = ast1.copy()
    for key in ["inner", "id"]:
        if key in ast0_noinner:
            del ast0_noinner[key]
        if key in ast1_noinner:
            del ast1_noinner[key]
    task2_logger.error('标准答案节点: \n' + str(ast0_noinner))
    task2_logger.error('用户答案节点: \n' + str(ast1_noinner))
    task2_logger.error('\n<---')
    return n


def output_node_include_inner(n, ast0, ast1, inner_n,
                              task2_logger: logging.Logger):
    task2_logger.error('\n>---')
    ast0_copy = ast0.copy()
    ast1_copy = ast1.copy()
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
    task2_logger.error('标准答案节点: \n' + str(ast0_copy) + '\n')
    task2_logger.error('标准答案节点inner的第n项: \n' + str(ast0_inner_n) + '\n')
    task2_logger.error('用户答案节点: \n' + str(ast1_copy) + '\n')
    task2_logger.error('用户答案节点inner的第n项: \n' + str(ast1_inner_n) + '\n')
    task2_logger.error('\n<---')
    return n


def get_value1(key, ast0, ast1, task2_test_log_level, level1_kind, level2_kind,
               correct_dict):
    if key not in ast1:
        if key not in level1_kind \
                and key not in level2_kind \
                and task2_test_log_level >= 3:
            task2_logger.error("\nERROR: 键 '" + key + "' 在用户答案节点内不存在")
            output_node(1, ast0, ast1, task2_logger)
        correct_dict["level3_correct"] = False
        if key in level2_kind:
            correct_dict["level2_correct"] = False
            if task2_test_log_level >= 2:
                task2_logger.error("\nERROR: 键 '" + key + "' 在用户答案节点内不存在")
                output_node(1, ast0, ast1, task2_logger)
        if key in level1_kind:
            correct_dict["level2_correct"] = False
            correct_dict["level1_correct"] = False
            if task2_test_log_level >= 1:
                task2_logger.error("\nERROR: 键 '" + key + "' 在用户答案节点内不存在")
                output_node(1, ast0, ast1, task2_logger)
    return ast1.get(key)


def check_ast(ast0, ast1, ast_info, status, task2_logger: logging.Logger,
              task2_test_log_level):
    key_inner = ["inner"]
    key_ignore = ["id"]
    level1_kind = ["kind", "name", "value"]
    level2_kind = ["type", "InitListExpr"]
    ast_info["nodes_count"] += 1

    # 用于记录每一个节点不同等级的正确性
    correct_dict = dict()
    correct_dict["level1_correct"] = True
    correct_dict["level2_correct"] = True
    correct_dict["level3_correct"] = True

    if status == 1:
        # status 为 1 时，说明 ast1 在之前已经不匹配了，但还是需要遍历所有节点统计节点数
        for key, value0 in ast0.items():
            if key in key_inner:
                value0 = list(
                    filter(
                        lambda x: not x.get("isImplicit", False) and not x.get(
                            "implicit", False), value0))
                for i in range(len(value0)):
                    check_ast(value0[i], None, ast_info, 1,
                              task2_test_log_level)
        correct_dict["level1_correct"] = False
        correct_dict["level2_correct"] = False
        correct_dict["level3_correct"] = False
        return correct_dict

    if type(ast0) is not type(ast1):
        if task2_test_log_level >= 1:
            task2_logger.error("\nERROR: 节点类型错误")
            output_node(1, ast0, ast1, task2_logger)
        check_ast(ast0, None, ast_info, 1, task2_logger, task2_test_log_level)
        correct_dict["level1_correct"] = False
        correct_dict["level2_correct"] = False
        correct_dict["level3_correct"] = False
        return correct_dict

    for key, value0 in ast0.items():
        if key in key_ignore:
            continue

        if key in key_inner:
            value0 = list(
                filter(
                    lambda x: not x.get("isImplicit", False) and not x.get(
                        "implicit", False), value0))
            value1 = get_value1(key, ast0, ast1, task2_test_log_level,
                                level1_kind, level2_kind, correct_dict)
            if value1 is None:
                for i in range(len(value0)):
                    son_correct_dict = check_ast(value0[i], None, ast_info, 1,
                                                 task2_logger,
                                                 task2_test_log_level)
                continue
            value1 = list(
                filter(
                    lambda x: not x.get("isImplicit", False) and not x.get(
                        "implicit", False), value1))
            if len(value0) != len(value1):
                correct_dict["level3_correct"] = False
                if key in level2_kind:
                    correct_dict["level2_correct"] = False
                    if task2_test_log_level >= 2:
                        task2_logger.error("\nERROR: inner 长度不匹配")
                        task2_logger.error("标准答案节点 inner 长度: " +
                                           str(len(value0)))
                        task2_logger.error("用户答案节点 inner 长度: " +
                                           str(len(value1)))
                        output_node(1, ast0, ast1, task2_logger)
                        for i in range(len(value0)):
                            son_correct_dict = check_ast(
                                value0[i], None, ast_info, 1, task2_logger,
                                task2_test_log_level)
                continue
            for i in range(len(value0)):
                son_correct_dict = check_ast(value0[i], value1[i], ast_info, 0,
                                             task2_logger,
                                             task2_test_log_level)
                if not son_correct_dict[
                        "level1_correct"] or not son_correct_dict[
                            "level2_correct"] or not son_correct_dict[
                                "level3_correct"]:
                    correct_dict["level3_correct"] = False
                    if task2_test_log_level >= 3:
                        task2_logger.error("\nERROR: inner 错误")
                        output_node_include_inner(1, ast0, ast1, i,
                                                  task2_logger)
                    if ast0.get('kind') == 'InitListExpr':
                        correct_dict["level2_correct"] = False
                        if task2_test_log_level >= 2 and task2_logger < 3:
                            task2_logger.error("\nERROR: inner 错误")
                            output_node(1, ast0, ast1, i, task2_logger)
        else:
            value1 = get_value1(key, ast0, ast1, task2_test_log_level,
                                level1_kind, level2_kind, correct_dict)
            if value1 is None:
                continue
            if value0 != value1:
                if key not in level1_kind \
                        and key not in level2_kind \
                        and task2_test_log_level >= 3:
                    task2_logger.error("\nERROR: 键值 '" + key + "' 错误")
                    output_node(1, ast0, ast1, task2_logger)
                correct_dict["level3_correct"] = False
                if key in level2_kind:
                    correct_dict["level2_correct"] = False
                    if task2_test_log_level >= 2:
                        task2_logger.error("\nERROR: 键值 '" + key + "' 错误")
                        output_node(1, ast0, ast1, task2_logger)
                if key in level1_kind:
                    correct_dict["level2_correct"] = False
                    correct_dict["level1_correct"] = False
                    if task2_test_log_level >= 1:
                        task2_logger.error("\nERROR: 键值 '" + key + "' 错误")
                        output_node(1, ast0, ast1, task2_logger)
    if correct_dict["level1_correct"]:
        ast_info["nodes_level1_correct_count"] += 1
    if correct_dict["level2_correct"]:
        ast_info["nodes_level2_correct_count"] += 1
    if correct_dict["level3_correct"]:
        ast_info["nodes_level3_correct_count"] += 1
    return correct_dict


def score_one_case(task2_logger, condition_dict, manager, task2_test_log_level,
                   task2_test_dir, case):
    # 为每一个算例单独生成一个日志文件
    case_abs_path = osp.join(task2_test_dir, case)
    # 创建过滤器
    one_case_file_filter = CustomFilter(name='one_case_file_filter',
                                        condition_dict=condition_dict,
                                        condition='one_case_file')

    # 创建文件处理器
    one_case_file_path = osp.join(case_abs_path, 'score.txt')
    file_handler = logging.FileHandler(one_case_file_path, mode='w')
    file_handler.addFilter(one_case_file_filter)
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    file_handler.setLevel(logging.INFO)
    task2_logger.addHandler(file_handler)
    condition_dict['one_case_file'] = True
    condition_dict['all_cases_file'] = False
    condition_dict['console'] = False

    task2_logger.info('测试用例: %s' % case)
    task2_logger.info('测试用例绝对路径: %s' % case_abs_path)

    score = 0.0

    def score_one_case_exit(score):
        task2_logger.info('分数: %f' % score)
        condition_dict['one_case_file'] = False
        condition_dict['all_cases_file'] = False
        condition_dict['console'] = True
        task2_logger.removeHandler(file_handler)
        return score

    # 如果 case_abs_path 下没有 answer.json 文件，就返回 0
    answer_path = osp.join(case_abs_path, 'answer.json')
    if not osp.exists(answer_path):
        task2_logger.error('%s 的标准答案未生成，请先生成 task2-answer' % case_abs_path)
        score = 0.0
        manager.add_test_report(case, score, 100.0, '标准答案未生成',
                                one_case_file_path)
        return score_one_case_exit(score)

    # 如果 case_abs_path 下没有 output.json 文件，就返回 0
    output_path = osp.join(case_abs_path, 'output.json')
    if not osp.exists(output_path):
        task2_logger.error('%s 的用户答案未生成，请调用测试查看是否能正常生成' % case_abs_path)
        score = 0.0
        manager.add_test_report(case, score, 100.0, '用户答案未生成',
                                one_case_file_path)
        return score_one_case_exit(score)

    # 读取 answer.json 和 output.json 文件
    with open(answer_path, 'r') as f:
        answers = f.read()
    gc.collect()
    with open(output_path, 'r') as f:
        outputs = f.read()
    gc.collect()

    try:
        ast0 = json.loads(answers)
    except Exception as e:
        task2_logger.error('标准答案格式错误')
        task2_logger.error(e)
        score = 0.0
        manager.add_test_report(case, score, 100.0, '标准答案格式错误',
                                one_case_file_path)
        return score_one_case_exit(score)
    gc.collect()

    try:
        ast1 = json.loads(outputs)
    except Exception as e:
        task2_logger.error('用户答案格式错误')
        task2_logger.error(e)
        score = 0.0
        manager.add_test_report(case, score, 100.0, '用户答案格式错误',
                                one_case_file_path)
        return score_one_case_exit(score)
    gc.collect()

    status = 0
    ast_info = dict()
    ast_info["nodes_count"] = 0
    # level 1 判断节点的kind，名字和值是否正确
    ast_info["nodes_level1_correct_count"] = 0
    # level 2 判断节点的type和"InitListExpr" 生成树是否正确
    ast_info["nodes_level2_correct_count"] = 0
    # level 3 判断节点的其他属性（除id属性外）是否正确
    ast_info["nodes_level3_correct_count"] = 0
    check_ast(ast0, ast1, ast_info, status, task2_logger, task2_test_log_level)
    score = (ast_info["nodes_level1_correct_count"] * 0.6 +
             ast_info["nodes_level2_correct_count"] * 0.3 +
             ast_info["nodes_level3_correct_count"] *
             0.1) * 1.0 / ast_info["nodes_count"] * 100.0
    manager.add_test_report(case, score, 100.0, '测试结果请具体查看',
                            one_case_file_path)

    task2_logger.info('\nINFO: 生成树节点总数: %d' % ast_info["nodes_count"])
    task2_logger.info('INFO: Level1 正确的节点数: %d' %
                      ast_info["nodes_level1_correct_count"])
    task2_logger.info('INFO: Level2 正确的节点数: %d' %
                      ast_info["nodes_level2_correct_count"])
    task2_logger.info('INFO: Level3 正确的节点数: %d' %
                      ast_info["nodes_level3_correct_count"])
    return score_one_case_exit(score)


def score_all_case(task2_logger, condition_dict, manager, task2_test_log_level,
                   task2_test_dir, task2_test_weight):

    # 检查 task2_test_dir, task2_case_dir, task2_test_weight 是否存在, 并获取算例名字
    flag, task2_test_weight_dict = check_and_get_case(task2_logger,
                                                      condition_dict,
                                                      task2_test_dir,
                                                      task2_test_weight)

    if not flag:
        task2_logger.error('检测目录出错')
        manager.add_test_report('检测目录', 0.0, 100.0, '检测目录出错')
        manager.add_leaderboard_report('总分', 0.0, 0, True)
        return 0

    # 对每一个算例进行评分
    weighted_average_score = 0.0
    weights_sum = 0.0
    case_idx = 1
    case_len = len(task2_test_weight_dict)
    for case, weight in task2_test_weight_dict.items():
        score = score_one_case(task2_logger, condition_dict, manager,
                               task2_test_log_level, task2_test_dir, case)
        task2_logger.info(f'[{case_idx}/{case_len}] {case} 分数: {score:.2f}')
        weighted_average_score, weights_sum = make_weighted_averge(
            weighted_average_score, weights_sum, score, weight)
        case_idx += 1

    manager.add_leaderboard_report("总分", weighted_average_score, 0, True)
    task2_logger.info(f'总分: {weighted_average_score:.2f}')
    return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('task2_test_ctest',
                        type=str,
                        help='task2 调用测试的可执行文件路径')
    parser.add_argument('task2_test_dir', type=str, help='task2 的测试总目录')
    parser.add_argument('task2_test_weight',
                        type=str,
                        help='保存 task2 的测试用例及权重的文件')
    # parser.add_argument('task2_test_log_level',
    #                     type=int,
    #                     help='保存 task2 的测试用例及权重的文件')
    args = parser.parse_args()
    args.task2_test_log_level = 3
    # 判断输入参数是否合法
    if args.task2_test_log_level < 1 or args.task2_test_log_level > 3:
        raise ValueError('task2_test_log_level must be 1, 2 or 3.')

    # 将路径转换为绝对路径
    args.task2_test_dir = osp.abspath(args.task2_test_dir)
    args.task2_test_weight = osp.abspath(args.task2_test_weight)
    condition_dict = {
        'console': True,
        'all_cases_file': False,
        'one_case_file': False
    }

    # 进行 CTEST
    os.system(f'{args.task2_test_ctest} --test-dir {args.task2_test_dir}')
    # 生成总成绩单的日志保存到 task2_test_dir 下的 score.txt 文件中
    all_cases_file_filter = CustomFilter(name='all_cases_file_filter',
                                         condition_dict=condition_dict,
                                         condition='all_cases_file')
    scoresfile_for_all_cases = osp.abspath(
        osp.join(args.task2_test_dir, 'score.txt'))
    file_handler = logging.FileHandler(scoresfile_for_all_cases, mode='w')
    file_handler.addFilter(all_cases_file_filter)
    file_handler.setLevel(logging.INFO)

    # 生成控制台的日志
    console_filter = CustomFilter(name='console_filter',
                                  condition_dict=condition_dict,
                                  condition='console')
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.addFilter(console_filter)
    console_handler.setLevel(logging.INFO)

    # 设置日志格式
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 设置日志产生器
    task2_logger = logging.getLogger('task2')
    task2_logger.setLevel(logging.INFO)
    task2_logger.addHandler(file_handler)
    task2_logger.addHandler(console_handler)

    # 打印输入参数
    task2_logger.info('Task2 测试总目录路径: %s' % args.task2_test_dir)
    task2_logger.info('Task2 测试用例及权重文件路径: %s' % args.task2_test_weight)

    task2_logger.info('-' * 40)
    manager = ReportsManager(task_name='task2')
    # 对 task2 的结果进行评分
    grade_done = score_all_case(task2_logger, condition_dict, manager,
                                args.task2_test_log_level, args.task2_test_dir,
                                args.task2_test_weight)
    if grade_done:
        task2_logger.info('Task2 评分完成.')
    else:
        task2_logger.error('Task2 评分出错.')
    task2_logger.info('-' * 40)
    results_txt = manager.to_txt()
    condition_dict['all_cases_file'] = True
    task2_logger.info(results_txt)
    condition_dict['all_cases_file'] = False
    task2_logger.info('评分结果已保存到: %s' % scoresfile_for_all_cases)
    task2_logger.info('各测例的评分结果已保存到各自的 score.txt 文件中.')

    results_json = manager.to_json()
    jsonfile_for_all_cases = osp.abspath(
        osp.join(args.task2_test_dir, 'score.json'))
    with open(jsonfile_for_all_cases, 'w') as f:
        f.write(results_json)
    task2_logger.info('JSON格式的评分结果已保存到: %s' % jsonfile_for_all_cases)
