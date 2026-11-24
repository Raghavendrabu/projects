from pymongo import MongoClient, ASCENDING, DESCENDING
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
    
    def connect(self, config=None):
        try:
            # Get MongoDB URI from config or environment
            mongo_uri = 'mongodb://localhost:27017/'
            db_name = 'gminsta'
            
            if config:
                if hasattr(config, 'MONGO_URI'):
                    mongo_uri = config.MONGO_URI
                    db_name = config.DB_NAME
                elif isinstance(config, dict):
                    mongo_uri = config.get('MONGO_URI', mongo_uri)
                    db_name = config.get('DB_NAME', db_name)
            
            # Override with environment variables if they exist
            if os.getenv('MONGO_URI'):
                mongo_uri = os.getenv('MONGO_URI')
            if os.getenv('DB_NAME'):
                db_name = os.getenv('DB_NAME')
            
            logger.info(f"Connecting to MongoDB at: {mongo_uri}")
            
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            
            # Test connection
            self.client.admin.command('ping')
            
            # Create indexes for performance
            self.db.users.create_index([('usn', ASCENDING)], unique=True)
            self.db.users.create_index([('username', ASCENDING)], unique=True)
            self.db.posts.create_index([('created_at', DESCENDING)])
            self.db.posts.create_index([('authorUsn', ASCENDING), ('created_at', DESCENDING)])
            self.db.messages.create_index([('timestamp', ASCENDING)])
            self.db.stories.create_index([('expires_at', ASCENDING)], expireAfterSeconds=0)
            
            logger.info(f"✓ Connected to MongoDB: {db_name}")
            return self.db
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    
    def close(self):
        if self.client:
            self.client.close()

db = Database()