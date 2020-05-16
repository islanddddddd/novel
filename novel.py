# encoding=utf8
import os
import re
from bs4 import BeautifulSoup
import requests, sys, time
import json


class down(object):
    def __init__(self):
        self.server = "https://qxs.la"  # 网站地址
        self.target = "https://qxs.la/181241/"  # 小说地址
        self.title = ""  # 小说名字
        self.novel_class = ""  # 小说类型
        self.author = ""  # 小说作者
        self.desc = ""  # 小说简介

        self.names = []  # 章节名字
        self.urls = []  # 章节地址
        self.nums = []  # 章节总数

        self.write_flag = False

    """
    函数说明:获取章节下载链接
    """

    def get_chapters(self):
        req = requests.get(url=self.target)
        html = req.text

        soup = BeautifulSoup(html, "html.parser")
        self.title = soup.h1.a.text
        self.novel_class = soup.find_all('div', class_='f_l t_r w3')[0].text.replace('类型： ', '')
        self.author = soup.find_all('div', class_='f_l t_c w2')[0].text.replace('作 者：', '')
        self.desc = soup.find_all('div', class_='desc')[0].text
        self.desc = re.sub('.*简介：.* ', '', self.desc)
        self.desc = self.desc.replace('　　', '\n')

        chapters = soup.find_all('div', class_='chapter')
        a_soup = BeautifulSoup(str(chapters), "html.parser")
        a = a_soup.find_all('a')
        self.nums = len(a)
        for each in a:
            self.names.append(each.string)
            self.urls.append((self.server + each.get("href")))

    """
    函数说明:获取章节内容
    """

    def get_contents(self, target):
        maxTryNum = 30
        for tries in range(maxTryNum):
            try:
                req = requests.get(url=target)
                html = req.text
                soup = BeautifulSoup(html, "html.parser")
                texts = soup.find_all('div', id='content')
                # 去除杂质
                texts = texts[0].text.replace('　　', '\n\u3000\u3000')
                texts = re.sub('.*（全小说无弹窗）', '', texts)
                texts = texts.replace('www@22ff!com', '')
                # # 添加标记
                # texts=texts+"{'last':'"+"'}"
                return texts
            except:
                if tries < (maxTryNum - 1):
                    continue
                else:
                    print("Has tried %d times to access url %s, all failed!" % (maxTryNum, target))
                    break

    """
    函数说明:写入文件
    参数说明:
        name:章节名
        path:文件路径
        text:章节内容
        num:当前进度
    """

    def writer(self, name, path, text, num):
        # print(path)
        # 判断novel文件夹是否存在
        if not os.path.exists('novel'):
            os.mkdir('novel')
        # 判断分类文件夹存在,不存在就创建
        if not os.path.exists('novel/' + self.novel_class):
            os.mkdir('novel/' + self.novel_class)
        # 判断文件是否存在,不存在则写入小说简介和进度标记
        if not os.path.exists(path):
            with open(path, 'a', encoding='utf-8') as f:
                f.write('作者:' + self.author + '\n')
                f.writelines('简介:\n' + self.desc)
                f.write('\n\n')
                # 进度标记
                # f.write('{"now":"999"}')  # 不知道为啥找不到这个;知道为啥了,因为这是个if else语句,根本不执行else内容
                # f.write('{"now":"' + str(num) + '"}')
                f.write('{"now":"' + str(num) + '"}')

        # 若存在
        else:
            with open(path, 'rt') as f:
                last = f.readlines()[-1]
                last = int(json.loads(last)['now'])
                print('last:%d' % last)
                print('num:%d' % num)
                if num <= last:
                    return
        # 写入
        with open(path, 'a', encoding='utf-8') as f:
            f.write('\n' + name + '\n')
            f.writelines(text)
            f.write('\n\n')
            f.write('{"now":"' + str(num) + '"}')


if __name__ == "__main__":
    dl = down()
    dl.get_chapters()
    # print(dl.names)
    # print(dl.nums)
    # print(dl.names, dl.urls)
    print(dl.title + " 下载开始:")
    # print(dl.get_contents(dl.urls[0]))

    path = './novel/' + dl.novel_class + '/' + dl.title + '.txt'
    for i in range(dl.nums):
        print('开始下载%5d章' % (i + 1))  # 开始下载i+1章
        dl.writer(dl.names[i], path, dl.get_contents(dl.urls[i]), i)
        # sys.stdout.write("  已下载:%.3f" % float(i / dl.nums))   # 不管用
        # sys.stdout.write("\r" + dl.names[i] + " %.5f" % float(i / dl.nums)+"%")   # 不好用
        # sys.stdout.write("\r%-20s %-0.5f%% \t" % (dl.names[i], float(i / dl.nums)))  # 完成品
        # sys.stdout.flush()
        print("\r%-20s %-0.5f%% \t" % (dl.names[i], float(i / dl.nums)))  # print
        # print('-------------------------------------------')
    print("下载完成")
