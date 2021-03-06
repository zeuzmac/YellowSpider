# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymongo
from scrapy.settings import Settings
from scrapy.exceptions import DropItem
from scrapy import log
from pymongo import ReturnDocument

class YellowPipeline(object):
	def __init__(self, mongo_uri, mongo_db, collection_name):
		self.mongo_uri = mongo_uri
		self.mongo_db = mongo_db
		self.collection_name = collection_name

	@classmethod
	def from_crawler(cls, crawler):
		return cls(
			mongo_uri=crawler.settings.get('MONGODB_SERVER'),
			mongo_db=crawler.settings.get('MONGODB_DB'),
			collection_name=crawler.settings.get('MONGODB_COLLECTION')
		)

	def open_spider(self, spider):
		log.msg("Open client", level=log.DEBUG, spider=spider)
		self.client = pymongo.MongoClient(self.mongo_uri)
		self.db = self.client[self.mongo_db]

	def close_spider(self, spider):
		log.msg("Close client", level=log.DEBUG, spider=spider)
		self.client.close()

	def process_item(self, item, spider):
		#self.db[self.collection_name].insert(dict(item))
		if('email' in item):
			self.db[self.collection_name].find_one_and_update(
				{ 'email': item['email'] }, #{ 'address': item['address'] },
				{ '$set': dict(item) },
				upsert=True)
			log.msg("Contact added to MongoDB database!", level=log.DEBUG, spider=spider)
		return item


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['id'])
            return item
