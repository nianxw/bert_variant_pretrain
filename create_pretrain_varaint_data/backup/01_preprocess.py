# coding=utf-8

# 贴吧数据进行预处理
import re
def Cleaning_data(x):
    """
    :param x:
    :return:
    """
    def clean(text):
        text = re.sub('<br>', '', text)
        text = text.strip()
        text = re.sub('<img class.*?>', '', text)
        text = re.sub('&.*?;', '', text)
        text = re.sub('<a href=.*?</a>', '', text)
        text = text.replace('\n', '').replace('\t', '').replace('\r', '')
        text = re.sub('回复(.*?)(:|：)', '', text)
        if text.isdigit():
            return ''
        return text

    def filter_tags(htmlstr):
        """
        # Python通过正则表达式去除(过滤)HTML标签
        :param htmlstr:
        :return:
        """
        # 先过滤CDATA
        re_cdata = re.compile('//<!\
        CDATA\[[ >]∗ //\
        CDATA\[[ >]∗ //\
        \] > ', re.I)  # 匹配CDATA
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)
        # Script
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)
        # style
        re_br = re.compile('<br\s*?/?>')
        # 处理换行
        re_h = re.compile('</?\w+[^>]*>')
        # HTML标签
        re_comment = re.compile('<!--[^>]*-->')
        # HTML注释
        s = re_cdata.sub('', htmlstr)
        # 去掉CDATA
        s = re_script.sub('', s)  # 去掉SCRIPT
        s = re_style.sub('', s)
        # 去掉style
        s = re_br.sub('\n', s)
        # 将br转换为换行
        s = re_h.sub('', s)  # 去掉HTML 标签
        s = re_comment.sub('', s)
        # 去掉HTML注释
        # 去掉多余的空行
        blank_line = re.compile('\n+')
        s = blank_line.sub('\n', s)
        s = replaceCharEntity(s)  # 替换实体
        return s

    def replaceCharEntity(htmlstr):
        """
        :param htmlstr:HTML字符串
        :function:过滤HTML中的标签
        """
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }

        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()  # entity全称，如>
            key = sz.group('name')  # 去除&;后entity,如>为gt
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                # 以空串代替
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

    def _repalce(s, re_exp, repl_string):
        return re_exp.sub(repl_string, s)

    def DeleteHttp(content):
        """

        :param content:
        :return:
        """

        content_deleteHttp = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                                    '', content, flags=re.MULTILINE)
        content_deleteHttp = content_deleteHttp.replace('\u200b', '')  # 除去\u200b
        pat = re.compile('<[^>]+?>', re.S)
        content_deleteHttp = pat.sub('', str(content_deleteHttp))
        # print(content_deleteHttp)
        return content_deleteHttp
    m2=str(x).replace('<p>&nbsp; &nbsp; &nbsp; &nbsp;', '').replace('</p><p><br></p>', '').\
        replace('<br>', '').replace('</p>', '').replace('<p>', '').\
        replace('       ', '').replace('[图片]', '').strip()
    m3=filter_tags(m2)
    m4=replaceCharEntity(m3)
    # print("m4:",m4)
    m5 = DeleteHttp(str(m4))
    m6 = clean(m5)
    return m6


def main():
    # sys.argv[1]
    input_file = 'src_data/20220822_head_1w'
    output_file = input_file + '.clean'

    output = open(output_file, 'w', encoding='utf8')
    with open(input_file, 'r') as f:
        for line in f:
            try:
                line = line.strip().split('\01')
                tid = line[0]
                pid = line[1]
                user_id = line[8]
                forum_name = line[11]
                title = line[6]
                content = line[7]
                title = Cleaning_data(title.replace("回复：", ""))
                content = Cleaning_data(content)
                output.write('\t'.join([pid, title, content]) + '\n')
                output.flush()
            except:
                continue
    output.close()


if __name__ == "__main__":
    main()

                
            