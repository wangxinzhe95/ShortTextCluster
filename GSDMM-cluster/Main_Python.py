from gsdmm import MovieGroupProcess
import time
import datetime
import pymysql
import numpy as np
import jieba
import jieba.posseg as psg
import setting
import codecs
import re
import os
import sys
from cilin import CilinSimilarity
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.datasets import load_svmlight_file
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.datasets import dump_svmlight_file
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.linear_model import RidgeClassifier
from sklearn.linear_model import Perceptron
from sklearn.neighbors import NearestCentroid
from sklearn.linear_model import SGDClassifier
from sklearn.svm import LinearSVC
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn import metrics
from sklearn.model_selection import GridSearchCV
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

mydir = '/Users/wangxinzhe/Desktop/gsdmm/'
# 数据获取
jieba.load_userdict(mydir + "user_dict.txt")
jieba.load_userdict(mydir + "Chinese_dict.txt")

def get_database_list(sql):
    """获取数据库中数据函数
    根据sql语句获取数据库中内容

    Args：
        sql:数据库操作语句

    Returns:
        list:数据库中取出文本数据数组
    """
    connect = pymysql.connect(host=setting.MYSQL_HOST, db=setting.MYSQL_DBNAME, user=setting.MYSQL_USER,
                              passwd=setting.MYSQL_PASSWD, charset='utf8', use_unicode=True)
    cursor = connect.cursor()
    cursor.execute(sql)
    k = cursor.fetchall()
    f2 = open(mydir + 'result_file/aid_bid', 'w', encoding='UTF-8')
    data_list = {}
    dir = ''
    for li in k:
        dir = "byr_" + li[0] + "_" + li[1]
        f2.write(dir + "\n")
        data_list["%s" % dir] = (li[5].strip('\n') + " " + li[6].strip('\n'))
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

def get_path_text(data_path):
    """获取train or test 数据
    根据路径读取文件
    Args:
        data_path：数据路径
    """
    f = open(data_path, 'r', encoding='UTF-8')
    data_list = []
    for te in f.readlines():
        data_list.append(te.strip('\n'))
    return data_list


def get_kind_list(kind_path):
    """获取类别模块
    训练集、测试集 返回不同类别list

    Args:
        kind_path:训练集、测试集类别文档路径2
    """
    f = open(kind_path, 'r', encoding='UTF-8')
    kind_list = []
    for l in f.readlines():
        kind_list.append(l.strip('\n'))
    return kind_list

def compute_V(texts):
    V = set()
    for text in texts:
        for word in text:
            V.add(word)
    return len(V)

def get_chi_wordlist(data_list, kind_list):
    """卡方检验获取特征词
    Args:
        data_list:文本list
        kind_list:种类list
    """
    i = 0
    while i < len(data_list):
        data_list[i] = cut_text_data(data_list[i])
    model1 = SelectKBest(chi2, k=8000)  # 选择k个最佳特征
    word_l = model1.fit_transform(data_list, kind_list)
    print(word_l)

def cut_text_data(text):
    """文本分词模块
    利用分词工具进行文本分词，目前使用jieba分词，全模式
    TODO： 后面添加取出停用词功能

    Args:
        text:文本，未切分中文文本

    Returns:
        text_cut:切分完的文本词list
    """

    return jieba.cut(text, cut_all=True)

def execute_sql(sql):
    """获取数据库中数据函数
    根据sql语句获取数据库中内容

    Args：
        sql:数据库操作语句

    Returns:
        list:数据库中取出文本数据数组
    """
    connect = pymysql.connect(host=setting.MYSQL_HOST, db=setting.MYSQL_DBNAME, user=setting.MYSQL_USER,
                              passwd=setting.MYSQL_PASSWD, charset='utf8', use_unicode=True)
    cursor = connect.cursor()
    cursor.execute(sql)
    k = cursor.fetchall()
    return k

if __name__ == "__main__":
    #count = get_database_count("SELECT `group_id` FROM `article_backup` WHERE `post_time` > '2018-11-01' GROUP BY `group_id` HAVING COUNT(`group_id`) > 100")
    #print(len(count))
    #texts = get_database_list("SELECT * FROM `article_backup` WHERE `post_time` > '2018-11-01' AND `group_id` IN (SELECT `group_id` FROM `article_backup` WHERE `post_time` > '2018-11-01' GROUP BY `group_id` HAVING COUNT(`group_id`) > 100)")

    '''
        要求在运行脚本时输入时间，否则默认是今天开始的前一周数据
    '''
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
    print("正在预处理从" + start_time + "起一周内的所有数据。。。。。。。。。。")
    #texts = get_database_list("SELECT * FROM `article` WHERE `post_time` > " + "'" + start_time + "'")
    start_time = '2018-11-21 00:00:00'
    now_time = '2018-11-21 01:00:00'

    Ad_job = " AND `bid` NOT IN ('Ad_Agent', 'Advertising', 'BookTrade', 'BUPTDiscount', 'Co_Buying', 'ComputerTrade', 'House', 'House_Agent', 'Ticket', 'Consulting', 'FamilyLife', 'Financecareer', 'Home', 'IT', 'JobInfo', 'Jump', 'ParttimeJob', 'PMatBUPT', 'Score')"
    Manager_board = " AND `bid` NOT IN ('Advice', 'Announce', 'BBShelp', 'Bet', 'BM_Market', 'BYR12', 'Cooperation', 'ForumCommittee', 'ID', 'Progress', 'Score', 'sysop', 'test', 'notepad', 'vote', 'BM_Apply', 'BoardManager', 'OutstandingBM', 'Board_Apply', 'Board_Document', 'Board_Management', 'BYR', 'BYRStar', 'Showcase', 'cnAdmin', 'cnAnnounce', 'cnLists', 'cnTest', 'BYRCourt', 'Complain', 'Blessing', 'buptAUTA')"
    main_sql = "SELECT * FROM `article` WHERE `post_time` > '" + start_time + "' AND `post_time` < '" + now_time + "'"
    origin_texts, texts = get_database_list(main_sql + Ad_job + Manager_board)
    print("预处理完毕！")
    data_list = []
    temp_list = []

    #构造所有词的集合
    all_words = set()
    for key in texts:
        for word in texts[key].split():
            all_words.add(word)

    print(all_words)
    #去重与生成同义词
    cl = CilinSimilarity()
    my_output = ''
    for key in texts:
        temp_list.clear()
        my_output = ''
        for word in texts[key].split():
            if word not in temp_list:
                temp_list.append(word)
                my_output += word
                my_output += ' '
                # try:
                #     codes = cl.get_code(word)
                #     for eachcode in codes:
                #         if eachcode.endswith('='):
                #             for eachword in cl.code_word.get(eachcode):
                #                 if len(eachword) > 1 and eachword in all_words and not eachword in temp_list:
                #                     temp_list.append(eachword)
                #                     my_output += eachword
                #                     my_output += ' '
                # except:
                #     print('no synonyms')
        data_list.append(my_output)
        #存放进行分词后的帖子
        f4 = open(mydir + 'segments/' + "%s" % key, 'w', encoding='UTF-8')
        f4.write(my_output)
        f4.close()

    data_list = [text.split() for text in data_list]
    print("data_list: ")
    print(data_list)
    V = compute_V(data_list)
    mgp = MovieGroupProcess(K=50, n_iters=1000, alpha=0.02, beta=0.01)
    print("GSDMM算法开始！")
    y = mgp.fit(data_list, V)
    print("GSDMM算法结束！")
    #生成聚类的result字典，并且写入cluster_result文件
    result = {}
    aid_bid = [line_content.strip() for line_content in codecs.open(mydir + 'result_file/aid_bid')]
    f5 = open(mydir + 'result_file/cluster_result', 'w', encoding='UTF-8')
    for index in range(len(data_list)):
        z = mgp.choose_best_label(data_list[index])
        f5.write("%s" % aid_bid[index] + " " + "%s" % z[0] + "\n")
        result["%s" % aid_bid[index]] = z[0]
    print(result)

    # 处理result
    dir = ''
    for key in result:
        if result[key] != -1:
            dir = mydir + 'cluster_result_text/' + "%s" % result[key]
            if not os.path.exists(dir):
                os.makedirs(dir)
            f6 = open(dir + '/' + "%s" % key, 'w', encoding='UTF-8')
            f6.write(texts["%s" % key])
            f6.close()



