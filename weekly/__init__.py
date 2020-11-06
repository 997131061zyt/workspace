# -*- coding=utf-8 -*-
# @FileName  :__init__.py.py
# @Time      :2020/10/19 19:54
# @Author    :zyt

from weekly.word import Word
from weekly.excel import Excel


def process(doc):
    doc.set_section(20.9, 29.6, 2.54, 2.54, 2.7, 2.7)
    text = '天然气销售情况'
    paragraph = doc.add_title_text(space_before=5, space_after=0, line_space=28, position=1)
    doc.add_run_text(paragraph, text, size=26, bold=False, underline=False, font_name='方正小标宋简体')

    text = '第{period}期'.format(period=92)
    paragraph = doc.add_title_text(space_before=0, space_after=0, line_space=28, position=1)
    doc.add_run_text(paragraph, text, size=16, bold=False, underline=False, font_name='方正小标宋简体')

    text = '资源采购部' + ' ' * 28
    paragraph = doc.add_title_text(space_before=13, space_after=13, line_space=20, position=3)
    doc.add_run_text(paragraph, text, size=16, bold=True, underline=True, font_name='宋体')
    text = '2020年09月25日'
    doc.add_run_text(paragraph, text, size=14, bold=True, underline=True, font_name='方正楷体_GBK')

    text = '一、天然气购销情况'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=False, underline=False, font_name='方正黑体简体')

    text = '（一）上周天然气购销运行情况'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=True, underline=False, font_name='方正楷体简体')

    text = '。'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=True, underline=False, font_name='方正仿宋简体')

    text = '（二）9月累计完成情况'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=True, underline=False, font_name='方正楷体简体')

    text = '。'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=True, underline=False, font_name='方正仿宋简体')

    text = '（三）采购与营销重点工作'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=True, underline=False, font_name='方正楷体简体')

    text = '。'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=True, underline=False, font_name='方正仿宋简体')

    text = '（四）管道开口情况'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=True, underline=False, font_name='方正楷体简体')

    text = '。'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=True, underline=False, font_name='方正仿宋简体')

    text = '二、天然气市场营销情况'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=False, underline=False, font_name='方正黑体简体')

    text = '（一）9月资源与储气库情况'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=True, underline=False, font_name='方正楷体简体')

    text = '1.天然气商品量'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=True, underline=False, font_name='方正仿宋简体')

    text = '9月份股份公司商品量计划128.44亿方，日均4.28亿方，月累计完成111.53亿方，日均完成4.46亿方，' \
           '超进度计划4.49亿方，日均超进度计划1797万方；同比增加2.95亿方，日均增加1179万方，增幅2.7%；' \
           '年累计完成1312.83亿方，为年计划的69.3%，欠年进度计划61.25亿方，同比减少1.53亿方，减幅0.1%。'
    paragraph = doc.add_para_text(space_before=0, space_after=0, line_space=28)
    doc.add_run_text(paragraph, text, size=16, bold=False, underline=False, font_name='方正仿宋简体')

    doc.document.save('E:/工作/规划院/20201019周报/weekly.docx')


if __name__ == '__main__':
    word = Word()
    excel = Excel()
    process(word, excel)
