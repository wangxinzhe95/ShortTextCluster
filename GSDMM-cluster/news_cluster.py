#-*- coding:utf-8 -*-
import jieba
import jieba.posseg as psg
from cilin import CilinSimilarity
import os
from textrank4zh import TextRank4Keyword, TextRank4Sentence
tr4w = TextRank4Keyword()
text = '2018年11月7日下午15:30，网络空间安全学院2018级研究生新生引航工程之心理团体辅导于教三305教室举行。本次心理讲座由网络空间安全学院心理顾问幸宇光老师主讲，全体2018级研究生新生参与了本次讲座。讲座开始，幸宇光老师首先表达了对来自五湖四海的同学的欢迎。紧接着幸宇光老师用一个游戏——“从相遇开始”让同学们彼此熟悉。同学们互相介绍自己的姓名、家乡、爱好，教室内一片欢声笑语。同学们从两人小组开始，彼此从陌生到相互了解；小组之间彼此进行介绍，同学们互相之间成为了能够一起谈笑的朋友。随后各个小组上台进行交流，介绍了自己组员的共同点，并摆出姿势进行合影留念。虽然活动的时间很短，但用心的交流让同学们之间形成了一种默契，也相信同学们能够在未来的生活中将这份友情维持下去，同时交到更多的朋友。随后进行第二个环节，幸宇光老师让同学们在纸上写下自己人生中遇到的困难和自己的解决办法。幸宇光老师旨在让同学们回顾自己克服困难的历程的同时，总结自己克服困难的经验，并勇于克服困难。在最后一个环节，幸宇光老师向同学们介绍了学校和学院为同学们的心理问题做出的保障，并建议同学们在遇到困难时积极寻求帮助。同时幸宇光老师向同学们提出了保持好心情的建议，并祝愿同学们享受研究生生活。相信通过本次团体辅导，更多的研究生新生们能够对自己有更加深刻的了解，能够对自己的心理问题及时干预并做出调整，始终热情饱满的面对生活。'
tr4w.analyze(text=text, lower=True, window=2)
tr4s = TextRank4Sentence()
tr4s.analyze(text=text, lower=True, source = 'all_filters')
print( '关键词：' )
for item in tr4w.get_keywords(20, word_min_len=1):
    print(item.word, item.weight)

print()
print( '关键短语：' )
for phrase in tr4w.get_keyphrases(keywords_num=20, min_occur_num= 3):
    print(phrase)
print( '摘要：' )
for item in tr4s.get_key_sentences(num=2):
    print(item.index, item.weight, item.sentence)
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