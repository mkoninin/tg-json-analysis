# %%

import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import seaborn as sns
from collections import defaultdict

import json, itertools, os
from datetime import datetime, date
from collections import namedtuple
from collections import Counter
import emoji
from operator import attrgetter

from enum import Enum

import sys
sys.path.append('c:/Users/mk/Python/1 - маркетплейсы/Аналитическая система по ВБ/wbClasses2/')
import wbbase

common_words = [c.strip() for c in open('common_words.txt').readlines()]


TOP_TD_IDF = 5

class tg_json_analysis:
    def __init__(self, filename) -> None:
        with open(filename, encoding='utf8') as fp:
            data = json.load(fp)

        self.chat_name = data['name']
        self.chat_id = data['id']
        self.fields = ['id', 'type', 'date', 'from_name', 'from_id', 'reply_to_message_id', 'text', 'words', 'year', 'month', 'day', 'week', 'weekday', 'hour', 'td_idf'] #'edited',

        self.msg = namedtuple('msg', self.fields)
        _df = []
        self.ids = set()
        self.userid_name = {}

        for message in data['messages']:
            if 'from' in message: message['from_name'] = message.pop('from')
            data_point = {k:None for k in self.fields}
            for k,v in ((k,v) for k,v in message.items() if k in self.fields and k in message): data_point[k] = v
            if data_point['from_name'] == None: data_point['from_name'] = ''
            text = []
            if isinstance(data_point['text'], list):
                for t in data_point['text']:
                    try:
                        if t['type'] != 'link':
                            text.append(t['text'])
                    except TypeError:
                        text.append(t)
                data_point['text'] = ' '.join(text)
            dt = datetime.fromisoformat(data_point['date'])
            data_point['hour'] = dt.hour
            data_point['year'], data_point['week'], data_point['weekday'] = date(dt.year, dt.month, dt.day).isocalendar()
            data_point['month'], data_point['day'] = dt.month, dt.day
            self.ids.add(data_point['id'])
            self.userid_name[data_point['from_id']] = data_point['from_name']
            _df.append(self.msg(**data_point))
        _df = [d for d in _df if d.type == 'message']
        self.df = {v.id:v for v in _df}
        
    def _genWords(self):
        '''
        вынес в отдельную функцию, чтобы генерировать слова только если надо
        '''
        self.nlp = wbbase.nlpWb()

        words_idf = Counter()
        self.lexicon = Counter()
        self.important_words = Counter()
        self.important_words2 = Counter()
        self.inverted_index = dict()
        for i, d in self.df.items():
            data_point = d._asdict()
            emojis = [x.chars for x in emoji.analyze(data_point['text'])]
            words = self.nlp.tokenizeNormalize(emoji.replace_emoji(data_point['text'], '.'))
            data_point['words'] = Counter(words + emojis)            
            for c in common_words:
                try:
                    del data_point['words'][c]
                except:
                    pass
            for word in data_point['words'].keys():
                if word in self.inverted_index:
                    self.inverted_index[word].append(data_point['id'])
                else: 
                    self.inverted_index[word] = [data_point['id']]
            words_idf.update(data_point['words'].keys())
            self.df[i] = self.msg(**data_point)
            self.lexicon.update(data_point['words'])
        lendf = len(self.df)
        words_idf = {k:math.log(lendf/v) for k,v in words_idf.items()}
        for i, d in self.df.items():
            data_point = d._asdict()
            num_words = data_point['words'].total()
            data_point['td_idf'] = {word: ((count/num_words)/words_idf[word]) for word, count in data_point['words'].items()}
            data_point['td_idf'] = Counter(data_point['td_idf']).most_common(TOP_TD_IDF)
            self.df[i] = self.msg(**data_point)
            self.important_words.update(dict(data_point['td_idf']).keys())
            self.important_words2.update(dict(data_point['td_idf']))

    def _groupBy(self, fields):
        if type(fields) == str:
            fields = [fields]
        ret = dict()
        grouping_target = sorted(self.df.values(), key=attrgetter(*fields))
        for key, group in itertools.groupby(grouping_target, attrgetter(*fields)):
            d = [elem[0] for elem in group]
            ret[key] = d
        return ret

    def statWeekdayHour(self):
        '''
        - Продуктивность пары: день недели - час дня (используется для heatmap)
        '''
        a = self._groupBy(['weekday', 'hour'])
        return Counter({k:len(v) for k,v in a.items()})

    
    def statMsgByPeriod(self, period='week'):
        '''
        Статистика сгруппированная по периодам:
        - Количество сообщений
        '''
        a = self._groupBy(['year', 'week'])
        return Counter({k:len(v) for k,v in a.items()})

    # def getUsers(self):
    #     '''
    #     Возвращает список пользователей, с количеством сообщений
    #     '''
    #     if not hasattr(self, '_userMsgList'):
    #         self._userMsgList = self._groupBy('from_name')
    #     return list(self._userMsgList.keys())

    def statByUser(self, period='week'):
        '''
        Статистика сгруппированная по пользователям:
        - Количество сообщений по пользователю (по периоду)
        '''
        a = self._groupBy(['year', 'week', 'from_name'])
        return Counter({k:len(v) for k,v in a.items()})

    def statTopUser(self):
        '''
        Статистика сгруппированная по пользователям:
        - Количество сообщений (по периоду)
        # - Важные слова
        '''
        a = self._groupBy(['from_name'])
        return Counter({k:len(v) for k,v in a.items()})

    def _genFullBranches(self):
        children = dict()
        for data_point in reversed(self.df.values()):
            if data_point.reply_to_message_id != None and data_point.reply_to_message_id in self.ids:
                try:
                    children[data_point.reply_to_message_id].append(data_point.id)
                except:
                    children[data_point.reply_to_message_id] = [data_point.id]
        self.children = dict(children)
        full_branches = dict(self.children)
        for parent, self.children in full_branches.items():
            for child in self.children:
                if child in full_branches.keys():
                    full_branches[parent] += full_branches[child]
        self.full_branches = dict(full_branches)

    def getTopics(self):
        '''
        Возвращает список доступных topicId с количеством ответов
        '''
        if not hasattr(self, 'full_branches'):
            self._genFullBranches()      
        return list(self.full_branches.keys())
        

    def statByTopic(self, topicId):
        '''
        Стататистика по топику:
        - Количество сообщений (сгруппировано по периоду?)
        - Важные слова в топике
        - Активные писатели в топике
        '''
        if not hasattr(self, 'full_branches'):
            self._genFullBranches()      

    def getWords(self, top=None):
        '''
        Возвращает дикт с полным лексиконом (слово:сколько раз встречалось)
        '''
        if top != None and type(top) == int:
            return self.lexicon.most_common(top)
        return self.lexicon

    def statByWord(self, word, period='week'):
        '''
        Статистика по конкретному слову:
        - Частота по периоду
        - Кто его пишет? (по идее в процентном соотношении надо) ?
        '''
        pass

    def __getitem__(self, name):
        if type(name) == str:
            f = attrgetter(name)
        else:
            f = attrgetter(*name)
        return {k:f(v) for k, v in self.df.items()}

# %%
