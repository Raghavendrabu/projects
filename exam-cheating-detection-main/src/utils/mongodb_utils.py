import os
import gridfs
import mimetypes
from bson.objectid import ObjectId
from pymongo import MongoClient

class MongoDBManager:
    def __init__(self, config):
        mongo_config = config.get('mongodb', {})
        self.uri = mongo_config.get('uri', 'mongodb://localhost:27017/')
        self.db_name = mongo_config.get('database', 'exam_cheating_detection')
        
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            # Force a connection check
            self.client.server_info()
            self.db = self.client[self.db_name]
            self.fs = gridfs.GridFS(self.db)
            self.sessions_col = self.db['sessions']
            self.violations_col = self.db['violations']
            self.exams_col = self.db['exams']
            self.quizzes_col = self.db['quizzes']
            print("[MongoDBManager] Successfully connected to MongoDB")
        except Exception as e:
            print(f"[MongoDBManager] WARNING: Failed to connect to MongoDB: {e}")
            print("[MongoDBManager] WARNING: MongoDB features will be disabled. Local file storage will still be used.")
            self.client = None
            self.db = None
            self.fs = None
            self.sessions_col = None
            self.violations_col = None
            self.exams_col = None
            self.quizzes_col = None
            
    def is_connected(self):
        return self.client is not None

    def save_file_to_gridfs(self, file_path, filename, content_type=None):
        """Saves a file to MongoDB GridFS and returns its file_id string."""
        if not self.is_connected() or not os.path.exists(file_path):
            return None
        
        # Infer content type if not provided
        if not content_type:
            content_type, _ = mimetypes.guess_type(file_path)
            
        try:
            with open(file_path, 'rb') as f:
                file_id = self.fs.put(
                    f, 
                    filename=filename, 
                    contentType=content_type
                )
            print(f"[MongoDBManager] File {filename} successfully uploaded to MongoDB GridFS with ID: {file_id}")
            return str(file_id)
        except Exception as e:
            print(f"[MongoDBManager] ERROR: Error saving file {filename} to GridFS: {e}")
            return None

    def get_file_from_gridfs(self, file_id_str):
        """Retrieves a file from GridFS by its file ID string."""
        if not self.is_connected():
            return None
        try:
            return self.fs.get(ObjectId(file_id_str))
        except Exception as e:
            print(f"[MongoDBManager] ERROR: Error fetching file {file_id_str} from GridFS: {e}")
            return None

    def save_session(self, session_data):
        """Saves or updates an exam session in MongoDB."""
        if not self.is_connected():
            return False
        try:
            self.sessions_col.update_one(
                {'student_info.id': session_data['student_info']['id']},
                {'$set': session_data},
                upsert=True
            )
            print(f"[MongoDBManager] Saved exam session for student {session_data['student_info']['name']} to MongoDB")
            return True
        except Exception as e:
            print(f"[MongoDBManager] ERROR: Error saving session to MongoDB: {e}")
            return False

    def log_violation(self, violation_data):
        """Logs a single violation to MongoDB."""
        if not self.is_connected():
            return False
        try:
            self.violations_col.insert_one(violation_data)
            print(f"[MongoDBManager] Logged violation {violation_data['type']} to MongoDB")
            return True
        except Exception as e:
            print(f"[MongoDBManager] ERROR: Error logging violation to MongoDB: {e}")
            return False
