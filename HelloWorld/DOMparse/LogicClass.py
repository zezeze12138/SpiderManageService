# -*- coding: utf-8 -*-
class LoginClass:
    def ifelse(self, LayerNumber, keyWord, judge):
        LayerStr = LoginClass.addIndent(LayerNumber)
        return LayerStr + keyWord + " " + judge + ':' + "\n"

    def forLogin(self, LayerNumer, entity, entityLogin):
        LayerStr = LoginClass.addIndent(LayerNumer)
        return LayerStr + "for " + entity + " in " + entityLogin + ":" + "\n"

    def itemsAndXpaths(self, LayerNumber, items, xpaths):
        LayerStr = LoginClass.addIndent(LayerNumber)
        itemsStr = ""
        for item,xpath in zip(items,xpaths):
            itemsStr = itemsStr + LayerStr + 'item["' + item + '"] = response.xpath("' + xpath + '").extract()' + "\n"
        return itemsStr

    #item.py字段代码编写
    def itemsScrapyField(self,itemsArr):
        itemStr = ""
        for item in itemsArr:
            itemStr = itemStr + "\t" + item + " = scrapy.Field()" + "\n"
        return itemStr

    @staticmethod
    def addIndent(num):
        IndentStr = ""
        for i in range(num):
            IndentStr = IndentStr + "\t"
        return IndentStr

