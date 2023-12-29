# %%

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import json, itertools, os
import datetime

import tganalysis

# paths = ['C:/Users/mk/Downloads/Telegram Desktop/ChatExport_2023-12-20']

paths = os.listdir('data')

paths

# %%
for path in paths:
    filename = os.path.join('data', path, 'result.json')

    tg = tganalysis.tg_json_analysis(filename)

    chat_data = {}

    chat_data['chat_id'] = tg.chat_id
    chat_data['chat_name'] = tg.chat_name

    output_path = f'output/{tg.chat_id}'
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    # самые популярные слова

    tg._genWords()

    # tg.lexicon.most_common(10)
    # chat_data['important_words'] = tg.important_words2.most_common(30)
    # tg.inverted_index

    chat_data['important_words_md'] = pd.DataFrame(tg.important_words2.most_common(30), columns=['Слово', 'Популярность']).set_index('Слово').round(3).to_markdown()

    # хитмап

    day_hour = tg.statWeekdayHour()
    df = pd.DataFrame(day_hour.values(), index=day_hour.keys())
    df = df.unstack().fillna(0)
    df = 100*df/df.sum().sum()
    # df = 100*df.div(df.sum(axis=1), axis=0)
    df.columns = [a[1] for a in df.columns.tolist()]
    sns.heatmap(df, cmap='RdYlGn_r', linewidths=0.5).set_title(f'Когда люди пишут в чате: {tg.chat_name}')

    chat_data['weekday_hour'] = df
    chat_data['weekday_hour_fig'] = f'{tg.chat_id}-weekday_hour.png'
    plt.savefig(os.path.join(output_path, chat_data['weekday_hour_fig']))

    # сообщений по неделям

    week = tg.statMsgByPeriod()
    df = pd.DataFrame(week.values(), index=week.keys(), columns=['Количество сообщений в неделю'])
    df.index.name = (('Год', 'Неделя'))
    df.plot()

    chat_data['msg_by_week'] = df
    chat_data['msg_by_week_fig'] = f'{tg.chat_id}-msg_by_week.png'
    plt.grid()

    plt.title('Количество сообщений по неделям')
    plt.xlabel('Неделя')
    plt.savefig(os.path.join(output_path, chat_data['msg_by_week_fig']))

    # Пользователей по неделям

    users = tg.statByUser().keys()
    df = pd.DataFrame(users, columns=['Год', 'Неделя', 'Имя пользователя'])
    df.groupby(['Год', 'Неделя']).count().plot()

    chat_data['users_by_week'] = df
    chat_data['users_by_week_fig'] = f'{tg.chat_id}-users_by_week.png'
    plt.grid()
    plt.title('Количество активных пользователей по неделям')
    plt.xlabel('Неделя')

    plt.savefig(os.path.join(output_path, chat_data['users_by_week_fig']))

    # Активные пользователи

    topUsers = tg.statTopUser().most_common(10)
    chat_data['top_users'] = topUsers
    chat_data['top_users_fig'] = f'{tg.chat_id}-top_users.png'

    df = pd.DataFrame(topUsers, columns=['Имя пользователя', 'Количество сообщений']).set_index('Имя пользователя')
    df.sort_values(by='Количество сообщений').plot(kind='barh')

    plt.title('Активные пользователи')
    plt.tight_layout()
    plt.grid(axis='x')

    plt.savefig(os.path.join(output_path, chat_data['top_users_fig']))

    # создание текстового описания

    md_list = f'''---
    title: "Анализ чата: {chat_data['chat_name']} - id: {chat_data['chat_id']}"
    description: ""
    date: {datetime.datetime.now().strftime ("%Y-%m-%dT%H:%M:%S+07:00")}
    images: []
    audio: []
    videos: []
    series: []
    tags: []
    draft: true
    private: false
    ---


    '''.splitlines()

    for key in chat_data.keys():
        print(key)

    tmp = [
        f"## Анализ чата {chat_data['chat_name']}",
        '',
        '### Количество сообщений по неделям',
        '', 
        f"![]({chat_data['msg_by_week_fig']})", 
        '', 
        '### Количество активных пользователей по неделям',
        '', 
        f"![]({chat_data['users_by_week_fig']})", 
        '', 
        '### Периоды активности в чате',
        '', 
        f"![]({chat_data['weekday_hour_fig']})", 
        '', 
        '### Активные пользователи',
        '', 
        f"![]({chat_data['top_users_fig']})", 
        '', 
        f'### Важность слов чата (сумма TD/IDF топ-{tganalysis.TOP_TD_IDF} слов каждого сообщения)',
        '', 
        f"{chat_data['important_words_md']}", 
    ]

    md_list += tmp

    open(os.path.join(output_path, 'index.md'), 'w').write('\n'.join(md_list))

# %%
