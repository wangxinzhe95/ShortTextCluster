#-*- coding:utf-8 -*-
import jieba
import jieba.posseg as psg
from cilin import CilinSimilarity
import os
import random
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import pymysql
import setting
import re
import codecs
import sys
from textrank4zh import TextRank4Keyword, TextRank4Sentence
tr4s = TextRank4Sentence()
mydir = '/Users/wangxinzhe/Desktop/gsdmm/'

def execute_sql(sql):
    """获取数据库中数据函数
    根据sql语句获取数据库中内容

    Args：
        sql:数据库操作语句

    Returns:
        list:数据库中取出文本数据数组
    """
    connect = pymysql.connect(host=setting.CLUSTER_HOST, db=setting.CLUSTER_DBNAME, user=setting.CLUSTER_USER,
                              passwd=setting.CLUSTER_PASSWD, charset='utf8', use_unicode=True)
    cursor = connect.cursor()
    cursor.execute(sql)
    k = cursor.fetchall()
    return k

def get_database_list(sql, bbses):
    """获取数据库中数据函数
    根据sql语句获取数据库中内容

    Args：
        sql:数据库操作语句

    Returns:
        list:数据库中取出文本数据数组
    """
    data_list = {}
    f2 = open(mydir + 'result_file/aid_bid', 'w', encoding='UTF-8')
    f2.close()
    for bbs in bbses:
        database = setting.BBS_DBNAME + '_' + bbs
        connect = pymysql.connect(host=setting.BBS_HOST, db=database, user=setting.BBS_USER,
                                  passwd=setting.BBS_PASSWD, charset='utf8', use_unicode=True)
        cursor = connect.cursor()
        cursor.execute(sql)
        k = cursor.fetchall()
        f2 = open(mydir + 'result_file/aid_bid', 'a', encoding='UTF-8')
        dir = ''
        for li in k:
            dir = "byr_" + li[0] + "_" + li[1]
            f2.write(dir + "\n")
            tr4s.analyze(text=(li[5].strip('\n') + " " + li[6].strip('\n')), lower=True, source='all_filters')
            output = ''
            for item in tr4s.get_key_sentences(num=1):
                output += item.sentence
                output += ' '
            data_list["%s" % dir] = output
            #存放进行分词前的文本
            f3 = open(mydir + 'texts/' + "%s" % dir, 'w', encoding='UTF-8')
            f3.write(li[5].strip('\n') + "\n" + li[6].strip('\n'))
            f3.close()
        connect.commit()
        connect.close()
        f2.close()
    result_list={}
    stopwords = {}.fromkeys([line_content.strip() for line_content in codecs.open(mydir + 'stopword.txt')])  # 停用词表
    #包含中文的正则模版
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    cl = CilinSimilarity()
    for li in data_list:
        # seglist = jieba.cut(data_list[li], cut_all=False)  # 精确模式
        seglist = psg.cut(data_list[li])
        output = ''
        for segs, flag in seglist:
            segs = segs.rstrip('\n')
            segs = segs.strip()
            seg = segs.lower()  # 英文字母小写
            if (seg not in stopwords) and (flag.startswith(('a','f','j','l','m','n','q','t','v'))):  # 去停用词,并且过滤指定词性的词
            #if seg not in stopwords:  # 去停用词
                if not re.search('^[a-zA-Z-0-9]+$', seg) and len(seg) > 1 and zhPattern.search(seg):  # 去掉分词为1个字的结果
                    output += seg
                    output += ' '
        # print output
        result_list["%s" % li] = output
    return data_list, result_list

def get_database_list_from_file(textCutBasePath):
    data_list = {}
    for root, dirs, files in os.walk(textCutBasePath):
        for file in files:
            if not (file.startswith('.')):
                eachFileContent = ''
                eachFileObj = open(root + '/' + file, 'r', encoding='UTF-8')
                for line in eachFileObj.readlines():
                    eachFileContent += line
                data_list["%s" % file] = eachFileContent
    print(data_list)
    return data_list
# tables = setting.cluster_table
# # tables = tables.split(',')
# # print(tables)
#
# for eachtable in tables:
#     add_type = 'ALTER TABLE `' + eachtable + '` ADD `start_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `file_id`, ADD `end_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `start_time`'
#     execute_sql(add_type)
#     print(eachtable)



# time_interval = "weekly"
# if (len(sys.argv) == 1):
#     time_interval = "weekly"
# elif (len(sys.argv) == 2):
#     time_interval = sys.argv[1]
#
# print(time_interval)
# textCutBasePath = mydir + 'texts/'
# get_database_list_from_file(textCutBasePath)
# start_time = '2018-11-24 00:00:00'
# now_time = '2018-11-24 02:00:00'
# news_bbses = setting.news_bbses
# result = {}
# main_sql = "SELECT * FROM `article` WHERE `post_time` > '" + start_time + "' AND `post_time` < '" + now_time + "'"
# origin_texts, texts = get_database_list(main_sql, news_bbses.split(','))
# print(origin_texts, texts)

mydir = '/Users/wangxinzhe/Desktop/gsdmm/'
jieba.load_userdict(mydir + "user_dict.txt")
seglist = jieba.cut('[原创]人生几何', cut_all=True)  # 精确模式
for segs in seglist:
    print(segs)
# # # print(glove.most_similar('physics'))
# cl = CilinSimilarity()
# code1 = cl.get_code("祝福")
# print(code1)
# synonyms.synonyms.main()
#
# for eachcode in code1:
#     if eachcode.endswith('='):
#         print(cl.code_word.get(eachcode))
# jieba.load_userdict("/Users/wangxinzhe/Desktop/gsdmm/user_dict.txt")
# jieba.load_userdict("/Users/wangxinzhe/Desktop/gsdmm/Chinese_dict.txt")
# word_list = psg.cut("肺结核")
# for x in word_list:
#     print(x.word, x.flag)
# texts = get_database_list("SELECT * FROM `article` WHERE `post_time` > '" + start_time + "' AND `post_time` < '" + now_time + "'")
# os.system('sh /Users/wangxinzhe/Desktop/gsdmm/gsdmm-rust.sh')
# f9 = open('/Users/wangxinzhe/GraduateWork/gsdmm-rust/examples/grades_out_labels.csv', 'r', encoding='UTF-8')
# label_list = []
# for te in f9.readlines():
#     label_list.append(te.strip('\n').split(','))
#
# print(label_list)