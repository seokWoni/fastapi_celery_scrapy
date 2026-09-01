
import json
import scrapy

from worker.scrapy.spiders import BaseSpider

class OrderSpider(BaseSpider):
    name = "mall0001.order"

    custom_settings = {
        "ITEM_PIPELINES": {
            "worker.scrapy.pipelines.mall0001.order.OrderPipeline": 300,
        },
    }

    def start_requests(self):
        url = "https://mall0001.example.com/orders"

        yield scrapy.Request(
            url=url,
            callback=self.parse,
            meta=self.build_meta(),
        )

    def parse(self, response):
        response_body = response.body.decode(response.encoding)
        response_json = json.loads(response_body)

        yield {
            "orders": response_json
        }