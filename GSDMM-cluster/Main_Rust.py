import datetime
import pymysql
import jieba
import jieba.posseg as psg
import setting
import codecs
import re
import os
import sys
from cilin import CilinSimilarity

mydir = '/home/tensorflow/wangxinzhe/'
# 数据获取
jieba.load_userdict(mydir + "user_dict.txt")
jieba.load_userdict(mydir + "Chinese_dict.txt")

def get_database_list(time_interval, sql, data_source):
    """获取数据库中数据函数
    根据sql语句获取数据库中内容

    Args：
        sql:数据库操作语句

    Returns:
        list:数据库中取出文本数据数组
    """
    data_list = {}
    dir_name = 'result_file/aid_bid'
    if (time_interval == 'monthly'):
        dir_name = 'result_file_monthly/aid_bid'

    f2 = open(mydir + dir_name, 'w', encoding='UTF-8')

    dir_name_text = 'texts/'
    if (time_interval == 'monthly'):
        dir_name_text = 'texts_monthly/'

    for eachterm in data_source.split(","):
        if eachterm.startswith('all'):
            temp_var = 'setting' + '.' + eachterm
            new_data_source = eval(temp_var)
            for eachterm in new_data_source.split(','):
                connect = pymysql.connect(host=setting.MYSQL_HOST, db=setting.MYSQL_DBNAME + eachterm,
                                          user=setting.MYSQL_USER,
                                          passwd=setting.MYSQL_PASSWD, charset='utf8', use_unicode=True)
                cursor = connect.cursor()
                cursor.execute(sql)
                k = cursor.fetchall()
                dir = ''
                for li in k:
                    dir = eachterm + "_" + li[0] + "_" + li[1]
                    f2.write(dir + "\n")
                    data_list["%s" % dir] = (li[5].strip('\n') + " " + li[6].strip('\n'))
                    # 存放进行分词前的文本
                    f3 = open(mydir + dir_name_text + "%s" % dir, 'w', encoding='UTF-8')
                    f3.write(li[5].strip('\n') + "\n" + li[6].strip('\n'))
                    f3.close()
                connect.commit()
                connect.close()
        else:
            connect = pymysql.connect(host=setting.MYSQL_HOST, db=setting.MYSQL_DBNAME + eachterm, user=setting.MYSQL_USER,
                                      passwd=setting.MYSQL_PASSWD, charset='utf8', use_unicode=True)
            cursor = connect.cursor()
            cursor.execute(sql)
            k = cursor.fetchall()
            dir = ''
            for li in k:
                dir = eachterm + "_" + li[0] + "_" + li[1]
                f2.write(dir + "\n")
                data_list["%s" % dir] = (li[5].strip('\n') + " " + li[6].strip('\n'))
                #存放进行分词前的文本
                f3 = open(mydir + dir_name_text + "%s" % dir, 'w', encoding='UTF-8')
                f3.write(li[5].strip('\n') + "\n" + li[6].strip('\n'))
                f3.close()
            connect.commit()
            connect.close()
    f2.close()
    return data_list

def get_database_list_from_file(time_interval, textCutBasePath):
    dir_name = 'result_file/aid_bid'
    if (time_interval == 'monthly'):
        dir_name = 'result_file_monthly/aid_bid'

    f2 = open(mydir + dir_name, 'w', encoding='UTF-8')
    data_list = {}
    for root, dirs, files in os.walk(textCutBasePath):
        for file in files:
            if not (file.startswith('.')):
                f2.write(file + "\n")
                eachFileContent = ''
                eachFileObj = open(root + '/' + file, 'r', encoding='UTF-8')
                for line in eachFileObj.readlines():
                    eachFileContent += line
                data_list["%s" % file] = eachFileContent
    f2.close()
    print(data_list)
    return data_list

def segment_word(data_list):
    result_list = {}
    stopwords = {}.fromkeys([line_content.strip() for line_content in codecs.open(mydir + 'stopword.txt')])  # 停用词表
    # 包含中文的正则模版
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
            if seg == 'wyy':
                output += '王远阳'
                output += ' '
            elif (seg not in stopwords) and (
            flag.startswith(('a', 'f', 'j', 'l', 'm', 'n', 'q', 't', 'v'))):  # 去停用词,并且过滤指定词性的词
                # if seg not in stopwords:  # 去停用词
                if not re.search('^[a-zA-Z-0-9]+$', seg) and len(seg) > 1 and zhPattern.search(seg):  # 去掉分词为1个字的结果
                    output += seg
                    output += ' '
        # print output
        result_list["%s" % li] = output
    return result_list

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
    # texts = get_database_list("SELECT * FROM `article_backup` WHERE `post_time` > '2018-11-01' AND `group_id` IN (SELECT `group_id` FROM `article_backup` WHERE `post_time` > '2018-11-01' GROUP BY `group_id` HAVING COUNT(`group_id`) > 100)")
    '''
        要求在运行脚本时输入时间，否则默认是今天开始的前一周数据
    '''

    if (len(sys.argv) == 1):
        data_source = "byr"
        time_interval = "weekly"
    elif (len(sys.argv) == 2):
        data_source = sys.argv[1]
        time_interval = "weekly"
    else:
        data_source = sys.argv[1]
        time_interval = sys.argv[2]

    # 初始化
    if (time_interval == 'monthly'):
        os.system('sh ' + mydir + 'init_monthly.sh')
    else:
        os.system('sh ' + mydir + 'init.sh')

    now_time = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d'), "%Y-%m-%d")
    start_time = now_time + datetime.timedelta(days=-7)
    if (time_interval == 'monthly'):
        start_time = now_time + datetime.timedelta(days=-30)
    start_time = start_time.strftime('%Y-%m-%d')
    now_time = now_time.strftime('%Y-%m-%d')
    print("正在预处理从" + start_time + "起至" + now_time + "内的所有数据。。。。。。。。。。")
    hot_count = "100"
    Ad_job = " AND `bid` NOT IN ('Ad_Agent', 'Advertising', 'BookTrade', 'BUPTDiscount', 'Co_Buying', 'ComputerTrade', 'House', 'House_Agent', 'Ticket', 'Consulting', 'FamilyLife', 'Financecareer', 'Home', 'IT', 'JobInfo', 'Jump', 'ParttimeJob', 'PMatBUPT', 'Score')"
    Manager_board = " AND `bid` NOT IN ('Advice', 'Announce', 'BBShelp', 'Bet', 'BM_Market', 'BYR12', 'Cooperation', 'ForumCommittee', 'ID', 'Progress', 'Score', 'sysop', 'test', 'notepad', 'vote', 'BM_Apply', 'BoardManager', 'OutstandingBM', 'Board_Apply', 'Board_Document', 'Board_Management', 'BYR', 'BYRStar', 'Showcase', 'cnAdmin', 'cnAnnounce', 'cnLists', 'cnTest', 'BYRCourt', 'Complain', 'Blessing', 'buptAUTA')"
    main_sql = "SELECT * FROM `article` WHERE `post_time` > '" + start_time + "' AND `post_time` < '" + now_time + "'"

    #从数据库拿数据
    origin_texts = get_database_list(time_interval, main_sql + Ad_job + Manager_board, data_source)

    #直接从文件夹里拿数据
    if (time_interval == 'monthly'):
        textCutBasePath = mydir + 'texts_monthly/'
    else:
        textCutBasePath = mydir + 'texts/'
    # origin_texts = get_database_list_from_file(time_interval, textCutBasePath)

    texts = segment_word(origin_texts)

    count_sql = "SELECT `group_id` FROM `article` WHERE `post_time` > '" + start_time + "' AND `post_time` < '" + now_time + "' GROUP BY `group_id` HAVING COUNT(`group_id`) > " + hot_count
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

    segments_dir = 'segments/'
    if (time_interval == 'monthly'):
        segments_dir = 'segments_monthly/'

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
                #                     word_property = psg.cut(eachword)
                #                     for word in word_property:
                #                         if word.flag.startswith('n'):
                #                             temp_list.append(eachword)
                #                             my_output += eachword
                #                             my_output += ' '
                # except:
                #     print('no synonyms')
        data_list.append(my_output.strip(' '))
        #存放进行分词后的帖子
        f4 = open(mydir + segments_dir + "%s" % key, 'w', encoding='UTF-8')
        f4.write(my_output.strip(' '))
        f4.close()

    data_list = [text.split() for text in data_list]
    print("data_list: ")
    print(data_list)

    rust_dir = '/home/tensorflow/wangxinzhe/GSDMM-cluster_Rust-version/gsdmm-rust/examples/byr'
    if (time_interval == 'monthly'):
        rust_dir += '_monthly'

    f8 = open(rust_dir + '/vocab.txt', 'w', encoding='UTF-8')
    for eachword in all_words:
        f8.write(eachword + '\n')
    f8.close()

    f7 = open(rust_dir + '/docs.txt', 'w', encoding='UTF-8')
    for eachfile in data_list:
        output = ''
        for eachword in eachfile:
            output += eachword
            output += ' '
        f7.write(output.strip() + '\n')
    f7.close()

    print("GSDMM算法开始！")

    count = 50
    if (time_interval == 'monthly'):
        os.system('sh ' + mydir + 'gsdmm-rust_monthly.sh ' + "%d" % count)
    else:
        os.system('sh ' + mydir + 'gsdmm-rust.sh ' + "%d" % count)
    print("GSDMM算法结束！")
    #生成聚类的result字典，并且写入cluster_result文件

    result = {}
    result_dir = 'result_file'
    if (time_interval == 'monthly'):
        result_dir += '_monthly'

    aid_bid = [line_content.strip() for line_content in codecs.open(mydir + result_dir + '/aid_bid')]

    if (time_interval == 'monthly'):
        f9 = open('/home/tensorflow/wangxinzhe/GSDMM-cluster_Rust-version/gsdmm-rust/examples/grades_out_monthly_labels.csv', 'r', encoding='UTF-8')
    else:
        f9 = open('/home/tensorflow/wangxinzhe/GSDMM-cluster_Rust-version/gsdmm-rust/examples/grades_out_labels.csv', 'r', encoding='UTF-8')


    label_list = []
    for te in f9.readlines():
        label_list.append(te.strip('\n').split(','))

    f5 = open(mydir + result_dir + '/cluster_result', 'w', encoding='UTF-8')
    for index in range(len(label_list)):
        if float(label_list[index][1]) > 0.95:
            f5.write("%s" % aid_bid[index] + " " + "%s" % label_list[index][0] + "\n")
            result["%s" % aid_bid[index]] = label_list[index][0]
        else:
            f5.write("%s" % aid_bid[index] + " " + "%s" % "-1" + "\n")
            result["%s" % aid_bid[index]] = -1
    print(result)

    # 处理result
    dir = ''
    cluster_result_dir = 'cluster_result_text'
    if (time_interval == 'monthly'):
        cluster_result_dir += '_monthly'
    for key in result:
        if result[key] != -1:
            dir = mydir + cluster_result_dir + '/' + "%s" % result[key]
            if not os.path.exists(dir):
                os.makedirs(dir)
            f6 = open(dir + '/' + "%s" % key, 'w', encoding='UTF-8')
            f6.write(texts["%s" % key].strip(' '))
            f6.close()



