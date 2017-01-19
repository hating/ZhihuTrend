# -*- encoding:utf-8-*-
import os
import sys
import datetime
import scrapy, re
from ZHtrend.DB import db


class ActivitySpider(scrapy.Spider):
    name = "activity"

    def start_requests(self):
        reload(sys)
        sys.setdefaultencoding('gbk')
        # db.SpiderActivityCreateDB()
        id = db.SpiderActivityGetID()
        for i in id:
            url = "https://www.zhihu.com/people/" + i[0] + "/answers"
            yield scrapy.Request(url=url, callback=lambda response,: self.parseAnswer(response, i[0]))

    def parseAnswer(self, response, id):
        question = response.css(".ContentItem-title").re('href="(.*)">')
        for i in question:
            url = "https://www.zhihu.com" + i
            yield scrapy.Request(url=url, callback=lambda response,: self.parseQuestion(response, id))

    def parseQuestion(self, response, id):
        filename = os.path.dirname(__file__) + "\\test\\" + id + "_.html"
        with open(filename, 'wb') as f:
            f.write(response.body)

        questionId = response.url.split("/")[-3]
        answerId = response.url.split("/")[-1]
        if not response.xpath('//*[@id="zh-question-title"]/h2/a').re(">\n(.*)\n</a>"):
            return
        title = response.xpath('//*[@id="zh-question-title"]/h2/a').re(">\n(.*)\n</a>")[0]
        total = response.css('.zh-answers-title').re(">查看全部 (.*) 个回答<".decode("utf-8"))[0]
        approve = response.xpath('//*[@id="zh-question-answer-wrap"]/div/div[1]/button[1]/span[1]').re(">(.*)<")[0]

        content = response.css(".zm-editable-content").extract()[
            len(response.css(".zm-editable-content").extract()) - 1]
        posttime = ""
        if response.css('.answer-date-link').re('发布于 (.*)" target="_blank"'.decode("utf-8")):
            posttime = response.css('.answer-date-link').re('发布于 (.*)" target="_blank"'.decode("utf-8"))[0]
        else:
            posttime = response.css('.answer-date-link').re('发布于 (.*)</a>'.decode("utf-8"))[0]
        edittime = posttime
        if response.xpath('//*[@id="zh-question-answer-wrap"]/div/div[4]/div/a[1]').re('编辑于 (.*)</a>'.decode("utf-8")):
            edittime = \
                response.xpath('//*[@id="zh-question-answer-wrap"]/div/div[4]/div/a[1]').re(
                    '编辑于 (.*)</a>'.decode("utf-8"))[
                    0]
        posttime = self.formatDate(posttime)
        edittime = self.formatDate(edittime)
        comment = 0
        if response.xpath('//*[@id="zh-question-answer-wrap"]/div/div[4]/div/a[2]').re("</i>(.*) 条评论".decode("utf-8")):
            comment = \
                response.xpath('//*[@id="zh-question-answer-wrap"]/div/div[4]/div/a[2]').re(
                    "</i>(.*) 条评论".decode("utf-8"))[
                    0]
        db.SpiderActivityInsert(
            id, questionId, answerId, title, total, approve, content, posttime, edittime, comment)
        os.remove(filename)

    def formatDate(self, pre):
        today = datetime.datetime.now()
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=2))
        ret = ""
        if re.search("昨天".decode("utf-8"), pre):
            ret = yesterday.strftime("%Y-%m-%d ") + pre[4:] + ":00"
        elif re.search("[012][0-9]:[0-5][0-9]", pre):
            ret = today.strftime("%Y-%m-%d ") + pre[4:] + ":00"
        else:
            ret = pre + " 00:00:00"
        return ret
