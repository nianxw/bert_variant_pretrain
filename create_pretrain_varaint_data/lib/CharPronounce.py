#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
Copyright (c) Baidu.com, Inc. All Rights Reserved
@Time    : 2020-07-29
@Author  : shengzhonghao
@Desc    : 管理汉字读音，将汉字转化为拼音，查找同音字等
"""

# 内建库
from collections import defaultdict
import io, os

# 第三方库
from pypinyin import pinyin, lazy_pinyin, Style


# Config
UNK_TOKEN = '<UNK>'
# 指定读音，不指定则数字字母都为UNK
EXTRA_PRON = dict()

digit2pron = {'0':'ling',
            '1':'yi',
            '2':'er',
            '3':'san',
            '4':'si',
            '5':'wu', 
            '6':'liu',
            '7':'qi',
            '8':'ba',
            '9':'jiu'}
EXTRA_PRON.update(digit2pron)

SIMILAR_PRONOUNCE_SUFFIX_REPLACE = {'en':'eng', 
                                    'eng':'en', 
                                    'in':'ing', 
                                    'ing':'in'}
SIMILAR_PRONOUNCE_PREFIX_REPLACE = {'c':'ch',  'ch':'c', 
                                    's':'sh',  'sh':'s', 
                                    'zh':'z',  'z':'zh'}

def load(file_path):
    data = []
    for line in open(file_path):
        data.extend(line.strip().split())
    return data

class CharPronounce(object):
    """
    CharPronounce
    """

    def __init__(self, vocab_path):
        self.style = Style.NORMAL
        self.unknown_token = lambda x: UNK_TOKEN + x
        self.all_chinese_character = load(vocab_path)
        self.same_pronounce_table = self.build_char_same_pronounce_table()

    def build_char_same_pronounce_table(self):
        table = defaultdict(list)
        for char in self.all_chinese_character:
            pinyinout = pinyin(char, style=(Style.NORMAL), heteronym=True, errors=(lambda x: None))
            if len(pinyinout) == 0:
                pass
            else:
                for pron in pinyinout[0]:
                    table[pron].append(char)

        table[UNK_TOKEN] = list()
        return table

    def postprocess(self, input_list):
        return_list = []
        for x in input_list:
            pron = x[0]
            if not pron.startswith(UNK_TOKEN):
                # 正常获得拼音的词
                return_list.append(pron)
            else:
                # 未正常获得拼音的字段，逐字添加。
                unknown_str = pron[len(UNK_TOKEN):]
                for char in unknown_str:
                    char_pron = UNK_TOKEN
                    if char in EXTRA_PRON.keys():
                        char_pron = EXTRA_PRON[char]
                    return_list.append(char_pron)

        return return_list

    def get_char_pronounce(self, input_char):
        assert type(input_char) == type(str())
        assert len(input_char) == 1
        return self.get_str_pronounce(input_char)[0]

    def get_str_pronounce(self, input_str):
        assert type(input_str) == type(str())
        pypinyin_output = pinyin(input_str, style=self.style, errors=(self.unknown_token))
        post_process_output = self.postprocess(pypinyin_output)
        return post_process_output

    def get_char_list_by_pronounce(self, input_pron):
        assert type(input_pron) == type(str())
        return self.same_pronounce_table.get(input_pron, list())

    def get_replace_prefix_list(self, input_prons):
        assert type(input_prons) == type(list())
        additional_prons = []
        for pron in input_prons:
            for replace_from, replace_to in SIMILAR_PRONOUNCE_PREFIX_REPLACE.items():
                if pron.startswith(replace_from):
                    similar_pron = replace_to + pron[len(replace_from):]
                    additional_prons.append(similar_pron)
        return input_prons + additional_prons

    def get_replace_suffix_list(self, input_prons):
        assert type(input_prons) == type(list())
        additional_prons = []
        for pron in input_prons:
            for replace_from, replace_to in SIMILAR_PRONOUNCE_SUFFIX_REPLACE.items():
                if pron.endswith(replace_from):
                    similar_pron = pron[:-len(replace_from)] + replace_to
                    additional_prons.append(similar_pron)
        return input_prons + additional_prons

    def get_similar_prononce_list(self, input_pron):
        assert type(input_pron) == type(str())
        # 这个逻辑会生成一些不存在的拼音，在后续查字的时候会自动查不到
        similar_pronounces = [input_pron]
        similar_pronounces = self.get_replace_prefix_list(similar_pronounces)
        similar_pronounces = self.get_replace_suffix_list(similar_pronounces)
        similar_pronounces = list(set(similar_pronounces))
        similar_pronounces.remove(input_pron)
        return similar_pronounces

    def get_char_list_by_similar_pronounce(self, input_pron):
        assert type(input_pron) == type(str())
        similar_pronounces = self.get_similar_prononce_list(input_pron)
        similar_pronounce_chars = []
        for similar_pronounce in similar_pronounces:
            additional_chars = self.get_char_list_by_pronounce(similar_pronounce)
            similar_pronounce_chars.extend(additional_chars)
        return similar_pronounce_chars

    def get_char_same_pronounce_list(self, input_char):
        # 有多音字情况，实际整句使用get_str_pronounce获得拼音后使用get_char_list_by_pronounce。整句获得拼音会智能处理多音字。
        assert type(input_char) == type(str())
        assert len(input_char) == 1
        pron = self.get_char_pronounce(input_char)
        return self.get_char_list_by_pronounce(pron)

    def get_char_similar_pronounce_list(self, input_char):
        # 有多音字情况，实际整句使用get_str_pronounce获得拼音后使用get_char_list_by_similar_pronounce。整句获得拼音会智能处理多音字。
        assert type(input_char) == type(str())
        assert len(input_char) == 1
        pron = self.get_char_pronounce(input_char)
        return self.get_char_list_by_similar_pronounce(pron)

    def get_all_pronounce(self):
        return list(self.same_pronounce_table.keys())

    def unittest(self):
        # print(self.all_chinese_character)
        # print(self.same_pronounce_table)
        print(self.get_char_pronounce('重'))
        print(self.get_str_pronounce('欢迎来重庆'))
        print(self.get_char_list_by_pronounce('sheng'))
        print(self.get_char_list_by_similar_pronounce('sheng'))
        print(self.get_similar_prononce_list('sheng'))
        print(self.get_char_same_pronounce_list('盛'))
        print(self.get_char_similar_pronounce_list('盛'))
        # print(self.get_all_pronounce())
        print(len(self.get_all_pronounce()) )



def main():
    """
    Main
    """
    CharPronounceObj = CharPronounce('/ssd1/nianxuanwei/2022/q3/01_black_spam/create_pretrain_data/lib/data/han.txt')
    CharPronounceObj.unittest()


if __name__ == "__main__":
    main()