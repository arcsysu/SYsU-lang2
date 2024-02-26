"""实验零评测脚本

参数：
  <bindir> 输出目录
  <task0_exe> task0 的可执行文件路径
"""

import json
import sys
import subprocess


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
                txt += f'{leaderboard.value}'.encode('utf-8').decode('utf-8')
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


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    bindir = sys.argv[1]
    task0_exe = sys.argv[2]

    score = 0.0
    max_score = 100.0
    output = "Hello, SYsU-lang!\n"

    reports = ReportsManager(task_name='task0')
    task0_exec_result = subprocess.run([task0_exe],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    if task0_exec_result.returncode == 0:
        output = task0_exec_result.stdout.decode('utf-8')
        if output == "Hello, SYsU-lang!\n":
            score = max_score
        else:
            output = f"输出不是 'Hello, SYsU-lang!'，而是 '{output}'"
            score = 0.0
    else:
        output = f"运行失败，返回码 {task0_exec_result.returncode}"
        score = 0.0
    reports.add_test_report("task0", score, max_score, output)
    reports.add_leaderboard_report("总分", score, 0)

    task0_txt_result = reports.to_txt()
    task0_json_result = reports.to_json()
    print(task0_txt_result)

    with open(f"{bindir}/task0.txt", "w") as f:
        f.write(task0_txt_result)

    with open(f"{bindir}/task0.json", "w") as f:
        f.write(task0_json_result)
