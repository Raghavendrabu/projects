from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['shoppal']
products = db['products']

# ALL 55 PRODUCTS with their images from your Downloads folder
all_products = [
    # SKINCARE (9)
    ("Minimalist SPF 50 Sunscreen", "minimalist_sunscreen.jpg"),
    ("Plum 10% Niacinamide Serum", "plum_serum.jpg"),
    ("Lakmé Sun Expert SPF 50", "lakme_sunscreen.jpg"),
    ("Mamaearth Vitamin C Face Wash", "mamaearth_facewash.jpg"),
    ("The Derma Co 10% Niacinamide Serum", "Derma_co_niacinamide_serum.jpg"),
    ("Dot & Key Vitamin C Serum", "Dot_and_key_vitamin_c_serum.jpg"),
    ("Cetaphil Gentle Skin Cleanser", "Cetaphil_gentle_cleanser.jpg"),
    ("Neutrogena Hydro Boost Water Gel", "Neutrogena_hydro_boost.jpg"),
    ("Biotique Bio Almond Oil", "Biotique_almond_oil.jpg"),
    
    # CLOTHING (11)
    ("Women Cotton Kurti", "biba_kurti.jpg"),
    ("Women's Cotton Kurti", "biba_kurti.jpg"),
    ("Men Casual Shirt", "roadster_shirt.jpg"),
    ("Men's Casual Shirt", "roadster_shirt.jpg"),
    ("Women Jeans", "levis_jeans.jpg"),
    ("Women's Jeans", "levis_jeans.jpg"),
    ("Women's Palazzo Pants", "Women_palazzo.jpg"),
    ("Men's Denim Jeans", "Men_Denim_jeans.jpg"),
    ("Men's Formal Shirt", "Men_formal_shirt.jpg"),
    ("Women's Sports Bra", "sports_bra.jpg"),
    ("Women's Silk Saree", "Women_silk_saree.jpg"),
    
    # KITCHEN (9)
    ("Prestige Pressure Cooker", "prestige_cooker.jpg.jpg"),
    ("Prestige Pressure Cooker 5L", "prestige_cooker.jpg.jpg"),
    ("Non-Stick Tawa", "pigeon_tawa.jpg"),
    ("Philips Air Fryer", "Phillips_Air_fryer.jpg"),
    ("Philips Air Fryer 4.5L", "Phillips_Air_fryer.jpg"),
    ("Prestige Mixer Grinder 750W", "Prestige_mixer_grinder.jpg"),
    ("Pigeon Non-Stick Kadhai", "Non_stick_kadhai.jpg"),
    ("Kent Water Purifier", "Kent_water_purifier.jpg"),
    ("Samsung Microwave Oven 20L", "Samsung_microwave.jpg"),
    
    # ELECTRONICS (11)
    ("boAt Airdopes 141", "boat_airdopes.jpg"),
    ("Samsung Fast Charger", "samsung_charger.jpg"),
    ("Samsung 20W Fast Charger", "samsung_charger.jpg"),
    ("Noise Smart Watch", "noise_watch.jpg"),
    ("Logitech Wireless Keyboard & Mouse", "Logitech_keyboard_mouse.jpg"),
    ("Anker USB-C Fast Charger 65W", "Anker_USB_charger.jpg"),
    ("JBL Bluetooth Speaker", "JBL_speaker.jpg"),
    ("Portronics Laptop Stand", "Portronics_laptop_stand.jpg"),
    ("Mi Power Bank 20000mAh", "Mi_power_bank.jpg"),
    ("Razer Gaming Mouse", "Razergaming_mouse.jpg"),
    ("Logitech HD Webcam", "Logitech_webcam.jpg"),
    
    # STATIONERY (5)
    ("Classmate Notebook Pack", "Classmate_notebook.jpg"),
    ("Unicorn Gel Pens Set", "pens.jpg"),
    ("Camlin Geometry Box", "Camlin_geometry_box.jpg"),
    ("JK Copier A4 Paper 500 Sheets", "JK_coppi_paper.jpg"),
    ("Faber-Castell Highlighter Pens Set", "Faber_castell_highlighter.jpg"),
    
    # GROCERY (3)
    ("India Gate Basmati Rice 5kg", "India_gate_basmati_rice.jpg"),
    ("Fortune Vegetable Oil 1L", "Fortune_oil.jpg"),
    ("Taj Mahal Tea 500g", "Tajmahal_tea.jpg"),
]

print("="*50)
print("ADDING IMAGES TO ALL 55 PRODUCTS")
print("="*50)

count = 0
for name, img in all_products:
    result = products.update_one(
        {"name": name},
        {"$set": {"image": f"http://localhost:5001/images/{img}"}}
    )
    if result.modified_count > 0:
        print(f"✅ {name[:40]}...")
        count += 1
    else:
        print(f"⚠️ Not found: {name}")

print("="*50)
print(f"✅ UPDATED {count} PRODUCTS WITH YOUR IMAGES!")
print("="*50)