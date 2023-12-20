# %%

import json, itertools, os
from datetime import datetime, date
from collections import namedtuple
from collections import Counter
import emoji

import sys
sys.path.append('c:/Users/mk/Python/1 - маркетплейсы/Аналитическая система по ВБ/wbClasses2/')
import wbbase

nlp = wbbase.nlpWb()

# %%

TOP_TD_IDF = 3

path = 'C:/Users/mk/Downloads/Telegram Desktop/ChatExport_2023-12-20'

# %%


class tg_json_analysis:
    def __init__(self, filename) -> None:
        pass

    def basicStat(self):
        '''
        Выводит базовую статистику, дикт с данными:
        - Сколько сообщений всего
        - Самые продуктивные пользователи
        - Продуктивность пары: день недели - час дня
        - Важные слова (top-3 слов по TD/IDF по каждому сообщению)
        
        '''
        pass
    
    def statByPeriod(self, period='week'):
        '''
        Статистика сгруппированная по периодам:
        - Количество сообщений
        - Самые продуктивные писатели (?)
        - Важные слова по периодам (?)
        '''
        pass

    def getUsers(self):
        '''
        Возвращает список пользователей, с количеством сообщений
        '''

    def statByUser(self, user, period='week'):
        '''
        Статистика сгруппированная по пользователям:
        - Количество сообщений (по периоду)
        - Важные слова
        '''
        pass

    def getTopics(self):
        '''
        Возвращает список доступных topicId с количеством ответов
        '''

    def statByTopic(self, topicId):
        '''
        Стататистика по топику:
        - Количество сообщений (сгруппировано по периоду?)
        - Важные слова в топике
        - Активные писатели в топике
        '''

    def getWords(self):
        '''
        Возвращает дикт с полным лексиконом (слово:сколько раз встречалось)
        '''

    def statByWord(self, word, period='week'):
        '''
        Статистика по конкретному слову:
        - Частота по периоду
        - Кто его пишет? (по идее в процентном соотношении надо) ?
        '''
        pass




# %%

with open(os.path.join(path, 'result.json'), encoding='utf8') as fp:
    data = json.load(fp)


# %%
extract_params = ['id', 'type', 'date', 'edited', 'from', 'from_id', 'reply_to_message_id', 'text', ]
fields = ['id', 'type', 'date', 'edited', 'from_name', 'from_id', 'reply_to_message_id', 'text', 'words', 'year', 'month', 'day', 'week', 'weekday', 'hour', 'td_idf']

msg = namedtuple('msg', fields)
df = []
words_idf = Counter()

ids = set()

for message in data['messages']:
    data_point = {k:None for k in extract_params}
    for k,v in ((k,v) for k,v in message.items() if k in extract_params): data_point[k] = v
    text = []
    if isinstance(data_point['text'], list):
        for t in data_point['text']:
            try:
                if t['type'] != 'link':
                    text.append(t['text'])
            except TypeError:
                text.append(t)
        data_point['text'] = ' '.join(text)
    # data_point['text'] = emoji.demojize(data_point['text'])
    emojis = [x.chars for x in emoji.analyze(data_point['text'])]
    words = nlp.tokenizeNormalize(emoji.replace_emoji(data_point['text'], '.'))
    data_point['words'] = Counter(words + emojis)
    words_idf.update(data_point['words'].keys())
    data_point['from_name'] = data_point.pop('from')
    dt = datetime.fromisoformat(data_point['date'])
    data_point['hour'] = dt.hour
    data_point['year'], data_point['week'], data_point['weekday'] = date(dt.year, dt.month, dt.day).isocalendar()
    data_point['month'], data_point['day'] = dt.month, dt.day
    data_point['td_idf'] = None
    ids.add(data_point['id'])
    df.append(msg(**data_point))
df = [d for d in df if d.type == 'message']

# %%
lexicon = Counter()
for obj in df:
    lexicon.update(obj.words)
# %%
lendf = len(df)
words_idf = {k:lendf/v for k,v in words_idf.items()}

for i, data_point in enumerate(df):
    num_words = sum(data_point.words.values())
    d = data_point._asdict()
    d['td_idf'] = {word: ((count/num_words)/words_idf[word]) for word, count in data_point.words.items()}
    tmp = [(k,v) for k,v in d['td_idf'].items()]
    d['td_idf'] = dict(sorted(tmp, key=lambda tup: tup[1], reverse=True))
    d['td_idf'] = dict(list(d['td_idf'].items())[0:TOP_TD_IDF])
    df[i] = msg(**d)


# %%
popular_words = Counter()
for d in df:
    # tmp = dict(list(d.td_idf.items())[0:10])
    tmp = d.td_idf
    popular_words.update(Counter(tmp.keys()))

popular_words
# %%
lexicon
# %%

# %%
children = dict()

for data_point in reversed(df):
    if data_point.reply_to_message_id != None and data_point.reply_to_message_id in ids:
        try:
            children[data_point.reply_to_message_id].append(data_point.id)
        except:
            children[data_point.reply_to_message_id] = [data_point.id]

children
# %%
full_branches = dict(children)

for parent, children in full_branches.items():
    for child in children:
        if child in full_branches.keys():
            full_branches[parent] += full_branches[child]

full_branches
            
# %%
df = {v.id:v for v in df}

# %%
df
# %%
