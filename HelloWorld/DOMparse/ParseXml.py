#coding=utf-8
from xml.dom.minidom import parse
from HelloWorld.DOMparse import EditClass
from HelloWorld.DOMparse import LogicClass

class ParseXml:
    def __init__(self):
        pass

    def CreateScarpyProgram(self,xmldoc):
        #新建Scrapy爬虫框架
        #执行Scrapy创建命令


        #在Scarpy目录下创建xml文件
        scarpyXml = open('F:\\autoScrapy\\demo1\\demo1\\scrapy.xml','w')
        scarpyXml.write(xmldoc)
        scarpyXml.close()

        #解析xml文件，读取到内存
        doc=parse('F:\\autoScrapy\\demo1\\demo1\\scrapy.xml')
        root=doc.documentElement

        #引入程序编写类
        editClass = EditClass.EditClass()
        logicClass = LogicClass.LoginClass()

        scrapyName = root.getAttribute("name")
        itemsClassName = scrapyName[:1].upper() + scrapyName[1:].lower() + "Item"

        #xml中获取item
        items=root.getElementsByTagName("items")[0]
        ItemArr = []
        for item in items.getElementsByTagName("item"):
            ItemArr.append(item.childNodes[0].data)

        #-------item.py文件编写------#
        #item类头部编写
        itemsPyStr = editClass.addVar(0,"import scrapy")
        itemsPyStr = itemsPyStr + editClass.addClassAndParams(itemsClassName, "scrapy.Item")
        #item方法主体编写
        itemsPyStr = itemsPyStr + logicClass.itemsScrapyField(ItemArr)
        print(itemsPyStr)

        #写入文件
        itemPyFile = open('F:\\autoScrapy\\demo1\\demo1\\items.py','w')
        itemPyFile.write(itemsPyStr)
        itemPyFile.close()


        #xml中获取spider
        spider = root.getElementsByTagName("spider")[0]
        name = spider.getElementsByTagName('name')[0]
        start_urls = spider.getElementsByTagName('start_urls')[0]
        allowed_domains = spider.getElementsByTagName('allowed_domains')[0]
        start_url = []
        allowed_domain = []
        start_url.append(start_urls.childNodes[0].data)
        allowed_domain.append(allowed_domains.childNodes[0].data)

        #获取解析方法内容
        parse1 = spider.getElementsByTagName('parse')[0]
        ##获取相应内容的xpath
        response = spider.getElementsByTagName('response')[0]
        responseXpath = response.getElementsByTagName('xpath')[0]
        responseXpathStr = responseXpath.childNodes[0].data
        #print(responseXpathStr)
        ##获取每个item对应的xpath
        xpaths = parse1.getElementsByTagName('xpaths')[0]
        xpathsArr = xpaths.getElementsByTagName('xpath')
        itemArr = []
        xpathArr = []
        for xpath in xpathsArr:
            itemArr.append(xpath.getAttribute("item"))
            xpathArr.append(xpath.childNodes[0].data)

        #-------spider.py文件编写------#
        #编写spider依赖
        spiderImportStr = editClass.addVar(0,"import scrapy")
        spiderImportStr = spiderImportStr + editClass.addVar(0,"from "+ scrapyName +".items import " + itemsClassName)
        #编写spider类初始化头部
        spiderImportStr = spiderImportStr + editClass.addSpiderClass("spiderTest", name.childNodes[0].data, allowed_domain, start_url)
        #编写parse解析方法
        spiderImportStr = spiderImportStr + editClass.addDefAndparam("parse",["self","response"])
        #编写解析方法头部
        spiderImportStr = spiderImportStr + editClass.addVar(3,"entity = response.xpath('"+ responseXpathStr +"')")
        spiderImportStr = spiderImportStr + editClass.addVar(3,"item = "+ itemsClassName +"()")
        #编写内容获取主体
        spiderImportStr = spiderImportStr + logicClass.itemsAndXpaths(2,itemArr,xpathArr)
        #编写内容打印
        spiderImportStr = spiderImportStr + editClass.addVar(3,"yield item")
        print(spiderImportStr)

        #写入文件
        spiderFile = open('F:\\autoScrapy\\demo1\\demo1\\spiders\\spider.py','w')
        spiderFile.write(spiderImportStr)
        spiderFile.close()


