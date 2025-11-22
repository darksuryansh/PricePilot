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

import os
import pymongo

# class MongoPipeline:

#     def __init__(self):
#         # 1. Connect to the MongoDB server
#         self.client = pymongo.MongoClient('mongodb://localhost:27017/')
#         # 2. Select the database
#         self.db = self.client['price_tracker_db']
#         # 3. Select the collection
#         self.collection = self.db['products']

#     def process_item(self, item, spider):
#         # This method is called for every item scraped by any spider.
#         # We simply insert the item (which is a dict) into our collection.
#         self.collection.insert_one(dict(item))
#         return item # It's good practice to return the item for other pipelines

#     def close_spider(self, spider):
#         # This method is called when the spider finishes.
#         # We close the connection to the database.
#         self.client.close()


#         import json
# import os
# from datetime import datetime


class AmazonPipeline:
    def open_spider(self, spider):
        self.file = open(f'amazon_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w', encoding='utf-8')
        self.items = []

    def close_spider(self, spider):
        # Write all items as a JSON array
        json.dump(self.items, self.file, indent=2, ensure_ascii=False)
        self.file.close()
        
        # Also save individual files per ASIN
        for item in self.items:
            asin = item.get('asin')
            if asin:
                with open(f'amazon_{asin}.json', 'w', encoding='utf-8') as f:
                    json.dump(item, f, indent=2, ensure_ascii=False)

    def process_item(self, item, spider):
        self.items.append(dict(item))
        return item



import pymongo
import json
import os
from datetime import datetime

import pymongo
import json
import os
from datetime import datetime


class MongoPipeline:
    def __init__(self):
        # 1. Connect to the MongoDB server using environment variable
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.client = pymongo.MongoClient(mongodb_uri)
        
        # 2. Select the database
        self.db = self.client['price_tracker_db']
        
        # 3. Select the collections
        self.products_collection = self.db['products']
        self.price_history_collection = self.db['price_history']
        self.reviews_collection = self.db['reviews']
        
        # Create indexes for better query performance (with error handling)
        self._create_indexes()

    def _create_indexes(self):
        """Create indexes on collections for faster queries"""
        try:
            # Check if index already exists before creating
            existing_indexes = self.products_collection.index_information()
            
            if 'asin_1' not in existing_indexes:
                # Create unique index on ASIN, but allow sparse (skip null values)
                self.products_collection.create_index(
                    "asin", 
                    unique=True, 
                    sparse=True  # Skip documents without ASIN
                )
            
            # Index on ASIN and timestamp for price history
            if 'asin_1_timestamp_-1' not in self.price_history_collection.index_information():
                self.price_history_collection.create_index([("asin", 1), ("timestamp", -1)])
            
            # Index on ASIN for reviews
            if 'asin_1' not in self.reviews_collection.index_information():
                self.reviews_collection.create_index("asin", sparse=True)
                
        except pymongo.errors.DuplicateKeyError as e:
            # If there are duplicate null values, remove them first
            print(f"Cleaning up duplicate null ASINs...")
            self.products_collection.delete_many({'asin': None})
            # Try creating index again
            self.products_collection.create_index("asin", unique=True, sparse=True)

    def process_item(self, item, spider):
        """
        Process each scraped item and store in MongoDB
        Works for both Amazon and Flipkart
        """
        # Determine product identifier based on spider
        if spider.name == 'amazon':
            product_id = item.get('asin')
            id_field = 'asin'
        elif spider.name == 'flipkart':
            product_id = item.get('product_id')
            id_field = 'product_id'
        else:
            product_id = item.get('asin') or item.get('product_id')
            id_field = 'product_id'
        
        timestamp = datetime.now()
        
        if not product_id:
            spider.logger.warning(f"Item missing {id_field}, skipping database storage...")
            return item

        # --- 1. STORE/UPDATE PRODUCT INFO ---
        # Parse price_numeric
        price_numeric = item.get('price_numeric') or self._extract_price(item.get('price'))
        
        # Check if product already exists
        existing_product = self.products_collection.find_one({id_field: product_id})
        
        if existing_product:
            # Product exists - check what changed
            old_price_numeric = existing_product.get('price_numeric')
            old_reviews_count = existing_product.get('total_reviews')
            
            # Detect changes
            price_changed = (price_numeric != old_price_numeric) if (price_numeric and old_price_numeric) else False
            reviews_changed = (item.get('total_reviews') != old_reviews_count) if (item.get('total_reviews') and old_reviews_count) else False
            
            # Always update these fields
            update_fields = {
                'last_updated': timestamp,
            }
            
            # Update current price (always use latest)
            update_fields['current_price'] = item.get('price')
            update_fields['price_numeric'] = price_numeric
            
            # Update if data changed
            if price_changed or reviews_changed:
                update_fields.update({
                    'spider': spider.name,
                    'url': item.get('url'),
                    'title': item.get('title'),
                    'brand': item.get('brand'),
                    'availability': item.get('availability'),
                    'rating': item.get('rating'),
                    'total_reviews': item.get('total_reviews'),
                    'total_ratings': item.get('total_ratings'),
                    'images': item.get('images', []),
                    'features': item.get('features', []) or item.get('highlights', []),
                    'description': item.get('description'),
                    'specifications': item.get('specifications', {}),
                    'categories': item.get('categories', []),
                    'variations': item.get('variations', {}),
                })
                
                # Add platform if it doesn't exist
                if not existing_product.get('platform') and item.get('platform'):
                    update_fields['platform'] = item.get('platform')
                
                # Add discount and original_price if available (Myntra)
                if item.get('original_price'):
                    update_fields['original_price'] = item.get('original_price')
                if item.get('discount'):
                    update_fields['discount'] = item.get('discount')
                
                log_msg = []
                if price_changed:
                    log_msg.append(f"Price: {existing_product.get('current_price')} → {item.get('price')}")
                if reviews_changed:
                    log_msg.append(f"Reviews: {old_reviews_count} → {item.get('total_reviews')}")
                
                spider.logger.info(f"✓ Updated product {product_id}: {', '.join(log_msg)}")
            else:
                # No significant changes, just update timestamp
                spider.logger.info(f"ℹ No changes for {product_id}, updated timestamp only")
            
            try:
                self.products_collection.update_one(
                    {id_field: product_id},
                    {'$set': update_fields}
                )
            except Exception as e:
                spider.logger.error(f"Error updating product {product_id}: {e}")
        else:
            # New product - store everything including initial price
            product_data = {
                id_field: product_id,
                'spider': spider.name,
                'platform': item.get('platform'),
                'url': item.get('url'),
                'title': item.get('title'),
                'brand': item.get('brand'),
                'current_price': item.get('price'),
                'price_numeric': price_numeric,
                'original_price': item.get('original_price'),
                'discount': item.get('discount'),
                'availability': item.get('availability'),
                'rating': item.get('rating'),
                'total_reviews': item.get('total_reviews'),
                'total_ratings': item.get('total_ratings'),
                'images': item.get('images', []),
                'features': item.get('features', []) or item.get('highlights', []),
                'description': item.get('description'),
                'specifications': item.get('specifications', {}),
                'categories': item.get('categories', []),
                'variations': item.get('variations', {}),
                'sizes': item.get('sizes', []),
                'colors': item.get('colors', []),
                'first_seen': timestamp,
                'last_updated': timestamp,
            }
            
            try:
                self.products_collection.insert_one(product_data)
                spider.logger.info(f"✓ Stored NEW product: {product_id} - {item.get('title', 'N/A')[:50]}")
            except Exception as e:
                spider.logger.error(f"Error storing product {product_id}: {e}")

        # --- 2. STORE PRICE HISTORY ---
        # Always store price with timestamp (for graph)
        price = item.get('price')
        if price and price_numeric:
            try:
                # Always add price entry for historical tracking
                price_history_entry = {
                    id_field: product_id,
                    'spider': spider.name,
                    'platform': item.get('platform'),
                    'price': price,
                    'price_numeric': price_numeric,
                    'availability': item.get('availability'),
                    'timestamp': timestamp,
                }
                
                self.price_history_collection.insert_one(price_history_entry)
                
                if existing_product and price_changed:
                    spider.logger.info(f"📈 Price CHANGED! Recorded: {product_id} - {price} (was {existing_product.get('current_price')})")
                else:
                    spider.logger.info(f"📊 Recorded price: {product_id} - {price}")
                    
            except Exception as e:
                spider.logger.error(f"Error storing price history for {product_id}: {e}")

        # --- 3. STORE REVIEWS (Keep old + add new) ---
        reviews_from_page = item.get('reviews_from_page', [])
        
        if reviews_from_page:
            try:
                # Add new reviews while keeping old ones (upsert to avoid duplicates)
                stored_count = 0
                updated_count = 0
                
                for review in reviews_from_page:
                    try:
                        review_copy = review.copy()
                        review_copy['source'] = 'web_scraping'
                        review_copy[id_field] = product_id
                        review_copy['spider'] = spider.name
                        review_copy['scraped_at'] = timestamp
                        
                        if review.get('text'):
                            # Use review text + author as unique identifier to avoid duplicates
                            review_identifier = {
                                id_field: product_id,
                                'text': review.get('text'),
                                'author': review.get('author', 'Anonymous')
                            }
                            
                            result = self.reviews_collection.update_one(
                                review_identifier,
                                {'$set': review_copy},
                                upsert=True
                            )
                            
                            if result.upserted_id:
                                stored_count += 1
                            elif result.modified_count > 0:
                                updated_count += 1
                                
                    except Exception as e:
                        spider.logger.error(f"Error storing review: {e}")
                
                if stored_count > 0 or updated_count > 0:
                    total_reviews = self.reviews_collection.count_documents({id_field: product_id})
                    spider.logger.info(f"✅ Reviews: +{stored_count} new, ~{updated_count} updated (Total: {total_reviews})")
            except Exception as e:
                spider.logger.error(f"Error managing reviews for {product_id}: {e}")

        return item


    def _extract_price(self, price_string):
        """
        Extract numeric price from string like '₹1,999' or '$19.99'
        Returns float or None
        """
        if not price_string:
            return None
        
        try:
            # Remove currency symbols and commas
            import re
            numeric_str = re.sub(r'[^\d.]', '', str(price_string))
            return float(numeric_str) if numeric_str else None
        except:
            return None

    def close_spider(self, spider):
        """
        Called when spider finishes. Generate summary statistics.
        """
        try:
            # Get statistics
            total_products = self.products_collection.count_documents({})
            total_price_records = self.price_history_collection.count_documents({})
            total_reviews = self.reviews_collection.count_documents({})
            
            spider.logger.info("=" * 60)
            spider.logger.info("DATABASE SUMMARY")
            spider.logger.info("=" * 60)
            spider.logger.info(f"Total Products: {total_products}")
            spider.logger.info(f"Total Price Records: {total_price_records}")
            spider.logger.info(f"Total Reviews: {total_reviews}")
            spider.logger.info("=" * 60)
        except Exception as e:
            spider.logger.error(f"Error generating summary: {e}")
        
        # Close the connection
        self.client.close()
        spider.logger.info("MongoDB connection closed")


class JsonExportPipeline:
    """
    Optional pipeline to also export data to JSON files
    """
    def open_spider(self, spider):
        # Create exports directory if it doesn't exist
        self.exports_dir = 'exports'
        os.makedirs(self.exports_dir, exist_ok=True)
        
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f'{self.exports_dir}/amazon_data_{timestamp}.json'
        self.file = open(self.filename, 'w', encoding='utf-8')
        self.items = []

    def close_spider(self, spider):
        # Write all items as a JSON array
        json.dump(self.items, self.file, indent=2, ensure_ascii=False)
        self.file.close()
        
        # Also save individual files per ASIN
        for item in self.items:
            asin = item.get('asin')
            if asin:
                individual_file = f'{self.exports_dir}/product_{asin}.json'
                with open(individual_file, 'w', encoding='utf-8') as f:
                    json.dump(item, f, indent=2, ensure_ascii=False)
        
        spider.logger.info(f"Exported data to: {self.filename}")

    def process_item(self, item, spider):
        self.items.append(dict(item))
        return item
