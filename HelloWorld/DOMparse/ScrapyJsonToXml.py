# -*- coding: utf-8 -*-
import json
import xml.etree.ElementTree as ET
import re
import cgi
class ScrapyJsonToXml:
    def __init__(self):
        pass

    def ScrapyJsonToXmlModel1(self,json_result):
        #读取爬虫标签,item项目
        scrapy_items = json_result["spiderItemList"]

        #生成爬虫xml
        scrapyRoot = ET.Element("scrapy")
        scrapyRoot.attrib = {"name" : json_result["scrapyName"]}

        #  1.爬虫初始化部分
        spider = ET.SubElement(scrapyRoot,"spider")
        #爬虫名称
        spider_name = ET.SubElement(spider,"name")
        spider_name.text = json_result["spiderName"]
        #爬虫过滤域名
        spider_allowed_domains = ET.SubElement(spider,"allowed_domains")
        spider_allowed_domains.text = json_result["allowed_domains"]
        #爬虫起始地址
        spider_start_urls = ET.SubElement(spider,"start_urls")
        spider_start_urls.text = json_result["start_uls"]

        #  1.1.爬虫主逻辑部分
        spider_parse = ET.SubElement(spider,"parse")
        #页面urls位置
        spider_parse_reponse = ET.SubElement(spider_parse,"response")
        spider_parse_reponse_xpath = ET.SubElement(spider_parse_reponse,"xpath")
        spider_parse_reponse_xpath.text = json_result["response_urls"]
        #获取item内容与爬取链接
        spider_parse_xpaths = ET.SubElement(spider_parse,"xpaths")
        for item in scrapy_items:
            spider_parse_xpaths_xpath = ET.SubElement(spider_parse_xpaths,"xpath")
            spider_parse_xpaths_xpath.attrib = {"item" : item["item"]}
            spider_parse_xpaths_xpath.text = item["xpath"]

        # 2.爬虫item项目部分
        items = ET.SubElement(scrapyRoot,"items")
        for item in scrapy_items:
            items_item = ET.SubElement(items,"item")
            items_item.text = item["item"]

        scrapyXml = ET.ElementTree(scrapyRoot)
        self.indent(scrapyRoot)
        return str(ET.tostring(scrapyRoot),encoding="utf8")

    #该方法为网页是ajax方式时使用
    def ScrapyJsonToXmlModel2(self,json_result):
        #读取爬虫标签,item项目
        scrapy_items = json_result["spiderItemList"]

        #生成爬虫xml
        scrapyRoot = ET.Element("scrapy")
        scrapyRoot.attrib = {"name" : json_result["projectName"]}

        #  1.爬虫初始化部分
        spider = ET.SubElement(scrapyRoot,"spider")
        #爬虫名称
        spider_name = ET.SubElement(spider,"name")
        spider_name.text = json_result["scrapyName"]

        #  1.1.爬虫主逻辑部分
        spider_parse = ET.SubElement(spider,"parse")
        #页面urls位置
        spider_parse_reponse = ET.SubElement(spider_parse,"response")
        spider_parse_reponse_request = ET.SubElement(spider_parse_reponse,"request")
        #url_re = re.compile('&(?!\w{4};)')
        #requestUrl = url_re.sub('&amp;', json_result["request"])
        requestUrl = json_result["request"].replace("\&", "\&amp;")
        #requestUrl = cgi.escape(json_result["request"])
        spider_parse_reponse_request.text = requestUrl

        spider_parse_reponse_page = ET.SubElement(spider_parse_reponse,"page")
        spider_parse_reponse_page.text = json_result["page"]

        spider_parse_reponse_datas = ET.SubElement(spider_parse_reponse,"datas")
        datas = json_result["datas"].split(";")
        for data in datas:
            spider_parse_reponse_datas_data = ET.SubElement(spider_parse_reponse_datas,"data")
            spider_parse_reponse_datas_data.text = data

        spider_parse_reponse_url = ET.SubElement(spider_parse_reponse,"url")
        spider_parse_reponse_url.text = json_result["url"]

        #获取item内容与爬取链接
        spider_parse_xpaths = ET.SubElement(spider_parse,"xpaths")
        for item in scrapy_items:
            spider_parse_xpaths_xpath = ET.SubElement(spider_parse_xpaths,"xpath")
            spider_parse_xpaths_xpath.attrib = {"item" : item["item"]}
            spider_parse_xpaths_xpath.text = item["xpath"]

        scrapyXml = ET.ElementTree(scrapyRoot)
        self.indent(scrapyRoot,0)
        return str(ET.tostring(scrapyRoot),encoding="utf8")

    #xml格式美化
    def indent(self,elem, level):
        i = "\n" + level*"\t"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i