import re


class EmailParser(object):

    def __init__(self, text):
        self._text = text

    def _parse_normal(self):
        """
        输入一个字符串，解析其中所有的 email 地址。
        如果存在某些 email 地址是数字开头，需要移除前面的数字部分。
        """
        # 定义正则表达式模式以匹配电子邮件地址
        email_pattern = r'\b(\d+)?([a-zA-Z][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'

        # 使用 re.findall 查找所有匹配的电子邮件地址
        matches = re.findall(email_pattern, self._text)

        # 处理提取的电子邮件地址，去掉前面的数字部分
        emails = [match[1] for match in matches]

        return emails  # 返回找到的电子邮件地址列表

    def _parse_combine(self, brackets, sep):
        """
        从多个 email 的联合形式中提取成标准的 email 形式，例如：
        {user_a, user.b, user-c}@example.com
        --> user_a@example.com, user.b@example.com, user-c@example.com

        其中逗号是分隔符',', 输入参数 sep 是分隔符的列表, 例如 sep = [',', ';']
        如果把上面例子中的',' 换成 sep 中的任意一个符号，也能实现上述功能。

        再进一步思考。
        上面例子中的括号也可以有其他形式，例如(), <>，如果把上面例子中的'{', '}' 分别替换成其他形式，例如
        '{' --> '(', '}' --> ')'，也能实现上述功能。
        括号的形式在输入参数 brackets 中，例如 brackets = ['{}', '()', '<>']。
        注意：其中每个元素的第一个字符是左括号，第二个字符是右括号。

        :param brackets: list, 其中的每一个元素代表一种括号的形式。
        :param sep: list, 其中每一个元素代表一个分隔符
        :return: list, 提取出的标准 email 地址
        """
        # 拆分括号为左括号和右括号
        left_brackets = [b[0] for b in brackets]
        right_brackets = [b[1] for b in brackets]

        # 构建正则表达式的括号部分
        left_bracket_pattern = '|'.join(re.escape(b) for b in left_brackets)
        right_bracket_pattern = '|'.join(re.escape(b) for b in right_brackets)

        # 将分隔符列表转换为正则表达式模式
        sep_pattern = r'\s*[' + ''.join(re.escape(s) for s in sep) + r']\s*'

        # 定义完整的正则表达式
        pattern = rf'({left_bracket_pattern})\s*([^@\}}]+?)\s*({right_bracket_pattern})\s*@\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{{2,}})'

        # 查找匹配
        match = re.search(pattern, self._text)

        if match:
            # 获取用户名部分并去掉前后空格
            usernames = re.split(sep_pattern, match.group(2).strip())
            # 获取域名部分并去掉前后空格
            domain = match.group(4).strip()

            # 处理用户名，去掉数字前缀并生成标准 email
            emails = []
            for username in usernames:
                # 去掉数字前缀
                clean_username = re.sub(r'^\d+', '', username.strip())
                emails.append(clean_username + '@' + domain)

            return emails

        return []  # 如果没有匹配，返回空列表

    def _parse_ignore1(self):
        """
        输入一个字符串，解析一种特殊的 email 地址，它是数字开头的。
        我们需要删除前面的数字，返回数字后面的标准 email 地址。
        例如 '1user@example.com'，应该解析成 user@example.com。
        如果解析失败，则返回 []。
        """
        # 使用正则表达式匹配以数字开头的电子邮件地址
        match = re.match(r'^\d+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$', self._text)

        # 如果匹配成功，返回去掉前面数字后的电子邮件地址
        if match:
            return [match.group(1)]

        return []  # 如果没有匹配，返回空列表

    @staticmethod
    def _remove_tail(text):
        """
        去尾巴, e.g. user@example.comAnotherone
        --> user@example.com
        """
        split = text.split('.')
        last = split[-1]
        for index, char in enumerate(last):
            if char.isupper():
                split[-1] = last[0: index]
                break
        return '.'.join(split)

    def _post_process(self, email_list):
        res = []
        # 去尾巴
        for em in email_list:
            res.append(self._remove_tail(em))
        # 去重
        res = list(set(res))
        return res

    def parse(self):
        res = []
        res += self._parse_normal()
        res += self._parse_combine(brackets=['{}', '()', '<>'], sep=[',', ';'])
        res += self._parse_ignore1()

        return self._post_process(res)
