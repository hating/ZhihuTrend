# -*- encoding:utf-8 -*-
import jieba.analyse
from ZHtrend.DB import db

if __name__ == "__main__":
    word = db.WFGetWord()
    l = []
    for i in word:
        l.append(i[0])
        l.append(i[1])
    seg_list = jieba.cut_for_search(" ".join(l))
    tags = jieba.analyse.extract_tags(" ".join(l), withWeight=True, topK=30000)
    db.WFUPloadWF(tags)
    print "已经成功生成词频。"
