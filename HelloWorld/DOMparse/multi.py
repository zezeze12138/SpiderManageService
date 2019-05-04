# This Python file uses the following encoding: utf-8
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cross_validation import cross_val_score

from sklearn.externals import joblib

stopwordPath = './stopword.txt'

def getStopwordList(stopwordPath):
    stopword_file = open(stopwordPath)
    stopword_content_string = stopword_file.read()
    stopword_list = stopword_content_string.split('\n');


def getSegmentContent(primaryDirPath):
    secondaryClasses=[]
    articleIds=[]
    articleContents=[]
    secondaryDirs = os.listdir(primaryDirPath)

    for secondaryDir in secondaryDirs:

            filesPath = "%s/%s"%(primaryDirPath,secondaryDir)
            files = os.listdir(filesPath)

            for file in files:
                filePath = "%s/%s"%(filesPath,file)
                with open(filePath, mode="r", encoding="utf-8") as f:
                    segmentContent = f.read()
                    secondaryClasses.append(secondaryDir)

                    fileId = file[:len(file)-4]
                    articleIds.append(fileId)
                    articleContents.append(segmentContent)

    return articleIds,articleContents,secondaryClasses

def content_vectorizer(data,vectorizerModelPath):
    vectorizer= CountVectorizer()
    articleContentsVec = vectorizer.fit_transform(data)
    articleContentsVecTF=  TfidfTransformer().fit_transform(articleContentsVec )
    joblib.dump(vectorizer, vectorizerModelPath)
    return articleContentsVecTF


def train(X_train,Y,multinomialNBModelPath):
    from sklearn.naive_bayes import MultinomialNB
    clf = MultinomialNB(alpha=0.001).fit(X_train, Y)
    joblib.dump(clf, multinomialNBModelPath)
    # print('交叉验证结果')
    # print(cross_val_score(clf, X_train, Y, cv=10, scoring='accuracy'))  # 交叉验证

def makeDir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def trainClasses(dataBasicPath,modelBasicPath,primaryClasses):
    primaryDirs = os.listdir(dataBasicPath)
    for primaryDir in primaryDirs:
        if not primaryDir in primaryClasses:
            continue
        basicPath="%s\%s"%(dataBasicPath,primaryDir)
        modelPath = "%s\%s"%(modelBasicPath,primaryDir)
        trainOneClass(basicPath,modelPath)

def trainOneClass(basicPath,modelPath):
    makeDir(modelPath)
    vectorizerModelPath="%s/%s"%(modelPath,"vectorizer.model")
    multinomialNBModelPath = "%s/%s"%(modelPath,"multinomialNB.model")
    articleIds,articleContents,secondaryClasses=getSegmentContent(basicPath)
    articleContentsTF=content_vectorizer(articleContents,vectorizerModelPath)
    train(articleContentsTF,secondaryClasses,multinomialNBModelPath)




def content_vectorizer_test(data,vectorizerModelPath):
    vectorizer_content = joblib.load(vectorizerModelPath)
    x_array = vectorizer_content.transform(data)
    X =  TfidfTransformer().fit_transform(x_array)
    return X

def predict(data,vectorizerModelPath,multinomialNBModelPath):
    check_file_vectorizer = content_vectorizer_test(data,vectorizerModelPath)
    clf = joblib.load(multinomialNBModelPath)
    predict_result = clf.predict(check_file_vectorizer)
    print('------>预测结果<------')
    print(predict_result)
    return predict_result

def getUnClasifyData(filesPath):
    files = os.listdir(filesPath)
    articleIds=[]
    articleContents=[]
    for file in files:
        filePath = "%s/%s" % (filesPath, file)
        with open(filePath, mode="r", encoding="utf-8") as f:
            segmentContent = f.read()
            fileId = file[:len(file) - 4]
            articleIds.append(fileId)
            articleContents.append(segmentContent)
    return articleIds,articleContents

def contentVectorizer1(data,vecModelPath):

    vectorizer = joblib.load(vecModelPath)
    vectorizerContent = vectorizer.transform(data)
    tfContent =  TfidfTransformer().fit_transform(vectorizerContent)
    return tfContent

def predict(tfData,multinomialNBModelPath):
    clf = joblib.load(multinomialNBModelPath)
    predictResult = clf.predict(tfData)
    return predictResult

def predictClasses(dataBasicPath,modelBasicPath, primaryClasses):
    allArticleIds = []
    allResultIds = []
    for primaryClass in primaryClasses:
        unClassifyDataPath = "%s/%s"%(dataBasicPath,primaryClass)
        vecModelPath = "%s/%s/%s"%(modelBasicPath,primaryClass,"vectorizer.model")
        multinomialNBModelPath = "%s/%s/%s"%(modelBasicPath,primaryClass,"multinomialNB.model")
        articleIds, articleContents = getUnClasifyData(unClassifyDataPath)
        tfContentsVectorizer = contentVectorizer1(articleContents, vecModelPath)
        result = predict(tfContentsVectorizer, multinomialNBModelPath)
        for i in range(len(articleIds)):
            allArticleIds.append(articleIds[i])
            allResultIds.append(result[i])
    return allArticleIds,allResultIds
# basicPath = "D:/Code/data/1001"
# modelPath="D:/Code/model"
# modelPath1="D:/Code/model/1001"
# makeDir(modelPath1)
# vectorizerModelPath="%s/%s"%(modelPath1,"vectorizer.model")
# multinomialNBModelPath = "%s/%s"%(modelPath1,"multinomialNB.model")
# articleIds,articleContents,secondaryClasses=getSegmentContent(basicPath)
# articleContentsTF=content_vectorizer(articleContents,vectorizerModelPath)
# train(articleContentsTF,secondaryClasses,multinomialNBModelPath)

#train_model
######################
# dataBasicPath = "F:/sina_news_data"
# modelBasicPath="F:/sina_news_data_model"
# primaryClasses=['11','12','13','14','15','16','17','18','19','20']
# trainClasses(dataBasicPath,modelBasicPath,primaryClasses)



# unClassifyDataPath="D:/Code/data1/1001"
# vecModelPath = "D:/Code/model/1001/vectorizer.model"
# multinomialNBModelPath = "D:/Code/model/1001/multinomialNB.model"
# articleIds,articleContents=getUnClasifyData(unClassifyDataPath)
# tfContentsVectorizer = contentVectorizer1(articleContents,vecModelPath)
# result = predict(tfContentsVectorizer,multinomialNBModelPath)
# print(articleIds)
# print(result)

#predict
def predictNewsTopic(NewsTopicId):
    dataBasicPath = "F:/tengxun_news_data"
    modelBasicPath = "F:/sina_news_data_model"
    primaryClasses = []
    primaryClasses.append(str(NewsTopicId))
    allArticleIds,allResultIds = predictClasses(dataBasicPath,modelBasicPath,primaryClasses)
    print(allArticleIds)
    print(allResultIds)
    return (allArticleIds,allResultIds)
