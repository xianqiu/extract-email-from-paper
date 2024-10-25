import os
import csv


class Loader(object):

    _fail_jobs = 'fail_jobs.csv'
    _success_jobs = 'data.csv'

    def __init__(self, directories):
        """
        给定文件夹的路径列表，返回其中所有 PDF 文件的路径。
        :param directories: list, 文件夹的路径
        :return: list, PDF文件的路径
        """
        self.__pdf_files = []

        for directory in directories:
            # 检查目录是否存在
            if os.path.isdir(directory):
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.lower().endswith('.pdf'):
                            self.__pdf_files.append(os.path.join(root, file))

    def jobs(self):
        return self.__pdf_files

    @classmethod
    def load_fail_jobs(cls):
        # 打开 CSV 文件
        jobs = []
        with open(cls._fail_jobs, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            # 逐行读取
            for row in reader:
                jobs.append(row[0])
        return jobs

    @classmethod
    def load_success_jobs(cls):
        # 打开 CSV 文件
        jobs = []
        with open(cls._success_jobs, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            # 逐行读取
            for row in reader:
                jobs.append(row[1])
        return jobs
