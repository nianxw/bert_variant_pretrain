# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
对数据进行攻击（数据增强）

1.同音字替换
2.形近字替换
3.近义词替换
4.偏旁部首拆分
5.增删改交换
6.替换为拼音

Authors: nianxuanwei(nianxuanwei01@baidu.com)
"""
import os
import re
import sys
import json
import jieba
import random
import time
import json


punctuation = r"""!"#$%&'()*,-./:;<=>?@[\]^_`{|}~“”？，！【】（）、。：；’‘……￥·"""
symbols = list(punctuation)

home_dir = os.path.dirname(os.path.realpath(__file__))
# print(home_dir)
sys.path.append(home_dir)

from pypinyin import pinyin, lazy_pinyin, Style
from collections import defaultdict
from tqdm import tqdm

from lib import CharPronounce
from lib import eda
from multiprocessing import Process


class VariantAttack(object):
    """ 文本数据增强 """
    def __init__(self, ):
        self.same_pinyin_words = CharPronounce.CharPronounce(home_dir + '/lib/data/han.txt') # 同音字、近音字
        self.near_c = json.load(open(home_dir + '/lib/data/near_character.json', 'r', encoding='utf8'))  # 形近字
        self.chai_c_src = json.load(open(home_dir + '/lib/data/chaizi-ft.json', 'r', encoding='utf8'))  # 拆分字
        self.chai_c = self.process_chai_c()
        self.enlarge_near_c()
        self.synonyms_dict = json.load(open(home_dir + '/lib/data/near_words.json', 'r', encoding='utf8'))  # 近义词

    
    def process_chai_c(self):
        new_chai_c = {}
        for k, v in self.chai_c_src.items():
            max_l = 0
            for vv in v:
                max_l = max(len(vv), max_l)
            if max_l <= 2:
                new_chai_c[k] = v
        return new_chai_c

    def enlarge_near_c(self):
        """ 扩充形近字 """
        for key, values in self.chai_c.items():
            for value in values:
                for w in value:
                    if w in self.near_c:
                        self.near_c[w].append(key)
        for key, values in self.near_c.items():
            new_values = list(set(values))
            self.near_c[key] = new_values

    def is_all_chinese(self, strs):
        for _char in strs:
            if not '\u4e00' <= _char <= '\u9fa5':
                return False
        return True
    
    def get_similar_pinyin_words(self, char):
        """ 获取同音、近音字 """
        var_char = ''
        pron = self.same_pinyin_words.get_char_pronounce(char)
        if pron:
            all_pron_char = self.same_pinyin_words.get_char_list_by_pronounce(pron)
            all_pron_char2 = self.same_pinyin_words.get_char_list_by_similar_pronounce(pron)
            all_pron_char = set(all_pron_char + all_pron_char2)
            
            simpron = self.same_pinyin_words.get_similar_prononce_list(pron)
            validpron = set([pron] + simpron)
            all_pron_freq_char = all_pron_char # SZH0616:非常用字
            candidate = list(filter(lambda x: self.same_pinyin_words.get_char_pronounce(x) in validpron, all_pron_freq_char))
            candidate = list(filter(lambda x:x!=char, candidate))
            if len(candidate) > 0:
                var_char = random.choice(candidate)
        return var_char

    def get_pinyin(self, char):
        """ 获取拼音 """
        var_char = ''
        porn = self.same_pinyin_words.get_char_pronounce(char)
        if porn and porn != '<UNK>':
            prob = random.random()
            if prob > 0.5:
                var_char = porn
            else:
                var_char = porn[0]

            new_prob = random.random()
            if new_prob > 0.95:
                sim_porn = self.same_pinyin_words.get_similar_prononce_list(porn)
                if sim_porn:
                    var_char = random.choice(sim_porn)
        return var_char

    def get_near_c(self, char):
        """ 获取形近字 """
        var_char = ''
        near_c_list = self.near_c.get(char, [])
        if near_c_list:
            var_char = random.choice(near_c_list)
        return var_char

    def get_chai_c(self, char):
        """ 获取拆字信息 """
        var_char = ''
        chai_c_list = self.chai_c.get(char, [])
        chai_c_list = [_ for _ in chai_c_list if len(_) == 2]
        if chai_c_list:
            var_char = ''.join(random.choice(chai_c_list))
        return var_char

    def get_word_variant(self, word):
        is_var = False
        var_word = ''
        not_var_prob = 0.05
        if len(word) > 1:
            not_var_prob = 0.1
        for char in word:
            prob = random.random()
            if prob < not_var_prob:
                var_word += char
                continue
            elif not_var_prob <= prob < 0.105:
                var_rule = self.get_similar_pinyin_words
            elif 0.105 <= prob < 0.45:
                var_rule = self.get_pinyin
            elif 0.45 <= prob < 0.95:
                var_rule = self.get_near_c
            else:
                var_rule = self.get_chai_c

            var_char = var_rule(char)
            if var_char:
                var_word += var_char
                is_var = True
            else:
                var_word += char
        return is_var, var_word

    def insert_symbol(self, sentence):
        new_sentence = ''

        sentence = [item for item in sentence if item not in symbols]
        backup = random.sample(symbols, 3)
        for index in range(len(sentence)):
            new_sentence += sentence[index]
            if random.random() < 0.1:
                new_sentence += random.choice(backup)
        return new_sentence

    def synonym_replacement(self, word_list, num):
        """ 同义词替换 """
        indexes = list(range(len(word_list)))
        change_indexes = random.sample(indexes, num)
        var_sen = False
        for c_index in change_indexes:
            sim_words = self.synonyms_dict.get(word_list[c_index], [])
            if sim_words:
                word_list[c_index] = random.choice(sim_words)
                var_sen = True
        return var_sen, word_list
    
    def random_insertion(self, word_list, num):
        """ 随机插入同义词 """
        indexes = list(range(len(word_list)))
        change_indexes = random.sample(indexes, num)
        var_sen = False
        for c_index in change_indexes:
            sim_words = self.synonyms_dict.get(word_list[c_index], [])
            if sim_words:
                random_idx = random.randint(0, len(word_list) - 1)
                word_list.insert(random_idx, random.choice(sim_words))
                var_sen = True
        return var_sen, word_list

    def random_deletion(self, word_list, num):
        """ 随机删除词 """
        indexes = list(range(len(word_list)))
        change_indexes = random.sample(indexes, num)
        var_sen = False
        word_list_new = []
        for index in indexes:
            if index in change_indexes:
                delete_prob = random.random()
                if delete_prob < 0.5:
                    word_list_new.append(word_list[index])
                else:
                    var_sen = True
            else:
                word_list_new.append(word_list[index])
        return var_sen, word_list_new

    def random_swap(self, word_list, num):
        """ 随机交换词 """
        random_idx_1 = random.randint(0, len(word_list)-1)
        random_idx_2 = random.randint(0, len(word_list)-1)
        var_sen = False
        if random_idx_1 != random_idx_2:
            word_list[random_idx_1], word_list[random_idx_2] = word_list[random_idx_2], word_list[random_idx_1]
            var_sen = True
        return var_sen, word_list

    def attack_sentence(self, sentence, attack_sen_num=10, ration=0.1, max_seq_len=128):
        sentence = sentence[: max_seq_len]
        var_sen_num = 0
        all_sentences = []
        while var_sen_num < attack_sen_num:
            var_sen = False
            attacked_sentence = ' '.join(list(jieba.cut(sentence)))
            if random.random() > 0.2:  # eda
                # var_sen, word_list = random.choice([self.synonym_replacement, self.random_deletion, self.random_insertion, self.random_swap])(attacked_sentence.split(), 1)
                var_sen, word_list = random.choice([self.synonym_replacement, self.random_insertion])(attacked_sentence.split(), 1)
            if var_sen:
                attacked_sentence_words = word_list
            else:
                attacked_sentence_words = attacked_sentence.split()
            num_to_attack = max(1, int(len(attacked_sentence_words) * ration))
            # num_to_attack = 1
            num_to_attack_index = random.sample(list(range(len(attacked_sentence_words))), num_to_attack)
            for index in num_to_attack_index:
                if not attacked_sentence_words[index]:
                    continue
                is_var, var_word = self.get_word_variant(attacked_sentence_words[index])
                if is_var:
                    var_sen = True
                attacked_sentence_words[index] = var_word
            
            var_sen_num += 1
            if not var_sen:
                var_sen, attacked_sentence_words = random.choice([self.synonym_replacement, self.random_deletion, self.random_insertion, self.random_swap])(attacked_sentence.split(), 1)

            all_sentences.append(''.join(attacked_sentence_words))
        return all_sentences
