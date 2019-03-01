#!/bin/bash

while read line
do
	bbs_name=$line
	echo $bbs_name
	cd /home/tensorflow/wangxinzhe/GSDMM-cluster
	/home/tensorflow/anaconda3/bin/python3 Main_Rust.py $bbs_name >> main.log

done < /home/tensorflow/wangxinzhe/bbs_to_run


#mkdir /home/user1/cluster/data
