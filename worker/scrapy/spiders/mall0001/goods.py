import json

import scrapy

from worker.scrapy.spiders import BaseSpider


class GoodsSpider(BaseSpider):
    name = "mall0001.goods"

    custom_settings = {
        "ITEM_PIPELINES": {
            "worker.scrapy.pipelines.mall0001.goods.GoodsPipeline": 300,
        },
    }

    def start_requests(self):
        url = f"https://mall0001.example.com/goods"
        yield scrapy.Request(url, callback=self.parse, meta=self.build_meta())

    def parse(self, response):
        response_body = response.body.decode(response.encoding)
        response_json = json.loads(response_body)

        yield {
            "goods": response_json,
        }
