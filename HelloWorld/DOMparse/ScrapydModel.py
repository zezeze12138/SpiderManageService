#coding=utf-8
import os
import json
from HelloWorld.DOMparse.multi import *
import pymysql
import uuid
import time
def dbHandle():
    conn = pymysql.connect(
        host = "localhost",
        user = "root",
        passwd = "123456",
        charset = "utf8",
        use_unicode = False
    )
    return conn

class ScrapydModel:

    #查看是否分类完成，未完成未1，完成为0
    def isClassifyFinish(self,firstTopicId):
        dbObject = dbHandle()
        cursor = dbObject.cursor()
        cursor.execute("USE news")
        sqlselect = "select count(*) from tb_article_other where FirstTopic_id = %s and SecondTopic_id is null"
        try:
            cursor.execute(sqlselect,(firstTopicId))
            cursor.connection.commit()
            rows = cursor.fetchall()
            newsNumber = rows[0][0]
            if newsNumber > 0:
                return 1
            else:
                return 0
        except BaseException as e:
            print("错误在这里>>>>>>>>>>>>>",e,"<<<<<<<<<<<<<错误在这里")
            dbObject.rollback()


    #调用分类算法
    def mutilNews(self,NewsTopicId):
        #predict
        allArticleIds,allResultIds = predictNewsTopic(NewsTopicId)
        print(allArticleIds)
        print(len(allArticleIds))
        print(allResultIds)
        print(len(allResultIds))
        dbObject = dbHandle()
        cursor = dbObject.cursor()
        cursor.execute("USE news")
        for articleId,ResultId in zip(allArticleIds,allResultIds):
            sqlselect = "UPDATE tb_article_other SET SecondTopic_id=%s WHERE Article_id=%s"
            try:
                cursor.execute(sqlselect,(ResultId,articleId))
                cursor.connection.commit()
            except BaseException as e:
                print("错误在这里>>>>>>>>>>>>>",e,"<<<<<<<<<<<<<错误在这里")
                dbObject.rollback()

    #将分类好的新闻数据推入推送表
    def UpdateArticleTable(self,NewsTopicId):
        dbObject = dbHandle()
        cursor = dbObject.cursor()
        cursor.execute("USE news")
        #先查到爬取表中还没进入推送表的文章，即isenter字段为0的
        sqlselect = "select * from tb_article_other WHERE IsEnter=0 and FirstTopic_id=%s"
        try:
            cursor.execute(sqlselect,(NewsTopicId))
            cursor.connection.commit()
            rows = cursor.fetchall()
            #对每一条即将插入推送表的数据进行操作
            for row in rows:
                #创建新的文章id
                Article_id = str(uuid.uuid1())[0:16]
                #将爬取并且分类好的新文章插入推送表
                sql = "INSERT INTO tb_article_other_old(Article_id,Article_name,Article_title,Article_context,Article_context_html,Separate_context,FirstTopic_id,SecondTopic_id,Date) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql,(str(Article_id),str(Article_id),row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
                cursor.connection.commit()
                #对新文章进入推送表的文章的isEnter字段进行更新，表示该文章已经进入推送表
                sql_updataScrapyTable="UPDATE tb_article_other SET IsEnter=1 WHERE Article_id=%s"
                try:
                    cursor.execute(sql_updataScrapyTable,(row[0]))
                    cursor.connection.commit()
                    print("suc")
                except BaseException as e:
                    print("错误在这里>>>>>>>>>>>>>",e,"<<<<<<<<<<<<<错误在这里")
                    dbObject.rollback()
        except BaseException as e:
            print("错误在这里>>>>>>>>>>>>>",e,"<<<<<<<<<<<<<错误在这里")
            dbObject.rollback()


#if __name__ == "__main__":
    #number = ScrapydModel.isClassifyFinish("11")
    #print(number)
    #ScrapydModel.mutilNews("11")
    #ScrapydModel.UpdateArticleTable("11")