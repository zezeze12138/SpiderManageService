from django.conf.urls import *
from django.contrib import admin
from . import view,testdb

urlpatterns = [
    url(r"^hello$",view.hello),
    url(r"^downScrapyXml$",view.DownScrapyXml),
    url(r"^createScrapyXml$",view.CreateScrapyXml),
    url(r"^createScrapyProgramAndDownload",view.createScrapyProgramAndDownload),
    url(r"^scrapyJsonToXmlStr$",view.ScrapyJsonToXmlStr),
    url(r"^scrapyConfig",view.getScrapyConfigList),
    url(r"^getItemListByProgramName",view.getItemListByProgramName),
    url(r"^uploadXml",view.uploadXml),
    url(r"^downloadScrapyProgramByXmlName",view.downloadScrapyProgramByXmlName),
    url(r"^deleteScrapyConfig",view.deleteScrapyConfig),
    url(r"^getListJob",view.getListJob),
    url(r"^chargeClassifyStatus",view.chargeClassifyStatus),
    url(r"^setTimingByProgramName",view.setTimingByProgramName),
    url(r"^addScrapyConfigAndUploadProgram",view.addScrapyConfigAndUploadProgram),
    url(r"^startSpider",view.startSpider),
    url(r"^deleteSpider",view.deleteSpider),
    url(r"^deploySpider",view.deploySpider),
    url(r"^spiderData",view.SpiderData),
    url(r"^testdb$",testdb.testdb),
    url(r'^admin/',admin.site.urls)
]