# -*- encoding:utf-8-*-
import os, scrapy, sys
from ZHtrend.DB import db


class UserSpider(scrapy.Spider):
    name = "user"
    resume = True
    ids = []

    def start_requests(self):
        reload(sys)
        sys.setdefaultencoding('gbk')
        try:
            self.ids = [i[0] for i in db.SpiderUserGetIDs()]
        except:
            db.SpiderUserCreateDB()
        if not self.ids:
            self.ids = ["wind", "zeng-kai-87", "tan-wu-yu-33", "jixin", "zhang-xiao-feng-86-35", "yueyihe"]
            self.resume = False
        for id in self.ids:
            if self.resume:
                url = "https://www.zhihu.com/people/" + id + "/following"
                yield scrapy.Request(url=url,
                                     callback=self.parseRemainFollowing)
            else:
                url = 'https://www.zhihu.com/people/' + id + '/answers'
                yield scrapy.Request(url=url, callback=self.parseAnswer)

    def parseRemainFollowing(self, response):
        res = response.css(".UserLink-link").re('href="([^\s]*)"')
        urls = []
        for i in range(0, len(res) / 2):
            if res[i * 2][8:] in self.ids:
                continue
            urls.append('https://www.zhihu.com' + res[i * 2] + '/answers')
        for url in urls:
            yield scrapy.Request(url=url,
                                 callback=self.parseAnswer)

    def parseAnswer(self, response):
        id = response.url.split("/")[-2]
        if self.resume and id in self.ids:
            return
        filename = os.path.dirname(__file__) + "\\fail\\" + id + ".html"
        with open(filename, 'wb') as f:
            f.write(response.body)

        name = response.css(".ProfileHeader-name").re(">(.*)<")[0]
        description = []
        if response.css(".ProfileHeader-headline").re(">(.*)<") != []:
            description = response.css(".ProfileHeader-headline").re(">(.*)<")[0]
        profession = " ".join(response.css(".ProfileHeader-infoItem::text").extract())
        if response.css(".List-headerText").re("<span>(.*)的回答".decode("utf-8"))[0] == "她".decode("utf-8"):
            sex = "female"
        else:
            sex = "male"
        answer = response.css(".Tabs-meta::text")[0].extract()
        share = response.css(".Tabs-meta::text")[1].extract()
        question = response.css(".Tabs-meta::text")[2].extract()
        collection = response.css(".Tabs-meta::text")[3].extract()
        receiveupprove = 0
        receivethank = 0
        receivecollect = 0
        if response.css(".IconGraf").re("获得 ([0-9]{1,}) 次赞同".decode("utf-8")) != []:
            receiveupprove = response.css(".IconGraf").re("获得 ([0-9]{1,}) 次赞同".decode("utf-8"))[0]
        if response.css(".Profile-sideColumnItemValue").re("获得 ([0-9]{1,}) 次".decode("utf-8")) != []:
            receivethank = response.css(".Profile-sideColumnItemValue").re("获得 ([0-9]{1,}) 次".decode("utf-8"))[0]
        if response.css(".Profile-sideColumnItemValue").re("，([0-9]{1,}) 次收藏".decode("utf-8")) != []:
            receivecollect = response.css(".Profile-sideColumnItemValue").re("，([0-9]{1,}) 次收藏".decode("utf-8"))[0]
        follower = response.css(".NumberBoard-value").re(">([0-9]{1,})<")[1]
        following = response.css(".NumberBoard-value").re(">([0-9]{1,})<")[0]
        spsonsorlive = 0
        interesttopic = 0
        interestcolumn = 0
        interestquestion = 0
        interestcollection = 0
        if response.xpath('//*[@id="root"]/div/main/div/div/div[2]/div[2]/div[3]/a[contains(@href, "lives")]').re(
                ">([0-9]{1,})<"):
            spsonsorlive = \
                response.xpath('//*[@id="root"]/div/main/div/div/div[2]/div[2]/div[3]/a[contains(@href, "lives")]').re(
                    ">([0-9]{1,})<")[0]
        if response.xpath('//*[@id="root"]/div/main/div/div/div[2]/div[2]/div[3]/a[contains(@href, "topics")]').re(
                ">([0-9]{1,})<"):
            interesttopic = \
                response.xpath('//*[@id="root"]/div/main/div/div/div[2]/div[2]/div[3]/a[contains(@href, "topics")]').re(
                    ">([0-9]{1,})<")[0]
        if response.xpath('//*[@id="root"]/div/main/div/div/div[2]/div[2]/div[3]/a[contains(@href, "columns")]').re(
                ">([0-9]{1,})<"):
            interestcolumn = \
                response.xpath(
                    '//*[@id="root"]/div/main/div/div/div[2]/div[2]/div[3]/a[contains(@href, "columns")]').re(
                    ">([0-9]{1,})<")[0]
        if response.xpath('//*[@id="root"]/div/main/div/div/div[2]/div[2]/div[3]/a[contains(@href, "questions")]').re(
                ">([0-9]{1,})<"):
            interestquestion = \
                response.xpath(
                    '//*[@id="root"]/div/main/div/div/div[2]/div[2]/div[3]/a[contains(@href, "questions")]').re(
                    ">([0-9]{1,})<")[0]
        if response.xpath('//*[@id="root"]/div/main/div/div/div[2]/div[2]/div[3]/a[contains(@href, "collections")]').re(
                ">([0-9]{1,})<"):
            interestcollection = response.xpath(
                '//*[@id="root"]/div/main/div/div/div[2]/div[2]/div[3]/a[contains(@href, "collections")]').re(
                ">([0-9]{1,})<")[0]
        db.SpiderUserInsert(id, name, description, profession, sex, answer, share, question, collection,
                            receiveupprove,
                            receivethank, receivecollect, follower, following, spsonsorlive, interesttopic,
                            interestcolumn,
                            interestquestion, interestcollection)

        os.remove(filename)

        url = "https://www.zhihu.com/people/" + id + "/following"
        yield scrapy.Request(url=url,
                             callback=self.parseFollowing)

    def parseFollowing(self, response):
        res = response.css(".UserLink-link").re('href="([^\s]*)"')
        urls = []
        for i in range(0, len(res) / 2):
            if res[i * 2][8:] in self.ids and self.resume:
                continue
            urls.append('https://www.zhihu.com' + res[i * 2] + '/answers')
        for url in urls:
            yield scrapy.Request(url=url,
                                 callback=self.parseAnswer)
