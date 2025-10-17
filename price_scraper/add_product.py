from pymongo import MongoClient
from datetime import datetime

def add_product_to_track(url, spider_name):
    """Adds a new product URL to our tracking list."""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['price_tracker_db']
    collection = db['tracked_products']

    # Check if the URL is already being tracked
    if collection.find_one({"url": url}):
        print(f"URL already exists: {url}")
        return

    # Insert the new product
    product_document = {
        "url": url,
        "spider_name": spider_name, # e.g., 'myntra', 'amazon'
        "date_added": datetime.utcnow(),
        "last_scraped": None,
        "is_active": True
    }
    collection.insert_one(product_document)
    print(f"Added '{spider_name}' product: {url}")
    client.close()

if __name__ == '__main__':
    # --- EXAMPLE: Add products here ---
    add_product_to_track(
        url="https://www.myntra.com/heels/roadster/the-roadster-lifestyle-co-women-textured-round-toe-sandals/34485376/buy",
        spider_name="myntra"
    )
    add_product_to_track(
        url="https://www.amazon.in/Wild-Stone-Edge-Perfume-Men/dp/B08TGSRW1S/",
        spider_name="amazon"
    )
    # Add more products by calling the function again...