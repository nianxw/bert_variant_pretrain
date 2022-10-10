# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
获取词表

Authors: nianxuanwei(nianxuanwei01@baidu.com)
Date:    2022/08/23
"""
import os
import re
import sys
import json
import jieba
import random
import time
import json

home_dir = os.path.dirname(os.path.realpath(__file__))
print(home_dir)
sys.path.append(home_dir)

from pypinyin import pinyin, lazy_pinyin, Style

from lib import CharPronounce
from lib import eda
from multiprocessing import Process


class VariantAttack(object):
    """ 文本数据增强 """
    def __init__(self, ):
        self.same_pinyin_words = CharPronounce.CharPronounce(home_dir + '/lib/data/han.txt') # 同音字、近音字
        self.near_c = json.load(open(home_dir + '/lib/data/near_character.json', 'r', encoding='utf8'))  # 形近字
        self.chai_c = json.load(open(home_dir + '/lib/data/chaizi-ft.json', 'r', encoding='utf8'))  # 拆分字
        self.enlarge_near_c()

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
            if new_prob > 0.9:
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
        for char in word:
            var_rule = random.choice([self.get_similar_pinyin_words, self.get_pinyin, self.get_near_c, self.get_chai_c])
            var_char = var_rule(char)
            if var_char:
                var_word += var_char
                is_var = True
            else:
                var_word += char
        return is_var, var_word

    def attack_sentence(self, sentence, attack_sen_num=10, ration=0.1, max_seq_len=128):
        sentence = sentence[: max_seq_len]
        var_sen_num = 0
        all_sentences = []
        while var_sen_num < attack_sen_num:
            var_sen = False
            attacked_sentence = ' '.join(list(jieba.cut(sentence)))
            if random.random() > 0.3:  # eda
                attacked_sentence = eda.eda(sentence, num_aug=1)
                var_sen = True
            attacked_sentence_words = attacked_sentence.split()
            num_to_attack = max(1, int(len(attacked_sentence_words) * ration))
            num_to_attack_index = random.sample(list(range(len(attacked_sentence_words))), num_to_attack)
            for index in num_to_attack_index:
                is_var, var_word = self.get_word_variant(attacked_sentence_words[index])
                if is_var:
                    var_sen = True
                attacked_sentence_words[index] = var_word
            
            var_sen_num += 1
            all_sentences.append(''.join(attacked_sentence_words))
        return all_sentences


if __name__ == "__main__":
    bert_vocab = set()
    for line in open('/home/ssd6/nianxuanwei01/13_variant_pretrain/create_pretrain_data/vocab.txt'):
        bert_vocab.add(line.strip())
    
    synonyms_dict = json.load(open('/home/ssd6/nianxuanwei01/13_variant_pretrain/create_pretrain_data/lib/data/near_words.json', 'r', encoding='utf8'))
    model = VariantAttack()
    add_vocab = set()
    for k, v in model.near_c.items():
        if k not in bert_vocab and k not in add_vocab:
            add_vocab.add(k)
        for vv in v:
            if vv not in bert_vocab and vv not in add_vocab:
                add_vocab.add(vv)
    
    for k, v in model.chai_c.items():
        if k not in bert_vocab and k not in add_vocab:
            add_vocab.add(k)
        for vv in v:
            for vvv in vv:
                if vvv not in bert_vocab and vvv not in add_vocab:
                    add_vocab.add(vvv)
    
    for k, v in synonyms_dict.items():
        for kk in k:
            if kk not in bert_vocab and kk not in add_vocab:
                add_vocab.add(kk)
        for vv in v:
            for vvv in vv:
                if vvv not in bert_vocab and vvv not in add_vocab:
                    add_vocab.add(vvv)

    for w in add_vocab:
        print(w)
    
    
        

    

