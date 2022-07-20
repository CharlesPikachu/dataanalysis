'''
Function:
    微信公众号文章爬取
Author:
    Charles
微信公众号:
    Charles的皮卡丘
'''
import os
import time
import json
import pdfkit
import random
import requests
import warnings
warnings.filterwarnings('ignore')


'''配置文件'''
class Config():
    # 目标公众号标识
    biz = 'MTI0MDU3NDYwMQ=='
    # 微信登录后的一些标识参数
    pass_ticket = 'ini/qyRDrKDSowwYFEGuBJxaGC1shL+bhT9CVwM82lnpkbQ2zIHAf1ZilY7CUoIV'
    appmsg_token = '1174_Lujxdhlrc%2BwGB1o4mvp_E8yRdpFLTwIJ4Tmgrw~~'
    uin = 'MjI5MzgwNDM1OA=='
    key = 'f2f504c7132618556037a79efb4e13997ccc28d1a468ab87951301bea484b3821a1cb39bc4cdf066849e6234f8d5d2e07af04f33fe339d618c38828e281f6315c8e22739512a1b34b8a60bb483c61148425886b8ffe8bae74b73834404d4575c7e0c9fbce1c9880f1ad2970fc1cdf65c4f0bedc41650483bdb49af5eab378bc0'
    # 安装的wkhtmltopdf.exe文件路径
    wkhtmltopdf_path = r'C:\software\wkhtmltopdf\bin\wkhtmltopdf.exe'


'''微信公众号文章爬取类'''
class WechatArticles():
    def __init__(self, config, savedir='yangshi'):
        self.config = config
        self.savedir = savedir
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6304051b)',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.profile_url = 'https://mp.weixin.qq.com/mp/profile_ext'
        self.touchdir(self.savedir)
    '''外部调用'''
    def run(self):
        self.fetcharticlebasicinfos()
        self.downloadarticles()
    '''获取所有文章的基础信息'''
    def fetcharticlebasicinfos(self):
        # 打印提示信息
        self.logging('开始获取目标公众号的所有文章的基础信息')
        # 开始爬取文章基础信息
        article_infos = {}
        params = {
            'action': 'getmsg', '__biz': self.config.biz, 'f': 'json', 'offset': '0',
            'count': '10', 'is_ok': '1', 'scene': '', 'uin': self.config.uin,
            'key': self.config.key, 'pass_ticket': self.config.pass_ticket,
            'wxtoken': '', 'appmsg_token': self.config.appmsg_token, 'x5': '0', 
        }
        while True:
            response = requests.get(self.profile_url, params=params, headers=self.headers)
            response.encoding = 'utf-8'
            response_json = response.json()
            self.logging(response_json)
            can_msg_continue = response_json.get('can_msg_continue', '')
            next_offset = response_json.get('next_offset', 10)
            general_msg_list = json.loads(response_json.get('general_msg_list', '{}'))
            if 'list' not in general_msg_list:
                break
            params.update({'offset': next_offset})
            for item in general_msg_list['list']:
                app_msg_ext_info = item.get('app_msg_ext_info', {})
                if not app_msg_ext_info:
                    continue
                title = app_msg_ext_info.get('title', '')
                content_url = app_msg_ext_info.get('content_url', '')
                if title and content_url:
                    article_infos[title] = content_url
                if app_msg_ext_info.get('is_multi', '') == 1:
                    for article in app_msg_ext_info.get('multi_app_msg_item_list', []):
                        title = article.get('title', '')
                        content_url = article.get('content_url', '')
                        if title and content_url:
                            article_infos[title] = content_url
            if can_msg_continue != 1: 
                break
            else: 
                time.sleep(1+random.random())
            fp = open(os.path.join(self.savedir, 'basicinfos.json'), 'w', encoding='utf-8')
            json.dump(article_infos, fp)
            fp.close()
        # 保存数据
        fp = open(os.path.join(self.savedir, 'basicinfos.json'), 'w', encoding='utf-8')
        json.dump(article_infos, fp)
        fp.close()
        # 打印提示信息
        self.logging(f'成功获取目标公众号的所有文章的基础信息, 数量为{len(article_infos)}')
    '''下载所有文章'''
    def downloadarticles(self):
        # 打印提示信息
        self.logging('开始下载目标公众号里的所有文章')
        # 开始爬取
        fp = open(os.path.join(self.savedir, 'basicinfos.json'), 'r', encoding='utf-8')
        article_infos = json.load(fp)
        for key, value in article_infos.items():
            self.logging('正在抓取文章 ——> %s' % key)
            key = key.replace('\\', '').replace('/', '').replace(':', '').replace('：', '') \
                     .replace('*', '').replace('?', '').replace('？', '').replace('“', '')  \
                     .replace('"', '').replace('<', '').replace('>', '').replace('|', '_')
            try:
                pdfkit.from_url(value, os.path.join(self.savedir, key+'.pdf'), configuration=pdfkit.configuration(wkhtmltopdf=self.config.wkhtmltopdf_path))
            except:
                continue
        # 打印提示信息
        self.logging('已成功爬取目标公众号里的所有文章')
    '''logging'''
    def logging(self, msg, tip='INFO'):
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} {tip}]: {msg}')
    '''touchdir'''
    def touchdir(self, dirname):
        if not os.path.exists(dirname):
            os.mkdir(dirname)
            return False
        return True


'''run'''
if __name__ == '__main__':
    config = Config()
    client = WechatArticles(config)
    client.run()