#!usr/bin/python
# -*- coding:utf-8 -*-
from Viterbi import *
import os
import time
import sys
import multiprocessing
# 测试分词算法，基于HMM模型的分词算法
# ChineseCutStr("我是一个中国人")
# 对搜狗预料库中的文本进行分词处理
ABSPATH = os.path.abspath(sys.argv[0])
ABSPATH=os.path.dirname(ABSPATH) + '/'
print ABSPATH

ClassCode = ['aoyun', 'fangchan', 'hulianwang', 'jiankang', 'jiaoyu', 'lvyou',  'qiche', 'shangye', 'shishang', 'tiyu', 'yule']
folderTextCount = 50000 # 在这里只选择搜狗预料库中的每个分类下的300个文本进行分词处理
# readFilePathPrefix = "G:\\ChineseTextClassify\\SogouC\\ClassFile\\"
readFilePathPrefix = os.path.dirname(os.path.abspath('__file__')).strip("ChineseSegmentation")+"sogou_all3\\"
# writeFilePathPrefix = "G:\\ChineseTextClassify\\SogouCCut\\"
writeFilePathPrefix = os.path.dirname(os.path.abspath('__file__')).strip("ChineseSegmentation") + "SogouallCut\\"
def cutText(index):
    test_file_path = os.path.dirname(os.path.abspath('__file__')).strip("ChineseSegmentation")+"sogou_all3\\" + index + "\\"
    print test_file_path
    file_list = os.listdir(test_file_path)
    print len(file_list)
    for i in xrange(0,len(file_list)):
    #for i in range(0, folderTextCount):
        if i%1000 == 0:
            print index + str(i)+ ".txt"
        readfilename = readFilePathPrefix+index+"\\"+str(i)+".txt"
        writefilename = writeFilePathPrefix+index+"\\"+str(i)+".txt"
        ChineseCut(readfilename, writefilename)

            
            


if __name__ == '__main__':
    #print "all beign %s" %ctime()
    #lock = multiprocessing.Lock() 
    p = multiprocessing.Pool(len(ClassCode))
    for canshu in ClassCode:
        p.apply_async(func = cutText,args=(canshu,))
    
    start = time.time()
    print "all beign %s" %start
    print(' [+] much process start')
    p.close()#关闭进程池
    p.join()#等待所有子进程完毕
    print(' [-] much process use ',time.time()-start,'s')
