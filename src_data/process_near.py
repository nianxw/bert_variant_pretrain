import json
import sys
import os
from collections import defaultdict


word_to_word = defaultdict(list)

def load1(file_path='/ssd1/nianxuanwei/2022/q3/01_black_spam/src_data/near_character4.txt'):
    for line in open(file_path):
        line = line.strip()
        line = line.split()
        if len(line) < 2:
            continue
        key = line[0]
        if len(key) > 1:
            print(key)
        value = list(line[1])
        for w in value:
            w = w.strip()
            if len(w) == 1:
                word_to_word[key].append(w)


def load2(file_path='/ssd1/nianxuanwei/2022/q3/01_black_spam/src_data/near_character2.txt'):
    for line in open(file_path):
        line = line.strip()
        line = line.split('：')
        if len(line) != 2:
            continue
    
        key = line[0]
        if len(key) > 1:
            print(key)
        value = line[1].split('，')
        for w in value:
            w = w.strip()
            if len(w) == 1:
                word_to_word[key].append(w)

def load3(file_path='/ssd1/nianxuanwei/2022/q3/01_black_spam/src_data/near_character3.txt'):
    for line in open(file_path):
        line = line.strip()
        if not line:
            continue
        line = line.split('，')

        key = line[0]
        if len(key) > 1:
            print(key)
        value = line[1:]
        for w in value:
            w = w.strip()
            if len(w) == 1:
                word_to_word[key].append(w)

load1()
load2()
load3()

latest_w = defaultdict(list)

for key_src, value_src in word_to_word.items():

    merge_key = [key_src] + value_src

    for key in merge_key:
        tmp_words = merge_key.copy()
        for w in merge_key:
            tmp_words.extend(word_to_word.get(w, []))
        tmp_words = list(set(tmp_words))
        tmp_words.remove(key)
        latest_w[key] = tmp_words

json.dump(latest_w, open('形近字词表.json', 'w'), ensure_ascii=False)
print(len(latest_w))


        