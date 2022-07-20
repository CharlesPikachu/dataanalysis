'''
Function:
    央视新闻标题分析
Author:
    Charles
微信公众号:
    Charles的皮卡丘
'''
import os
import json
import jieba
from snownlp import SnowNLP
from wordcloud import WordCloud
from pyecharts.charts import Bar, Pie
from pyecharts import options as opts
from pyecharts.globals import ThemeType


'''画饼图'''
def drawpie(title, infos, savepath):
    pie = Pie(init_opts=dict(theme='westeros', page_title=title)).add(title, data_pair=tuple(zip(infos.keys(), infos.values())), rosetype='area')
    pie.set_global_opts(title_opts=opts.TitleOpts(title=title))
    pie.render(savepath)


'''画柱状图'''
def drawbar(title, data, savepath):
    bar = (Bar(init_opts=opts.InitOpts(theme=ThemeType.VINTAGE))
          .add_xaxis(list(data.keys()))
          .add_yaxis('', list(data.values()))
          .set_global_opts(xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-25)),
                           title_opts=opts.TitleOpts(title=title, pos_left='center'), legend_opts=opts.LegendOpts(orient='vertical', pos_top='15%', pos_left='2%')))
    bar.render(savepath)


'''生成词云'''
def generatewordcloud(infos, savepath):
    wc = WordCloud(background_color='white', font_path=os.path.join(os.path.split(os.path.abspath(__file__))[0], 'sources/font_cn.TTF'))
    result = wc.generate_from_frequencies(infos)
    result.to_file(savepath)


'''央视新闻标题分析'''
class YangshiTitleAnalysis():
    def __init__(self):
        fp = open(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'sources/basicinfos.json'), 'r', encoding='utf-8')
        self.article_infos = json.load(fp)
        fp.close()
    '''run'''
    def run(self):
        self.nlpanalysis()
        self.wordfreqstatistic()
    '''情感分析'''
    def nlpanalysis(self):
        nlp_dict = {'内容极度负面': 0, '内容较为负面': 0, '内容中性': 0, '内容较为正面': 0, '内容非常正面': 0}
        for title in self.article_infos.keys():
            score = SnowNLP(title).sentiments
            if score < 0.2:
                nlp_dict['内容极度负面'] += 1
            elif score >= 0.2 and score < 0.4:
                nlp_dict['内容较为负面'] += 1 
            elif score >= 0.4 and score < 0.6:
                nlp_dict['内容中性'] += 1 
            elif score >= 0.6 and score < 0.8:
                nlp_dict['内容较为正面'] += 1 
            else:
                nlp_dict['内容非常正面'] += 1
        drawbar('央视新闻标题情感分析', nlp_dict, '央视新闻标题情感分析.html')
    '''词频统计'''
    def wordfreqstatistic(self):
        wordfreq_dict = {}
        for title in self.article_infos.keys():
            words = jieba.cut(title)
            for word in words:
                word = word.strip()
                if not word or len(word) < 2: continue
                if word in wordfreq_dict:
                    wordfreq_dict[word] += 1
                else:
                    wordfreq_dict[word] = 1
        generatewordcloud(wordfreq_dict, '央视新闻标题高频词汇TOP10.png')
        wordfreq_dict = sorted(wordfreq_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        drawbar('央视新闻标题高频词汇TOP10', dict(wordfreq_dict), '央视新闻标题高频词汇TOP10.html')


'''run'''
if __name__ == '__main__':
    client = YangshiTitleAnalysis()
    client.run()