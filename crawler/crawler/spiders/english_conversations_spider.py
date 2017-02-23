import scrapy
import re
import json
import os

class EnglishConversationsSpider(scrapy.Spider):
    name = "english-conversations"
    start_urls = [
        'http://www.agendaweb.org/listening/practical-english-conversations.html',
    ]

    def parse(self, response):
        if response.url == "http://www.agendaweb.org/listening/practical-english-conversations.html":
            # Find urls in current page, and crawl them
            for link in response.xpath('//li').xpath('.//a'):
                url = link.xpath('@href').extract_first()
                yield scrapy.Request(url, callback=self.parse)
        elif not re.compile("[\d]+").search(response.url):
            # Find urls in current page, and crawl them
            for link in response.xpath('//blockquote').xpath('.//a'):
                url = response.urljoin(link.xpath('@href').extract_first())
                yield scrapy.Request(url, callback=self.parse)
        else:
            # Crawl conversations
            lines = []
            for line in response.xpath('//font[@size="5"]/text()').extract():
                if "\n" in line or re.compile("^[\d ]+$").match(line):
                    continue
                if line == "Repeat":
                    lines.append("Scene divider")
                else:
                    lines.append(line.strip())
            relative_path = response.url.replace("http://www.eslfast.com/robot/topics/", "") \
                                        .split(".")[0] + ".json"
            path_and_name = relative_path.split("/")
            path_to_save = os.path.join("../data/english-conversations", path_and_name[0])
            if not os.path.exists(path_to_save):
                os.makedirs(path_to_save)
            with open(os.path.join(path_to_save, path_and_name[1]), "w") as json_file:
                json.dump(lines, json_file)
