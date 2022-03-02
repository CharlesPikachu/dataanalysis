'''
Function:
    各国纸面实力对比
Author:
    Charles
微信公众号:
    Charles的皮卡丘
'''
import os
import pickle
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
matplotlib.rcParams['font.family'] = 'FangSong'


'''各国纸面实力对比'''
class CompareCountries():
    def __init__(self, source_dir='source', output_dir='outputs', selected_countries=['中国', '美国', '俄罗斯联邦', '法国', '英国']):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.selected_countries = selected_countries
        self.touchdir(output_dir)
        self.country_to_color = {
            '中国': 'red', 
            '美国': 'yellow', 
            '俄罗斯联邦': 'lime', 
            '法国': 'cyan', 
            '英国': 'darkviolet', 
            '德国': 'thistle', 
            '日本': 'deeppink', 
            '印度': 'skyblue', 
            '意大利': 'orange', 
            '加拿大': 'tan', 
            '大韩民国': 'coral',
        }
        if self.selected_countries is None: self.selected_countries = list(self.country_to_color.keys())
        self.item_to_figcfg = {
            'gdp': ['单位: 亿美元', '{}年五常GDP对比' if len(self.selected_countries) == 5 else '{}年各国GDP对比'],
            'gdpoil': ['单位: 2011年不变价购买力平价美元/千克石油当量', '{}年五常GDP单位能源消耗对比' if len(self.selected_countries) == 5 else '{}年各国GDP单位能源消耗对比'],
            'gdpavg': ['单位: 现价国际元', '{}年五常人均GDP对比' if len(self.selected_countries) == 5 else '{}年各国人均GDP对比'],
            '10%': ['单位: 百分比', '{}年五常最高10%占有收入份额对比' if len(self.selected_countries) == 5 else '{}年各国最高10%占有收入份额对比'],
            'military': ['单位: 占中央政府支出的百分比', '{}年五常军费对比' if len(self.selected_countries) == 5 else '{}年各国军费对比'],
            'population': ['单位: 人', '{}年五常人口对比' if len(self.selected_countries) == 5 else '{}年各国人口对比'],
            'citypopulation': ['单位: 人', '{}年五常人口超过100万的城市群中的人口对比' if len(self.selected_countries) == 5 else '{}年各国人口超过100万的城市群中的人口对比'],
            'sci': ['单位: 篇', '{}年五常科技期刊文章对比' if len(self.selected_countries) == 5 else '{}年各国科技期刊文章对比'],
            'gini': ['单位: 百分比', '{}年五常基尼系数对比' if len(self.selected_countries) == 5 else '{}年各国基尼系数对比'],
            'co2': ['单位: 人均公吨数', '{}年五常二氧化碳排放量对比' if len(self.selected_countries) == 5 else '{}年各国二氧化碳排放量对比'],
            'powerconsumption': ['单位: 人均千瓦时', '{}年五常耗电量对比' if len(self.selected_countries) == 5 else '{}年各国耗电量对比'],
            'oilprice': ['单位: 美元', '{}年五常汽油的市场价格对比' if len(self.selected_countries) == 5 else '{}年各国汽油的市场价格对比'],
            'researcher': ['单位: 人/每百万人', '{}年五常研究人员数量对比' if len(self.selected_countries) == 5 else '{}年各国研究人员数量对比'],
            'traveller': ['单位: 人', '{}年五常国际旅游入境人数对比' if len(self.selected_countries) == 5 else '{}年各国国际旅游入境人数对比'],
            'recyclepower': ['单位: 千瓦时', '{}年五常可再生能源发电量(不包括水电)对比' if len(self.selected_countries) == 5 else '{}年各国可再生能源发电量(不包括水电)对比'],
            'forest': ['单位: 平方公里', '{}年五常森林面积对比' if len(self.selected_countries) == 5 else '{}年各国森林面积对比'],
            'debt': ['单位: 现价美元', '{}年五常外债总额存量对比' if len(self.selected_countries) == 5 else '{}年各国外债总额存量对比'],
            'immigrant': ['单位: 人', '{}年五常移民对比' if len(self.selected_countries) == 5 else '{}年各国移民对比'],
            'reserve': ['单位: 现价美元', '{}年五常总储备(包括黄金)对比' if len(self.selected_countries) == 5 else '{}年各国总储备(包括黄金)对比'],
        }
    '''运行'''
    def run(self):
        for filename in os.listdir(self.source_dir):
            if not filename.endswith('.pkl'): continue
            filepath = os.path.join(self.source_dir, filename)
            data = self.loaddata(filepath)
            item_name = filename.split('.')[0]
            self.visualization(data, item_name)
    '''导入数据'''
    def loaddata(self, filepath):
        return pickle.load(open(filepath, 'rb'))
    '''新建文件夹'''
    def touchdir(self, dirname):
        if not os.path.exists(dirname):
            os.mkdir(dirname)
            return False
        return True
    '''可视化'''
    def visualization(self, data, item_name):
        writer, fig, savepath = FFMpegWriter(), plt.figure(), os.path.join(self.output_dir, self.item_to_figcfg[item_name][1].format('历')+'.gif')
        formatted_data = {}
        for country in self.selected_countries:
            for item in data[country]:
                value, year = item
                if year in formatted_data:
                    formatted_data[year].update({country: value})
                else:
                    formatted_data[year] = {country: value}
        with writer.saving(fig, savepath, 100):
            for year, country_info in formatted_data.items():
                x_list, y_list, color_list = [], [], []
                country_info = dict(sorted(country_info.items(), key=lambda x: x[1], reverse=False))
                for name, value in country_info.items():
                    x_list.append(name)
                    y_list.append(value)
                    color_list.append(self.country_to_color[name])
                if sum(y_list) == 0.: continue 
                plt.barh(x_list, y_list, color=color_list)
                plt.title(self.item_to_figcfg[item_name][1].format(year))
                plt.xlabel(self.item_to_figcfg[item_name][0])
                writer.grab_frame()
                plt.pause(0.1)
                plt.clf()
                plt.cla()


'''run'''
if __name__ == '__main__':
    # 五常
    client = CompareCountries()
    client.run()
    # 各国
    client = CompareCountries(selected_countries=None)
    client.run()