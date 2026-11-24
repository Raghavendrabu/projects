import unittest
import sys
import os
from datetime import datetime, timedelta

# Ensure workspace is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine import AIEngine

class TestAIEngine(unittest.TestCase):
    
    def test_analyze_sentiment_empty(self):
        """Test sentiment analysis when no reviews are present"""
        res = AIEngine.analyze_sentiment([])
        self.assertEqual(res["overall_sentiment"], "No reviews available")
        self.assertEqual(res["average_polarity"], 0.0)
        self.assertEqual(res["positive_percentage"], 0)

    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis with positive reviews"""
        reviews = [
            {"user": "A", "rating": 5, "text": "Absolutely love this, best purchase ever! Perfect and amazing.", "date": "2026-05-10"},
            {"user": "B", "rating": 4, "text": "Very good product, works extremely well and very happy.", "date": "2026-05-11"}
        ]
        res = AIEngine.analyze_sentiment(reviews)
        self.assertIn("Positive", res["overall_sentiment"])
        self.assertGreater(res["average_polarity"], 0.0)
        self.assertGreater(res["positive_percentage"], 50)

    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis with negative reviews"""
        reviews = [
            {"user": "A", "rating": 1, "text": "This is worse and poor. Sticky and dry, very bad.", "date": "2026-05-10"},
            {"user": "B", "rating": 2, "text": "Worst quality, broke down instantly. Very disappointed.", "date": "2026-05-11"}
        ]
        res = AIEngine.analyze_sentiment(reviews)
        self.assertEqual(res["overall_sentiment"], "Negative")
        self.assertLess(res["average_polarity"], 0.0)
        self.assertGreater(res["negative_percentage"], 50)

    def test_predict_price_trend_stable(self):
        """Test 7-day price predictions when price remains completely flat"""
        history = [
            {"date": "2026-05-01", "amazon": 500, "flipkart": 510},
            {"date": "2026-05-02", "amazon": 500, "flipkart": 510},
            {"date": "2026-05-03", "amazon": 500, "flipkart": 510},
            {"date": "2026-05-04", "amazon": 500, "flipkart": 510},
            {"date": "2026-05-05", "amazon": 500, "flipkart": 510}
        ]
        res = AIEngine.predict_price_trend(history, vendor_name="amazon")
        self.assertEqual(res["recommendation"], "Price stable")
        self.assertEqual(res["price_change_predicted"], 0)
        self.assertEqual(len(res["predictions_7_days"]), 7)

    def test_predict_price_trend_upward(self):
        """Test price predictions with rising price history"""
        history = [
            {"date": "2026-05-01", "amazon": 500},
            {"date": "2026-05-02", "amazon": 510},
            {"date": "2026-05-03", "amazon": 520},
            {"date": "2026-05-04", "amazon": 530},
            {"date": "2026-05-05", "amazon": 540}
        ]
        res = AIEngine.predict_price_trend(history, vendor_name="amazon")
        self.assertEqual(res["recommendation"], "Buy Now!")
        self.assertGreater(res["price_change_predicted"], 0)
        self.assertGreater(res["predicted_price_7_days"], 540)

    def test_predict_price_trend_downward(self):
        """Test price predictions with dropping price history"""
        history = [
            {"date": "2026-05-01", "amazon": 500},
            {"date": "2026-05-02", "amazon": 490},
            {"date": "2026-05-03", "amazon": 480},
            {"date": "2026-05-04", "amazon": 470},
            {"date": "2026-05-05", "amazon": 460}
        ]
        res = AIEngine.predict_price_trend(history, vendor_name="amazon")
        self.assertEqual(res["recommendation"], "Wait for drop!")
        self.assertLess(res["price_change_predicted"], 0)
        self.assertLess(res["predicted_price_7_days"], 460)

    def test_calculate_fake_discount_genuine(self):
        """Test fake discount check when prices are competitively varied"""
        vendors = [
            {"name": "amazon", "price": 400},
            {"name": "flipkart", "price": 420},
            {"name": "nykaa", "price": 450}
        ]
        res = AIEngine.calculate_fake_discount(500, vendors)
        self.assertEqual(res["rating"], "Genuine Discount")
        self.assertLess(res["score"], 35)

    def test_calculate_fake_discount_suspicious(self):
        """Test fake discount check when pricing spread is tight and claim discount is high"""
        vendors = [
            {"name": "amazon", "price": 300},
            {"name": "flipkart", "price": 300},
            {"name": "nykaa", "price": 305}
        ]
        res = AIEngine.calculate_fake_discount(800, vendors)
        self.assertEqual(res["rating"], "Highly Suspicious")
        self.assertGreater(res["score"], 70)

    def test_chat_response_greetings(self):
        """Test chat response greeting intent"""
        res = AIEngine.chat_response("Hi, who are you?", None)
        self.assertIn("Hello! I am your Shoppal AI Shopping Assistant.", res["response"])
        self.assertNotIn("suggested_products", res)

    def test_chat_response_audit_no_product(self):
        """Test chat response audit when no active product is opened"""
        res = AIEngine.chat_response("Can you audit this product?", None)
        self.assertIn("MSRP Discount Auditor", res["response"])
        self.assertIn("click on any product card", res["response"])

    def test_chat_response_audit_with_product(self):
        """Test chat response audit with an active product ID"""
        class MockDB:
            def get_product(self, pid):
                return {
                    "_id": "mock_id",
                    "title": "Minimalist Sunscreen",
                    "brand": "Minimalist",
                    "category": "Skincare",
                    "original_price": 600,
                    "vendors": [
                        {"name": "amazon", "price": 500},
                        {"name": "flipkart", "price": 510}
                    ],
                    "reviews": [
                        {"user": "A", "rating": 5, "text": "Perfect sunscreen, love it!", "date": "2026-05-10"}
                    ],
                    "price_history": [
                        {"date": "2026-05-01", "amazon": 500},
                        {"date": "2026-05-02", "amazon": 500},
                        {"date": "2026-05-03", "amazon": 500}
                    ]
                }
        db = MockDB()
        res = AIEngine.chat_response("Please audit this product", db, active_product_id="mock_id")
        self.assertIn("AI Audit Report for `Minimalist Sunscreen`", res["response"])
        self.assertIn("suggested_products", res)
        self.assertEqual(res["suggested_products"][0]["title"], "Minimalist Sunscreen")

    def test_chat_response_category_trend(self):
        """Test chat response trend forecast for a specific category"""
        class MockDB:
            def get_products(self, category=None):
                return [
                    {
                        "_id": "id1",
                        "title": "Minimalist Sunscreen",
                        "brand": "Minimalist",
                        "category": "Skincare",
                        "original_price": 600,
                        "vendors": [
                            {"name": "amazon", "price": 500},
                            {"name": "flipkart", "price": 510}
                        ],
                        "price_history": [
                            {"date": "2026-05-01", "amazon": 500},
                            {"date": "2026-05-02", "amazon": 500},
                            {"date": "2026-05-03", "amazon": 500}
                        ]
                    }
                ]
        db = MockDB()
        res = AIEngine.chat_response("Will skincare drop in price next week?", db)
        self.assertIn("AI Market Forecast for `Skincare` Category", res["response"])

    def test_chat_response_search_products(self):
        """Test chat response searching and recommending matching products"""
        class MockDB:
            def get_products(self, category=None):
                return [
                    {
                        "_id": "id1",
                        "title": "boAt Rockerz Headphones",
                        "brand": "boAt",
                        "category": "Electronics",
                        "rating": 4.5,
                        "num_reviews": 100,
                        "original_price": 2000,
                        "vendors": [
                            {"name": "amazon", "price": 1200},
                            {"name": "flipkart", "price": 1250}
                        ]
                    },
                    {
                        "_id": "id2",
                        "title": "Minimalist Sunscreen",
                        "brand": "Minimalist",
                        "category": "Skincare",
                        "rating": 4.6,
                        "num_reviews": 100,
                        "original_price": 600,
                        "vendors": [
                            {"name": "amazon", "price": 500},
                            {"name": "flipkart", "price": 510}
                        ]
                    }
                ]
        db = MockDB()
        res = AIEngine.chat_response("Suggest some headphones", db)
        self.assertIn("AI Recommendations matching your interest", res["response"])
        self.assertEqual(len(res["suggested_products"]), 1)
        self.assertEqual(res["suggested_products"][0]["title"], "boAt Rockerz Headphones")

if __name__ == '__main__':
    unittest.main()
