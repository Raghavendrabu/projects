import os
import bcrypt
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from database import DatabaseManager
from ai_engine import AIEngine

app = Flask(__name__)
# Secure standard key for session cookie encryption
app.secret_key = os.urandom(24)

# Initialize Database Manager
db_manager = DatabaseManager()

def get_stable_hash(val):
    h = 0
    for char in str(val):
        h = (31 * h + ord(char)) & 0xFFFFFFFF
    return h


# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_api_stub'  # For redirecting to API endpoints

class User(UserMixin):
    def __init__(self, user_id, email, name):
        self.id = str(user_id)
        self.email = email
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    user_dict = db_manager.get_user_by_id(user_id)
    if user_dict:
        return User(user_dict["_id"], user_dict["email"], user_dict["name"])
    return None

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Authentication required"}), 401

@app.route('/')
def index():
    return render_template('index.html')

# Core Products APIs
@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category', 'All')
    search_query = request.args.get('q', None)
    
    products = db_manager.get_products(category=category, search_query=search_query)
    
    # Format current price and calculate discount rating for summary cards
    for p in products:
        p["_id"] = str(p["_id"])
        p["current_price"] = min(v["price"] for v in p["vendors"])
        p["discount_pct"] = round(((p["original_price"] - p["current_price"]) / p["original_price"]) * 100)
        
        # Add basic AI summaries for the list view
        p["ai_prediction_badge"] = "Best time to buy!" if "Best" in p.get("ai_insight", "") else "Price stable"
        
        # Add availability and delivery attributes deterministically using stable hash
        p_hash = get_stable_hash(p["title"])
        p["in_stock"] = (p_hash % 10 != 0)
        p["free_delivery"] = (p_hash % 2 == 0)
        
        # Add favorite indicator if user is authenticated
        p["is_favorited"] = False
        if current_user.is_authenticated:
            p["is_favorited"] = db_manager.is_favorite(current_user.id, p["_id"])
            
    return jsonify(products)

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product_detail(product_id):
    product = db_manager.get_product(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    product["_id"] = str(product["_id"])
    product["current_price"] = min(v["price"] for v in product["vendors"])
    product["discount_pct"] = round(((product["original_price"] - product["current_price"]) / product["original_price"]) * 100)
    
    # Add availability and delivery attributes deterministically using stable hash
    p_hash = get_stable_hash(product["title"])
    product["in_stock"] = (p_hash % 10 != 0)
    product["free_delivery"] = (p_hash % 2 == 0)
    
    # 1. Run Dynamic AI Sentiment Analysis using TextBlob / Fallback
    sentiment_data = AIEngine.analyze_sentiment(product.get("reviews", []))
    product["ai_sentiment"] = sentiment_data
    
    # 2. Run Dynamic AI Price Trend Prediction using scikit-learn
    # We predict the trend for the lowest-priced vendor (usually amazon or similar)
    cheapest_vendor = min(product["vendors"], key=lambda x: x["price"])
    prediction_data = AIEngine.predict_price_trend(product.get("price_history", []), cheapest_vendor["name"])
    product["ai_price_prediction"] = prediction_data
    
    # 3. Run Fake Discount Analysis
    fake_discount_data = AIEngine.calculate_fake_discount(product["original_price"], product["vendors"])
    product["ai_fake_discount"] = fake_discount_data
    
    # 4. Suggest similar products (same category, lower/similar price, excluding current)
    similar_raw = db_manager.get_products(category=product["category"])
    similar_filtered = []
    for s in similar_raw:
        if str(s["_id"]) != str(product["_id"]):
            s["_id"] = str(s["_id"])
            s["current_price"] = min(v["price"] for v in s["vendors"])
            s["discount_pct"] = round(((s["original_price"] - s["current_price"]) / s["original_price"]) * 100)
            
            s_hash = get_stable_hash(s["title"])
            s["in_stock"] = (s_hash % 10 != 0)
            s["free_delivery"] = (s_hash % 2 == 0)
            
            similar_filtered.append(s)
            
    # Sort similar products by price (ascending) and grab top 3
    similar_filtered = sorted(similar_filtered, key=lambda x: x["current_price"])[:3]
    product["similar_products"] = similar_filtered
    
    # Favorite state
    product["is_favorited"] = False
    if current_user.is_authenticated:
        product["is_favorited"] = db_manager.is_favorite(current_user.id, product["_id"])
        
    return jsonify(product)

# System Health & Status
@app.route('/api/system-status', methods=['GET'])
def get_system_status():
    return jsonify({
        "status": "online",
        "database": "MongoDB" if db_manager.use_mongodb else "JSON Failover File",
        "mongodb_connected": db_manager.use_mongodb
    })

# User Authentication APIs
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({"error": "All fields (Name, Email, Password) are required."}), 400
        
    existing_user = db_manager.get_user_by_email(email)
    if existing_user:
        return jsonify({"error": "An account with this email already exists."}), 400
        
    # Securely hash password with salt using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user_dict = {
        "name": name,
        "email": email.lower(),
        "password": hashed_password
    }
    
    created_user = db_manager.create_user(user_dict)
    if not created_user:
        return jsonify({"error": "Failed to create account. Please try again."}), 500
        
    # Log user in immediately after registration
    user_obj = User(created_user["_id"], created_user["email"], created_user["name"])
    login_user(user_obj)
    
    return jsonify({
        "message": "Account created successfully!",
        "user": {
            "name": user_obj.name,
            "email": user_obj.email
        }
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and Password are required."}), 400
        
    user_dict = db_manager.get_user_by_email(email)
    if not user_dict:
        return jsonify({"error": "Invalid email or password."}), 401
        
    # Verify hashed password
    hashed_pw = user_dict["password"].encode('utf-8')
    if bcrypt.checkpw(password.encode('utf-8'), hashed_pw):
        user_obj = User(user_dict["_id"], user_dict["email"], user_dict["name"])
        login_user(user_obj, remember=True)
        return jsonify({
            "message": "Logged in successfully!",
            "user": {
                "name": user_obj.name,
                "email": user_obj.email
            }
        })
        
    return jsonify({"error": "Invalid email or password."}), 401

@app.route('/api/auth/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"})

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    if current_user.is_authenticated:
        return jsonify({
            "logged_in": True,
            "user": {
                "name": current_user.name,
                "email": current_user.email
            }
        })
    return jsonify({"logged_in": False})

@app.route('/api/auth/stub')
def login_api_stub():
    return jsonify({"error": "Authentication required"}), 401

# Favorites Management APIs
@app.route('/api/favorites', methods=['GET'])
@login_required
def get_favorites():
    fav_products = db_manager.get_favorites(current_user.id)
    # Mark as favorited and process prices
    for p in fav_products:
        p["_id"] = str(p["_id"])
        p["current_price"] = min(v["price"] for v in p["vendors"])
        p["discount_pct"] = round(((p["original_price"] - p["current_price"]) / p["original_price"]) * 100)
        p["is_favorited"] = True
        p["ai_prediction_badge"] = "Best time to buy!" if "Best" in p.get("ai_insight", "") else "Price stable"
        
        # Add availability and delivery attributes deterministically using stable hash
        p_hash = get_stable_hash(p["title"])
        p["in_stock"] = (p_hash % 10 != 0)
        p["free_delivery"] = (p_hash % 2 == 0)
        
    return jsonify(fav_products)

@app.route('/api/favorites/toggle', methods=['POST'])
@login_required
def toggle_favorite():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({"error": "product_id parameter is required."}), 400
        
    res = db_manager.toggle_favorite(current_user.id, product_id)
    return jsonify(res)

# AI Shopping Agent Interactive Chat API
@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.get_json() or {}
    message = data.get('message', '')
    product_id = data.get('product_id', None)
    
    response_data = AIEngine.chat_response(message, db_manager, active_product_id=product_id)
    return jsonify(response_data)

if __name__ == '__main__':
    # Run server locally on standard port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)

