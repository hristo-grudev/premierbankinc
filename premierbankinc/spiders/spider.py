import re

import scrapy

from scrapy.loader import ItemLoader

from ..items import PremierbankincItem
from itemloaders.processors import TakeFirst


class PremierbankincSpider(scrapy.Spider):
	name = 'premierbankinc'
	start_urls = ['https://www.premierbankinc.com/News']

	def parse(self, response):
		post_links = response.xpath('//*[(@id = "dnn_RightWideSection1")]//a')
		for post in post_links:
			url = post.xpath('./@href').get()
			title = post.xpath('./text()').get()
			if url:
				yield response.follow(url, self.parse_post, cb_kwargs={'title': title})

		next_page = response.xpath('/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, title):
		description = response.xpath('//*[(@id = "dnn_LeftWidePane")]//text()[normalize-space()] | //*[(@id = "dnn_RightWideSection1")]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		# date = re.findall(r'[A-Za-z]+\s\d{1,2},\s\d{2,4}', description) or ['']

		item = ItemLoader(item=PremierbankincItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		# item.add_value('date', date[0])

		return item.load_item()
