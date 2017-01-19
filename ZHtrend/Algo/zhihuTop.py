# -*- encoding:utf-8 -*-
import time, datetime
from scrapy.crawler import CrawlerProcess
from ZHtrend.spiders import activity
from scrapy.utils.project import get_project_settings
import sys

sys.path.append("..")

from ZHtrend.DB import db


def UpdateTrend():
    questionids = db.AlgoGetQuestionIDs()
    allRank = []
    for questionid in questionids:
        ids = db.AlgoGetQuestionID(questionid)
        rank = 0
        for id in ids:
            rankStr = db.AlgoGetFollowers(id)
            if rankStr != ():
                rank += rankStr[0][0]
            else:
                rank += 0
        allRank.append((questionid[0], rank))
    allRank.sort(lambda x, y: cmp(y[1], x[1]))
    today = datetime.datetime.now()
    table = "trend_" + today.strftime("%Y_%m_%d")
    db.AlgoDropTable()
    db.AlgoCreateTable()
    db.AlgoInsertTable(allRank)
    db.AlgoSwitchTable(table)
    print "已经生成最新的趋势。"


if __name__ == "__main__":
    i = 0
    process = CrawlerProcess(get_project_settings())
    process.start()
    while True:
        process.crawl(activity.ActivitySpider)
        UpdateTrend()
        time.sleep(3600)
