# %%

# тут я хочу выделить общие слова в чатах, чтобы потом их исключать

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import json, itertools, os
import datetime
from collections import Counter

import tganalysis

# paths = ['C:/Users/mk/Downloads/Telegram Desktop/ChatExport_2023-12-20']

paths = os.listdir('data')

paths

# %%
words = {}

for path in paths:
    filename = os.path.join('data', path, 'result.json')

    tg = tganalysis.tg_json_analysis(filename)

    output_path = f'output/tg-{tg.chat_id}'
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    tg._genWords()
    words[tg.chat_id] = tg.lexicon.most_common(500)

# %%

wds_counter = Counter()
for k, wds in words.items():
    for (k,v) in wds:
        wds_counter[k] += 1

common_words = [k for k, v in wds_counter.items() if v >3]
# wds

open('common_words.txt', 'w').write('\n'.join(common_words))

# # %%

# words_index = set()
# words_only = {}
# for k, wds in words.items():
#     # Counter({k:v for (k,v) in wds})
#     words_only[k] = [wd for (wd, _) in wds]
#     for (k,v) in wds:
#         words_index.add(k) 


# # %%

# words_onehot = {}
# for k, wds in words_only.items():
#     count = Counter(list(words_index) + wds)
#     count.subtract(words_index)
#     words_onehot[k] = count

# # %%
# df = pd.DataFrame(words_onehot)
# df.sum(axis=1).sort_values()
# # %%
