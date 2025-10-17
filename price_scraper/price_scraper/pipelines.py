# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


# class PriceScraperPipeline:
#     def process_item(self, item, spider):
#         return item



# price_scraper/pipelines.py

import pymongo

class MongoPipeline:

    def __init__(self):
        # 1. Connect to the MongoDB server
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        # 2. Select the database
        self.db = self.client['price_tracker_db']
        # 3. Select the collection
        self.collection = self.db['products']

    def process_item(self, item, spider):
        # This method is called for every item scraped by any spider.
        # We simply insert the item (which is a dict) into our collection.
        self.collection.insert_one(dict(item))
        return item # It's good practice to return the item for other pipelines

    def close_spider(self, spider):
        # This method is called when the spider finishes.
        # We close the connection to the database.
        self.client.close()