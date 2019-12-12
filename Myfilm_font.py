"""
应对猫眼字体反爬,获取电影票房
"""

import requests
from scrapy import Selector
import re
from fontTools.ttLib import TTFont
import json
import time


class MyfilmBox():
    def __init__(self):
        self.url = "https://maoyan.com/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"}

    def get_url(self, url):
        html = requests.get(url, headers=self.headers).text
        return html

    def parse(self, html):
        item = dict()
        selector = Selector(text=html)
        li_list = selector.xpath("//ul[@class='ranking-wrapper ranking-box']/li")
        for li in li_list:
            item["title"] = li.xpath("./a/span[@class='normal-link']/span[@class='ranking-movie-name']/text("
                                     ")").extract_first()
            if item["title"] is None:
                item["title"] = li.xpath("./a/div[2]//span[@class='ranking-top-moive-name']/text()").extract_first()
            item["box"] = li.xpath("./a/span[@class='normal-link']/span[@class='ranking-num-info']//text()").extract()
            item["box"] = "".join([i.strip() for i in item["box"] if len(i) > 0])

            if item["box"] == "":
                item["box"] = li.xpath("./a/div[2]/div/p//text()").extract()
                item["box"] = "".join([i.strip() for i in item["box"] if len(i) > 0])
            yield item

    def get_font(self, html):
        """
        获取字体
        :return:
        """
        font_url = re.findall("//(.*?).woff", html)
        font_url = "http://" + font_url[0] + ".woff"
        # 可以发现字体地址每次都不一样,是变化的
        print(font_url)
        resp = requests.get(font_url, headers=self.headers)
        with open("./word.woff", "wb") as f:
            f.write(resp.content)
        # ----------------------------------------------
        font = TTFont("./word.woff")
        xml = font.saveXML("./word.xml")  # 保存xml文件
        name = font.getGlyphOrder()  # --->获取新unicode编码
        num = []  # --->用于存储新字体真实对应数字

        # 读取参考字体的坐标信息(提前下载一份,并通过fontcreator查看字体对应关系)
        base_font = TTFont("./word_base.woff")
        base_name = base_font.getGlyphOrder()
        """
        结果为:
        base_name = ['glyph00000', 'x', 'uniE1C0', 'uniF1A3', 'uniEF8B', 'uniE180', 'uniE7D2', 'uniEE9C', 'uniE454', 'uniF885', 'uniEF1E', 'uniF201']
        """
        base_num = [5, 9, 3, 1, 2, 8, 4, 6, 7, 0]  # --->参考真实字体

        # 获取新的字体的坐标信息,并与参考字体坐标信息对比
        # 逐个获取新生字体的坐标信息列表
        for j in range(2, len(name)):
            coordinate = font["glyf"][name[j]].coordinates
            # 逐个遍历参考字体,并获取其坐标列表,然后与新生字体坐标信息列表进行对比
            for i in range(2, len(base_name)):
                base_coordinate = base_font["glyf"][base_name[i]].coordinates
                # 由于5,9,3三个数字前面坐标相识度比较大,所有需要比较的坐标信息要比其他数字的要多才准确(此次比较30次),因此单独提出来
                if base_name[i] == 'uniE1C0' or base_name[i] == 'uniF1A3' or base_name[i] == 'uniEF8B':
                    count = 0
                    # 字体坐标存在一定的差别,设置偏离值value,只要在允许的范围内,即认为是同一个字体
                    value1 = 150
                    for m in range(30):
                        xn, yn = coordinate[m]
                        base_xn, base_yn = base_coordinate[m]
                        if abs(xn - base_xn) < value1 and abs(yn - base_yn) < value1:
                            count += 1
                        else:
                            break
                        if count == 30:
                            # 当比较的次数达到预定值时,将参考字体坐标对应的数字,提取出来,与新字体坐标对应
                            num.append(base_num[i - 2])
                            break

                else:
                    count = 0
                    value2 = 50
                    for m in range(4):
                        xn, yn = coordinate[m]
                        base_xn, base_yn = base_coordinate[m]
                        if abs(xn - base_xn) < value2 and abs(yn - base_yn) < value2:
                            count += 1
                        else:
                            break
                        if count == 4:
                            num.append(base_num[i - 2])
                            break
        # ---------------------------------------------
        # 将字体unicode编码重构,从而与网页中的数据相匹配
        trs_name = [eval(r"u'\u" + i[3:] + "'") for i in name[2:]]
        return trs_name, num

    def main(self):
        num = []
        trs_name = []
        item = {}
        # 由于每次比较字体坐标信息时存在误差,不一定都能获得到正确的数据(数据可能会大于10或者小于10个)
        # 因此需要加以筛选,只有当获得的数据刚好等于10个的时候,才是正确的
        while not len(num) == 10:
            html = self.get_url(self.url)
            trs_name, num = self.get_font(html)
            print(trs_name)
            print(num)
            item = self.parse(html)
            time.sleep(2)
        for i in item:
            i = json.dumps(i, ensure_ascii=False)
            for j in range(len(num)):
                i = i.replace(trs_name[j], str(num[j]))
            print(i)


if __name__ == '__main__':
    spider = MyfilmBox()
    spider.main()
