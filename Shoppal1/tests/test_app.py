import unittest
import json
import sys
import os

# Ensure workspace is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db_manager

class TestAppAPI(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Add a unique test user in seed database if needed
        self.test_email = "tester@shoppal.in"
        self.test_password = "securePassword123"
        self.test_name = "API Tester"

    def test_system_status(self):
        """Test the backend connection health reporting endpoint"""
        response = self.client.get('/api/system-status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "online")
        self.assertIn("database", data)

    def test_products_list_all(self):
        """Test getting all items in e-commerce catalog"""
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        products = json.loads(response.data)
        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 0)
        
        # Validate schema structure
        first_item = products[0]
        self.assertIn("_id", first_item)
        self.assertIn("title", first_item)
        self.assertIn("brand", first_item)
        self.assertIn("category", first_item)
        self.assertIn("current_price", first_item)
        self.assertIn("original_price", first_item)
        self.assertIn("vendors", first_item)

    def test_products_list_filter_category(self):
        """Test category filter routing"""
        response = self.client.get('/api/products?category=Skincare')
        self.assertEqual(response.status_code, 200)
        products = json.loads(response.data)
        for p in products:
            self.assertEqual(p["category"], "Skincare")

    def test_products_list_search_query(self):
        """Test text search matching"""
        response = self.client.get('/api/products?q=sunscreen')
        self.assertEqual(response.status_code, 200)
        products = json.loads(response.data)
        for p in products:
            self.assertTrue(
                "sunscreen" in p["title"].lower() or 
                "sunscreen" in p["brand"].lower() or
                "sunscreen" in p["category"].lower()
            )

    def test_product_detail_and_ai_payload(self):
        """Test detailed route fetches scikit-learn forecasts and TextBlob sentiments"""
        # Fetch any product ID first
        list_response = self.client.get('/api/products')
        products = json.loads(list_response.data)
        test_id = products[0]["_id"]
        
        # Call detail endpoint
        response = self.client.get(f'/api/products/{test_id}')
        self.assertEqual(response.status_code, 200)
        p_detail = json.loads(response.data)
        
        # Verify AI parameters
        self.assertEqual(p_detail["_id"], test_id)
        self.assertIn("ai_sentiment", p_detail)
        self.assertIn("ai_price_prediction", p_detail)
        self.assertIn("ai_fake_discount", p_detail)
        self.assertIn("similar_products", p_detail)
        
        # Validate detailed formats
        self.assertIn("overall_sentiment", p_detail["ai_sentiment"])
        self.assertIn("recommendation", p_detail["ai_price_prediction"])
        self.assertIn("score", p_detail["ai_fake_discount"])
        self.assertIsInstance(p_detail["similar_products"], list)

    def test_auth_status_anonymous(self):
        """Test auth status is false by default"""
        response = self.client.get('/api/auth/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data["logged_in"])

    def test_favorites_requires_login(self):
        """Test anonymous favorite watchlist access is blocked"""
        response = self.client.get('/api/favorites')
        self.assertEqual(response.status_code, 401)
        
        response_toggle = self.client.post('/api/favorites/toggle', 
            data=json.dumps({"product_id": "anyid"}),
            content_type='application/json'
        )
        self.assertEqual(response_toggle.status_code, 401)

    def test_auth_and_favorites_flow(self):
        """Test full user auth cycle: signup -> login -> favorites toggle -> logout"""
        # 1. Sign up new test user
        signup_data = {
            "name": self.test_name,
            "email": self.test_email,
            "password": self.test_password
        }
        # Check if user already exists in db to prevent collision errors
        existing = db_manager.get_user_by_email(self.test_email)
        if existing:
            # Clean it up for fresh testing
            if db_manager.use_mongodb:
                db_manager.db["users"].delete_one({"email": self.test_email.lower()})
                db_manager.db["favorites"].delete_one({"user_id": str(existing["_id"])})
            else:
                data = db_manager._read_fallback()
                data["users"] = [u for u in data["users"] if u["email"].lower() != self.test_email.lower()]
                if str(existing["_id"]) in data.get("favorites", {}):
                    del data["favorites"][str(existing["_id"])]
                db_manager._write_fallback(data)
                
        response_signup = self.client.post('/api/auth/signup',
            data=json.dumps(signup_data),
            content_type='application/json'
        )
        self.assertEqual(response_signup.status_code, 200)
        
        # Verify authenticated state
        response_status = self.client.get('/api/auth/status')
        data_status = json.loads(response_status.data)
        self.assertTrue(data_status["logged_in"])
        self.assertEqual(data_status["user"]["name"], self.test_name)
        
        # 2. Toggle Favorite Watchlist item
        list_response = self.client.get('/api/products')
        products = json.loads(list_response.data)
        test_product_id = products[0]["_id"]
        
        response_toggle = self.client.post('/api/favorites/toggle',
            data=json.dumps({"product_id": test_product_id}),
            content_type='application/json'
        )
        self.assertEqual(response_toggle.status_code, 200)
        data_toggle = json.loads(response_toggle.data)
        self.assertEqual(data_toggle["status"], "added")
        
        # Verify it lists in favorites now
        response_favs = self.client.get('/api/favorites')
        self.assertEqual(response_favs.status_code, 200)
        favs = json.loads(response_favs.data)
        self.assertEqual(len(favs), 1)
        self.assertEqual(favs[0]["_id"], test_product_id)
        
        # Untoggle it
        response_untoggle = self.client.post('/api/favorites/toggle',
            data=json.dumps({"product_id": test_product_id}),
            content_type='application/json'
        )
        self.assertEqual(response_untoggle.status_code, 200)
        data_untoggle = json.loads(response_untoggle.data)
        self.assertEqual(data_untoggle["status"], "removed")
        
        # 3. Log out user
        response_logout = self.client.post('/api/auth/logout')
        self.assertEqual(response_logout.status_code, 200)
        
        # Verify logged out
        response_status_final = self.client.get('/api/auth/status')
        data_status_final = json.loads(response_status_final.data)
        self.assertFalse(data_status_final["logged_in"])

if __name__ == '__main__':
    unittest.main()
