# %%

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import json, itertools, os
import datetime
import json, itertools, os
from collections import Counter

import tganalysis

path = 'C:/Users/mk/Downloads/Telegram Desktop/ChatExport_2023-12-20'
# path = 'C:/Users/mk/Downloads/Telegram Desktop/ChatExport_2023-12-23 (5)'
# path = 'C:/Users/mk/Downloads/Telegram Desktop/ChatExport_2023-12-23 (4)'
# path = 'C:/Users/mk/Downloads/Telegram Desktop/ChatExport_2023-12-23 (3)'
# path = 'C:/Users/mk/Downloads/Telegram Desktop/ChatExport_2023-12-23 (2)'
# path = 'C:/Users/mk/Downloads/Telegram Desktop/ChatExport_2023-12-23 (1)'
# path = 'C:/Users/mk/Downloads/Telegram Desktop/ChatExport_2023-12-23'
path = 'data/ChatExport_2023-12-30'
filename = os.path.join(path, 'result.json')

tg = tganalysis.tg_json_analysis(filename)

chat_data = {}

chat_data['chat_id'] = tg.chat_id
chat_data['chat_name'] = tg.chat_name

output_path = '1'


# %%
tg.fields
# %%
replies = [(tg.userid_name[x.from_id],tg.userid_name[tg.df[x.reply_to_message_id].from_id]) for x in tg.df.values() if x.reply_to_message_id is not None and x.reply_to_message_id in tg.df]
# %%
replies = sorted(replies)
# %%
count = Counter()

for key, group in itertools.groupby(replies):
    d = [elem for elem in group]
    count[key] = len(d)
# %%
[(f'{a} -> {b}', count) for ((a,b), count) in count.most_common(30)]
# %%
df = pd.DataFrame([(f'{a} -> {b}', count) for ((a,b), count) in count.most_common(30)], columns=['От кого -> Кому', "Кол-во сооб."])

print(df.to_clipboard(index=False))
# %%
Counter([x for (_,x) in count.keys()]).most_common(30)
# %%
