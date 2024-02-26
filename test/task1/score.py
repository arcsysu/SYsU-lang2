import json
import os
import sys
import argparse
import logging
import os.path as osp
import gc


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


def check_and_get_case(task1_logger, condition_dict, task1_test_dir,
                       task1_test_weight):
    # 判断 task1_test_dir 是否存在
    task1_test_dir = osp.abspath(task1_test_dir)
    if not osp.exists(task1_test_dir):
        task1_logger.error('task1_test_dir: %s does not exist.' %
                           task1_test_dir)
        return 0, {}
    # 判断 task1_test_weight 是否存在
    if not osp.exists(task1_test_weight):
        task1_logger.error('task1_test_weight: %s does not exist.' %
                           task1_test_weight)
        return 0, {}

    task1_test_weight_dict = {}
    try:
        with open(task1_test_weight, 'r') as f:
            for line in f:
                case_line = line.strip().split()
                if len(case_line) == 2:
                    case = case_line[0]
                    weight = case_line[1]
                    task1_test_weight_dict[case] = float(weight)
                elif len(case_line) == 1:
                    case = case_line[0]
                    task1_test_weight_dict[case] = 1.0
    except Exception as e:
        task1_logger.error('task1_test_weight: %s format error.' %
                           task1_test_weight)
        task1_logger.error(e)
        return 0, {}

    return 1, task1_test_weight_dict


def make_weighted_averge(now_weighted_averge, now_weights_sum, new_value,
                         new_weight):
    new_weights_sum = now_weights_sum + new_weight
    new_weighted_averge = now_weighted_averge + (
        new_value - now_weighted_averge) * new_weight * 1.0 / new_weights_sum
    return new_weighted_averge, new_weights_sum


def score_one_case(task1_logger, condition_dict, manager, task1_test_log_level,
                   task1_test_dir, case):
    # 为每一个算例单独生成一个日志文件
    case_abs_path = osp.join(task1_test_dir, case)
    # 创建过滤器
    one_case_file_filter = CustomFilter(name='one_case_file_filter',
                                        condition_dict=condition_dict,
                                        condition='one_case_file')

    # 创建文件处理器
    one_case_file_path = osp.join(case_abs_path, 'score.txt')
    file_handler = logging.FileHandler(one_case_file_path,
                                       mode='w',
                                       encoding='utf-8')
    file_handler.addFilter(one_case_file_filter)
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    file_handler.setLevel(logging.INFO)
    task1_logger.addHandler(file_handler)
    condition_dict['one_case_file'] = True
    condition_dict['all_cases_file'] = False
    condition_dict['console'] = False

    task1_logger.info('测试用例: %s' % case)
    task1_logger.info('测试用例绝对路径: %s' % case_abs_path)

    score = 0.0

    def score_one_case_exit(score):
        task1_logger.info('分数: %f' % score)
        condition_dict['one_case_file'] = False
        condition_dict['all_cases_file'] = False
        condition_dict['console'] = True
        task1_logger.removeHandler(file_handler)
        return score

    # 如果 case_abs_path 下没有 answer.txt 文件，就返回 0
    answer_path = osp.join(case_abs_path, 'answer.txt')
    if not osp.exists(answer_path):
        task1_logger.error('%s 的标准答案未生成，请先生成 task1-answer' % case_abs_path)
        score = 0.0
        manager.add_test_report(case, score, 100.0, '标准答案未生成',
                                one_case_file_path)
        return score_one_case_exit(score)

    # 如果 case_abs_path 下没有 output.txt 文件，就返回 0
    output_path = osp.join(case_abs_path, 'output.txt')
    if not osp.exists(output_path):
        task1_logger.error('%s 的用户答案未生成，请调用测试查看是否能正常生成' % case_abs_path)
        score = 0.0
        manager.add_test_report(case, score, 100.0, '用户答案未生成',
                                one_case_file_path)
        return score_one_case_exit(score)

    # 读取 answer.txt 和 output.txt 文件
    with open(answer_path, 'r') as f:
        answers = f.readlines()
    gc.collect()
    with open(output_path, 'r') as f:
        outputs = f.readlines()
    gc.collect()

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
        str0 = tmp[k1 + 1:k2].strip()
        mid0 = str(tmp[k2 + 1:k3].strip().split())
        loc0 = tmp[k3:].strip()
        return [tok0, str0, mid0, loc0, flag0]

    # 计算评分
    tokens_count = len(answers)
    tokens_kind_correct_count = 0
    tokens_location_correct_count = 0
    tokens_unrelated_correct_count = 0
    output_tokens_count = len(outputs)

    if tokens_count != output_tokens_count:
        task1_logger.error('用户答案的词法单元数量与标准答案不一致，请检查是否有遗漏或多余的词法单元')
        score = 0.0
        manager.add_test_report(case, score, 100.0, '词法单元数量不一致',
                                one_case_file_path)
        return score_one_case_exit(score)

    for i in range(tokens_count):

        tok0, str0, mid0, loc0, flag0 = split_tokens(answers[i])
        tok1, str1, mid1, loc1, flag1 = split_tokens(outputs[i])

        if flag1 != 1:
            if task1_test_log_level >= 1:
                task1_logger.error("\nERROR: 词法单元 " + str(i + 1) + " 输出格式错误")
                task1_logger.error("< " + answers[i])
                task1_logger.error("---")
                task1_logger.error("> " + outputs[i])
            continue

        if i == tokens_count - 1:
            if tok1 == 'eof' and str1 == '':
                tokens_kind_correct_count += 1
                tokens_location_correct_count += 1
                tokens_unrelated_correct_count += 1
                break
            else:
                if task1_test_log_level >= 1:
                    task1_logger.error("\nERROR: 词法单元 " + str(i + 1) + " 类型错误")
                    task1_logger.error("< " + tok0)
                    task1_logger.error("---")
                    task1_logger.error("> " + tok1)
                continue

        if tok0 != tok1:
            if task1_test_log_level >= 1:
                task1_logger.error("\nERROR: 词法单元 " + str(i + 1) + " 类型错误")
                task1_logger.error("< " + tok0)
                task1_logger.error("---")
                task1_logger.error("> " + tok1)
            continue
        if str0 != str1:
            if task1_test_log_level >= 1:
                task1_logger.error("\nERROR: 词法单元 " + str(i + 1) + " 值错误")
                task1_logger.error("< " + str0)
                task1_logger.error("---")
                task1_logger.error("> " + str1)
            continue
        tokens_kind_correct_count += 1

        if loc0 != loc1:
            if task1_test_log_level >= 2:
                task1_logger.error("\nERROR: 词法单元 " + str(i + 1) + " 位置错误")
                task1_logger.error("< " + loc0)
                task1_logger.error("---")
                task1_logger.error("> " + loc1)
            continue
        tokens_location_correct_count += 1

        if mid0 != mid1:
            if task1_test_log_level >= 2:
                task1_logger.error("\nERROR: 词法单元 " + str(i + 1) + " 识别无关字符错误")
                task1_logger.error("< " + mid0)
                task1_logger.error("---")
                task1_logger.error("> " + mid1)
            continue
        tokens_unrelated_correct_count += 1

    task1_logger.info('\n')
    task1_logger.info(
        f'INFO: 类型及值正确的词法单元数目: {tokens_kind_correct_count}/{tokens_count}')
    task1_logger.info(
        f'INFO: 位置正确的词法单元数目: {tokens_location_correct_count}/{tokens_count}')
    task1_logger.info('INFO: 识别无关字符正确的词法单元数目: ' +
                      f'{tokens_unrelated_correct_count}/{tokens_count}')
    # 计算评分
    score = (tokens_kind_correct_count * 1.0 / tokens_count * 0.6 +
             tokens_location_correct_count * 1.0 / tokens_count * 0.3 +
             tokens_unrelated_correct_count * 1.0 / tokens_count * 0.1) * 100.0
    manager.add_test_report(case, score, 100.0, '评测正常执行', one_case_file_path)
    return score_one_case_exit(score)


def score_all_case(task1_logger, condition_dict, manager, task1_test_log_level,
                   task1_test_dir, task1_test_weight):

    # 检查 task1_test_dir, task1_case_dir, task1_test_weight 是否存在, 并获取算例名字
    flag, task1_test_weight_dict = check_and_get_case(task1_logger,
                                                      condition_dict,
                                                      task1_test_dir,
                                                      task1_test_weight)

    if not flag:
        task1_logger.error('检测目录出错')
        manager.add_test_report('检测目录', 0.0, 100.0, '检测目录出错')
        manager.add_leaderboard_report('总分', 0.0, 0, True)
        return 0

    # 对每一个算例进行评分
    weighted_average_score = 0.0
    weights_sum = 0.0
    case_idx = 1
    case_len = len(task1_test_weight_dict)
    for case, weight in task1_test_weight_dict.items():
        score = score_one_case(task1_logger, condition_dict, manager,
                               task1_test_log_level, task1_test_dir, case)
        task1_logger.info(f'[{case_idx}/{case_len}] {case} 分数: {score:.2f}')
        weighted_average_score, weights_sum = make_weighted_averge(
            weighted_average_score, weights_sum, score, weight)
        case_idx += 1

    manager.add_leaderboard_report('总分', weighted_average_score, 0, True)
    task1_logger.info(f'总分: {weighted_average_score:.2f}')
    return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('task1_test_ctest',
                        type=str,
                        help='task1 调用测试的可执行文件路径')
    parser.add_argument('task1_test_dir', type=str, help='task1 的测试总目录')
    parser.add_argument('task1_test_weight',
                        type=str,
                        help='保存 task1 的测试用例及权重的文件')
    # parser.add_argument('task1_test_log_level',
    #                     type=int,
    #                     help='保存 task1 的测试用例及权重的文件')
    args = parser.parse_args()
    args.task1_test_log_level = 3
    # 判断输入参数是否合法
    if args.task1_test_log_level < 1 or args.task1_test_log_level > 3:
        raise ValueError('task1_test_log_level must be 1, 2 or 3.')

    # 将路径转换为绝对路径
    args.task1_test_dir = osp.abspath(args.task1_test_dir)
    args.task1_test_weight = osp.abspath(args.task1_test_weight)
    condition_dict = {
        'console': True,
        'all_cases_file': False,
        'one_case_file': False
    }

    # 进行 CTEST
    os.system(f'{args.task1_test_ctest} --test-dir {args.task1_test_dir}')
    # 生成总成绩单的日志保存到 task1_test_dir 下的 score.txt 文件中
    all_cases_file_filter = CustomFilter(name='all_cases_file_filter',
                                         condition_dict=condition_dict,
                                         condition='all_cases_file')
    scoresfile_for_all_cases = osp.abspath(
        osp.join(args.task1_test_dir, 'score.txt'))
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
    task1_logger = logging.getLogger('task1')
    task1_logger.setLevel(logging.INFO)
    task1_logger.addHandler(file_handler)
    task1_logger.addHandler(console_handler)

    # 打印输入参数
    task1_logger.info('Task1 测试总目录路径: %s' % args.task1_test_dir)
    task1_logger.info('Task1 测试用例及权重文件路径: %s' % args.task1_test_weight)

    task1_logger.info('-' * 40)
    manager = ReportsManager(task_name='task1')
    # 对 task1 的结果进行评分
    grade_done = score_all_case(task1_logger, condition_dict, manager,
                                args.task1_test_log_level, args.task1_test_dir,
                                args.task1_test_weight)
    if grade_done:
        task1_logger.info('Task1 评分完成.')
    else:
        task1_logger.error('Task1 评分出错.')
    task1_logger.info('-' * 40)
    results_txt = manager.to_txt()
    condition_dict['all_cases_file'] = True
    task1_logger.info(results_txt)
    condition_dict['all_cases_file'] = False
    task1_logger.info('评分结果已保存到: %s' % scoresfile_for_all_cases)
    task1_logger.info('各测例的评分结果已保存到各自的 score.txt 文件中.')

    results_json = manager.to_json()
    jsonfile_for_all_cases = osp.abspath(
        osp.join(args.task1_test_dir, 'score.json'))
    with open(jsonfile_for_all_cases, 'w') as f:
        f.write(results_json)
    task1_logger.info('JSON格式的评分结果已保存到: %s' % jsonfile_for_all_cases)
