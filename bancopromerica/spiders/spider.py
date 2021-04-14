import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbancopromericaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BbancopromericaSpider(scrapy.Spider):
	name = 'bancopromerica'
	start_urls = ['https://www.bancopromerica.com.gt/quienes-somos/noticias/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="row"]//h2/a[@class="newlink"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = ''.join(response.xpath('//div[@class="col-xs-12"]/p[position()<3]/text()').getall())
		date = re.findall(r'\d+\sde\s\w+\s\d+', date)
		if not date:
			date = "Date is not published"
		title = response.xpath('//h6/text()').get()
		content = response.xpath('(//div[@class="col-xs-12"])[last()]//text()[not (ancestor::h6)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BbancopromericaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
