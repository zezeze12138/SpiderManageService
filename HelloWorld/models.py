from django.db import models

class ScrapyConfig(models.Model):
    id = models.CharField(primary_key=True,max_length=50)
    program = models.CharField(max_length=50)
    scrapy = models.CharField(max_length=50)
    jobId = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    firstTopic = models.CharField(max_length=10)
    secondTopic = models.CharField(max_length=10)
    timing = models.CharField(max_length=10)
    isclassify = models.CharField(max_length=10)
    filePath = models.CharField(max_length=200)

class Storage(models.Model):
    id = models.CharField(primary_key=True,max_length=30)
    scrapy = models.CharField(max_length=50)
    item = models.CharField(max_length=50)
    itemName = models.CharField(max_length=50)
    xpath = models.CharField(max_length=200)
    remark = models.CharField(max_length=200)
