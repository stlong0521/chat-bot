import scrapy

class SentenceSpider(scrapy.Spider):
    name = "sentence"
    start_urls = [
        'http://www.talkenglish.com/speaking/listbasics.aspx',
        'http://www.talkenglish.com/speaking/listregular.aspx',
    ]

    def parse(self, response):
        # Find urls in current page, and crawl them
        for link in response.xpath('//div[contains(@style, "padding-left:15px;")]/a'):
            url = response.urljoin(link.xpath('@href').extract_first())
            yield scrapy.Request(url, callback=self.parse)
        # Crawl regular sentences
        for sentence in response.xpath('//table[@id="GridView1"]/tr/td/a'):
            yield {
                'sentence': sentence.xpath('text()').extract_first().replace(u'\xa0', ''),
            }
        # Crawl conversations
        for sentence in response.xpath('//table[@border=0]/tr/td/text()').re(r'[AB]: \s*(.*)'):
            yield {
                'sentence': self._clean_string(sentence),
            }

    def _clean_string(self, string):
        if string.startswith('"') and string.endswith('"'):
            string = string[1:-1]
        return string.replace(u'\xa0', '')
