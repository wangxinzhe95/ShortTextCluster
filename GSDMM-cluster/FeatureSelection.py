# -*- coding:utf-8 -*-
import os
import jieba
import jieba.posseg as psg
import sys
# 使用开方检验选择特征
# 按UTF-8编码格式读取文件

mydir = '/home/tensorflow/wangxinzhe/'
jieba.load_userdict(mydir + "user_dict.txt")
jieba.load_userdict(mydir + "Chinese_dict.txt")

# 定义停止词
def MakeWordsSet(words_file):
    words_set = set()
    with open(words_file, 'r') as fp:
        for line in fp.readlines():
            word = line.strip()
            if len(word) > 0 and word not in words_set: # 去重
                words_set.add(word)
    return words_set

# print(stopwords)

# 对卡方检验所需的 a b c d 进行计算
# a：在这个分类下包含这个词的文档数量
# b：不在该分类下包含这个词的文档数量
# c：在这个分类下不包含这个词的文档数量
# d：不在该分类下，且不包含这个词的文档数量

# 构建每个类别的词Set

# 分词后的文件路径

# 构建每个类别的词向量
def buildItemSets(time_interval, stopwords_set=set()):
    textCutBasePath = mydir + 'cluster_result_text/'
    if (time_interval == 'monthly'):
        textCutBasePath = mydir + 'cluster_result_text_monthly/'
    # stopwords_set_final = set()
    # for content in stopwords_set:
    #     stopwords_set_final.add(content.decode('utf-8'))
    termDic = dict()
    # 每个类别下的文档集合用list<set>表示, 每个set表示一个文档，整体用一个dict表示
    termClassDic = dict()
    # for eachclass in ClassCode:
    flag = 0
    for root, dirs, files in os.walk(textCutBasePath):
        eachclass = root.split('/')[-1]
        print (eachclass)
        if eachclass=="":
            continue
        eachClassWordSets = set()
        eachClassWordList = list()
        flag = -1
        for f in files:
            if not (f.startswith('.')):
                flag = flag + 1
                eachFileObj = open(root + '/'+ f, 'r')
                eachFileContent = eachFileObj.read()
                eachFileWords = eachFileContent.split(" ")
                # print (json.dumps(eachFileWords).decode('unicode-escape'))
                eachFileSet = set()
                for eachword in eachFileWords:
                    # 判断是否是停止词
                    if (not eachword.isdigit()) and (eachword not in stopwords_set):#长度大于3是为了筛掉单个汉字
                        eachFileSet.add(eachword)
                        eachClassWordSets.add(eachword)
                eachClassWordList.append(eachFileSet)
        termDic[eachclass] = eachClassWordSets
        termClassDic[eachclass] = eachClassWordList
    return termDic, termClassDic



# 对得到的两个词典进行计算，可以得到a b c d 值
# K 为每个类别选取的特征个数

# 卡方计算公式
def ChiCalc(a, b, c, d):
    result = (float(pow((a*d - b*c), 2)))*float(a+b+c+d) /float((a+c) * (a+b) * (b+d) * (c+d))
    return result

def featureSelection(termDic, termClassDic, K):
    termCountDic = dict()
    temp = 0
    for key in termDic:
        temp = temp + 1
        print (temp, key)
        classWordSets = termDic[key]
        classTermCountDic = dict()
        for eachword in classWordSets:  # 对某个类别下的每一个单词的 a b c d 进行计算
            a = 0
            b = 0
            c = 0
            d = 0
            for eachclass in termClassDic:
                if eachclass == key: #在这个类别下进行处理
                    for eachdocset in termClassDic[eachclass]:
                        if eachword in eachdocset:
                            a = a + 1
                        else:
                            c = c + 1
                else: # 不在这个类别下进行处理
                    for eachdocset in termClassDic[eachclass]:
                        if eachword in eachdocset:
                            b = b + 1
                        else:
                            d = d + 1
            # print("a+c:"+str(a+c)+"b+d"+str(b+d))
            # 防止有的词一次没出现
            if ((a + c) * (a + b) * (b + d) * (c + d)) == 0:
                continue
            eachwordcount = ChiCalc(a, b, c, d)
            print (temp, key, eachwordcount)
            classTermCountDic[eachword] = eachwordcount
        # 对生成的计数进行排序选择前K个
        # 这个排序后返回的是元组的列表
        sortedClassTermCountDic = sorted(classTermCountDic.items(), key=lambda d:d[1], reverse=True)
        count = 0
        subDic = dict()
        for i in range(K):
            subDic[sortedClassTermCountDic[i][0]] = sortedClassTermCountDic[i][1]
        termCountDic[key] = subDic
    return termCountDic
        # print(sortedClassTermCountDic)

def featureSelectionFrequency(termDic):
    totalWordSet = set()
    temp = 0
    for key in termDic:
        temp = temp + 1
        for eachword in termDic[key]:
            totalWordSet.add(eachword)

    return totalWordSet

def writeFeatureToFile(termCountDic , fileName):
    featureSet = set()
    for key in termCountDic:
        for eachkey in termCountDic[key]:
            featureSet.add(eachkey)
    count = 1
    file = open(fileName, 'w')
    for feature in featureSet:
        # 判断feature 不为空
        stripfeature = feature.strip()
        if len(stripfeature) > 0 and feature != ' ':
            file.write(str(count)+ " " +feature+"\n")
            count = count + 1
    file.close()

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

if (len(sys.argv) == 1):
    time_interval = "weekly"
elif (len(sys.argv) == 2):
    time_interval = sys.argv[1]

# 调用buildItemSets
# buildItemSets形参表示每个类别的文档数目
stopwords_file = mydir + "stopword.txt"
stopwords_set = MakeWordsSet(stopwords_file)
termDic, termClassDic = buildItemSets(stopwords_set)
print(termDic)
# print (json.dumps(eachFileWords).decode('unicode-escape'))
termCountDic = featureSelection(termDic, termClassDic, 10)
print(termCountDic)
result_dir = 'result_file'
if (time_interval == 'monthly'):
    result_dir += '_monthly'
writeTermCountDicToFile(termCountDic, mydir + result_dir + '/topics.txt')
# totalWordSet = featureSelectionFrequency(termDic)
# print(totalWordSet)
writeFeatureToFile(termCountDic, mydir + result_dir + '/Cluster_Feature.txt')















