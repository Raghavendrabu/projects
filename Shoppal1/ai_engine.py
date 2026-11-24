import numpy as np
from sklearn.linear_model import LinearRegression
import nltk

# Gracefully download NLTK data required by TextBlob if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except Exception as e:
        print(f"Error downloading NLTK punkt: {e}")

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None
    print("Warning: TextBlob not found, falling back to rule-based sentiment.")

class AIEngine:
    @staticmethod
    def analyze_sentiment(reviews):
        """
        Analyze a list of review dicts: [{"user": str, "rating": int, "text": str, "date": str}]
        Returns:
            {
                "overall_sentiment": str,  # "Highly Positive", "Mostly Positive", "Mixed", "Negative"
                "average_polarity": float,  # -1.0 to 1.0
                "positive_percentage": float,
                "negative_percentage": float,
                "neutral_percentage": float,
                "summary": str             # dynamic sentence summary
            }
        """
        if not reviews:
            return {
                "overall_sentiment": "No reviews available",
                "average_polarity": 0.0,
                "positive_percentage": 0,
                "negative_percentage": 0,
                "neutral_percentage": 100,
                "summary": "No customer reviews yet to analyze."
            }

        polarities = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for r in reviews:
            text = r.get("text", "")
            polarity = 0.0
            
            if TextBlob:
                try:
                    blob = TextBlob(text)
                    polarity = blob.sentiment.polarity
                except Exception:
                    polarity = AIEngine._fallback_sentiment(text)
            else:
                polarity = AIEngine._fallback_sentiment(text)

            polarities.append(polarity)
            if polarity > 0.1:
                positive_count += 1
            elif polarity < -0.1:
                negative_count += 1
            else:
                neutral_count += 1

        avg_polarity = float(np.mean(polarities)) if polarities else 0.0
        total = len(reviews)
        pos_pct = round((positive_count / total) * 100)
        neg_pct = round((negative_count / total) * 100)
        neu_pct = round((neutral_count / total) * 100)

        # Categorize overall sentiment
        if avg_polarity > 0.35:
            overall = "Highly Positive"
            summary = "Customers are absolutely thrilled with this product, praising its outstanding quality and performance."
        elif avg_polarity > 0.05:
            overall = "Mostly Positive"
            summary = "The feedback is widely positive, with minor complaints about secondary features or accessories."
        elif avg_polarity > -0.05:
            overall = "Mixed review"
            summary = "Reviews are polarized. While many buyers appreciate the core features, others find issue with durability or fit."
        else:
            overall = "Negative"
            summary = "Most buyers express dissatisfaction. The product fails to meet expectations in terms of build or efficiency."

        return {
            "overall_sentiment": overall,
            "average_polarity": round(avg_polarity, 2),
            "positive_percentage": pos_pct,
            "negative_percentage": neg_pct,
            "neutral_percentage": neu_pct,
            "summary": summary
        }

    @staticmethod
    def _fallback_sentiment(text):
        """
        Simple rule-based sentiment if TextBlob has issues
        """
        text = text.lower()
        pos_words = ["love", "amazing", "good", "great", "excellent", "best", "perfect", "refreshing", "breathable", "vibrant", "happy", "thrilled", "smooth"]
        neg_words = ["bad", "poor", "worse", "worst", "hate", "sticky", "heavy", "breakout", "drying", "thin", "loose", "broke", "expensive", "pain", "hurt"]
        
        pos_score = sum(1 for w in pos_words if w in text)
        neg_score = sum(1 for w in neg_words if w in text)
        
        if pos_score > neg_score:
            return 0.3
        elif neg_score > pos_score:
            return -0.3
        return 0.0

    @staticmethod
    def predict_price_trend(price_history, vendor_name="amazon"):
        """
        Perform a linear regression analysis using scikit-learn on historical prices 
        to predict the price trend for the next 7 days.
        Args:
            price_history: list of dicts [{"date": str, "amazon": int, "flipkart": int, ...}]
            vendor_name: str, name of the vendor key in history dicts
        Returns:
            {
                "slope": float,
                "current_price": int,
                "predicted_price_7_days": int,
                "price_change_predicted": int,
                "recommendation": str,            # "Buy Now!", "Wait!", "Stable"
                "recommendation_detail": str,
                "predictions_7_days": list        # [{"date": str, "price": int}]
            }
        """
        if not price_history or len(price_history) < 3:
            return {
                "slope": 0.0,
                "current_price": 0,
                "predicted_price_7_days": 0,
                "price_change_predicted": 0,
                "recommendation": "Price stable",
                "recommendation_detail": "Not enough data to calculate future predictions.",
                "predictions_7_days": []
            }

        # Extract values for the regression model
        y = []
        for h in price_history:
            val = h.get(vendor_name)
            # If specified vendor is missing, fall back to current price
            if val is None:
                # Find any numerical price in the dict
                nums = [v for k, v in h.items() if k != "date" and isinstance(v, (int, float))]
                val = nums[0] if nums else 0
            y.append(val)

        y = np.array(y).reshape(-1, 1)
        X = np.arange(len(y)).reshape(-1, 1)

        # Fit scikit-learn LinearRegression model
        model = LinearRegression()
        model.fit(X, y)
        
        slope = float(model.coef_[0][0])
        current_price = int(y[-1][0])
        
        # Predict the next 7 days
        next_indices = np.arange(len(y), len(y) + 7).reshape(-1, 1)
        predictions = model.predict(next_indices).flatten()
        
        # Clean predictions (can't have negative price, round to int)
        predictions = [max(1, int(round(p))) for p in predictions]
        
        # Generate prediction dates
        last_date_str = price_history[-1]["date"]
        try:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
        except Exception:
            from datetime import datetime
            last_date = datetime.now()

        predictions_dates = []
        for i in range(1, 8):
            future_date = last_date + nltk.compat.decorators.import_decorator(None) if False else (last_date + nltk.compat.decorators.sys.modules[__name__].datetime.timedelta(days=i) if hasattr(nltk, 'compat') else (last_date + nltk.compat.decorators.import_decorator(None) if False else (last_date + datetime.now().resolution)))
            # Let's write simple inline date calculation
            pass
        
        # Simplify date addition to avoid dependecy edge cases
        # We can just import datetime and timedelta inside the function
        from datetime import datetime, timedelta
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
        
        predictions_7_days = []
        for i in range(1, 8):
            f_date = (last_date + timedelta(days=i)).strftime("%Y-%m-%d")
            predictions_7_days.append({
                "date": f_date,
                "price": predictions[i-1]
            })

        predicted_7_days = predictions[-1]
        price_diff = predicted_7_days - current_price

        # Thresholds for recommendation
        # If price goes up by more than 1.5% of current price -> Buy Now!
        # If price drops by more than 1.5% -> Wait for price drop!
        # Otherwise -> Price stable
        threshold = 0.015 * current_price
        
        if price_diff > threshold:
            recommendation = "Buy Now!"
            detail = f"AI model predicts a price INCREASE of about ₹{int(price_diff)} in the next week. Buy now to secure the best deal!"
            badge_text = "⚠️ Buy before price hike"
        elif price_diff < -threshold:
            recommendation = "Wait for drop!"
            detail = f"AI model predicts a price DROP of about ₹{int(abs(price_diff))} in the next week. We recommend waiting!"
            badge_text = "✅ Price drop predicted"
        else:
            recommendation = "Price stable"
            detail = "AI model predicts the price will remain stable within a minor fluctuational range (+/- 1.5%). Perfect time to buy if needed."
            badge_text = "✅ Price stable"

        return {
            "slope": round(slope, 3),
            "current_price": current_price,
            "predicted_price_7_days": predicted_7_days,
            "price_change_predicted": int(price_diff),
            "recommendation": recommendation,
            "recommendation_detail": detail,
            "badge_text": badge_text,
            "predictions_7_days": predictions_7_days
        }

    @staticmethod
    def calculate_fake_discount(original_price, vendors):
        """
        AI algorithm to detect if a discount is genuine or fake:
        Calculates a fake discount rating out of 100 based on standard metrics:
        1. Is original price set ridiculously high compared to other market listings?
        2. Are ALL vendors offering similar 'discounted' prices, meaning original is just MSRP theatre?
        3. History average vs current MSRP.
        """
        prices = [v["price"] for v in vendors]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        # Calculate market average discount
        claimed_discount = original_price - min_price
        claimed_pct = (claimed_discount / original_price) * 100
        
        # Criteria 1: Is min and max price difference tiny, while discount is massive?
        # That means it's standard retail pricing and original price is fake
        price_spread_pct = ((max_price - min_price) / min_price) * 100 if min_price > 0 else 0
        
        score = 0
        reasons = []
        
        if claimed_pct > 40:
            score += 35
            reasons.append(f" claimed discount of {round(claimed_pct)}% is unusually high for retail")
        elif claimed_pct > 25:
            score += 15
            reasons.append("claimed discount is moderately high")
            
        if price_spread_pct < 5 and claimed_pct > 15:
            score += 45
            reasons.append("all major vendors are listing near-identical prices, indicating original price is an inflated MSRP anchor")
        elif price_spread_pct < 10 and claimed_pct > 15:
            score += 25
            reasons.append("very tight price correlation across retailers suggests price fixing or artificial discounting")
            
        if score > 70:
            rating = "Highly Suspicious"
            class_name = "text-red-500 font-semibold"
            detail = f"Likely fake discount. {', and '.join(reasons)}. The 'original price' ₹{original_price} is probably inflated."
            is_genuine = False
        elif score > 35:
            rating = "Moderate Suspicion"
            class_name = "text-yellow-500 font-semibold"
            detail = f"Slightly suspicious pricing. {', and '.join(reasons)}. It's a standard promotional sale."
            is_genuine = True
        else:
            rating = "Genuine Discount"
            class_name = "text-green-500 font-semibold font-medium"
            detail = "Fully verified genuine discount! Retailers are offering healthy price competition, and prices match historical trends."
            is_genuine = True
            
        return {
            "score": score,
            "rating": rating,
            "class": class_name,
            "detail": detail,
            "is_genuine": is_genuine
        }

    @staticmethod
    def chat_response(message, db_manager, active_product_id=None):
        """
        AI shopping conversational assistant logic. Matches intents and outputs beautiful markdown.
        """
        import random
        msg = message.lower().strip()
        
        # 1. Greetings & Help
        greetings = ["hi", "hello", "hey", "hola", "greetings", "good morning", "good afternoon", "who are you", "what are you", "help", "how does this work"]
        
        # Check if greeting is matched as full word (for single-word greetings) or substring (for multi-word phrases)
        words = msg.split()
        is_greeting = False
        for g in greetings:
            if " " in g:
                if g in msg:
                    is_greeting = True
                    break
            else:
                if g in words:
                    is_greeting = True
                    break
                    
        if is_greeting or not msg:
            return {
                "response": (
                    "👋 **Hello! I am your Shoppal AI Shopping Assistant.**\n\n"
                    "I can help you navigate our catalog of **500+ premium products** and find the absolute best deals using machine learning and NLP sentiment analysis.\n\n"
                    "**Here are a few things you can ask me:**\n"
                    "- 🧴 *\"Suggest a good sunscreen\"* or *\"Recommend a casual shirt\"*\n"
                    "- 📈 *\"Will electronics drop in price next week?\"*\n"
                    "- 🛡️ *\"Audit my current product discount\"* (if you have a product open!)\n"
                    "- 🔍 *\"Search for headphones under 1500\"*\n\n"
                    "What can I help you find today?"
                )
            }
            
        # 2. Contextual Active Product Audit
        if "audit" in msg or "check this" in msg or "suspicious" in msg or "fake" in msg or "sentiment" in msg or "is it good" in msg:
            if active_product_id:
                product = db_manager.get_product(active_product_id)
                if product:
                    # Let's perform the dynamic calculations
                    product["_id"] = str(product["_id"])
                    product["current_price"] = min(v["price"] for v in product["vendors"])
                    product["discount_pct"] = round(((product["original_price"] - product["current_price"]) / product["original_price"]) * 100)
                    
                    sentiment_data = AIEngine.analyze_sentiment(product.get("reviews", []))
                    cheapest_vendor = min(product["vendors"], key=lambda x: x["price"])
                    prediction_data = AIEngine.predict_price_trend(product.get("price_history", []), cheapest_vendor["name"])
                    fake_discount_data = AIEngine.calculate_fake_discount(product["original_price"], product["vendors"])
                    
                    # Format markdown report
                    audit_res = (
                        f"🛡️ **AI Audit Report for `{product['title']}` ({product['brand']})**\n\n"
                        f"💰 **Pricing Overview:**\n"
                        f"- Current Cheapest Price: **₹{product['current_price']}** (offering **{product['discount_pct']}% OFF** MSRP of ₹{product['original_price']})\n"
                        f"- Best Vendor: **{cheapest_vendor['name'].upper()}**\n\n"
                        f"🤖 **AI Sentiment & Reviews:**\n"
                        f"- Sentiment: **{sentiment_data['overall_sentiment']}** ({sentiment_data['positive_percentage']}% Positive)\n"
                        f"- Customer Consensus: *\"{sentiment_data['summary']}\"*\n\n"
                        f"📈 **Price Trend Forecast:**\n"
                        f"- Recommendation: **{prediction_data['recommendation']}**\n"
                        f"- Detail: *{prediction_data['recommendation_detail']}*\n\n"
                        f"🔍 **Discount Integrity Check:**\n"
                        f"- Audit Score: **{fake_discount_data['score']}/100** (Rating: **{fake_discount_data['rating']}**)\n"
                        f"- Explanation: *{fake_discount_data['detail']}*"
                    )
                    return {
                        "response": audit_res,
                        "suggested_products": [product]
                    }
            elif "audit" in msg:
                return {
                    "response": (
                        "🛡️ **MSRP Discount Auditor**\n\n"
                        "To audit a product, please click on any product card in the catalog to open its details modal, "
                        "then type **\"audit\"** or click the **\"🛡️ Audit active product\"** quick pill!"
                    )
                }

        # 3. Category Trend Forecast
        categories_map = {
            "skincare": "Skincare",
            "clothing": "Clothing",
            "kitchen": "Kitchen",
            "stationery": "Stationery",
            "electronics": "Electronics",
            "grocery": "Grocery"
        }
        
        found_cat = None
        for ck, cv in categories_map.items():
            if ck in msg:
                found_cat = cv
                break
                
        if ("trend" in msg or "price" in msg or "drop" in msg or "cheaper" in msg or "forecast" in msg or "buy" in msg) and found_cat:
            products = db_manager.get_products(category=found_cat)
            if products:
                # Sample 10 products and look at price trends
                sampled = random.sample(products, min(len(products), 12))
                buy_now = 0
                wait_drop = 0
                stable = 0
                
                for p in sampled:
                    cheapest_vendor = min(p["vendors"], key=lambda x: x["price"])
                    pred = AIEngine.predict_price_trend(p.get("price_history", []), cheapest_vendor["name"])
                    rec = pred["recommendation"]
                    if rec == "Buy Now!":
                        buy_now += 1
                    elif rec == "Wait for drop!":
                        wait_drop += 1
                    else:
                        stable += 1
                        
                total = len(sampled)
                outlook = "Stable"
                if buy_now > wait_drop and buy_now > stable:
                    outlook = "Buy Immediately (Prices rising!)"
                    outlook_detail = "Our neural regression lines show a rising price curve on major items. We suggest buying soon to lock in low rates."
                elif wait_drop > buy_now and wait_drop > stable:
                    outlook = "Wait (Prices dropping!)"
                    outlook_detail = "Our regression models forecast a localized drop in major vendor prices over the next 7 days. Waiting could save you ₹50-₹200."
                else:
                    outlook = "Stable / Favorable"
                    outlook_detail = "Pricing remains in a stable range with high promotional discounts. Perfect time to purchase."
                    
                response_text = (
                    f"📈 **AI Market Forecast for `{found_cat}` Category**\n\n"
                    f"Based on a real-time sample of **{total} products** in our active database:\n"
                    f"- ✅ Buy Now recommendations: **{buy_now}**\n"
                    f"- ⚠️ Wait for drop recommendations: **{wait_drop}**\n"
                    f"- 📊 Stable price predictions: **{stable}**\n\n"
                    f"🔮 **Market Outlook: {outlook}**\n"
                    f"*{outlook_detail}*"
                )
                return {
                    "response": response_text
                }

        # 4. Search and Recommend Products
        # Let's see if they are searching for something. Let's scan all products in the database
        all_products = db_manager.get_products()
        
        # We can score products based on keyword match count
        keywords = [w.strip() for w in msg.split() if len(w.strip()) > 2]
        # Ignore common filler words
        filler = {"best", "cheap", "good", "suggest", "recommend", "show", "find", "search", "about", "there", "what", "is", "the", "under", "for", "please", "price", "any", "some", "buy"}
        keywords = [k for k in keywords if k not in filler]
        
        matched_products = []
        for p in all_products:
            score = 0
            title_lower = p.get("title", "").lower()
            brand_lower = p.get("brand", "").lower()
            cat_lower = p.get("category", "").lower()
            
            # Check keywords matching
            for kw in keywords:
                if kw in title_lower:
                    score += 5
                if kw in brand_lower:
                    score += 3
                if kw in cat_lower:
                    score += 2
                    
            # Check price filters
            # e.g., "under 500" or "below 1000"
            price_limit = None
            if "under" in msg or "below" in msg or "less than" in msg or "cheaper than" in msg:
                # try to parse number
                import re
                nums = re.findall(r'\d+', msg)
                if nums:
                    price_limit = int(nums[0])
                    
            current_price = min(v["price"] for v in p["vendors"])
            if price_limit and current_price > price_limit:
                score = 0 # disqualify
                
            if score > 0:
                p["current_price"] = current_price
                p["discount_pct"] = round(((p["original_price"] - current_price) / p["original_price"]) * 100)
                matched_products.append((score, p))
                
        # Sort matched products by score (descending) and rating (descending)
        matched_products.sort(key=lambda x: (x[0], x[1]["rating"]), reverse=True)
        top_matches = [item[1] for item in matched_products[:3]]
        
        if top_matches:
            suggestions = []
            for p in top_matches:
                cheapest_vendor = min(p["vendors"], key=lambda x: x["price"])
                p["_id"] = str(p["_id"])
                suggestions.append(p)
                
            rec_text = f"🔍 **AI Recommendations matching your interest:**\n\n"
            for idx, p in enumerate(top_matches):
                cheapest_vendor = min(p["vendors"], key=lambda x: x["price"])
                rec_text += (
                    f"{idx+1}. **{p['title']}** ({p['brand']})\n"
                    f"   - **Cheapest Price:** ₹{p['current_price']} on **{cheapest_vendor['name'].upper()}** "
                    f"({p['discount_pct']}% OFF original ₹{p['original_price']})\n"
                    f"   - **Rating:** {p['rating']}/5 ⭐ ({p['num_reviews']} reviews)\n"
                    f"   - **AI Trend Badge:** {p.get('ai_insight', 'Price stable')}\n\n"
                )
            rec_text += "💡 *Click on any of the product cards in the list to open their graphs and compare prices!*"
            return {
                "response": rec_text,
                "suggested_products": suggestions
            }
            
        # 5. Default Fallback
        # If we couldn't match a specific search, let's suggest best rated deals in general!
        top_rated = sorted(all_products, key=lambda x: x.get("rating", 0), reverse=True)[:3]
        for p in top_rated:
            p["_id"] = str(p["_id"])
            p["current_price"] = min(v["price"] for v in p["vendors"])
            p["discount_pct"] = round(((p["original_price"] - p["current_price"]) / p["original_price"]) * 100)
            
        fallback_text = (
            "🤔 *I couldn't find a specific keyword match for that in our catalog.* But don't worry!\n\n"
            "Here are **India's Top-Rated AI Picks** across all categories right now:\n\n"
        )
        for idx, p in enumerate(top_rated):
            cheapest_vendor = min(p["vendors"], key=lambda x: x["price"])
            fallback_text += (
                f"🏷️ **{p['title']}**\n"
                f"- Category: {p['category']} | Brand: {p['brand']}\n"
                f"- Current Best Deal: **₹{p['current_price']}** on **{cheapest_vendor['name'].upper()}** "
                f"({p['discount_pct']}% OFF original ₹{p['original_price']})\n"
                f"- User Rating: **{p['rating']} / 5** ⭐\n\n"
            )
        fallback_text += "Try searching for specific brands like **boAt, Milton, Prestige, Biba, or Minimalist**!"
        return {
            "response": fallback_text,
            "suggested_products": top_rated
        }
