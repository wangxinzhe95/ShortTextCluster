# -*- coding:utf-8 -*-
import math
import os
import jieba.posseg as psg
import sys
# 采用TF-IDF 算法对选取得到的特征进行计算权重
#必须与Test中的ClassCode顺序一样！！！！！！！！！！
# 构建每个类别的词Set
# 分词后的文件路径

def readFeature(featureName):
    featureFile = open(featureName, 'r')
    featureContent = featureFile.read().split('\n')
    featureFile.close()
    feature = list()
    for eachfeature in featureContent:
        eachfeature = eachfeature.split(" ")
        if (len(eachfeature)==2):
            feature.append(eachfeature[1])
    # print(feature)
    return feature

# 读取所有类别的训练样本到字典中,每个文档是一个list
def readFileToList(textCutBasePath):
    dic = dict()
    for root, dirs, files in os.walk(textCutBasePath):
    # for eachclass in ClassCode:
        eachclass = root.split('/')[-1]
        if eachclass == "":
            continue
        eachclasslist = list()
        for f in files:
            # eachfile = open(currClassPath+str(i)+".txt")
            eachfile = open(root + '/' + f, 'r')
            eachfilecontent = eachfile.read()
            eachfilewords = eachfilecontent.split(" ")
            eachclasslist.append(eachfilewords)
            # print(eachfilewords)
        dic[eachclass] = eachclasslist
    return dic

# 计算特征的逆文档频率
def featureIDF(dic, feature, dffilename):
    dffile = open(dffilename, "w")
    dffile.close()
    dffile = open(dffilename, "a")
    totaldoccount = 0
    idffeature = dict()
    dffeature = dict()
    for eachfeature in feature:
        docfeature = 0
        for key in dic:
            totaldoccount = totaldoccount + len(dic[key])
            classfiles = dic[key]
            for eachfile in classfiles:
                if eachfeature in eachfile:
                    docfeature = docfeature + 1
        # 计算特征的逆文档频率
        featurevalue = math.log(float(totaldoccount)/(docfeature+1))
        dffeature[eachfeature] = docfeature
        # 写入文件，特征的文档频率
        dffile.write(eachfeature + " " + str(docfeature)+"\n")
        # print(eachfeature+" "+str(docfeature))
        idffeature[eachfeature] = featurevalue
    dffile.close()
    return idffeature

# 计算Feature's TF-IDF 值
def TFIDFCal(feature, dic,idffeature,K):
    termCountDic = dict()
    for key in dic:
        print (key)
        classFiles = dic[key]
        # 谨记字典的键是无序的
        count_word = {}
        for eachfile in classFiles:
            # 对每个文件进行特征向量转化
            for eachfeature in feature:
                if eachfeature in eachfile:
                    currentfeature = eachfeature
                    featurecount = eachfile.count(eachfeature)
                    tf = float(featurecount)/(len(eachfile))
                    # 计算逆文档频率
                    featurevalue = idffeature[currentfeature]*tf
                    if eachfeature in count_word.keys():
                        count_word[eachfeature] = count_word[eachfeature]+featurevalue
                    else:
                        count_word[eachfeature] = featurevalue
        sorted_count_word = sorted(count_word.items(), key=lambda d:d[1], reverse=True)
        subDic = dict()
        for i in range(K):
            subDic[sorted_count_word[i][0]] = sorted_count_word[i][1]
        termCountDic[key] = subDic
    return termCountDic

def writeTermCountDicToFile(termCountDic, fileName):
    file = open(fileName, 'w', encoding='UTF-8')
    #获取话题词的词性
    for key in termCountDic:
        for eachword in termCountDic[key]:
            seglist = psg.cut(eachword)
            for x in seglist:
                termCountDic[key][eachword] = [termCountDic[key][eachword], x.flag]

    for key in termCountDic:
        file.write(str(key) + ":")
        prev = ''
        tail = ''
        countT = 0
        countN = 0
        countV = 0
        countA = 0
        countL = 0
        output = ''
        for eachword in termCountDic[key]:
            output += eachword
            output += ' '
            flag = termCountDic[key][eachword][1]
            if flag.startswith('t'):
                countT += 1
                if countT <= 2:
                    prev += eachword
                    prev += ' '
                else:
                    tail += eachword
                    tail += ' '
            elif flag.startswith('n'):
                countN += 1
                if countN <= 2:
                    prev += eachword
                    prev += ' '
                else:
                    tail += eachword
                    tail += ' '
            elif flag.startswith('v'):
                countV += 1
                if countV <= 2:
                    prev += eachword
                    prev += ' '
                else:
                    tail += eachword
                    tail += ' '
            elif flag.startswith('a'):
                countA += 1
                if countA <= 2:
                    prev += eachword
                    prev += ' '
                else:
                    tail += eachword
                    tail += ' '
            elif flag.startswith('l'):
                countL += 1
                if countL <= 2:
                    prev += eachword
                    prev += ' '
                else:
                    tail += eachword
                    tail += ' '
        # file.write(" " + prev + tail)
        file.write(" " + output)
        file.write("\n")
    file.close()

mydir = '/home/tensorflow/wangxinzhe/'
time_interval = "weekly"
if (len(sys.argv) == 1):
    time_interval = "weekly"
elif (len(sys.argv) == 2):
    time_interval = sys.argv[1]

if (time_interval == 'monthly'):
    textCutBasePath = mydir + "cluster_result_text_monthly/"
else:
    textCutBasePath = mydir + "cluster_result_text/"

dic = readFileToList(textCutBasePath)
result_dir = 'result_file'
if (time_interval == 'monthly'):
    result_dir += '_monthly'
print(dic)
feature = readFeature(mydir + result_dir + "/Cluster_Feature.txt")
print(feature)
idffeature = featureIDF(dic, feature, mydir + result_dir + "/dffeature.txt")
termCountDic = TFIDFCal(feature, dic,idffeature, 10)
writeTermCountDicToFile(termCountDic, mydir + result_dir + '/topics.txt')












