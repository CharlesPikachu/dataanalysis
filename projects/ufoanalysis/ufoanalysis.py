'''
Function:
    UFO目击数据分析
Author:
    Charles
微信公众号:
    Charles的皮卡丘
'''
import os
import folium
import pickle
import matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from cutecharts.charts import Pie
from cutecharts.charts import Bar
from cutecharts.charts import Line
from cutecharts.charts import Radar
from matplotlib.animation import FFMpegWriter
matplotlib.rcParams['font.family'] = 'FangSong'


'''UFO目击数据分析'''
class UFOAnalysis():
    def __init__(self):
        self.rootdir = os.path.split(os.path.abspath(__file__))[0]
        self.ufo_infos = self.load(os.path.join(self.rootdir, 'source/ufos.pkl'))
    '''运行'''
    def run(self):
        # UFO目击数量随时间的变化
        ufo_number_by_year = {}
        for value in self.ufo_infos.values():
            year = value['datetime'].split(' ')[0].split('/')[-1]
            if year in ufo_number_by_year:
                ufo_number_by_year[year] += 1
            else:
                ufo_number_by_year[year] = 1
        ufo_number_by_year = dict(sorted(ufo_number_by_year.items(), key=lambda x: x[0], reverse=False))
        self.drawdynamicline(ufo_number_by_year, 'UFO目击数量随时间的变化.gif')
        # UFO出现的时间段分布
        ufo_number_period = {'0-3点': 0, '3-6点': 0, '6-9点': 0, '9-12点': 0, '12-15点': 0, '15-18点': 0, '18-21点': 0, '21-24点': 0}
        for value in self.ufo_infos.values():
            hour = int(value['datetime'].split(' ')[-1].split(':')[0])
            if hour in list(range(0, 3)) + [24]:
                ufo_number_period['0-3点'] += 1
            elif hour in list(range(3, 6)):
                ufo_number_period['3-6点'] += 1
            elif hour in list(range(6, 9)):
                ufo_number_period['6-9点'] += 1
            elif hour in list(range(9, 12)):
                ufo_number_period['9-12点'] += 1
            elif hour in list(range(12, 15)):
                ufo_number_period['12-15点'] += 1
            elif hour in list(range(15, 18)):
                ufo_number_period['15-18点'] += 1
            elif hour in list(range(18, 21)):
                ufo_number_period['18-21点'] += 1
            elif hour in list(range(21, 24)):
                ufo_number_period['21-24点'] += 1
        self.drawpie(ufo_number_period, 'UFO出现的时间段分布')
        # UFO出现的月份分布
        ufo_number_month = {}
        for month in range(1, 13):
            ufo_number_month[f'{month}'] = 0
        for value in self.ufo_infos.values():
            month = value['datetime'].split(' ')[0].split('/')[0]
            ufo_number_month[month] += 1
        ufo_number_month_new = {}
        for key, value in ufo_number_month.items():
            ufo_number_month_new[key + '月'] = value
        self.drawbar(ufo_number_month_new, 'UFO出现的月份分布', '目击数量', '月份', '目击数量')
        # UFO出现后持续的时长分布
        duration_distribute = {'1分钟以内': 0, '1-5分钟': 0, '5-10分钟': 0, '10分钟以上': 0}
        for value in self.ufo_infos.values():
            if value['duration'].strip():
                duration = int(value['duration'].split('.')[0].strip('`'))
            else:
                continue
            if duration < 60:
                duration_distribute['1分钟以内'] += 1
            elif duration >= 60 and duration < 300:
                duration_distribute['1-5分钟'] += 1
            elif duration >= 300 and duration < 600:
                duration_distribute['5-10分钟'] += 1
            elif duration >= 600:
                duration_distribute['10分钟以上'] += 1
        self.drawpie(duration_distribute, 'UFO出现后持续的时长分布')
        # UFO出现的国家分布
        country_distribution = {}
        for value in self.ufo_infos.values():
            country = value['country']
            try:
                country = {'us': '美国', 'gb': '英国', 'ca': '加拿大', 'au': '澳大利亚', 'de': '德国'}[country]
            except:
                country = '其他国家或地区'
            if country in country_distribution: country_distribution[country] += 1
            else: country_distribution[country] = 1
        self.drawpie(country_distribution, 'UFO出现的国家分布')
        # UFO的形状分布
        shape_distribution = {}
        for value in self.ufo_infos.values():
            shape = value['shape']
            if shape in shape_distribution: shape_distribution[shape] += 1
            else: shape_distribution[shape] = 1
        shape_distribution = dict(sorted(shape_distribution.items(), key=lambda x: x[1], reverse=True)[:8])
        self.drawpie(shape_distribution, 'UFO的形状分布')
        # 关于UFO的目击者描述词云
        stopwords = open(os.path.join(self.rootdir, 'source/enstopwords.data'), 'r', encoding='utf-8').read().split('\n')
        word_freq = {}
        for value in self.ufo_infos.values():
            desp = value['desp']
            for word in desp.split(' '):
                if word in stopwords: continue
                word = word.lower().replace('[', '').replace(']', '').replace('.', '').replace(',', '').replace('(', '').replace(')', '')
                if word in stopwords: continue
                if word in word_freq: word_freq[word] += 1
                else: word_freq[word] = 1
        self.drawwordcloud(word_freq, '关于UFO的目击者描述词云')
        # UFO目击地点分布可视化
        locations = []
        for value in self.ufo_infos.values():
            location = value['location']
            try:
                locations.append((float(location[0]), float(location[1])))
            except:
                continue
        self.drawmap(locations, 'UFO目击地点分布可视化')
    '''画地图'''
    def drawmap(self, locations, title):
        world_map = folium.Map()
        incidents = folium.map.FeatureGroup()
        lats, lngs = [], []
        for lat, lng, in locations:
            lats.append(lat)
            lngs.append(lng)
            incidents.add_child(folium.CircleMarker([lat, lng], radius=5, color='yellow', fill=True, fill_color='red', fill_opacity=0.4))
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
                plt.plot(list(range(len(x_list))), y_list)
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
    def load(self, filepath='source/ufos.pkl'):
        fp = open(filepath, 'rb')
        return pickle.load(fp)


'''run'''
if __name__ == '__main__':
    client = UFOAnalysis()
    client.run()