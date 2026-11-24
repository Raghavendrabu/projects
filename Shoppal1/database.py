import json
import os
import random
from datetime import datetime, timedelta
import pymongo
from bson import ObjectId

# Keyword-to-Image Map for Exact Image Matches
EXACT_IMAGE_MAP = {
    "sunscreen": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=500&q=80",
    "face wash": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?auto=format&fit=crop&w=500&q=80",
    "serum": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=500&q=80",
    "toner": "https://images.unsplash.com/photo-1612817288484-6f916006741a?auto=format&fit=crop&w=500&q=80",
    "moisturizer": "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?auto=format&fit=crop&w=500&q=80",
    "aloe vera": "https://images.unsplash.com/photo-1596547609652-9cf5d8d76921?auto=format&fit=crop&w=500&q=80",
    "scrub": "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?auto=format&fit=crop&w=500&q=80",
    "lip balm": "https://images.unsplash.com/photo-1617897903246-719242758050?auto=format&fit=crop&w=500&q=80",
    "mask": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=500&q=80",
    "cream": "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?auto=format&fit=crop&w=500&q=80",
    "oil": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=500&q=80",
    "saree": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=500&q=80",
    "kurta": "https://images.unsplash.com/photo-1607990283143-e81e7a2c93ab?auto=format&fit=crop&w=500&q=80",
    "kurti": "https://images.unsplash.com/photo-1607990283143-e81e7a2c93ab?auto=format&fit=crop&w=500&q=80",
    "sherwani": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=500&q=80",
    "jeans": "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=500&q=80",
    "denim": "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=500&q=80",
    "shirt": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=500&q=80",
    "t-shirt": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=500&q=80",
    "socks": "https://images.unsplash.com/photo-1582966772680-860e372bb558?auto=format&fit=crop&w=500&q=80",
    "shoes": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=500&q=80",
    "sneakers": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=500&q=80",
    "watch": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=500&q=80",
    "sunglasses": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?auto=format&fit=crop&w=500&q=80",
    "tawa": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=500&q=80",
    "cooker": "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&w=500&q=80",
    "induction": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=500&q=80",
    "water bottle": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=500&q=80",
    "lunch box": "https://images.unsplash.com/photo-1539132223700-11202867ee97?auto=format&fit=crop&w=500&q=80",
    "kettle": "https://images.unsplash.com/photo-1594897030264-ab7d87efc473?auto=format&fit=crop&w=500&q=80",
    "mixer": "https://images.unsplash.com/photo-1578643463396-0997cb5328c1?auto=format&fit=crop&w=500&q=80",
    "grinder": "https://images.unsplash.com/photo-1578643463396-0997cb5328c1?auto=format&fit=crop&w=500&q=80",
    "air fryer": "https://images.unsplash.com/photo-1621972750749-0fbb1abb7736?auto=format&fit=crop&w=500&q=80",
    "pan": "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&w=500&q=80",
    "glass": "https://images.unsplash.com/photo-1518063319789-7217e6706b04?auto=format&fit=crop&w=500&q=80",
    "notebook": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=500&q=80",
    "journal": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=500&q=80",
    "pen": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?auto=format&fit=crop&w=500&q=80",
    "geometry": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?auto=format&fit=crop&w=500&q=80",
    "pencil": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=500&q=80",
    "calculator": "https://images.unsplash.com/photo-1574607383476-f517f220d398?auto=format&fit=crop&w=500&q=80",
    "headphones": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=500&q=80",
    "earbuds": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=500&q=80",
    "speaker": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=500&q=80",
    "smartwatch": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=500&q=80",
    "power bank": "https://images.unsplash.com/photo-1609592424109-dd9892f1b17c?auto=format&fit=crop&w=500&q=80",
    "tv": "https://images.unsplash.com/photo-1593305841991-05c297ba4575?auto=format&fit=crop&w=500&q=80",
    "basmati rice": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=500&q=80",
    "atta": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=500&q=80",
    "tea": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=500&q=80",
    "coffee": "https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&w=500&q=80",
    "ghee": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=500&q=80",
    "honey": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=500&q=80",
    "biscuits": "https://images.unsplash.com/photo-1558961309-dbdf03b33d08?auto=format&fit=crop&w=500&q=80",
    "cookies": "https://images.unsplash.com/photo-1558961309-dbdf03b33d08?auto=format&fit=crop&w=500&q=80",
    "chocolate": "https://images.unsplash.com/photo-1511381939415-e44015466834?auto=format&fit=crop&w=500&q=80",
    "milk": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=500&q=80",
    "paneer": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=500&q=80",
    "butter": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=500&q=80",
    "cold drink": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=500&q=80",
    "juice": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?auto=format&fit=crop&w=500&q=80",
    "coconut water": "https://images.unsplash.com/photo-1543362906-acfc16c67564?auto=format&fit=crop&w=500&q=80",
    "protein powder": "https://images.unsplash.com/photo-1593095948071-474c5cc2989d?auto=format&fit=crop&w=500&q=80",
    "dal": "https://images.unsplash.com/photo-1546833999-b9e579fcbe5e?auto=format&fit=crop&w=500&q=80"
}

def get_exact_image(title, category):
    title_lower = title.lower()
    for keyword, url in EXACT_IMAGE_MAP.items():
        if keyword in title_lower:
            return url
    
    # Fallback to category standard placeholder pools
    fallback_pools = {
        "Skincare": "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?auto=format&fit=crop&w=400&q=80",
        "Clothing": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=400&q=80",
        "Kitchen": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=400&q=80",
        "Stationery": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=400&q=80",
        "Electronics": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=400&q=80",
        "Grocery": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=400&q=80"
    }
    return fallback_pools.get(category, fallback_pools["Skincare"])

class DatabaseManager:
    def __init__(self):
        self.use_mongodb = False
        self.mongo_client = None
        self.db = None
        self.fallback_file = "shoppal_db.json"
        
        # Try to connect to MongoDB
        try:
            # Short timeout to avoid stalling if it's not responsive
            self.mongo_client = pymongo.MongoClient(
                "mongodb://localhost:27017/", 
                serverSelectionTimeoutMS=2000
            )
            # Test connection
            self.mongo_client.server_info()
            self.db = self.mongo_client["shoppal_db"]
            self.use_mongodb = True
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(f"MongoDB connection failed: {e}. Falling back to JSON file storage: {self.fallback_file}")
            self._init_fallback_db()
            
        # Ensure we have seed data in the system
        self.seed_if_empty()

    def _init_fallback_db(self):
        if not os.path.exists(self.fallback_file):
            initial_data = {
                "products": [],
                "users": [],
                "favorites": {}  # user_id: list of product_ids
            }
            with open(self.fallback_file, "w") as f:
                json.dump(initial_data, f, indent=4)

    def _read_fallback(self):
        try:
            with open(self.fallback_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading fallback DB: {e}")
            return {"products": [], "users": [], "favorites": {}}

    def _write_fallback(self, data):
        try:
            with open(self.fallback_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error writing fallback DB: {e}")

    def seed_if_empty(self):
        if self.use_mongodb:
            # Re-seed if catalog is less than 600 or any record lacks the "image" field
            if self.db["products"].count_documents({}) < 600 or self.db["products"].count_documents({"image": {"$exists": True}}) < 600:
                print("Catalog update: Seeding MongoDB with 600 premium products with unique images...")
                self.db["products"].delete_many({}) # clear old seed
                products = self._generate_seed_products()
                self.db["products"].insert_many(products)
                print(f"Seeded {len(products)} products into MongoDB.")
        else:
            data = self._read_fallback()
            # Re-seed if catalog is less than 600 or any record lacks the "image" field
            has_no_images = not data.get("products") or any("image" not in p for p in data["products"])
            if not data.get("products") or len(data["products"]) < 600 or has_no_images:
                print("Catalog update: Seeding Fallback JSON with 600 premium products with unique images...")
                products = self._generate_seed_products()
                # For JSON serializability, ensure string IDs
                for p in products:
                    if "_id" in p and isinstance(p["_id"], ObjectId):
                        p["_id"] = str(p["_id"])
                data["products"] = products
                self._write_fallback(data)
                print(f"Seeded {len(products)} products into JSON database.")

    def _generate_seed_products(self):
        # Generate 30 days of price history
        today = datetime.now()
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]

        def get_price_history(base_amazon, base_flipkart, base_other, other_name):
            history = []
            # Make the prices fluctuate slightly over the last 30 days
            for d in dates:
                # Random fluctuations around base prices
                amz = int(base_amazon * random.uniform(0.95, 1.05))
                flp = int(base_flipkart * random.uniform(0.95, 1.05))
                oth = int(base_other * random.uniform(0.96, 1.04))
                
                # Make current date price equal to the actual current values
                if d == dates[-1]:
                    amz = base_amazon
                    flp = base_flipkart
                    oth = base_other

                history.append({
                    "date": d,
                    "amazon": amz,
                    "flipkart": flp,
                    other_name: oth
                })
            return history

        products = [
            {
                "_id": ObjectId(),
                "title": "Minimalist SPF 50 Sunscreen",
                "brand": "Minimalist",
                "category": "Skincare",
                "image": "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?auto=format&fit=crop&w=400&q=80",
                "rating": 4.5,
                "num_reviews": 1000,
                "original_price": 649,
                "vendors": [
                    {"name": "amazon", "price": 549, "link": "https://www.amazon.in/Minimalist-Sunscreen-Multi-Vitamins-Lightweight-Protection/dp/B095YCM3VJ"},
                    {"name": "flipkart", "price": 569, "link": "https://www.flipkart.com/minimalist-multi-vitamin-spf-50-pa-sunscreen/p/itm2c99a80e14ea8"},
                    {"name": "nykaa", "price": 579, "link": "https://www.nykaa.com/minimalist-multi-vitamin-spf-50-pa-sunscreen/p/1324838"}
                ],
                "ai_insight": "Best time to buy!",
                "discount_check": "Genuine discount!",
                "review_sentiment": "Highly Positive",
                "reviews": [
                    {"user": "Ananya Sharma", "rating": 5, "text": "Absolutely love this sunscreen! It leaves zero white cast and feels like a lightweight moisturizer. Highly recommended!", "date": "2026-05-18"},
                    {"user": "Rohan Das", "rating": 4, "text": "Good protection and very light on the skin. Doesn't feel oily. However, the pump could be designed better.", "date": "2026-05-15"},
                    {"user": "Meera Iyer", "rating": 5, "text": "Perfect for my combination skin. Protects well under Delhi sun. No breakouts so far!", "date": "2026-05-10"},
                    {"user": "Vikram Singh", "rating": 3, "text": "It provides good protection, but it pills slightly when layered with my moisturizer.", "date": "2026-05-02"}
                ]
            },
            {
                "_id": ObjectId(),
                "title": "Plum 10% Niacinamide Serum",
                "brand": "Plum",
                "category": "Skincare",
                "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=400&q=80",
                "rating": 4.3,
                "num_reviews": 1000,
                "original_price": 899,
                "vendors": [
                    {"name": "amazon", "price": 675, "link": "https://www.amazon.in/Plum-Niacinamide-Blemish-Clearing-Hyper-pigmentation/dp/B09BF97KVX"},
                    {"name": "flipkart", "price": 695, "link": "https://www.flipkart.com/plum-10-niacinamide-serum-rice-water/p/itm5a84ea1de281f"},
                    {"name": "nykaa", "price": 705, "link": "https://www.nykaa.com/plum-10-niacinamide-face-serum-with-rice-water/p/2776412"}
                ],
                "ai_insight": "Price stable",
                "discount_check": "Genuine discount!",
                "review_sentiment": "Mixed review",
                "reviews": [
                    {"user": "Shruti K.", "rating": 4, "text": "Helped reduce my acne scars over 3 weeks. Skin feels smoother.", "date": "2026-05-16"},
                    {"user": "Amit Verma", "rating": 3, "text": "It's slightly sticky on application, but sinks in after a few minutes. Decent results.", "date": "2026-05-12"},
                    {"user": "Sneha Sen", "rating": 5, "text": "Amazing serum! Rice water works like magic for glass skin. Will buy again.", "date": "2026-05-08"},
                    {"user": "Rahul G.", "rating": 2, "text": "Didn't suit my skin at all, caused minor bumps. Be careful if you have sensitive skin.", "date": "2026-04-28"}
                ]
            },
            {
                "_id": ObjectId(),
                "title": "Lakmé Sun Expert SPF 50",
                "brand": "Lakmé",
                "category": "Skincare",
                "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=400&q=80",
                "rating": 4.1,
                "num_reviews": 1000,
                "original_price": 585,
                "vendors": [
                    {"name": "amazon", "price": 399, "link": "https://www.amazon.in/Lakme-Expert-Ultra-Matte-Lotion/dp/B01N22K09W"},
                    {"name": "flipkart", "price": 419, "link": "https://www.flipkart.com/lakme-sun-expert-spf-50-pa-ultra-matte-lotion/p/itmexfgfkyhhefyu"},
                    {"name": "nykaa", "price": 429, "link": "https://www.nykaa.com/lakme-sun-expert-spf-50-pa-ultra-matte-lotion-sunscreen/p/95460"}
                ],
                "ai_insight": "Best time to buy!",
                "discount_check": "Genuine discount!",
                "review_sentiment": "Mostly Positive",
                "reviews": [
                    {"user": "Pooja Hegde", "rating": 5, "text": "Classic sunscreen. Smells great and blocks sun perfectly. Good for beach trips.", "date": "2026-05-14"},
                    {"user": "Deepak K.", "rating": 3, "text": "It says ultra matte but it makes my face shiny after an hour. Decent protection though.", "date": "2026-05-11"},
                    {"user": "Arjun M.", "rating": 4, "text": "Very affordable compared to newer brands. Reliable sunblock.", "date": "2026-05-05"}
                ]
            },
            {
                "_id": ObjectId(),
                "title": "Mamaearth Vitamin C Face Wash",
                "brand": "Mamaearth",
                "category": "Skincare",
                "image": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?auto=format&fit=crop&w=400&q=80",
                "rating": 4.4,
                "num_reviews": 1000,
                "original_price": 399,
                "vendors": [
                    {"name": "amazon", "price": 249, "link": "https://www.amazon.in/Mamaearth-Vitamin-Wash-Turmeric-Skin-Illumination/dp/B07N6ML88L"},
                    {"name": "flipkart", "price": 269, "link": "https://www.flipkart.com/mamaearth-vitamin-c-face-wash-with-foaming-nozzle/p/itmd0436d4dfba8c"},
                    {"name": "nykaa", "price": 279, "link": "https://www.nykaa.com/mamaearth-vitamin-c-face-wash-with-vitamin-c-and-turmeric/p/579998"}
                ],
                "ai_insight": "Best time to buy!",
                "discount_check": "Genuine discount!",
                "review_sentiment": "Mixed review",
                "reviews": [
                    {"user": "Neha J.", "rating": 4, "text": "Love the cooling effect and fresh orange scent. Cleanses oil well.", "date": "2026-05-19"},
                    {"user": "Karan Malhotra", "rating": 3, "text": "A bit drying for winter, but perfect for hot humid summer. Turmeric glow is dynamic.", "date": "2026-05-13"},
                    {"user": "Divya P.", "rating": 5, "text": "Squeaky clean feel! Best face wash for daily dirt extraction.", "date": "2026-05-07"}
                ]
            },
            {
                "_id": ObjectId(),
                "title": "Women Cotton Kurti",
                "brand": "Biba",
                "category": "Clothing",
                "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=400&q=80",
                "rating": 4.6,
                "num_reviews": 1000,
                "original_price": 1299,
                "vendors": [
                    {"name": "amazon", "price": 849, "link": "https://www.amazon.in/Biba-Women-Cotton-Kurti/dp/B08XYZ1234"},
                    {"name": "flipkart", "price": 829, "link": "https://www.flipkart.com/biba-women-printed-pure-cotton-straight-kurta/p/itme12345"},
                    {"name": "myntra", "price": 799, "link": "https://www.myntra.com/kurta/biba/biba-women-blue-printed-cotton-kurta/123456"}
                ],
                "ai_insight": "Best time to buy!",
                "discount_check": "Genuine discount!",
                "review_sentiment": "Highly Positive",
                "reviews": [
                    {"user": "Priya Nair", "rating": 5, "text": "Very breathable fabric. The color doesn't fade after multiple washes. Elegant print!", "date": "2026-05-18"},
                    {"user": "Ritu Kapoor", "rating": 4, "text": "Fit is excellent, standard Biba quality. Comfortable for office wear.", "date": "2026-05-12"},
                    {"user": "Kavita S.", "rating": 5, "text": "Worth every rupee. Colors are as vibrant as shown in photos.", "date": "2026-05-02"}
                ]
            },
            {
                "_id": ObjectId(),
                "title": "Men Casual Shirt",
                "brand": "Roadster",
                "category": "Clothing",
                "image": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=400&q=80",
                "rating": 4.2,
                "num_reviews": 1000,
                "original_price": 999,
                "vendors": [
                    {"name": "amazon", "price": 649, "link": "https://www.amazon.in/Roadster-Men-Casual-Shirt/dp/B08ABC123"},
                    {"name": "flipkart", "price": 629, "link": "https://www.flipkart.com/roadster-men-solid-casual-shirt/p/itmasd123"},
                    {"name": "myntra", "price": 599, "link": "https://www.myntra.com/shirt/roadster/roadster-men-olive-green-solid-casual-shirt/789123"}
                ],
                "ai_insight": "Price stable",
                "discount_check": "Genuine discount!",
                "review_sentiment": "Mostly Positive",
                "reviews": [
                    {"user": "Aditya Roy", "rating": 4, "text": "Great color and regular fit. Soft fabric. Ideal for daily casual styling.", "date": "2026-05-17"},
                    {"user": "Suresh P.", "rating": 5, "text": "Stitching quality is superb. Incredible shirt for just 599!", "date": "2026-05-10"},
                    {"user": "Abhishek T.", "rating": 3, "text": "Sizes run a bit small, order one size up. Fabric thickness is moderate.", "date": "2026-04-29"}
                ]
            },
            {
                "_id": ObjectId(),
                "title": "Non-Stick Cookware Set",
                "brand": "Prestige",
                "category": "Kitchen",
                "image": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=400&q=80",
                "rating": 4.5,
                "num_reviews": 1000,
                "original_price": 2999,
                "vendors": [
                    {"name": "amazon", "price": 1899, "link": "https://www.amazon.in/Prestige-Omega-Select-Plus-Cookware/dp/B00EIAYSA6"},
                    {"name": "flipkart", "price": 1999, "link": "https://www.flipkart.com/prestige-omega-select-plus-ib-non-stick-kitchen-set/p/itmdexfbtyhzheyu"},
                    {"name": "tatacliq", "price": 2099, "link": "https://www.tatacliq.com/prestige-nonstick-cookware-set/p/mp123456"}
                ],
                "ai_insight": "Best time to buy!",
                "discount_check": "Genuine discount!",
                "review_sentiment": "Highly Positive",
                "reviews": [
                    {"user": "Meenakshi K.", "rating": 5, "text": "Excellent non-stick performance. Requires very little oil. Heat distribution is very uniform.", "date": "2026-05-15"},
                    {"user": "Ramesh Rao", "rating": 4, "text": "Strong handles, high premium feel. Cooking dosa and rotis is so easy now.", "date": "2026-05-11"},
                    {"user": "Preeti J.", "rating": 4, "text": "Good set for a family of 3-4. Clean and sleek design.", "date": "2026-05-01"}
                ]
            },
            {
                "_id": ObjectId(),
                "title": "Stainless Steel Water Bottle",
                "brand": "Milton",
                "category": "Kitchen",
                "image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=400&q=80",
                "rating": 4.4,
                "num_reviews": 1000,
                "original_price": 699,
                "vendors": [
                    {"name": "amazon", "price": 549, "link": "https://www.amazon.in/Milton-Thermosteel-Duo-Deluxe-Bottle/dp/B013W3B1K6"},
                    {"name": "flipkart", "price": 579, "link": "https://www.flipkart.com/milton-duo-dlx-1000-ml-flask/p/itmeyfgfkyhhefyu"},
                    {"name": "dmart", "price": 529, "link": "https://www.dmart.in/milton-steel-bottle-1l"}
                ],
                "ai_insight": "Price stable",
                "discount_check": "Genuine discount!",
                "review_sentiment": "Mostly Positive",
                "reviews": [
                    {"user": "Vivek G.", "rating": 5, "text": "Holds temperature for a full 24 hours. Robust steel body, doesn't dent easily.", "date": "2026-05-16"},
                    {"user": "Nisha S.", "rating": 4, "text": "Leak-proof cap. Perfect for kids going to school or carrying to the gym.", "date": "2026-05-12"},
                    {"user": "Rohan P.", "rating": 3, "text": "A bit heavy to carry when full, but keeps water ice cold.", "date": "2026-04-25"}
                ]
            },
            {
                "_id": ObjectId(),
                "title": "boAt Rockerz 450 Headphones",
                "brand": "boAt",
                "category": "Electronics",
                "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=400&q=80",
                "rating": 4.3,
                "num_reviews": 1000,
                "original_price": 1990,
                "vendors": [
                    {"name": "amazon", "price": 1199, "link": "https://www.amazon.in/boAt-Rockerz-450-Lightweight-Playback/dp/B07PR1CL3S"},
                    {"name": "flipkart", "price": 1249, "link": "https://www.flipkart.com/boat-rockerz-450-bluetooth-headset/p/itmf3qyhgezfkyhu"},
                    {"name": "reliance", "price": 1299, "link": "https://www.reliancedigital.in/boat-rockerz-450-headphones/p/491234"}
                ],
                "ai_insight": "Best time to buy!",
                "discount_check": "Genuine discount!",
                "review_sentiment": "Highly Positive",
                "reviews": [
                    {"user": "Samir K.", "rating": 4, "text": "Amazing bass response! Battery easily lasts 15 hours on a single charge. Punchy sound.", "date": "2026-05-18"},
                    {"user": "Kritika Chawla", "rating": 5, "text": "Matte black looks very premium. Fits snugly on my head. Super volume range.", "date": "2026-05-14"},
                    {"user": "Varun T.", "rating": 3, "text": "Good sound quality, but the clamping force is high. Ears start aching after 2 hours.", "date": "2026-05-09"}
                ]
            },
            {
                "_id": ObjectId(),
                "title": "A5 Leatherette Journal",
                "brand": "Factor Notes",
                "category": "Stationery",
                "image": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=400&q=80",
                "rating": 4.7,
                "num_reviews": 1000,
                "original_price": 499,
                "vendors": [
                    {"name": "amazon", "price": 299, "link": "https://www.amazon.in/Factor-Notes-Notebook-Leatherette-Unruled/dp/B08VXYZ123"},
                    {"name": "flipkart", "price": 319, "link": "https://www.flipkart.com/factor-notes-a5-ruled-journal/p/itme123efd"},
                    {"name": "dmart", "price": 289, "link": "https://www.dmart.in/factor-notes-journal-a5"}
                ],
                "ai_insight": "Best time to buy!",
                "discount_check": "Genuine discount!",
                "review_sentiment": "Highly Positive",
                "reviews": [
                    {"user": "Akansha D.", "rating": 5, "text": "Best journal I've ever owned. Pages are 100 GSM, zero ink bleed even with fountain pens!", "date": "2026-05-19"},
                    {"user": "Harsh J.", "rating": 5, "text": "Beautiful hardbound finish. The ribbon bookmark and elastic band feel premium.", "date": "2026-05-13"},
                    {"user": "Tanvi R.", "rating": 4, "text": "Lovely texture. Good size to carry in a handbag. Writing in this is pure joy.", "date": "2026-04-30"}
                ]
            },
            {
                "_id": ObjectId(),
                "title": "Tata Tea Premium 1kg",
                "brand": "Tata Tea",
                "category": "Grocery",
                "image": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=400&q=80",
                "rating": 4.4,
                "num_reviews": 1000,
                "original_price": 450,
                "vendors": [
                    {"name": "amazon", "price": 380, "link": "https://www.amazon.in/Tata-Tea-Premium-1kg/dp/B00T7O91XY"},
                    {"name": "flipkart", "price": 390, "link": "https://www.flipkart.com/tata-tea-premium/p/itme123abc"},
                    {"name": "dmart", "price": 375, "link": "https://www.dmart.in/tata-tea-1kg"}
                ],
                "ai_insight": "Price stable",
                "discount_check": "Genuine discount!",
                "review_sentiment": "Mostly Positive",
                "reviews": [
                    {"user": "Gaurav S.", "rating": 5, "text": "Perfect chai blend. Strong taste and lovely aroma. Essential for morning tea.", "date": "2026-05-17"},
                    {"user": "Savita Patil", "rating": 4, "text": "Reliable brand and product quality. Standard pricing, good discount on DMart/Amazon.", "date": "2026-05-10"},
                    {"user": "Manoj B.", "rating": 4, "text": "Strong black tea leaves, good flavor. Value pack lasts a long time.", "date": "2026-05-01"}
                ]
            }
        ]

        # Define arrays of brands, names, categories, and prices to programmatically generate 200+ distinct products
        categories_data = {
            "Skincare": {
                "brands": ["Minimalist", "Plum", "Lakmé", "Mamaearth", "Cetaphil", "L'Oreal", "Neutrogena", "The Derma Co", "Innisfree", "Nivea", "Biotique", "Forest Essentials"],
                "types": ["Moisturizer Gel", "Foaming Face Wash", "Salicylic Acid Serum", "Hydrating Toner", "Sunscreen Lotion", "Vitamin C Face Cream", "Clay Mask", "Hydrating Lip Balm", "Night Recovery Cream", "Brightening Face Scrub"],
                "base_price_range": (150, 950),
                "other_vendor": "nykaa"
            },
            "Clothing": {
                "brands": ["Biba", "Roadster", "Allen Solly", "FabIndia", "Levi's", "W", "Zara", "H&M", "Puma", "Peter England", "U.S. Polo Assn.", "Jack & Jones"],
                "types": ["Pure Cotton Kurti", "Slim Fit Denim Jeans", "Casual Button Shirt", "Graphic Round Neck Tee", "Athletic Polo Shirt", "Warm Hooded Sweatshirt", "Summer Floral Dress", "Chino Trousers", "Light Denim Jacket", "Ethnic Kurta Pajama"],
                "base_price_range": (399, 2999),
                "other_vendor": "myntra"
            },
            "Kitchen": {
                "brands": ["Prestige", "Milton", "Hawkins", "Pigeon", "Butterfly", "Borosil", "Cello", "Wonderchef", "Philips", "Bajaj", "Morphy Richards", "Kent"],
                "types": ["Non-Stick Fry Pan", "Insulated Water Flask", "Classic Pressure Cooker", "Glass Mixing Bowl Set", "Electric Cordless Kettle", "Induction Cooktop Set", "Manual Vegetable Chopper", "Hard Anodized Tawa", "Airtight Plastic Container Set", "Stainless Steel Lunchbox"],
                "base_price_range": (299, 3999),
                "other_vendor": "tatacliq"
            },
            "Stationery": {
                "brands": ["Factor Notes", "Classmate", "Parker", "Luxor", "Staedtler", "Pilot", "Uniball", "Doms", "Maped", "Cross", "Lamy", "Faber-Castell"],
                "types": ["A5 Dotted Notebook", "Fountain Pen Matte Black", "Dual Brush Color Pens", "A4 Wirebound Sketchbook", "Gel Pen Box Pack", "Assorted Sticky Notes", "Rotating Desk Organizer", "Pocket Pastel Highlighters", "Classic Geometry Box", "Zippered Leather Pencil Case"],
                "base_price_range": (99, 1499),
                "other_vendor": "dmart"
            },
            "Electronics": {
                "brands": ["boAt", "Noise", "Realme", "OnePlus", "JBL", "Sony", "Portronics", "Zebronics", "Ambrane", "pTron", "Boult", "Mivi"],
                "types": ["Wireless Over-Ear Headphones", "Smart Activity Tracker", "Portable Bluetooth Speaker", "In-Ear Neckband Earphones", "20000mAh Power Bank", "65W USB Fast Charger", "Ergonomic Wireless Mouse", "Smart Wi-Fi LED Bulb", "Multi-Device Wireless Keyboard", "Heavy Duty Extension Cord Set"],
                "base_price_range": (349, 5999),
                "other_vendor": "reliance"
            },
            "Grocery": {
                "brands": ["Tata Tea", "Tata Salt", "Fortune", "Saffola", "Kellogg's", "Nescafe", "Catch", "Britannia", "Haldiram's", "Dabur", "Bikanervala", "Aashirvaad"],
                "types": ["Premium Gold Tea Bag Set", "Cold Pressed Mustard Oil 1L", "Organic Rolled Oats 1kg", "Classic Instant Coffee 200g", "Rozana Basmati Rice 5kg", "California Almonds 500g", "Pure Natural Honey 500g", "Chakki Fresh Atta 5kg", "Mixed Fruit Sweet Jam", "Super Digestive Oats Biscuits"],
                "base_price_range": (60, 1499),
                "other_vendor": "dmart"
            }
        }

        # Premium Unsplash Stock Images Pool per Category
        category_images = {
            "Skincare": [
                "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1612817288484-6f916006741a?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=400&q=80"
            ],
            "Clothing": [
                "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1543087903-1ac2ec7aa8c5?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?auto=format&fit=crop&w=400&q=80"
            ],
            "Kitchen": [
                "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1506368249639-73a05d6f6488?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?auto=format&fit=crop&w=400&q=80"
            ],
            "Stationery": [
                "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1586075010923-2dd4570fb338?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1473186578172-c141e6798cf4?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1519751138087-5bf79df62d5b?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=400&q=80"
            ],
            "Electronics": [
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1572569511254-d8f925fe7cbb?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1527690710607-e57cd53b3772?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1546054454-aa26e2b734c7?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1563770660941-20978e870e26?auto=format&fit=crop&w=400&q=80"
            ],
            "Grocery": [
                "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1588964895597-cfccd6e2dbf9?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1608686207856-001b95cf60ca?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1515003197210-e0cd71810b5f?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1550989460-0adf9ea622e2?auto=format&fit=crop&w=400&q=80",
                "https://images.unsplash.com/photo-1578916171728-46686eac8d58?auto=format&fit=crop&w=400&q=80"
            ]
        }

        # Helper to generate robust search-result URLs for each Indian marketplace
        def get_vendor_link(vendor_name, prod_title):
            term = prod_title.replace(' ', '+')
            if vendor_name == "amazon":
                return f"https://www.amazon.in/s?k={term}"
            elif vendor_name == "flipkart":
                return f"https://www.flipkart.com/search?q={term}"
            elif vendor_name == "nykaa":
                return f"https://www.nykaa.com/search/result/?q={term}"
            elif vendor_name == "myntra":
                return f"https://www.myntra.com/search/result?q={term}"
            elif vendor_name == "reliance":
                return f"https://www.reliancedigital.in/search?q={term}"
            elif vendor_name == "tatacliq":
                return f"https://www.tatacliq.com/search/?text={term}"
            elif vendor_name == "dmart":
                return f"https://www.dmart.in/search?q={term}"
            else:
                return f"https://www.google.com/search?q={term}"

        # Load user_products.json if it exists and process them
        user_products = []
        user_products_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_products.json")
        if os.path.exists(user_products_file):
            try:
                with open(user_products_file, "r", encoding="utf-8") as f:
                    user_products = json.load(f)
                print(f"Loaded {len(user_products)} user products from user_products.json")
            except Exception as e:
                print(f"Error loading user_products.json: {e}")

        import re
        def is_duplicate(item, existing_list):
            item_title_lower = item["title"].lower().strip()
            item_brand_lower = item["brand"].lower().strip()
            
            for p in existing_list:
                p_title_lower = p.get("title", "").lower().strip()
                p_brand_lower = p.get("brand", "").lower().strip()
                
                # Check for brand matches
                if p_brand_lower == item_brand_lower:
                    # Strip brand name from titles to compare the core product name
                    p_core = p_title_lower.replace(p_brand_lower, "").strip()
                    item_core = item_title_lower.replace(item_brand_lower, "").strip()
                    
                    # Remove punctuation and generic terms
                    for term in ["(₹)", "premium", "pack", "special", "edition", "1kg", "5kg", "(5kg)", "(1l)", "1l", "set", "box"]:
                        p_core = p_core.replace(term, "").strip()
                        item_core = item_core.replace(term, "").strip()
                        
                    p_core = re.sub(r'\s+', ' ', p_core)
                    item_core = re.sub(r'\s+', ' ', item_core)
                    
                    if p_core == item_core or p_core in item_core or item_core in p_core:
                        return True
            return False

        # Ingest and enrich user products
        users = ["Rajesh Kumar", "Amit Singh", "Sunita Devi", "Priya Sharma", "Sanjay Dutt", "Vijay Prashad", "Aarav Gupta", "Sneha Rao", "Rohan Mehta", "Patel Kumar"]
        positive_comments = [
            "Extremely satisfied with the build quality and cost performance.",
            "Authentic product, fast shipping and perfect packing. Highly recommended!",
            "Value for money deal. Meets all expectations flawlessly.",
            "Good product, works perfectly for my daily needs.",
            "Matches descriptions perfectly. Very reliable and sturdy."
        ]
        critical_comments = [
            "Decent product, but delivery was delayed.",
            "Quality is fine, but packaging could have been better.",
            "Good value, though fits slightly tight.",
            "Average performance, minor issues with secondary features.",
            "A bit expensive compared to offline retail options, but okay."
        ]

        added_user_count = 0
        for item in user_products:
            if len(products) >= 600:
                break
            # Check if this item is already in our hardcoded seed set
            if is_duplicate(item, products):
                continue

            # Settle stock Unsplash image
            cat = item["category"]
            image_url = item.get("image")
            if not image_url:
                image_url = get_exact_image(item["title"], cat)

            
            # Settle vendors and pricing
            current_price = item["current_price"]
            p_amz = current_price
            p_flp = int(current_price * random.uniform(1.00, 1.05))
            
            other_name = categories_data[cat]["other_vendor"]
            p_oth = int(current_price * random.uniform(0.99, 1.04))
            
            # Ensure Amazon is chepeast baseline or adjust min value
            if p_flp < p_amz: p_flp = p_amz
            if p_oth < p_amz: p_oth = p_amz
            
            rating = item["rating"]
            num_reviews = random.randint(50, 2500)
            
            # Mock reviews
            reviews = []
            for i in range(2):
                user = random.choice(users) + f" {random.randint(1,99)}"
                text = random.choice(positive_comments if rating >= 4.3 else critical_comments)
                rev_rating = int(rating) if random.random() > 0.3 else min(5, int(rating) + 1)
                date = (datetime.now() - timedelta(days=random.randint(1,25))).strftime("%Y-%m-%d")
                reviews.append({"user": user, "rating": rev_rating, "text": text, "date": date})
                
            insights = ["Best time to buy!", "Price stable", "Wait for price drop!", "Price is at 30-day low"]
            insight = random.choice(insights)
            
            products.append({
                "_id": ObjectId(),
                "title": item["title"],
                "brand": item["brand"],
                "category": cat,
                "image": image_url,
                "rating": rating,
                "num_reviews": num_reviews,
                "original_price": item["original_price"],
                "vendors": [
                    {"name": "amazon", "price": p_amz, "link": get_vendor_link("amazon", item["title"])},
                    {"name": "flipkart", "price": p_flp, "link": get_vendor_link("flipkart", item["title"])},
                    {"name": other_name, "price": p_oth, "link": get_vendor_link(other_name, item["title"])}
                ],
                "ai_insight": insight,
                "discount_check": "Genuine discount!" if random.random() > 0.15 else "artificial MSRP inflation suspicious",
                "review_sentiment": "Highly Positive" if rating >= 4.5 else ("Mostly Positive" if rating >= 4.1 else "Mixed review"),
                "reviews": reviews
            })
            added_user_count += 1
            
        print(f"Added {added_user_count} unique user products after deduplication check.")

        # Seed generator to guarantee 600 distinct products
        generated_count = 0
        target_total = 600
        
        # Keep track of existing titles to avoid exact duplicates
        existing_titles = {p["title"] for p in products}
        categories = list(categories_data.keys())
        
        while len(products) < target_total:
            cat = categories[generated_count % len(categories)]
            meta = categories_data[cat]
            
            brand = random.choice(meta["brands"])
            ptype = random.choice(meta["types"])
            
            # Combine brand and type, adding minor variations to ensure unique titles
            variation = ""
            if generated_count > 50 and generated_count <= 100:
                variation = " (Premium Edition)"
            elif generated_count > 100 and generated_count <= 180:
                variation = " (Pro Pack)"
            elif generated_count > 180 and generated_count <= 260:
                variation = " (Value Pack)"
            elif generated_count > 260 and generated_count <= 340:
                variation = " (Special Edition)"
            elif generated_count > 340 and generated_count <= 420:
                variation = " (Signature Series)"
            elif generated_count > 420:
                variation = " (Travel Pack)"
                
            title = f"{brand} {ptype}{variation}"
            
            if title in existing_titles:
                generated_count += 1
                continue
                
            existing_titles.add(title)
            
            # Base price range
            min_p, max_p = meta["base_price_range"]
            original_price = int(random.uniform(min_p, max_p))
            discount = random.uniform(0.10, 0.45) # 10% to 45% discount
            
            # Price calculations
            current_price = int(original_price * (1 - discount))
            if current_price < 20: current_price = 20
            if original_price <= current_price:
                original_price = int(current_price * 1.3)
                
            # Randomize vendor pricing around current price
            other_name = meta["other_vendor"]
            
            p_amz = int(current_price * random.uniform(0.98, 1.05))
            p_flp = int(current_price * random.uniform(0.98, 1.05))
            p_oth = int(current_price * random.uniform(0.97, 1.04))
            
            # Ensure the minimum of the three equals current_price
            min_val = min(p_amz, p_flp, p_oth)
            if min_val > current_price:
                diff = min_val - current_price
                p_amz -= diff
                p_flp -= diff
                p_oth -= diff
            elif min_val < current_price:
                if p_amz == min_val: p_amz = current_price
                elif p_flp == min_val: p_flp = current_price
                else: p_oth = current_price
            
            insights = ["Best time to buy!", "Price stable", "Wait for price drop!", "Price is at 30-day low"]
            insight = random.choice(insights)
            
            rating = round(random.uniform(3.8, 4.9), 1)
            num_reviews = random.randint(30, 2500)
            
            reviews = []
            users = ["Rajesh Kumar", "Amit Singh", "Sunita Devi", "Priya Sharma", "Sanjay Dutt", "Vijay Prashad", "Aarav Gupta", "Sneha Rao", "Rohan Mehta", "Patel Kumar"]
            positive_comments = [
                "Extremely satisfied with the build quality and cost performance.",
                "Authentic product, fast shipping and perfect packing. Highly recommended!",
                "Value for money deal. Meets all expectations flawlessly.",
                "Good product, works perfectly for my daily needs.",
                "Matches descriptions perfectly. Very reliable and sturdy."
            ]
            critical_comments = [
                "Decent product, but delivery was delayed.",
                "Quality is fine, but packaging could have been better.",
                "Good value, though fits slightly tight.",
                "Average performance, minor issues with secondary features.",
                "A bit expensive compared to offline retail options, but okay."
            ]
            
            for i in range(2):
                user = random.choice(users) + f" {random.randint(1,99)}"
                text = random.choice(positive_comments if rating >= 4.3 else critical_comments)
                rev_rating = int(rating) if random.random() > 0.3 else min(5, int(rating) + 1)
                date = (datetime.now() - timedelta(days=random.randint(1,25))).strftime("%Y-%m-%d")
                reviews.append({"user": user, "rating": rev_rating, "text": text, "date": date})
            
            # Select premium image deterministically based on title
            image_url = get_exact_image(title, cat)

            products.append({
                "_id": ObjectId(),
                "title": title,
                "brand": brand,
                "category": cat,
                "image": image_url,
                "rating": rating,
                "num_reviews": num_reviews,
                "original_price": original_price,
                "vendors": [
                    {"name": "amazon", "price": p_amz, "link": get_vendor_link("amazon", title)},
                    {"name": "flipkart", "price": p_flp, "link": get_vendor_link("flipkart", title)},
                    {"name": other_name, "price": p_oth, "link": get_vendor_link(other_name, title)}
                ],
                "ai_insight": insight,
                "discount_check": "Genuine discount!" if random.random() > 0.15 else "artificial MSRP inflation suspicious",
                "review_sentiment": "Highly Positive" if rating >= 4.5 else ("Mostly Positive" if rating >= 4.1 else "Mixed review"),
                "reviews": reviews
            })
            
            generated_count += 1

        # Load the harvested Unsplash cache
        unsplash_cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unsplash_cache.json")
        unsplash_cache = {"keywords": {}, "categories": {}}
        if os.path.exists(unsplash_cache_file):
            try:
                with open(unsplash_cache_file, "r", encoding="utf-8") as f:
                    unsplash_cache = json.load(f)
            except Exception as e:
                print(f"Error loading unsplash_cache.json: {e}")

        # Keep track of used Unsplash photo IDs to prevent duplicates
        used_photo_ids = set()

        def get_unique_photo_id(title, category):
            title_lower = title.lower()
            
            # Map title substring to keyword in cache
            for kw in unsplash_cache.get("keywords", {}).keys():
                if kw in title_lower or (kw == "waterbottle" and "water bottle" in title_lower) or (kw == "facewash" and "face wash" in title_lower):
                    for photo_id in unsplash_cache["keywords"][kw]:
                        if photo_id not in used_photo_ids:
                            used_photo_ids.add(photo_id)
                            return photo_id
            
            # Fallback to category list
            cat_name = category
            if cat_name in unsplash_cache.get("categories", {}):
                for photo_id in unsplash_cache["categories"][cat_name]:
                    if photo_id not in used_photo_ids:
                        used_photo_ids.add(photo_id)
                        return photo_id

            # Ultimate fallback - search any category for an unused ID
            for cat_list in unsplash_cache.get("categories", {}).values():
                for photo_id in cat_list:
                    if photo_id not in used_photo_ids:
                        used_photo_ids.add(photo_id)
                        return photo_id
            for kw_list in unsplash_cache.get("keywords", {}).values():
                for photo_id in kw_list:
                    if photo_id not in used_photo_ids:
                        used_photo_ids.add(photo_id)
                        return photo_id

            return None

        # Populate price histories and assign a completely unique matching Unsplash image URL to every product
        for idx, p in enumerate(products):
            photo_id = get_unique_photo_id(p["title"], p["category"])
            if photo_id:
                if photo_id.startswith("http"):
                    p["image"] = photo_id
                else:
                    p["image"] = f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=600&q=80"
            else:
                fallback_url = get_exact_image(p["title"], p["category"])
                p["image"] = f"{fallback_url}&sig={idx + 1}"

            amz_p = next(v["price"] for v in p["vendors"] if v["name"] == "amazon")
            flp_p = next(v["price"] for v in p["vendors"] if v["name"] == "flipkart")
            other_vendor = next(v for v in p["vendors"] if v["name"] not in ["amazon", "flipkart"])
            other_name = other_vendor["name"]
            other_p = other_vendor["price"]
            
            p["price_history"] = get_price_history(amz_p, flp_p, other_p, other_name)
            p["current_price"] = min(v["price"] for v in p["vendors"])
            p["discount_pct"] = round(((p["original_price"] - p["current_price"]) / p["original_price"]) * 100)

        return products


    # API CRUD operations helper
    def get_products(self, category=None, search_query=None):
        if self.use_mongodb:
            query = {}
            if category and category != "All":
                query["category"] = category
            if search_query:
                keywords = [k.strip() for k in search_query.lower().split() if k.strip()]
                if keywords:
                    and_clauses = []
                    for kw in keywords:
                        and_clauses.append({
                            "$or": [
                                {"title": {"$regex": kw, "$options": "i"}},
                                {"brand": {"$regex": kw, "$options": "i"}},
                                {"category": {"$regex": kw, "$options": "i"}}
                            ]
                        })
                    query["$and"] = and_clauses
            cursor = self.db["products"].find(query)
            # Convert ObjectId to string
            result = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                result.append(doc)
            return result
        else:
            data = self._read_fallback()
            products = data.get("products", [])
            result = []
            for p in products:
                # Filter category
                if category and category != "All" and p.get("category") != category:
                    continue
                # Filter search query
                if search_query:
                    keywords = [k.strip() for k in search_query.lower().split() if k.strip()]
                    if keywords:
                        match = True
                        for kw in keywords:
                            title_match = kw in p.get("title", "").lower()
                            brand_match = kw in p.get("brand", "").lower()
                            cat_match = kw in p.get("category", "").lower()
                            if not (title_match or brand_match or cat_match):
                                match = False
                                break
                        if not match:
                            continue
                result.append(p)
            return result

    def get_product(self, product_id):
        if self.use_mongodb:
            try:
                # Handle both string ID and ObjectId
                oid = ObjectId(product_id) if ObjectId.is_valid(product_id) else product_id
                doc = self.db["products"].find_one({"_id": oid})
                if doc:
                    doc["_id"] = str(doc["_id"])
                return doc
            except Exception:
                return None
        else:
            data = self._read_fallback()
            for p in data.get("products", []):
                if str(p.get("_id")) == str(product_id):
                    return p
            return None

    def get_user_by_email(self, email):
        if self.use_mongodb:
            user = self.db["users"].find_one({"email": email.lower()})
            if user:
                user["_id"] = str(user["_id"])
            return user
        else:
            data = self._read_fallback()
            for u in data.get("users", []):
                if u.get("email").lower() == email.lower():
                    return u
            return None

    def get_user_by_id(self, user_id):
        if self.use_mongodb:
            try:
                oid = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
                user = self.db["users"].find_one({"_id": oid})
                if user:
                    user["_id"] = str(user["_id"])
                return user
            except Exception:
                return None
        else:
            data = self._read_fallback()
            for u in data.get("users", []):
                if str(u.get("_id")) == str(user_id):
                    return u
            return None

    def create_user(self, user_dict):
        user_dict["email"] = user_dict["email"].lower()
        if self.use_mongodb:
            # Check if user exists
            if self.db["users"].find_one({"email": user_dict["email"]}):
                return None
            user_dict["_id"] = ObjectId()
            result = self.db["users"].insert_one(user_dict)
            user_dict["_id"] = str(result.inserted_id)
            return user_dict
        else:
            data = self._read_fallback()
            # Check if user exists
            for u in data.get("users", []):
                if u.get("email") == user_dict["email"]:
                    return None
            
            user_dict["_id"] = str(ObjectId())
            data["users"].append(user_dict)
            self._write_fallback(data)
            return user_dict

    def get_favorites(self, user_id):
        user_id = str(user_id)
        if self.use_mongodb:
            fav_doc = self.db["favorites"].find_one({"user_id": user_id})
            if not fav_doc:
                return []
            fav_ids = fav_doc.get("product_ids", [])
            # Fetch details of those favorited items
            cursor = self.db["products"].find({"_id": {"$in": [ObjectId(pid) if ObjectId.is_valid(pid) else pid for pid in fav_ids]}})
            result = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                result.append(doc)
            return result
        else:
            data = self._read_fallback()
            favs = data.get("favorites", {})
            fav_ids = favs.get(user_id, [])
            result = []
            for pid in fav_ids:
                p = self.get_product(pid)
                if p:
                    result.append(p)
            return result

    def toggle_favorite(self, user_id, product_id):
        user_id = str(user_id)
        product_id = str(product_id)
        
        # Verify product exists
        if not self.get_product(product_id):
            return {"status": "error", "message": "Product not found"}
            
        if self.use_mongodb:
            fav_doc = self.db["favorites"].find_one({"user_id": user_id})
            if not fav_doc:
                self.db["favorites"].insert_one({"user_id": user_id, "product_ids": [product_id]})
                return {"status": "added", "message": "Added to favorites"}
            
            product_ids = fav_doc.get("product_ids", [])
            if product_id in product_ids:
                product_ids.remove(product_id)
                self.db["favorites"].update_one({"user_id": user_id}, {"$set": {"product_ids": product_ids}})
                return {"status": "removed", "message": "Removed from favorites"}
            else:
                product_ids.append(product_id)
                self.db["favorites"].update_one({"user_id": user_id}, {"$set": {"product_ids": product_ids}})
                return {"status": "added", "message": "Added to favorites"}
        else:
            data = self._read_fallback()
            favs = data.setdefault("favorites", {})
            product_ids = favs.setdefault(user_id, [])
            
            if product_id in product_ids:
                product_ids.remove(product_id)
                status = "removed"
                msg = "Removed from favorites"
            else:
                product_ids.append(product_id)
                status = "added"
                msg = "Added to favorites"
                
            self._write_fallback(data)
            return {"status": status, "message": msg}

    def is_favorite(self, user_id, product_id):
        user_id = str(user_id)
        product_id = str(product_id)
        if self.use_mongodb:
            fav_doc = self.db["favorites"].find_one({"user_id": user_id})
            if not fav_doc:
                return False
            return product_id in fav_doc.get("product_ids", [])
        else:
            data = self._read_fallback()
            favs = data.get("favorites", {})
            return product_id in favs.get(user_id, [])
