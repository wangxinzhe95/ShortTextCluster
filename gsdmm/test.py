from gsdmm import MovieGroupProcess
import time
import pymysql
import numpy as np
import jieba
import setting
import codecs
import re
from functools import reduce
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

# 数据获取
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
    f2 = open('/Users/wangxinzhe/Desktop/gsdmm/aid_bid', 'w', encoding='UTF-8')
    f3 = open('/Users/wangxinzhe/Desktop/gsdmm/texts', 'w', encoding='UTF-8')
    data_list = []
    for li in k:
        f2.write("byr_" + li[0] + "_" + li[1] + "\n")
        data_list.append(li[5].strip('\n') + " " + li[6].strip('\n'))
        f3.write(li[5].strip('\n') + li[6].strip('\n') + "\n=====================================\n")
    connect.commit()
    f2.close()
    f3.close()
    result_list=[]
    stopwords = {}.fromkeys([line_content.strip() for line_content in codecs.open('/Users/wangxinzhe/Desktop/gsdmm/stopword.txt')])  # 停用词表
    for li in data_list:
        seglist = jieba.cut(li, cut_all=False)  # 精确模式
        output = ''
        for segs in seglist:
            segs = segs.rstrip('\n')
            segs = segs.strip()
            seg = segs.lower()  # 英文字母小写
            if seg not in stopwords:  # 去停用词
                if not re.search('^[a-zA-Z-0-9]+$', seg) and len(seg) > 1:  # 去掉分词为1个字的结果
                    output += seg
                    output += ' '
        # print output
        result_list.append(output)
    return result_list


def get_database_incremental():
    """增量获取数据库中内容
    根据数据库中增量表来获取新的内容，配合定时使用

    Returns:
        list:数据库中取出的二维数组
    """


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
        kind_path:训练集、测试集类别文档路径
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


# 预处理
def preprocess_data_word2vec(data_list, kind_list, path):
    """数据预处理模块 根据词向量构建
    将输入文本list进行预处理，生成用于svm等分类器的格式数据(不含标签),并进行持久化

    Args:
        data_list: 输入的文本list，一条条文本数据
        kind_list: 输入文本的种类list
        path: 用于区分训练集 测试集 真实数据集
    """
    f = open(path, 'w', encoding='UTF-8')
    i = 0
    for text in data_list:
        text_cut = cut_text_data(text)
        word_vector_list = get_word_vector(text_cut)
        text_vector = get_text_vector(word_vector_list)
        vector_string = vector_format(text_vector)
        f.write(kind_list[i] + " " + vector_string)
        if i % 500 == 0:
            print(i)
        i = i + 1


# TODO 没有写完  根据词频构建向量待修改
def preprocess_data_cipin(data_list, kind_list, path):
    """数据预处理模块 根据词频来构建
    将输入文本list进行预处理，生成用于svm等分类器的格式数据(不含标签),并进行持久化

    Args:
        data_list: 输入的文本list，一条条文本数据
        kind_list: 输入文本的种类list
        path: 用于区分训练集 测试集 真实数据集
    """
    f = open(path, 'w', encoding='UTF-8')
    i = 0
    for text in data_list:
        text_cut = cut_text_data(text)
        word_vector_list = get_word_vector(text_cut)
        text_vector = get_text_vector(word_vector_list)
        vector_string = vector_format(text_vector)
        f.write(kind_list[i] + " " + vector_string)
        if i % 500 == 0:
            print(i)
        i = i + 1


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


def get_word_vector(text_cut):
    """词语词向量获取模块
    连接mysql数据库，根据词取出词向量值

    Args:
        text_cut: 文本词list

    Returns:
        word_vector_list:文本词向量list
    """
    connect = pymysql.connect(host=setting.VECTOR_MYSQL_HOST, db=setting.VECTOR_MYSQL_DBNAME,
                              user=setting.VECTOR_MYSQL_USER,
                              passwd=setting.VECTOR_MYSQL_PASSWD, charset='utf8', use_unicode=True)
    cursor = connect.cursor()
    vector_list = []
    for word in text_cut:
        if (cursor.execute("select vector from word_vector where word = %s", (word)) != 0):
            res = cursor.fetchall()
            # print(res[0][0])
            vector_list.append(list(map(float, res[0][0].split(" "))))
    return vector_list


def get_text_vector(word_vector_list):
    """句向量获取模块
    通过词向量获得句子向量，目前使用平均

    Args:
        word_vector_list:词向量list

    Returns:
        word_vector:句向量 200维
    """
    a = np.sum(word_vector_list, axis=0)
    a.tolist()
    number = len(word_vector_list)
    text_vector = [i / number for i in a]
    return text_vector

def vector_format(text_vector):
    """向量格式化模块
    将200维词向量格式成svm等分类器输入向量

    Args:
        text_vector:语句向量 一维数组 长度 200

    Returns:
        vector_string: 字符串，格式同svm等分类器输入向量,结尾有\n用于持久化到文件
    """
    vector_string = ""
    i = 1
    for vector in text_vector:
        vector_string = vector_string + str(i) + ":" + str(vector) + " "
        i = i + 1
    return vector_string + "\n"


if __name__ == "__main__":
    #texts = get_database_list("SELECT * FROM `article_backup` WHERE `post_time` > '2018-11-01' AND `group_id` IN (SELECT `group_id` FROM `article_backup` WHERE `post_time` > '2018-11-01' GROUP BY `group_id` HAVING COUNT(`group_id`) > 120)")
    texts = get_database_list("SELECT * FROM `article` WHERE `post_time` > '2018-11-08'")
    print(texts)
    data_list = []
    temp_list = []
    #去重
    my_output = ''
    num = 0
    for text in texts:
        temp_list.clear()
        my_output = ''
        num = num + 1
        for word in text.split():
            if word not in temp_list:
                temp_list.append(word)
                my_output += word
                my_output += ' '
        data_list.append(my_output)
        # f4 = open('/Users/wangxinzhe/Desktop/gsdmm/segments/' + "%d" % num, 'w', encoding='UTF-8')
        # f4.write(my_output)
        # f4.close()
    data_list = [text.split() for text in data_list]
    print(data_list)
    V = compute_V(data_list)
    mgp = MovieGroupProcess(K=100, n_iters=10, alpha=0.2, beta=0.01)
    y = mgp.fit(data_list, V)
    print(len(y))
    result = {}

    aid_bid = [line_content.strip() for line_content in codecs.open('/Users/wangxinzhe/Desktop/gsdmm/aid_bid')]
    lf = open('/Users/wangxinzhe/Desktop/gsdmm/cluster_result', 'w', encoding='UTF-8')
    for index in range(len(data_list)):
        z = mgp.choose_best_label(data_list[index])
        lf.write("%s" % aid_bid[index] + " " + "%s" % z[0] + "\n")
        result["%s" % aid_bid[index]] = z[0]
    print(result)

