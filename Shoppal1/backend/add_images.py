from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['shoppal']
products = db['products']

print("="*50)
print("ADDING REAL IMAGES TO YOUR PRODUCTS")
print("="*50)

# First, let's see what products you have
print("\n📦 Your products by category:")
categories_count = {}
for cat in ['skincare', 'clothing', 'kitchen', 'electronics', 'stationery', 'grocery']:
    count = products.count_documents({"category": cat})
    if count > 0:
        categories_count[cat] = count
        print(f"   {cat}: {count} products")

print("\n" + "="*50)
print("Updating images...")
print("="*50)

# Map categories to your image files
category_images = {
    "skincare": "lakme_sunscreen.jpg",
    "clothing": "biba_kurti.jpg",
    "kitchen": "prestige_cooker.jpg.jpg",
    "electronics": "boat_airdopes.jpg",
    "stationery": "notebook.jpg",
    "grocery": "rice.jpg"
}

updated = 0
for category, filename in category_images.items():
    image_url = f"http://localhost:5001/images/{filename}"
    result = products.update_many(
        {"category": category},
        {"$set": {"image": image_url}}
    )
    if result.modified_count > 0:
        print(f"✅ Updated {result.modified_count} {category} products")
        updated += result.modified_count
    else:
        print(f"⚠️ No {category} products found (or already updated)")

print(f"\n✅ Total products updated: {updated}")

# Verify
print("\n📸 Verification - checking a few products:")
sample_products = products.find({}).limit(3)
for p in sample_products:
    print(f"   {p['name']} -> {p.get('image', 'No image')}")