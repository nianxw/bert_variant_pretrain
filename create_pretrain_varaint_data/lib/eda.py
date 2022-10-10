#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import jieba
# import synonyms
import random
import json
from random import shuffle

# random.seed(2022)

home_dir = os.path.dirname(__file__)
print(home_dir)
sys.path.append(home_dir)

#停用词列表，默认使用哈工大停用词表
f = open(home_dir + '/stopwords-master/hit_stopwords.txt')
stop_words = list()
for stop_word in f.readlines():
    stop_words.append(stop_word[:-1])

synonyms_dict = json.load(open(home_dir + '/data/near_words.json', 'r', encoding='utf8'))

#考虑到与英文的不同，暂时搁置
#文本清理
def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


########################################################################
# 同义词替换
# 替换一个语句中的n个单词为其同义词
########################################################################
def synonym_replacement(words, n):
    new_words = words.copy()
    random_word_list = set()
    for word in words:
        if is_Chinese(word) and word not in stop_words:
            random_word_list.add(word)
    random_word_list = list(random_word_list)
    if not random_word_list:
        return new_words
    random.shuffle(random_word_list)

    for index in range(n):
        random_word = random_word_list[index]
        synonyms = get_synonyms(random_word)
        if len(synonyms) >= 1:
            synonym = random.choice(synonyms)
            new_words = [synonym if word == random_word else word for word in new_words]

    # num_replaced = 0  
    # for random_word in random_word_list:          
    #     synonyms = get_synonyms(random_word)
    #     if len(synonyms) >= 1:
    #         synonym = random.choice(synonyms)
    #         new_words = [synonym if word == random_word else word for word in new_words]   
    #         num_replaced += 1
    #     if num_replaced >= n: 
    #         break

    sentence = ' '.join(new_words)
    new_words = sentence.split(' ')

    return new_words

def get_synonyms(word):
    # return synonyms.nearby(word)[0]
    return synonyms_dict.get(word, [])


########################################################################
# 随机插入
# 随机在语句中插入n个词
########################################################################
def random_insertion(words, n):
    new_words = words.copy()
    random_word_list = set()
    for word in words:
        if is_Chinese(word) and word not in stop_words:
            random_word_list.add(word)
    random_word_list = list(random_word_list)
    if not random_word_list:
        return new_words
    random.shuffle(random_word_list)

    for index in range(n):
        synonyms = get_synonyms(random_word_list[index])
        if synonyms:
            random_synonym = random.choice(synonyms)
            random_idx = random.randint(0, len(new_words)-1)
            new_words.insert(random_idx, random_synonym)
    return new_words

########################################################################
# Random swap
# Randomly swap two words in the sentence n times
########################################################################

def random_swap(words, n):
    new_words = words.copy()
    for _ in range(n):
        new_words = swap_word(new_words)
    return new_words

def swap_word(new_words):
    random_idx_1 = random.randint(0, len(new_words)-1)
    random_idx_2 = random_idx_1
    counter = 0
    while random_idx_2 == random_idx_1:
        random_idx_2 = random.randint(0, len(new_words)-1)
        counter += 1
        if counter > 3:
            return new_words
    new_words[random_idx_1], new_words[random_idx_2] = new_words[random_idx_2], new_words[random_idx_1] 
    return new_words

########################################################################
# 随机删除
# 以概率p删除语句中的词
########################################################################
def random_deletion(words, p):

    if len(words) == 1:
        return words

    new_words = []
    for word in words:
        r = random.uniform(0, 1)
        if r > p:
            new_words.append(word)

    if len(new_words) == 0:
        rand_int = random.randint(0, len(words)-1)
        return [words[rand_int]]

    return new_words


########################################################################
#EDA函数
def eda(sentence, alpha_sr=0.1, alpha_ri=0.1, alpha_rs=0.1, p_rd=0.1, num_aug=9):
    seg_list = jieba.cut(sentence)
    seg_list = " ".join(seg_list)
    words = list(seg_list.split())
    num_words = len(words)

    augmented_sentences = []
    num_new_per_technique = int(num_aug/4)+1
    # n_sr = max(1, int(alpha_sr * num_words))
    # n_ri = max(1, int(alpha_ri * num_words))
    # n_rs = max(1, int(alpha_rs * num_words))

    #print(words, "\n")


    prob = random.random()
    if 0 < prob < 0.4:
        #同义词替换sr
        for _ in range(num_new_per_technique):
            a_words = synonym_replacement(words, 1)
            augmented_sentences.append(' '.join(a_words))
    elif 0.4 < prob < 0.7:

        #随机插入ri
        for _ in range(num_new_per_technique):
            a_words = random_insertion(words, 1)
            augmented_sentences.append(' '.join(a_words))
    else:
        #随机删除rd
        for _ in range(num_new_per_technique):
            a_words = random_deletion(words, 1)
            augmented_sentences.append(' '.join(a_words))

    
    #随机交换rs
    # for _ in range(num_new_per_technique):
    #     a_words = random_swap(words, n_rs)
    #     augmented_sentences.append(' '.join(a_words))

   
    # #随机删除rd
    # for _ in range(num_new_per_technique):
    #     a_words = random_deletion(words, p_rd)
    #     augmented_sentences.append(' '.join(a_words))
    
    #print(augmented_sentences)
    shuffle(augmented_sentences)

    if num_aug >= 1:
        augmented_sentences = augmented_sentences[:num_aug]
    else:
        keep_prob = num_aug / len(augmented_sentences)
        augmented_sentences = [s for s in augmented_sentences if random.uniform(0, 1) < keep_prob]

    # augmented_sentences.append(seg_list)

    # return augmented_sentences
    return random.choice(augmented_sentences)

if __name__ == "__main__":
    #测试用例
    res = eda(sentence="我们就像蒲公英，我也祈祷着能和你飞去同一片土地")
    print(res)