import csv
import re
import time

from pypdf import PdfReader
from parser import EmailParser


class Reader(object):

    def __init__(self, job):
        self._job = job
        self._text = self._read_the_first_page()
        self._clean()

    def _read_the_first_page(self):
        r = PdfReader(self._job)
        page = r.pages[0]
        return page.extract_text()

    def _remove_abstract(self):
        """
        输入一段文本，找到关键字 'abstract', 然后返回它之前的内容。如果没找到，则返回原来的文本。
        注意：关键字不区分大小写。
        """
        # 转换文本为小写，查找关键字 'abstract'
        index = self._text.lower().find('abstract')

        # 如果找到关键字，返回其之前的内容
        if index != -1:
            self._text[:index].strip()

    def _keep_email_lines(self):
        """ 输入一段文本，对它按行进行分割。
        仅保留满足如下条件的行：存在字符'@'且存在字符'.'
        把满足条件的行拼接起来然后返回。
        """
        # 按行分割文本
        lines = self._text.splitlines()
        # 筛选满足条件的行
        email_lines = [line for line in lines if '@' in line and '.' in line]
        # 拼接满足条件的行并返回
        self._text = '\n'.join(email_lines)

    def _remove_special_chars(self, chars):
        """
        输入字符串 text，移除其中 chars 包含的特殊字符。
        """
        # 创建一个集合以提高查找效率
        chars_set = set(chars)
        # 使用列表推导式构建新字符串，过滤掉特殊字符
        self._text = ''.join(char for char in self._text if char not in chars_set)

    def _refine(self, chars):
        """
        已知 text 是一段文本， chars 是字符的列表。
        假设 x 是 chars 中的一个字符，需要对 text 做如下事情：去掉 x 代表的字符前后的空格（如果存在）。
        返回修改后的文本。
        """
        for char in chars:
            # 使用正则表达式去掉字符前后的空格
            self._text = re.sub(rf'\s*{re.escape(char)}\s*', char, self._text)

    def _clean(self):
        self._remove_abstract()
        self._keep_email_lines()
        self._remove_special_chars(chars=['*', '#'])
        self._refine(chars=['@', '.', '-', '_'])

    def read(self):
        return self._text

    def _ignore(self):
        """ 忽略掉无email地址的情况。
        """
        i = self._text.find('@')
        # 如果 '@' 不在字符串中，返回 True
        if i == -1:
            return True
        # 在'@'之后的 k 个字符内，如果找不到`.`，返回 True
        k = 15
        if '.' not in self._text[i + 1:i + 1 + k]:
            return True
        return False

    def extract_email(self):
        if self._ignore():
            return {
                'result': [],
                'status': 'IGNORE'
            }
        return {
            'result': EmailParser(self._text).parse(),
            'status': 'OK'
        }


class BatchReader(object):

    def __init__(self, jobs):
        self._start_time = time.time()
        self._jobs = jobs
        self._email_list = []
        self._result = []
        self._stat = {
            'job count': 0,
            'success': 0,
            'ignore': 0,
            'fail': 0,
        }
        self._fail_jobs = []

    def read(self):
        for job in self._jobs:
            self._stat['job count'] += 1
            res = Reader(job).extract_email()
            items = []
            if res['status'] == 'OK':
                if len(res['result']) > 0:
                    items += [(em, job) for em in res['result']]
                    self._stat['success'] += 1
                else:
                    self._stat['fail'] += 1
                    self._fail_jobs.append(job)
            elif res['status'] == 'IGNORE':
                self._stat['ignore'] += 1
            self._result += items
        return self

    def save(self):
        res = list(set(self._result))  # 去重
        _save_tuple(res, header=['EMAIL', 'JOB'])
        duration = time.time() - self._start_time
        print('==== Report ====')
        print(f"Email list saved to \'data.csv\'.")
        print(f"+ Processing Time: %.1f s" % duration)
        print(f"+ Email Count: {len(res)}")
        print(f"+ Job Count: {self._stat['job count']}")
        print(f"  - Success: {self._stat['success']}")
        print(f"  - Ignore: {self._stat['ignore']}")
        print(f"  - Fail: {self._stat['fail']}")
        print('====')

    def save_fail_jobs(self):
        data = [tuple([e]) for e in self._fail_jobs]
        _save_tuple(data, file_name='fail_jobs.csv')


def _save_tuple(data, header=None, file_name=None):
    """
    把 data 保存成 csv 文件
    :param data: list, 其中每一个元素是一个tuple，它代表表格的一行。
    :param header: list，它是表格的列标题，如果 header 不为空，那么它是表格的第一行。
    :param file_name: str, csv文件的文件名。如果 file_name 为 None，则默认的文件名为 data.csv
    :return: None
    """
    # 设置默认文件名
    if file_name is None:
        file_name = 'data.csv'

    # 打开文件并写入数据
    with open(file_name, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # 如果有表头，先写入表头
        if header:
            writer.writerow(header)

        # 写入数据
        writer.writerows(data)



