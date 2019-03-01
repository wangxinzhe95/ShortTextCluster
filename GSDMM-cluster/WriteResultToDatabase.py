import datetime
import pymysql
import setting
import os
import sys
import random

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
            # 随机生成一个权重
            eachclassstring += "," + str(round(random.uniform(1.5, 10), 2)) + ";"
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


def writeResultToDatabase(database, time_interval, cluster_result, file_info, start_time, now_time):
    # 备份
    # 移动现在的Cluster_byr_wxz到Cluster_byr_wxz_old中
    backup_database = 'Cluster_' + database + '_old'
    insert_database = 'Cluster_' + database

    if (time_interval == "monthly"):
        insert_database = insert_database + '_' + time_interval

    execute_sql("INSERT INTO `" + backup_database + "`(`cluster_id`, `topic`, `file_num`, `top_terms`, `file_id`, `start_time`, `end_time`) SELECT `cluster_id`, `topic`, `file_num`, `top_terms`, `file_id`, `start_time`, `end_time` FROM `" + insert_database + "`")

    write_result("TRUNCATE TABLE `" + insert_database + "`")
    for eachcluster in cluster_result:
        write_result("INSERT INTO `" + insert_database + "` (`cluster_id`, `topic`, `file_num`, `top_terms`, `file_id`, `start_time`, `end_time`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (eachcluster, 'no topic', file_info[eachcluster][1], cluster_result[eachcluster], file_info[eachcluster][0], start_time, now_time))

if (len(sys.argv) == 1):
    data_source = "byr"
    time_interval = "weekly"
elif (len(sys.argv) == 2):
    data_source = sys.argv[1]
    time_interval = "weekly"
else:
    data_source = sys.argv[1]
    time_interval = sys.argv[2]

mydir = '/home/tensorflow/wangxinzhe/'

if (time_interval == 'monthly'):
    textCutBasePath = mydir + "cluster_result_text_monthly/"
else:
    textCutBasePath = mydir + "cluster_result_text/"

result_dir = 'result_file'
if (time_interval == 'monthly'):
    result_dir += '_monthly'

result_file = mydir + result_dir + '/topics.txt'
now_time = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d'), "%Y-%m-%d")
start_time = now_time + datetime.timedelta(days=-7)
if (time_interval == "monthly"):
    start_time = now_time + datetime.timedelta(days=-30)
start_time = start_time.strftime('%Y-%m-%d')
now_time = now_time.strftime('%Y-%m-%d')

file_info = readFileToString(textCutBasePath)
print(file_info)
cluster_result = readResult(result_file)
print(cluster_result)
writeResultToDatabase(data_source, time_interval, cluster_result, file_info, start_time, now_time)
