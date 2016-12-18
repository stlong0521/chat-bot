import scrapy
import re
import json
import os

class FriendsScriptsSpider(scrapy.Spider):
    name = "friends-scripts"
    start_urls = [
        'http://www.livesinabox.com/friends/scripts.shtml',
    ]

    def parse(self, response):
        if response.url == "http://www.livesinabox.com/friends/scripts.shtml":
            # Find urls in current page, and crawl them
            for link in response.xpath('//li').xpath('.//a'):
                url = response.urljoin(link.xpath('@href').extract_first())
                yield scrapy.Request(url, callback=self.parse)
        else:
            # Crawl scripts
            lines = []
            for para in response.xpath('//p').xpath('string()').extract():
                for line in re.split(" *\n *\n *", para):
                    if (line.startswith('[') and line.endswith(']') or \
                        line.startswith('(') and line.endswith(')')):
                        continue
                    line = self._clean_line(line)
                    role_and_line = re.split(": *", line, 1)
                    if len(role_and_line) == 2 and role_and_line[1].strip() != "" \
                       and len(role_and_line[0]) < 10: # A name should be short
                        lines.append({
                            role_and_line[0].strip(): role_and_line[1].strip(),
                        })
            relative_path = response.url.replace("http://www.livesinabox.com/friends/", "") \
                                        .split(".")[0] + ".json"
            path_and_name = relative_path.split("/")
            if len(path_and_name) == 2:
                json_file_name = path_and_name[1]
                path_to_save = os.path.join("../data/friends-scripts", path_and_name[0])
            else:
                json_file_name = path_and_name[0]
                path_to_save = os.path.join("../data/friends-scripts", "season10")
            if not os.path.exists(path_to_save):
                os.makedirs(path_to_save)
            with open(os.path.join(path_to_save, json_file_name), "w") as json_file:
                json.dump(lines, json_file)

    def _clean_line(self, line):
        # Hard line break ('\n') -> space
        # Non-breaking space (u'\xa0') -> ""
        # Special "'" (u'\x92') -> "'"
        line = line.replace('\n', ' ') \
                   .replace(u'\xa0', '') \
                   .replace(u'\x92', "'")
        line = re.sub(r'[^\x00-\x7F]+', ' ', line) # Any other weird characters -> space
        return re.sub(" *[\(\[].*?[\)\]] *", " ", line) # Remove scene descriptions with brackets
