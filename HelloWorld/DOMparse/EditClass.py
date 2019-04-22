#coding=utf-8
class EditClass:
    def __init__(self):
        pass
    #生成类
    @staticmethod
    def addClass(className):
        return "class "+className+":" + "\n"

    #生成类含入参
    def addClassAndParams(self,className,params):
        return "class " + className + "("+ params +"):" + "\n"

    #生成方法
    @staticmethod
    def addDef(defName):
        return "\t" + "def " + defName + "():" + "\n"

    #生成方法self
    def addDefSelf(defName, params):
        paramContext = ""
        for param in params:
            paramContext = paramContext + param + ","
        return "\t" + "def " + defName + "(self,"+ paramContext[:-1] +"):" + "\n"

    #生成方法，带参数
    @staticmethod
    def addDefAndparam(defName, params):
        paramContext = ""
        for param in params:
            paramContext = paramContext + param + ","
        return "\t" + "def " + defName + "(" + paramContext[:-1] +"):" + "\n"

    #增加变量与缩进
    @staticmethod
    def addVar(bNum,param):
        blank = "";
        for i in range(1,bNum):
            blank = blank + '\t'
        param = blank + param
        return param + "\n"

    #获取数组str串
    def getArrayStr(self,params):
        paramStr = ""
        for param in params:
            paramStr = paramStr+ "'" + param + "',"
        if paramStr == "":
            return ""
        else:
            return paramStr[:-1]

    #获取爬虫类
    def addSpiderClass(self,className,spiderName,allows,startUrls):
        classContext1 = "class " + className + "(scrapy.Spider):" +"\n"
        classContext2 = "\t" + "name = '" + spiderName +"'\n"
        classContext3 = "\t" + "allowed_domains = [" + self.getArrayStr(allows) + "]\n"
        classContext4 = "\t" + "start_urls = [" + self.getArrayStr(startUrls) + "]\n"
        return classContext1+classContext2+classContext3+classContext4




