import sys
import json
from collections import defaultdict

word_to_chai = defaultdict(list)
for line in open('/ssd1/nianxuanwei/2022/q3/01_black_spam/src_data/chaizi-ft.txt'):
    line = line.strip().split('\t')
    key = line[0]
    values = line[1:]
    for value in values:
        value = value.split()
        word_to_chai[key].append(value)
json.dump(word_to_chai, open('chaizi-ft.json', 'w'), ensure_ascii=False)