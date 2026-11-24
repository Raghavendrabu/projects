from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['shoppal']
products = db['products']

print("=" * 60)
print("ADDING IMAGES TO ALL 55 PRODUCTS")
print("=" * 60)

# First, add a default image to ALL products
result = products.update_many({}, {'$set': {'image': 'http://localhost:5001/images/lakme_sunscreen.jpg'}})
print(f"✅ Added default image to {result.modified_count} products")

# Now update specific products with their own images
updates = [
    # Skincare
    ('Minimalist SPF 50 Sunscreen', 'minimalist_sunscreen.jpg'),
    ('Plum 10% Niacinamide Serum', 'plum_serum.jpg'),
    ('Lakmé Sun Expert SPF 50', 'lakme_sunscreen.jpg'),
    ('Mamaearth Vitamin C Face Wash', 'mamaearth_facewash.jpg'),
    ('The Derma Co Niacinamide Serum', 'Derma_co_niacinamide_serum.jpg'),
    ('Dot & Key Vitamin C Serum', 'Dot_and_key_vitamin_c_serum.jpg'),
    ('Cetaphil Gentle Cleanser', 'Cetaphil_gentle_cleanser.jpg'),
    ('Neutrogena Hydro Boost', 'Neutrogena_hydro_boost.jpg'),
    ('Biotique Almond Oil', 'Biotique_almond_oil.jpg'),
    
    # Clothing
    ('Women Cotton Kurti', 'biba_kurti.jpg'),
    ('Men Casual Shirt', 'roadster_shirt.jpg'),
    ('Women Jeans', 'levis_jeans.jpg'),
    ('Women Palazzo', 'Women_palazzo.jpg'),
    ('Men Denim Jeans', 'Men_Denim_jeans.jpg'),
    ('Men Formal Shirt', 'Men_formal_shirt.jpg'),
    ('Women Silk Saree', 'Women_silk_saree.jpg'),
    
    # Kitchen
    ('Prestige Pressure Cooker', 'prestige_cooker.jpg.jpg'),
    ('Non-Stick Tawa', 'pigeon_tawa.jpg'),
    ('Philips Air Fryer', 'Phillips_Air_fryer.jpg'),
    ('Prestige Mixer Grinder', 'Prestige_mixer_grinder.jpg'),
    ('Non-Stick Kadhai', 'Non_stick_kadhai.jpg'),
    ('Kent Water Purifier', 'Kent_water_purifier.jpg'),
    ('Samsung Microwave', 'Samsung_microwave.jpg'),
    
    # Electronics
    ('boAt Airdopes 141', 'boat_airdopes.jpg'),
    ('Noise Smart Watch', 'noise_watch.jpg'),
    ('Samsung Fast Charger', 'samsung_charger.jpg'),
    ('Anker USB-C Charger', 'Anker_USB_charger.jpg'),
    ('JBL Speaker', 'JBL_speaker.jpg'),
    ('Logitech Keyboard Mouse', 'Logitech_keyboard_mouse.jpg'),
    ('Logitech Webcam', 'Logitech_webcam.jpg'),
    ('Mi Power Bank', 'Mi_power_bank.jpg'),
    ('Razer Gaming Mouse', 'Razergaming_mouse.jpg'),
    ('Portronics Laptop Stand', 'Portronics_laptop_stand.jpg'),
    
    # Stationery
    ('Classmate Notebook', 'Classmate_notebook.jpg'),
    ('Unicorn Gel Pens', 'pens.jpg'),
    ('Camlin Geometry Box', 'Camlin_geometry_box.jpg'),
    ('JK Copier Paper', 'JK_coppi_paper.jpg'),
    ('Faber-Castell Highlighters', 'Faber_castell_highlighter.jpg'),
    
    # Grocery
    ('India Gate Basmati Rice', 'India_gate_basmati_rice.jpg'),
    ('Fortune Oil', 'Fortune_oil.jpg'),
    ('Taj Mahal Tea', 'Tajmahal_tea.jpg'),
]

count = 0
for product_name, image_file in updates:
    result = products.update_one(
        {'name': product_name},
        {'$set': {'image': f'http://localhost:5001/images/{image_file}'}}
    )
    if result.modified_count > 0:
        print(f"✅ {product_name}")
        count += 1

print("=" * 60)
print(f"✅ Updated {count} specific products")
print(f"✅ Total products with images: {products.count_documents({'image': {'$exists': True}})}")
print("=" * 60)