# -*- coding:utf-8 -*-
import os
import re


mydir = '/Users/wangxinzhe/Desktop/gsdmm/'

data_dir = mydir + 'texts/'

def read_data():
    origin_texts = []
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            if not (f.startswith('.')):
                eachFileObj = open(data_dir + f, 'r')
                eachFileContent = eachFileObj.read()
                origin_texts.append(eachFileContent)
    return origin_texts

def read_candidate(fileName, K):
    candidates = {}
    file = open(fileName, 'r', encoding='UTF-8')
    for te in file.readlines():
        candidate_word = te.split(':')[1].strip()
        output = ''
        count = 0
        for eachword in candidate_word.split():
            count = count + 1
            if count <= K:
                output += eachword
                output += ' '
        candidates["%s" % te.split(':')[0]] = output.strip()
    return candidates


def extract_topic(candidates, origin_texts):
    result = {}

    # 所有标点符号
    pattern = r',|\.|/|;|\'|`|\[|\]|<|>|\?|:|"|\{|\}|\~|!|@|#|\$|%|\^|&|\(|\)|-|=|\_|\+|，|。|、|；|‘|’|【|】|·|！| |…|（|）|\n'
    count = 0
    for eachclass in candidates:
        count = count + 1
        print(str(count) + ": " + eachclass)
        final_flag = True
        for key in origin_texts:
            flag2 = False
            for eachstring in re.split(pattern, key):
                flag = True
                for eachword in candidates[eachclass].split():
                    if not eachword in eachstring:
                        flag = False
                        break
                if flag == True:
                    result["%s" % eachclass] = eachstring
                    flag2 = True
                    break
            if flag2 == True:
                final_flag = False
                break
        if final_flag == True:
            result["%s" % eachclass] = candidates[eachclass]
    return result

def writeTermCountDicToFile(result_topics, fileName):
    file = open(fileName, 'w', encoding='UTF-8')
    for key in result_topics:
        file.write(str(key) + ":")
        file.write(" " + result_topics[key])
        file.write("\n")
    file.close()

print("读取原文章。。。。。。。")
origin_texts = read_data()
print("读取原文章完成！")
topics_dir = mydir + 'result_file/topics.txt'
print("读取候选话题词。。。。。。。")
candidates = read_candidate(topics_dir, 3)
print("读取候选话题词完成！")
print("提取话题中。。。。。。")
result_topic = extract_topic(candidates, origin_texts)
print("提取话题完成！")
writeTermCountDicToFile(result_topic, mydir + 'result_file/readable_topics.txt')




