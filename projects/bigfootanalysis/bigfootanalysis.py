'''
Function:
    大脚怪目击数据分析
Author:
    Charles
微信公众号:
    Charles的皮卡丘
'''
import os
import csv
import folium
import matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from cutecharts.charts import Pie
from cutecharts.charts import Bar
from cutecharts.charts import Line
from cutecharts.charts import Radar
from matplotlib.animation import FFMpegWriter
matplotlib.rcParams['font.family'] = 'FangSong'


'''大脚怪目击数据分析'''
class BigFootAnalysis():
    def __init__(self):
        self.rootdir = os.path.split(os.path.abspath(__file__))[0]
        self.bigfoot_infos = self.load(os.path.join(self.rootdir, 'source/bigfoot.csv'))
    '''运行'''
    def run(self):
        # 大脚怪相关描述的词云和高频词统计
        word_counts = {}
        stopwords = open(os.path.join(self.rootdir, 'source/enstopwords.data'), 'r', encoding='utf-8').read().split('\n')
        for idx, item in enumerate(self.bigfoot_infos):
            if idx == 0: continue
            sentence = ''.join(item[1].split(':')[1:]).strip()
            for word in sentence.split(' '):
                if word in stopwords: continue
                word = word.lower().replace('[', '').replace(']', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '')
                if word in stopwords: continue
                if word in word_counts: word_counts[word] += 1
                else: word_counts[word] = 1
        self.drawwordcloud(word_counts, '大脚怪相关描述的词云')
        word_counts_top10 = dict(sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        self.drawbar(word_counts_top10, '大脚怪相关描述中高频词统计', '频次', '单词', '频次')
        # 每年观察到大脚怪的次数
        observe_year_counts = {}
        for idx, item in enumerate(self.bigfoot_infos):
            if idx == 0: continue
            try:
                year = str(int(item[3].split('T')[0].split('-')[0].strip()))
            except:
                continue
            if year in observe_year_counts: observe_year_counts[year] += 1
            else: observe_year_counts[year] = 1
        observe_year_counts.pop('2053')
        observe_year_counts = dict(sorted(observe_year_counts.items(), key=lambda x: x[0], reverse=False))
        self.drawdynamicline(observe_year_counts, '每年观察到大脚怪的次数.gif')
        # 每月观察到大脚怪的次数
        observe_month_counts = {}
        for idx, item in enumerate(self.bigfoot_infos):
            if idx == 0: continue
            try:
                month = item[3].split('T')[0].split('-')[1]
            except:
                continue
            if month in observe_month_counts: observe_month_counts[month] += 1
            else: observe_month_counts[month] = 1
        observe_month_counts = dict(sorted(observe_month_counts.items(), key=lambda x: x[0], reverse=False))
        self.drawdynamicline(observe_month_counts, '每月观察到大脚怪的次数.gif', '月份')
        # 一个月每个日期观察到大脚怪的次数
        observe_day_counts = {}
        for idx, item in enumerate(self.bigfoot_infos):
            if idx == 0: continue
            try:
                day = item[3].split('T')[0].split('-')[2]
            except:
                continue
            if day in observe_day_counts: observe_day_counts[day] += 1
            else: observe_day_counts[day] = 1
        observe_day_counts = dict(sorted(observe_day_counts.items(), key=lambda x: x[0], reverse=False))
        self.drawdynamicline(observe_day_counts, '一个月每个日期观察到大脚怪的次数.gif', '号')
        # 大脚怪目的地点分布
        locations = []
        for idx, item in enumerate(self.bigfoot_infos):
            if idx == 0: continue
            lat, lng = float(item[-2]), float(item[-1])
            locations.append((lat, lng))
        self.drawmap(locations, '大脚怪目的地点分布')
    '''画地图'''
    def drawmap(self, locations, title):
        world_map = folium.Map()
        incidents = folium.map.FeatureGroup()
        lats, lngs = [], []
        for lat, lng, in locations:
            if lng < -180: continue
            lats.append(lat)
            lngs.append(lng)
            incidents.add_child(folium.CircleMarker([lat, lng], radius=7, color='yellow', fill=True, fill_color='red', fill_opacity=0.4))
        world_map = folium.Map(location=[sum(lats) / len(lats), sum(lngs) / len(lngs)], zoom_start=5)
        world_map.add_child(incidents)
        world_map.save(title+'.html')
    '''词云'''
    def drawwordcloud(self, words, title):
        wc = WordCloud(background_color='white', max_words=2000, width=1920, height=1080, margin=5)
        wc.generate_from_frequencies(words)
        wc.to_file(title+'.png')
    '''画饼图'''
    def drawpie(self, data, title):
        chart = Pie(title)
        chart.set_options(labels=list(data.keys()))
        chart.add_series(list(data.values()))
        chart.render(title+'.html')
    '''柱状图'''
    def drawbar(self, data, title, series_name, x_label, y_label):
        chart = Bar(title)
        chart.set_options(labels=list(data.keys()), x_label=x_label, y_label=y_label)
        chart.add_series(series_name, list(data.values()))
        chart.render(title+'.html')
    '''画动态折线图'''
    def drawdynamicline(self, data, savepath, xlabel='年份', ylable='目击数量'):
        writer, fig = FFMpegWriter(), plt.figure()
        x_list, y_list = [], []
        with writer.saving(fig, savepath, 100):
            for key, value in data.items():
                x_list.append(key)
                y_list.append(value)
                plt.style.use('ggplot')
                plt.plot(x_list, y_list)
                plt.title(x_list[-1])
                plt.xticks(rotation=90)
                plt.xlabel(xlabel)
                plt.ylabel(ylable)
                plt.legend()
                plt.grid(True)
                writer.grab_frame()
                plt.pause(0.1)
                plt.clf()
                plt.cla()
    '''数据导入'''
    def load(self, filepath='source/bigfoot.csv'):
        fp = open(filepath, 'r', encoding='utf-8')
        csv_reader = csv.reader(fp)
        return csv_reader


'''run'''
if __name__ == '__main__':
    client = BigFootAnalysis()
    client.run()