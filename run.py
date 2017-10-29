# coding:utf-8
# __author__ = 'qshine'


from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
process = CrawlerProcess(get_project_settings())

from Zhihu.spiders.zhihu_user import ZhihuUserSpider

process.crawl(ZhihuUserSpider)
process.start()
