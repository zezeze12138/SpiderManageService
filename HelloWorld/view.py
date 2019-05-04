# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse, FileResponse
from HelloWorld.DOMparse import ParseXml
from HelloWorld.DOMparse import ScrapyJsonToXml
from HelloWorld.DOMparse import CreateScrapyProgram
from HelloWorld.DOMparse import ScrapydModel
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

#爬虫服务器地址
SCRAPYD_IP = 'http://127.0.0.1:6800'
#爬虫程序存放地址
SCRAPY_PROGRAM_PATH = 'F:/autoScrapy'
#xml文件临时存放位置
XML_TEMP_PATH = 'F:/autoScrapyTemp'

def hello(request):
    #resp = {'errorcode': 100, 'detail': 'Get success'}
    if(request.method == 'POST'):
        #获取请求体内容
        postBody = request.body
        #读取爬虫初始化信息
        json_result = json.loads(postBody)

    return JsonResponse(json_result)

#删除爬虫配置
def deleteScrapyConfig(request):
    if(request.method == 'POST'):
        postBody = request.body
        print (postBody)
        postJson = json.loads(postBody)
        programName = postJson["programName"]
        status = postJson["status"]
        if status != '0':
            json_result = {"data":"false"}
            return JsonResponse(json_result)
        else:
            models.ScrapyConfig.objects.filter(program=programName).delete()
            json_result = {"data":"true"}
    return JsonResponse(json_result)

#通过xmlId生成爬虫程序，下载接口
def downloadScrapyProgramByXmlName(request):
    if(request.method == 'POST'):
        postBody = request.body
        print (postBody)
        postJson = json.loads(postBody)
        xmlId = postJson["xmlId"]
        programName = postJson["programName"]
        xmlPath = XML_TEMP_PATH + '/' + xmlId + '.xml'
        xmlfile=open(xmlPath,'rb')
        xmlStr = xmlfile.read()
        xmlfile.close()
        xmlStr = str(xmlStr, encoding = "utf8")
        print(xmlStr)
        #创建爬虫程序
        createScrapyProgram = CreateScrapyProgram.CreateScrapyProgram()
        zipfilePath = createScrapyProgram.CreateScrapyProgramAjax(xmlStr,programName)

        file=open(zipfilePath,'rb')
        response =HttpResponse(file)
        response['Content-Type']='application/octet-stream'
        response['Content-Disposition']='attachment;filename='+ programName +'.zip'
    return response


#上传爬虫xml文件，下载爬虫程序
def uploadXml(request):
    if(request.method == 'POST'):
        file = request.FILES.get("file", None)
        nPos=file.name.index('.')
        programName = str(file.name)[0:nPos]
        xmlId = str(uuid.uuid1())
        filename = os.path.join("F://autoScrapyTemp",xmlId+'.xml')
        fobj = open(filename,'wb');
        for chrunk in file.chunks():
            fobj.write(chrunk);
        fobj.close();
        json_result = {"data":xmlId,"programName":programName}
    return JsonResponse(json_result)


#创建爬虫程序
def createScrapyProgramAndDownload(request):
    if(request.method == 'POST'):
        #获取请求体内容
        postBody = request.body
        #获取参数
        json_result = json.loads(postBody)
        projectName = json_result["projectName"]
        scrapyForm = json_result["scrapyForm"]
        #生成爬虫xml
        scrapyProgramXml = ScrapyJsonToXml.ScrapyJsonToXml()
        xmlResult = scrapyProgramXml.ScrapyJsonToXmlModel2(scrapyForm)
        #创建爬虫程序
        createScrapyProgram = CreateScrapyProgram.CreateScrapyProgram()
        zipfilePath = createScrapyProgram.CreateScrapyProgramAjax(xmlResult,projectName)

        file=open(zipfilePath,'rb')
        response =HttpResponse(file)
        response['Content-Type']='application/octet-stream'
        response['Content-Disposition']='attachment;filename='+ projectName +'.zip'
        #response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
    return response

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
        projectcmd = SCRAPY_PROGRAM_PATH+ '/'+projectName+'/'
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
        requrl = str(SCRAPYD_IP + '/listprojects.json')
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
        print (postBody)
        requrl = str(SCRAPYD_IP + '/schedule.json')
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
def getItemListByProgramName(request):
    if(request.method == 'GET'):
        programName = request.GET["programName"]
        obj = models.ScrapyConfig.objects.filter(program=programName)
        data = json.loads(serializers.serialize("json", obj))
    json_result = {"data":data}
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
    ScarpyProgramXml = ScrapyJsonToXml.ScrapyJsonToXml()
    xml = ScarpyProgramXml.ScrapyJsonToXmlModel2(json_result)
    return xml

#输入json，创建xml,返回给前端进行预览
def ScrapyJsonToXmlStr(request):
    if(request.method == 'POST'):
        #获取请求体内容
        postBody = request.body
        #读取爬虫初始化信息
        json_result = json.loads(postBody)
        scrapyProgramXml = ScrapyJsonToXml.ScrapyJsonToXml()
        xmlResult = scrapyProgramXml.ScrapyJsonToXmlModel2(json_result)
    json_result = {"data":xmlResult}
    return JsonResponse(json_result)

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
    #检测是否需要分类
    isNeedClassify(projectName)

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
                _thread.start_new_thread(startSpiderTiming, (programName,spiderName))
            except:
                print("Error: unable to start thread")
    print(nowtime)
    print('定时任务1结束\n')
#运行启动定时任务
sched.start()


#启动爬虫方法
def startSpiderTiming(programName,spiderName):
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

#判断是否需要分类
def isNeedClassify(projectName):
    #获取配置信息，查看该爬虫是否需要分类
    obj = models.ScrapyConfig.objects.filter(program=projectName)
    data = json.loads(serializers.serialize("json", obj))
    isclassify = data[0]["fields"]["isclassify"]
    firstTopicId = data[0]["fields"]["firstTopic"]
    #如果isclassify为1，则需要进行分类操作
    if isclassify == '1':
        print("需要分类")
        #修改数据库配置表状态为“正在分类”
        models.ScrapyConfig.objects.filter(program=projectName).update(status='4')
        runClassifyModel(firstTopicId,projectName)

#爬虫分类、入库模块
def runClassifyModel(firstTopicId,projectName):
    print("进行分类")
    scrapyModel = ScrapydModel.ScrapydModel()
    #运行分类模型
    scrapyModel.mutilNews(firstTopicId)
    #进入循环，判断是否完成分类
    while True:
        time.sleep(1)
        print("正在分类")
        if scrapyModel.isClassifyFinish(firstTopicId) == 0:
            break
    print("分类结束")
    #完成分类后将新爬取的数据推入新闻推送表
    print("新闻更新到推送表")
    scrapyModel.UpdateArticleTable(firstTopicId)
    print("新闻更新到推送表结束")
    #修改数据库配置表状态为爬取完成，回到“已部署状态”
    models.ScrapyConfig.objects.filter(program=projectName).update(status='1')


