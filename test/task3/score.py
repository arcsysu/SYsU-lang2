import gzip
import json
import os
import re
import subprocess
import sys
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


def check_and_get_case(task3_logger, condition_dict, task3_test_dir,
                       task3_test_weight):
    # 判断 task3_test_dir 是否存在
    task3_test_dir = osp.abspath(task3_test_dir)
    if not osp.exists(task3_test_dir):
        task3_logger.error('task3_test_dir: %s does not exist.' %
                           task3_test_dir)
        return 0, {}
    # 判断 task3_test_weight 是否存在
    if not osp.exists(task3_test_weight):
        task3_logger.error('task3_test_weight: %s does not exist.' %
                           task3_test_weight)
        return 0, {}

    task3_test_weight_dict = {}
    try:
        with open(task3_test_weight, 'r') as f:
            for line in f:
                case_line = line.strip().split()
                if len(case_line) == 2:
                    case = case_line[0]
                    weight = case_line[1]
                    task3_test_weight_dict[case] = float(weight)
                elif len(case_line) == 1:
                    case = case_line[0]
                    task3_test_weight_dict[case] = 1.0
    except Exception as e:
        task3_logger.error('task3_test_weight: %s format error.' %
                           task3_test_weight)
        task3_logger.error(e)
        return 0, {}

    return 1, task3_test_weight_dict


def make_weighted_averge(now_weighted_averge, now_weights_sum, new_value,
                         new_weight):
    new_weights_sum = now_weights_sum + new_weight
    new_weighted_averge = now_weighted_averge + (
        new_value - now_weighted_averge) * new_weight * 1.0 / new_weights_sum
    return new_weighted_averge, new_weights_sum


def get_tm(sp):
    val = -1
    matchObj = re.findall(b'TOTAL: (\\d*)H-(\\d*)M-(\\d*)S-(\\d*)us',
                          sp.stderr)
    if len(matchObj) == 0:
        return val
    matchObj = matchObj[-1]
    val = int(matchObj[0])
    val = val * 60 + int(matchObj[1])
    val = val * 60 + int(matchObj[2])
    val = val * 1000000 + int(matchObj[3])
    return val


def score_one_case(task3_logger, condition_dict, manager, task3_test_log_level,
                   task3_test_dir, case, task3_test_clang,
                   task3_test_rtlib_path, task3_test_timeout):
    # 为每一个算例单独生成一个日志文件
    case_abs_path = osp.join(task3_test_dir, case)

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
    task3_logger.addHandler(file_handler)
    condition_dict['one_case_file'] = True
    condition_dict['all_cases_file'] = False
    condition_dict['console'] = False

    task3_logger.info('测试用例: %s' % case)
    task3_logger.info('测试用例绝对路径: %s' % case_abs_path)

    score = 0.0

    def score_one_case_exit(score):
        task3_logger.info('分数: %f' % score)
        condition_dict['one_case_file'] = False
        condition_dict['all_cases_file'] = False
        condition_dict['console'] = True
        task3_logger.removeHandler(file_handler)
        return score

    # 如果 case_abs_path 下没有 answer.ll 文件，就返回 0
    answer_path = osp.join(case_abs_path, 'answer.ll')
    if not osp.exists(answer_path):
        task3_logger.error('%s 的标准答案未生成，请先生成 task3-answer' % case_abs_path)
        score = 0.0
        manager.add_test_report(case, score, 100.0, '标准答案未生成',
                                one_case_file_path)
        return score_one_case_exit(score)

    # 如果 case_abs_path 下没有 output.ll 文件，就返回 0
    output_path = osp.join(case_abs_path, 'output.ll')
    if not osp.exists(output_path):
        task3_logger.error('%s 的用户答案未生成，请调用测试查看是否能正常生成' % case_abs_path)
        score = 0.0
        manager.add_test_report(case, score, 100.0, '用户答案未生成',
                                one_case_file_path)
        return score_one_case_exit(score)

    # 计算评分
    try:
        inputs = None
        gz = osp.join(case_abs_path, "answer.in.gz")
        if osp.exists(gz):
            try:
                with gzip.open(gz, "rb") as f:
                    inputs = f.read()
            except gzip.BadGzipFile as e:
                task3_logger.error('读取输入文件出错')
                task3_logger.error(e)
                score = 0.0
                manager.add_test_report(case, score, 100.0, '读取输入文件出错',
                                        one_case_file_path)
                return score_one_case_exit(score)
        answer_exe = osp.join(case_abs_path, 'answer.out')
        output_exe = osp.join(case_abs_path, 'output.out')

        try:
            answer_comp_result = subprocess.run([
                task3_test_clang, "-O0", "-L" + task3_test_rtlib_path, "-o",
                answer_exe, answer_path, "-ltest-rtlib"
            ],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                timeout=task3_test_timeout)
        except subprocess.TimeoutExpired as e:
            raise subprocess.TimeoutExpired(e.cmd, task3_test_timeout, None,
                                            "编译标准答案超时")
        except Exception as e:
            raise e
        if answer_comp_result is None or answer_comp_result.returncode:
            task3_logger.error('\nERROR: 编译标准答案失败')
            task3_logger.error(answer_comp_result)
            score = 0.0
            manager.add_test_report(case, score, 100.0, '编译标准答案失败',
                                    one_case_file_path)
            return score_one_case_exit(score)
        try:
            answer_exec_result = subprocess.run([answer_exe],
                                                input=inputs,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                timeout=task3_test_timeout)
        except subprocess.TimeoutExpired as e:
            raise subprocess.TimeoutExpired(e.cmd, task3_test_timeout, None,
                                            "运行标准答案超时")
        except Exception as e:
            raise e
        answer_log = "clang -O0 代码执行用时: {}us, 返回值 {}".format(
            get_tm(answer_exec_result), answer_exec_result.returncode)
        task3_logger.info(answer_log)
        answer_stdout = osp.join(case_abs_path, "answer_stdout")
        with open(answer_stdout, 'w') as f:
            f.write(answer_exec_result.stdout.decode())

        try:
            output_comp_result = subprocess.run([
                task3_test_clang, "-O0", "-L" + task3_test_rtlib_path, "-o",
                output_exe, output_path, "-ltest-rtlib"
            ],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                timeout=task3_test_timeout)
        except subprocess.TimeoutExpired as e:
            raise subprocess.TimeoutExpired(e.cmd, task3_test_timeout, None,
                                            "编译用户答案超时")
        except Exception as e:
            raise e
        if output_comp_result is None or output_comp_result.returncode:
            task3_logger.error('\nERROR: 编译用户答案失败')
            task3_logger.error(output_comp_result)
            score = 0.0
            manager.add_test_report(case, score, 100.0, '编译用户答案失败',
                                    one_case_file_path)
            return score_one_case_exit(score)
        try:
            output_exec_result = subprocess.run([output_exe],
                                                input=inputs,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                timeout=task3_test_timeout)
        except subprocess.TimeoutExpired as e:
            raise subprocess.TimeoutExpired(e.cmd, task3_test_timeout, None,
                                            "运行标准答案超时")
        except Exception as e:
            raise e
        output_log = "sysu-lang 代码执行用时: {}us, 返回值 {}".format(
            get_tm(output_exec_result), output_exec_result.returncode)
        task3_logger.info(output_log)
        output_stdout = osp.join(case_abs_path, "output_stdout")
        with open(output_stdout, 'w') as f:
            f.write(output_exec_result.stdout.decode())

        if answer_exec_result.returncode != output_exec_result.returncode:
            task3_logger.info("\n返回值不匹配")
            task3_logger.info(">----")
            task3_logger.info("标准答案返回值: %d" % answer_exec_result.returncode)
            task3_logger.info("用户答案返回值: %d" % output_exec_result.returncode)
            task3_logger.info("<----")
            score = 0.0
            manager.add_test_report(case, score, 100.0, '返回值不匹配',
                                    one_case_file_path)
            return score_one_case_exit(score)

        if answer_exec_result.stdout != output_exec_result.stdout:
            task3_logger.info("\n输出不匹配")
            task3_logger.info(">----")
            task3_logger.info("标准答案输出: %s" % answer_exec_result.stdout)
            task3_logger.info("用户答案输出: %s" % output_exec_result.stdout)
            task3_logger.info("<----")
            score = 0.0
            manager.add_test_report(case, score, 100.0, '输出不匹配',
                                    one_case_file_path)
            return score_one_case_exit(score)

    except subprocess.TimeoutExpired as e:
        task3_logger.error(f'{e.stderr}超时')
        score = 0.0
        manager.add_test_report(case, score, 100.0, e.stderr,
                                one_case_file_path)
        return score_one_case_exit(score)
    except Exception as e:
        # 输出异常信息，及在哪一行出现的异常
        task3_logger.error('评分出错')
        task3_logger.error(e)
        task3_logger.error('出错位置: %s' % e.__traceback__.tb_lineno)
        task3_logger.error('出错文件: %s' %
                           e.__traceback__.tb_frame.f_globals['__file__'])
        score = 0.0
        manager.add_test_report(case, score, 100.0, '评分出错', one_case_file_path)
        return score_one_case_exit(score)

    task3_logger.info('\nINFO: 测试用例 %s 通过' % case)
    # 计算评分
    score = 100.0
    manager.add_test_report(case, score, 100.0, '测试通过', one_case_file_path)
    return score_one_case_exit(score)


def score_all_case(task3_logger, condition_dict, manager, task3_test_log_level,
                   task3_test_dir, task3_test_weight, task3_test_clang,
                   task3_test_rtlib_path, task3_test_timeout):
    # 检查 task3_test_dir, task3_case_dir, task3_test_weight 是否存在, 并获取算例名字
    flag, task3_test_weight_dict = check_and_get_case(task3_logger,
                                                      condition_dict,
                                                      task3_test_dir,
                                                      task3_test_weight)

    if not flag:
        task3_logger.error('检测目录出错')
        manager.add_test_report('检测目录', 0.0, 100.0, '检测目录出错')
        manager.add_leaderboard_report('总分', 0.0, 0, True)
        return 0

    # 对每一个算例进行评分
    weighted_average_score = 0.0
    weights_sum = 0.0
    case_idx = 1
    case_len = len(task3_test_weight_dict)
    for case, weight in task3_test_weight_dict.items():
        score = score_one_case(task3_logger, condition_dict, manager,
                               task3_test_log_level, task3_test_dir, case,
                               task3_test_clang, task3_test_rtlib_path,
                               task3_test_timeout)
        task3_logger.info(f'[{case_idx}/{case_len}] {case} 分数: {score:.2f}')
        weighted_average_score, weights_sum = make_weighted_averge(
            weighted_average_score, weights_sum, score, weight)
        case_idx += 1

    manager.add_leaderboard_report("总分", weighted_average_score, 0,
                                   True)
    task3_logger.info(f'总分: {weighted_average_score:.2f}')
    return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('task3_test_ctest',
                        type=str,
                        help='task3 调用测试的可执行文件路径')
    parser.add_argument('task3_test_dir', type=str, help='task3 的测试总目录')
    parser.add_argument('task3_test_weight',
                        type=str,
                        help='保存 task3 的测试用例及权重的文件')
    parser.add_argument('task3_test_clang',
                        type=str,
                        help='用于编译 task3 的 clang 路径')
    parser.add_argument('task3_test_rtlib_path',
                        type=str,
                        help='保存 task3 的运行时库的路径')
    parser.add_argument('task3_test_timeout', type=int, help='task3 的测试时间限制')
    # parser.add_argument('task3_test_log_level',
    #                     type=int,
    #                     help='task3 的日志输出等级')
    args = parser.parse_args()
    args.task3_test_log_level = 1
    # 判断输入参数是否合法
    if args.task3_test_log_level < 1 or args.task3_test_log_level > 3:
        raise ValueError('task3_test_log_level must be 1, 2 or 3.')

    # 将路径转换为绝对路径
    args.task3_test_dir = osp.abspath(args.task3_test_dir)
    args.task3_test_weight = osp.abspath(args.task3_test_weight)
    condition_dict = {
        'console': True,
        'all_cases_file': False,
        'one_case_file': False
    }

    # 进行 CTEST
    os.system(f'{args.task3_test_ctest} --test-dir {args.task3_test_dir}')
    # 生成总成绩单的日志保存到 task3_test_dir 下的 score.txt 文件中
    all_cases_file_filter = CustomFilter(name='all_cases_file_filter',
                                         condition_dict=condition_dict,
                                         condition='all_cases_file')
    scoresfile_for_all_cases = osp.abspath(
        osp.join(args.task3_test_dir, 'score.txt'))
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
    task3_logger = logging.getLogger('task3')
    task3_logger.setLevel(logging.INFO)
    task3_logger.addHandler(file_handler)
    task3_logger.addHandler(console_handler)

    # 打印输入参数
    task3_logger.info('Task3 测试总目录路径: %s' % args.task3_test_dir)
    task3_logger.info('Task3 测试用例及权重文件路径: %s' % args.task3_test_weight)

    task3_logger.info('-' * 40)
    manager = ReportsManager(task_name='task3')
    # 对 task3 的结果进行评分
    grade_done = score_all_case(task3_logger, condition_dict, manager,
                                args.task3_test_log_level, args.task3_test_dir,
                                args.task3_test_weight, args.task3_test_clang,
                                args.task3_test_rtlib_path,
                                args.task3_test_timeout)
    if grade_done:
        task3_logger.info('Task3 评分完成.')
    else:
        task3_logger.error('Task3 评分出错.')
    task3_logger.info('-' * 40)
    results_txt = manager.to_txt()
    condition_dict['all_cases_file'] = True
    task3_logger.info(results_txt)
    condition_dict['all_cases_file'] = False
    task3_logger.info('评分结果已保存到: %s' % scoresfile_for_all_cases)
    task3_logger.info('各测例的评分结果已保存到各自的 score.txt 文件中.')

    results_json = manager.to_json()
    jsonfile_for_all_cases = osp.abspath(
        osp.join(args.task3_test_dir, 'score.json'))
    with open(jsonfile_for_all_cases, 'w') as f:
        f.write(results_json)
    task3_logger.info('JSON格式的评分结果已保存到: %s' % jsonfile_for_all_cases)
