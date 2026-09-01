from worker.scrapy.pipelines import BasePipeline

class OrderPipeline(BasePipeline):
    def process_item(self, item):
        return item
