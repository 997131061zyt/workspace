# -*- coding=utf-8 -*-
# @FileName  :excel.py
# @Time      :2020/10/24 19:06
# @Author    :zyt

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
from matplotlib import font_manager
# 设置展示图表的内容字体，可以从Windows字体里面拷贝字体文件到当前文件目录
my_font = font_manager.FontProperties(fname=r'c:\windows\fonts\msyh.ttc')
month = 10


def read_excel():
    data_df = pd.read_excel(filepath, sheet_name='股份公司商品量')
    name_change = {'日期': 'date', '完成量': 'done_now', '月计划': 'plan', '同期完成量': 'done_yoy'}
    data_df = data_df.rename(columns=name_change)
    data_df['date'] = data_df['date'].apply(date)
    done_df = data_df.dropna()
    print(done_df)
    desc_df = done_df.describe()
    print(desc_df)
    print(data_df)

    fig = plt.figure(figsize=(12, 4))
    ax = fig.add_subplot(111)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.subplots_adjust(bottom=0.15)
    plt.plot(data_df['date'], data_df['done_now'], color='blue', linestyle='-', label='完成量')
    plt.plot(data_df['date'], data_df['plan'], color='purple', linestyle='-.', label='月度计划')
    plt.plot(data_df['date'], data_df['done_yoy'], color=r'green', linestyle='--', label='同期完成量')
    plt.gca().xaxis.set_major_formatter(mdate.DateFormatter('%m-%d'))
    plt.xticks(data_df['date'].values[::2])
    plt.yticks(np.linspace(35000, 50000, 4))
    plt.text(data_df['date'].iloc[-1], desc_df['plan'].loc['mean'], str(int(desc_df['plan'].loc['mean'])),
             ha='left', va='center', fontsize=12)
    plt.title('股份公司商品量2020年{}月运行图'.format(month), fontproperties=my_font, fontsize=14)
    plt.grid(alpha=0.5, linestyle='-.', axis='y')
    plt.legend(bbox_to_anchor=(0.5, -0.2), loc='lower center', ncol=3, prop=my_font).get_frame().set_linewidth(0.0)
    plt.show()
    fig.savefig('supply_total.png')


def date(para):
    delta = pd.Timedelta(str(para)+'days')
    time = pd.to_datetime('1899-12-30') + delta
    return time


if __name__ == '__main__':
    filepath = 'E:/工作/规划院/20201019周报/资源.xlsx'
    read_excel()
