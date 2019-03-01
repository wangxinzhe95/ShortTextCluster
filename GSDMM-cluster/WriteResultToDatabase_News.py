from gsdmm import MovieGroupProcess
import time
import datetime
import pymysql
import numpy as np
import jieba
import setting
import codecs
import re
import os
import sys

mydir = '/Users/wangxinzhe/Desktop/gsdmm/'
textCutBasePath = mydir + 'cluster_result_text/'
result_file = mydir + 'result_file/readable_topics.txt'

def write_result(sql):
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
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 执行sql语句
        connect.commit()
        print("insert sucessfully")
    except:
        # 发生错误时回滚
        connect.rollback()
    # 关闭数据库连接
    connect.close()

def readFileToString(textCutBasePath):
    dic = dict()

    for root, dirs, files in os.walk(textCutBasePath):
    # for eachclass in ClassCode:
        eachclass = root.split('/')[-1]
        if eachclass == "":
            continue
        eachclasslist = []
        eachclassstring = ''
        eachclasscount = 0
        for f in files:
            # eachfile = open(currClassPath+str(i)+".txt")
            eachclassstring += "%s" % f
            eachclassstring += ';'
            eachclasscount += 1
            # print(eachfilewords)
        eachclasslist.append(eachclassstring)
        eachclasslist.append(eachclasscount)
        dic[eachclass] = eachclasslist
    return dic

def readResult(filepath):
    dic = dict()
    f = open(filepath, 'r', encoding='UTF-8')

    for line in f:
        eachclassstring = ''
        if line == "":
            continue
        cluster_id = line.split(":")[0]
        topic_term = line.split(":")[1].strip('\n').split(" ")
        for eachword in topic_term:
            if eachword == "":
                continue
            eachclassstring += "%s" % eachword
            eachclassstring += ",2.0;"
        dic[cluster_id] = eachclassstring
    return dic

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
    try:
        cursor.execute(sql)
        connect.commit()
        print("Success Backup!")
    except:
        print("失败！")
    connect.close()


def writeResultToDatabase(cluster_result, file_info, start_time, now_time):
    # 备份
    # 移动现在的Cluster_byr_wxz到Cluster_byr_wxz_old中
    execute_sql("INSERT INTO `Cluster_allNews_wxz_old`(`cluster_id`, `topic`, `file_num`, `top_terms`, `file_id`, `start_time`, `end_time`) SELECT `cluster_id`, `topic`, `file_num`, `top_terms`, `file_id`, `start_time`, `end_time` FROM `Cluster_allNews_wxz`")

    write_result("TRUNCATE TABLE `Cluster_allNews_wxz`")
    for eachcluster in cluster_result:
        write_result("INSERT INTO `Cluster_allNews_wxz` (`cluster_id`, `topic`, `file_num`, `top_terms`, `file_id`, `start_time`, `end_time`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (eachcluster, 'no topic', file_info[eachcluster][1], cluster_result[eachcluster], file_info[eachcluster][0], start_time, now_time))

if (len(sys.argv) == 1):
    now_time = datetime.datetime.now()
else:
    try:
        now_time = (datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d"))
    except:
        print("The format of time is incorrect, the usage is 'XXXX-XX-XX'")
        exit(0)
start_time = now_time + datetime.timedelta(days=-7)
start_time = start_time.strftime('%Y-%m-%d')
now_time = now_time.strftime('%Y-%m-%d')
file_info = readFileToString(textCutBasePath)
print(file_info)
cluster_result = readResult(result_file)
print(cluster_result)
start_time = '2018-11-23'
now_time = '2018-11-30'
writeResultToDatabase(cluster_result, file_info, start_time, now_time)
