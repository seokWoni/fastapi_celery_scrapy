from worker.scrapy.pipelines import BasePipeline

class GoodsPipeline(BasePipeline):
    def process_item(self, item):
        return item
