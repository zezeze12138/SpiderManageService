#coding=utf-8
from xml.dom import minidom
from HelloWorld.DOMparse import EditClass
from HelloWorld.DOMparse import LogicClass
import os
import time
import zipfile

class CreateScrapyProgram:
    def __init__(self):
        pass

    #网站为ajax请求时调用的程序编写方法
    def CreateScrapyProgramAjax(self,xmldoc,programName):
        #创建项目
        #os.makedirs("F:\\autoScrapyCreate\\"+programName)
        os.chdir("F:\\autoScrapyCreate")
        createResult = os.system("scrapy startproject " + programName)
        print(createResult)
        #进入项目创建文件
        #os.chdir("F:\\autoScrapyCreate\\"+programName+"\\"+programName+"\\spiders")
        #createResult = os.system("scrapy startproject " + programName)


        #在Scarpy目录下创建xml文件
        ScrapyPath = "F:\\autoScrapyCreate\\"+ programName +"\\" + programName +"\\"
        print(ScrapyPath)
        scarpyXml = open(ScrapyPath+"scrapy.xml",'w')
        scarpyXml.write(xmldoc)
        scarpyXml.close()

        #解析xml文件，读取到内存
        #with open(ScrapyPath+"scrapy.xml",'r',encoding='utf8') as fh:
        doc=minidom.parse(ScrapyPath+"scrapy.xml")
        root=doc.documentElement

        #引入程序编写类
        editClass = EditClass.EditClass()
        logicClass = LogicClass.LoginClass()

        #编写类头
        scrapyName = root.getAttribute("name")
        itemsClassName = scrapyName[:1].upper() + scrapyName[1:].lower() + "Item"

        #xml中获取spider
        spider = root.getElementsByTagName("spider")[0]
        name = spider.getElementsByTagName('name')[0]

        #获取解析方法内容
        parse = spider.getElementsByTagName('parse')[0]
        ##获取相应内容的xpath
        response = spider.getElementsByTagName('response')[0]
        #获取爬虫类型
        type = response.getAttribute("type")

        #获取request
        responseRequest = response.getElementsByTagName('request')[0]
        responseRequestStr = responseRequest.childNodes[0].data
        #获取page
        responsePage = response.getElementsByTagName('page')[0]
        responsePageStr = responsePage.childNodes[0].data
        #获取data
        responseDatas = response.getElementsByTagName('datas')[0]
        responseDataArr = responseDatas.getElementsByTagName('data')
        dataArr = []
        for dataNode in responseDataArr:
            dataArr.append(dataNode.childNodes[0].data)
        #获取url
        responseUrl = response.getElementsByTagName('url')[0]
        responseUrlStr = responseUrl.childNodes[0].data

        ##获取每个item对应的xpath
        xpaths = parse.getElementsByTagName('xpaths')[0]
        xpathsArr = xpaths.getElementsByTagName('xpath')
        itemArr = []
        xpathArr = []
        for xpath in xpathsArr:
            itemArr.append(xpath.getAttribute("item"))
            xpathArr.append(xpath.childNodes[0].data)


        #xml中获取item
        #items=root.getElementsByTagName("items")[0]
        ItemArr = itemArr

        #-------item.py文件编写------#
        #item类头部编写
        itemsPyStr = editClass.addVar(0,"import scrapy")
        itemsPyStr = itemsPyStr + editClass.addClassAndParams(itemsClassName, "scrapy.Item")
        #item方法主体编写
        itemsPyStr = itemsPyStr + logicClass.itemsScrapyField(ItemArr)
        print(itemsPyStr)

        #写入文件
        itemPyFile = open(ScrapyPath + "items.py",'w')
        itemPyFile.write(itemsPyStr)
        itemPyFile.close()



        #-------spider.py文件编写------#
        #编写spider依赖
        spiderImportStr = editClass.addVar(0,"import scrapy")
        spiderImportStr = spiderImportStr + editClass.addVar(0,"from scrapy.selector import Selector")
        spiderImportStr = spiderImportStr + editClass.addVar(0,"from scrapy.http import Request")
        spiderImportStr = spiderImportStr + editClass.addVar(0,"import json")
        spiderImportStr = spiderImportStr + editClass.addVar(0,"from "+ scrapyName +".items import " + itemsClassName)
        #编写spider类初始化头部
        spiderImportStr = spiderImportStr + editClass.addSpiderClass("spiderTest", name.childNodes[0].data, [], [])


        #编写解析方法主体
        #编写start_requests解析方法
        spiderImportStr = spiderImportStr + editClass.addDefAndparam("start_requests",["self"])
        spiderImportStr = spiderImportStr + editClass.addVar(3,"page = '&"+ responsePageStr +"='")
        spiderImportStr = spiderImportStr + logicClass.forLogin(2,"i","range(0,30)")
        spiderImportStr = spiderImportStr + editClass.addVar(4,"url = '"+ responseRequestStr + "'")
        spiderImportStr = spiderImportStr + editClass.addVar(4,"url = url + page + str(i)")
        spiderImportStr = spiderImportStr + editClass.addVar(4,"yield Request(url, method='GET',callback=self.parse_model,encoding='utf-8')")
        #通过url请求页面
        spiderImportStr = spiderImportStr + editClass.addDefAndparam("parse_model",["self","response"])
        spiderImportStr = spiderImportStr + editClass.addVar(3,"result = json.loads(response.body)")
        #对data层数解析
        for i in range(0,len(dataArr)-1):
            spiderImportStr = spiderImportStr + editClass.addVar(3,"result = result.get('"+ dataArr[i] +"')")
        spiderImportStr = spiderImportStr + logicClass.ifelse(2,"if","result.get('"+ dataArr[len(dataArr)-1] +"') != None")
        spiderImportStr = spiderImportStr + logicClass.forLogin(3,"jsonData","result.get('"+ dataArr[len(dataArr)-1] +"')")
        spiderImportStr = spiderImportStr + editClass.addVar(5,"yield Request(jsonData.get('"+ responseUrlStr +"'),dont_filter=True,callback=self.parse_data)")
        #编写内容获取主体
        spiderImportStr = spiderImportStr + editClass.addDefAndparam("parse_data",["self","response"])
        spiderImportStr = spiderImportStr + editClass.addVar(3,"item = "+itemsClassName+"()")
        spiderImportStr = spiderImportStr + logicClass.itemsAndXpaths(2,itemArr,xpathArr)
        #编写内容打印
        spiderImportStr = spiderImportStr + editClass.addVar(3,"yield item")
        print(spiderImportStr)

        #写入文件
        spiderFile = open(ScrapyPath + "spiders\\spider.py",'w')
        spiderFile.write(spiderImportStr)
        spiderFile.close()

        #开启部署
        scrapydFile = open("F:\\autoScrapyCreate\\"+programName+'\\scrapy.cfg','w')
        scrapydStr = '[settings]\n' + 'default = '+ programName +'.settings\n'
        scrapydStr = scrapydStr + '[deploy:'+programName+']\n'+'url = http://localhost:6800/\n'
        scrapydStr = scrapydStr + 'project = ' + programName
        scrapydFile.write(scrapydStr)
        scrapydFile.close()


        #进行文件压缩
        startdir = "F:\\autoScrapyCreate\\"+programName  #要压缩的文件夹路径
        file_news = startdir +'.zip' # 压缩后文件夹的名字
        z = zipfile.ZipFile(file_news,'w',zipfile.ZIP_DEFLATED) #参数一：文件夹名
        for dirpath, dirnames, filenames in os.walk(startdir):
            fpath = dirpath.replace(startdir,'') #这一句很重要，不replace的话，就从根目录开始复制
            fpath = fpath and fpath + os.sep or ''#这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
            for filename in filenames:
                z.write(os.path.join(dirpath, filename),fpath+filename)
                print ('压缩成功')
        z.close()

        #返回压缩文件路径
        zipFilePath = "F:\\autoScrapyCreate\\"+programName+".zip"
        return zipFilePath