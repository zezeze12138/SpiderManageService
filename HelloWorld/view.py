# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse, FileResponse
from HelloWorld.DOMparse import ParseXml
import json
import xml.etree.ElementTree as ET
from HelloWorld import models
import tempfile
import string
import _thread
import time
import urllib
from django.core import serializers
import os
import zipfile
import uuid
from apscheduler.scheduler import Scheduler
from time import sleep

def hello(request):
    #resp = {'errorcode': 100, 'detail': 'Get success'}
    if(request.method == 'POST'):
        #获取请求体内容
        postBody = request.body
        #读取爬虫初始化信息
        json_result = json.loads(postBody)

    return JsonResponse(json_result)

#设置定时任务
def setTimingByProgramName(request):
    if(request.method == 'POST'):
        postBody = request.body
        print (postBody)
        postJson = json.loads(postBody)
        programList = postJson["programList"]
        timing = postJson["timing"]
        for i in range(len(programList)):
            models.ScrapyConfig.objects.filter(program=programList[i]).update(timing=timing)
        json_result = {"data":"success"}
    return JsonResponse(json_result)


#修改是否进行分类的状态
def chargeClassifyStatus(request):
    if(request.method == 'POST'):
        postBody = request.body
        print (postBody)
        postJson = json.loads(postBody)
        projectName = postJson["project"]
        isclassify = postJson["isclassify"]
        models.ScrapyConfig.objects.filter(program=projectName).update(isclassify=isclassify)
        json_result = {"data":"success"}
    return JsonResponse(json_result)

#新增爬虫配置，上传爬虫程序
def addScrapyConfigAndUploadProgram(request):
    if(request.method == 'POST'):
        projectName = request.POST.get("projectName", None)
        scrapyName = request.POST.get("scrapyName", None)
        firstTopic = request.POST.get("firstTopic", None)
        file = request.FILES.get("file", None)
        filename = os.path.join("F://autoScrapyTemp",file.name);
        fobj = open(filename,'wb');
        for chrunk in file.chunks():
            fobj.write(chrunk);
        fobj.close();
        z = zipfile.ZipFile('F://autoScrapyTemp/'+file.name, 'r')
        z.extractall(path=r"F://autoScrapy/")
        z.close()
        id = uuid.uuid1()
        obj = models.ScrapyConfig(id=id,program=projectName,scrapy=scrapyName,status='0',firstTopic=firstTopic)
        obj.save()
    json_result = {"data":"true"}
    return JsonResponse(json_result)


#查看爬虫运行状态
def getListJob(request):
    if(request.method == 'POST'):
        #获取请求体内容
        postBody = request.body
        print (postBody)
        postJson = json.loads(postBody)
        # requrl = "http://127.0.0.1:6800/listjobs.json?project="+postJson["project"]
        # req = urllib.request.Request(url=requrl)
        # print (req)
        # res_data = urllib.request.urlopen(req)
        # res = res_data.read()
        # print (res)
        scrapyRunHeartBeat(postJson["project"],"c7418ea862c011e9b4007c7635ec430b")
    json_result = {"data":"true"}

    return JsonResponse(json_result)

#部署爬虫
def deploySpider(request):
    if(request.method == 'POST'):
        postBody = request.body
        print (postBody)
        postJson = json.loads(postBody)
        projectName = postJson["project"]
        scrapyName = postJson["scrapy"]
        #进入爬虫项目
        projectcmd = 'F:/autoScrapy/'+projectName+'/'
        print (projectcmd)
        os.chdir(projectcmd)
        #部署前运行命令
        deploycmd = 'scrapyd-deploy -l'
        os.system(deploycmd)
        #运行部署命令:scrapyd-deploy 部署名称 -p 项目名称
        deploySpideCmd = 'scrapyd-deploy '+ projectName + ' -p ' + projectName
        os.system(deploySpideCmd)
        print (deploycmd)
        os.system(deploycmd)
        #发送请求，查看是否部署成功
        requrl = "http://127.0.0.1:6800/listprojects.json"
        req = urllib.request.Request(url=requrl)
        print (req)
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        #获取返回结果，更新数据库状态
        result = eval(str(res, encoding = "utf-8"))
        status = result["status"]
        #如果部署成功，则将数据库状态设置为1：已部署
        if status == 'ok':
            models.ScrapyConfig.objects.filter(program=projectName).update(status='1')

    json_result = {"data":str(res, encoding = "utf-8")}
    return JsonResponse(json_result)

#删除爬虫部署
def deleteSpider(request):
    if(request.method == 'POST'):
        #获取请求体内容
        postBody = request.body
        print (postBody)
        postJson = json.loads(postBody)
        postD = {"project":postJson["project"]}
        postData = bytes(urllib.parse.urlencode(postD).encode('utf-8'))
        #postData = parse.urlencode(str(postBody)).encode('utf-8')
        print (postBody)
        requrl = "http://127.0.0.1:6800/delproject.json"
        req = urllib.request.Request(url=requrl,data=postData)
        print (req)
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        #获取返回结果，更新数据库状态
        result = eval(str(res, encoding = "utf-8"))
        status = result["status"]
        #如果删除成功，则将数据库状态设置为0：未部署
        if status == 'ok':
            models.ScrapyConfig.objects.filter(program=postJson["project"]).update(status='0')
    json_result = {"data":str(res, encoding = "utf-8")}
    return JsonResponse(json_result)

#启动爬虫
def startSpider(request):
    if(request.method == 'POST'):
        #获取请求体内容
        postBody = request.body
        print (postBody)
        postJson = json.loads(postBody)
        postD = {"project":postJson["project"],"spider":postJson["spider"]}
        postData = bytes(urllib.parse.urlencode(postD).encode('utf-8'))
        #postData = parse.urlencode(str(postBody)).encode('utf-8')
        print (postBody)
        requrl = "http://127.0.0.1:6800/schedule.json"
        req = urllib.request.Request(url=requrl,data=postData)
        print (req)
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        #获取返回结果，如果启动成功，则进行心跳检测
        result = eval(str(res, encoding = "utf-8"))
        status = result["status"]
        if status == 'ok':
            jobId = result["jobid"]
            #心跳检测线程
            try:
                _thread.start_new_thread(scrapyRunHeartBeat, (postJson["project"],jobId))
            except:
                print("Error: unable to start thread")

    json_result = {"data":str(res, encoding = "utf-8")}
    return JsonResponse(json_result)

#删除爬虫配置
def deleteConfig(request):
    if(request.method == 'POST'):
        postBody = request.body
        print (postBody)
        postJson = json.loads(postBody)
        projectName = postJson["project"]
        models.ScrapyConfig.objects.filter(program=projectName).delete()
    json_result = {"data":"success"}
    return JsonResponse(json_result)

#获取爬虫所爬item列表
def getItemListByScrapyName(request):
    if(request.method == 'GET'):
        scrapyName = request.GET["scrapyName"]
        obj = models.Storage.objects.filter(scrapy=scrapyName)
        data = json.loads(serializers.serialize("json", obj))
    json_result = {"data":""}
    return JsonResponse(json_result)



#获取爬虫配置列表
def getScrapyConfigList(request):
    obj = models.ScrapyConfig.objects.all()
    data = json.loads(serializers.serialize("json", obj))
    json_result = {"data":data}
    return JsonResponse(json_result)

#爬取数据，返回结果集mangoDB
def SpiderData(request):
    if(request.method == 'POST'):
        #获取请求体内容
        postBody = request.body
        #读取爬虫初始化信息
        json_result = json.loads(postBody)
        xmldoc = editScarpyXml(json_result)
        print (xmldoc)
        #解析爬虫xml创建爬虫程序
        EditScarpyProgram = ParseXml.ParseXml()
        EditScarpyProgram.CreateScarpyProgram(xmldoc)
        #执行爬虫程序，返回结果集mangoDB


    json_result = {"function":"spiderData"}
    return JsonResponse(json_result)

#下载xml文件
def DownScrapyXml(request):
    if(request.method == 'POST'):
        xmlStr = request.body
        print ("*****************")
        print (xmlStr)
        print ("*****************")
        #file = open('F:\scrapy.xml','rb')
        file_name = 'scrapy' + '.xml'
        # 将文件下载下来，默认下载到下载目录下
        tempFile = tempfile.NamedTemporaryFile()
        tempFile.write(xmlStr)
        # 确保string立即写入文件
        tempFile.flush()
        # 将文件读取指针返回到文件开头位置
        tempFile.seek(0)
        response = HttpResponse(tempFile)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
    return response
    #json_result = {"asdasd":"asdasd"}
    #return JsonResponse(json_result)

#返回创建的xml文件字符串
def CreateScrapyXml(request):
    if(request.method == 'POST'):
        #获取请求体内容
        postBody = request.body
        #读取爬虫初始化信息
        json_result = json.loads(postBody)
        xmldoc = editScarpyXml(json_result)
        scrapyJson = {"json":xmldoc}
        return JsonResponse(scrapyJson)

#输入json，创建xml
def editScarpyXml(json_result):

    #读取爬虫标签
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

    #  2.爬虫item项目部分
    items = ET.SubElement(scrapyRoot,"items")
    for item in scrapy_items:
        items_item = ET.SubElement(items,"item")
        items_item.text = item["item"]

    scrapyXml = ET.ElementTree(scrapyRoot)
    indent(scrapyRoot)
    return str(ET.tostring(scrapyRoot),encoding="utf8")


def indent(elem, level=0):
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

#爬虫状态心跳监测
def scrapyRunHeartBeat(projectName,jobId):
    while True:
        time.sleep(1)
        requrl = "http://127.0.0.1:6800/listjobs.json?project="+projectName
        req = urllib.request.Request(url=requrl)
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        result = eval(str(res, encoding = "utf-8"))
        newStatus = scrapyStatusNow(result,jobId)
        if newStatus == 3:
            #修改数据库配置表状态为正在启动
            models.ScrapyConfig.objects.filter(program=projectName).update(status='3',jobId=jobId)
        if newStatus == 2:
            #修改数据库配置表状态为正在运行
            models.ScrapyConfig.objects.filter(program=projectName).update(status='2',jobId=jobId)
        if newStatus == 1:
            #修改数据库配置表状态为爬取完成，回到“已部署状态”
            models.ScrapyConfig.objects.filter(program=projectName).update(status='1',jobId='')
            break

#爬虫状态检查判断，如果是预备状态返回：1  运行状态返回：2   完成返回：3
def scrapyStatusNow(data,jobId):
    #是否在等待队列存在
    if len(data["pending"]):
        for pending in data["pending"]:
            if pending["id"] == jobId:
                print("pending:----------------")
                return 3
    #是否在运行队列存在
    if len(data["running"]):
        for running in data["running"]:
            if running["id"] == jobId:
                print("running:----------------")
                return 2
    #是否在完成队列存在
    if len(data["finished"]):
        for finished in data["finished"]:
            if finished["id"] == jobId:
                print("finished:----------------")
                return 1

#定时任务，轮询需要运行的爬虫，时间间隔1分钟
#精度为1分钟，获取到运行的爬虫名称后，将爬虫放入线程，推迟两分钟后运行，避免多次启动爬虫
sched = Scheduler()
@sched.interval_schedule(seconds=60)
def my_task1():
    print('定时任务1开始\n')
    nowtime = time.strftime("%H:%M",time.localtime(time.time()))
    obj = models.ScrapyConfig.objects.exclude(timing='').filter(timing__isnull=False)
    data = json.loads(serializers.serialize("json", obj))
    for i in range(len(data)):
        if nowtime == data[i]["fields"]["timing"]:
            programName = data[i]["fields"]["program"]
            spiderName = data[i]["fields"]["scrapy"]
            print(programName)
            print(spiderName)
            try:
                _thread.start_new_thread(startSpider, (programName,spiderName))
            except:
                print("Error: unable to start thread")
    print(nowtime)
    print('定时任务1结束\n')

sched.start()


#启动爬虫方法
def startSpider(programName,spiderName):
    #推迟两分钟后运行
    time.sleep(120)
    #获取请求体内容
    postD = {"project":programName,"spider":spiderName}
    postData = bytes(urllib.parse.urlencode(postD).encode('utf-8'))
    requrl = "http://127.0.0.1:6800/schedule.json"
    req = urllib.request.Request(url=requrl,data=postData)
    print (req)
    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    #获取返回结果，如果启动成功，则进行心跳检测
    result = eval(str(res, encoding = "utf-8"))
    status = result["status"]
    if status == 'ok':
        jobId = result["jobid"]
        #心跳检测线程
        try:
            _thread.start_new_thread(scrapyRunHeartBeat, (programName,jobId))
        except:
            print("Error: unable to start thread")