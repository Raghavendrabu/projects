"""
Test Suite - Authentication Tests
Valid and Invalid test cases for User Registration and Login
"""
import pytest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app
from database import db

@pytest.fixture
def app():
    """Create app for testing"""
    flask_app.config['TESTING'] = True
    flask_app.config['MONGO_URI'] = 'mongodb://localhost:27017/'
    flask_app.config['DB_NAME'] = 'gminsta_test'
    return flask_app

@pytest.fixture
def client(app):
    """Create test client for API testing"""
    with app.test_client() as client:
        with app.app_context():
            # Clear test database before each test
            db.db.users.delete_many({})
            db.db.posts.delete_many({})
            db.db.stories.delete_many({})
            db.db.messages.delete_many({})
        yield client


class TestAuthentication:
    """Test authentication endpoints with valid and invalid cases"""
    
    # ============ VALID TEST CASES ============
    
    def test_valid_registration(self, client):
        """TC-001: Valid User Registration"""
        response = client.post('/api/register', json={
            'fullname': 'Test User',
            'username': 'testuser',
            'usn': 'TEST001',
            'password': 'password123'
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'token' in data
        print("✅ TC-001 PASSED: Valid Registration")
    
    def test_valid_login_with_usn(self, client):
        """TC-002: Valid Login with USN"""
        # First register
        client.post('/api/register', json={
            'fullname': 'Login User',
            'username': 'loginuser',
            'usn': 'TEST002',
            'password': 'pass123'
        })
        
        # Then login
        response = client.post('/api/login', json={
            'usn': 'TEST002',
            'password': 'pass123'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'token' in data
        print("✅ TC-002 PASSED: Valid Login with USN")
    
    def test_valid_login_with_username_field(self, client):
        """TC-003: Valid Login - Note: API uses USN field"""
        # First register
        client.post('/api/register', json={
            'fullname': 'Username User',
            'username': 'usernameuser',
            'usn': 'TEST003',
            'password': 'pass123'
        })
        
        # Login with USN (your API expects 'usn' field)
        response = client.post('/api/login', json={
            'usn': 'TEST003',
            'password': 'pass123'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        print("✅ TC-003 PASSED: Valid Login")
    
    # ============ INVALID TEST CASES ============
    
    def test_invalid_registration_duplicate_usn(self, client):
        """TC-004: Invalid - Duplicate USN"""
        # Register first user
        client.post('/api/register', json={
            'fullname': 'First User',
            'username': 'firstuser',
            'usn': 'DUPLICATE001',
            'password': 'pass123'
        })
        
        # Try to register with same USN
        response = client.post('/api/register', json={
            'fullname': 'Second User',
            'username': 'seconduser',
            'usn': 'DUPLICATE001',
            'password': 'pass123'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'already exists' in data['error'].lower()
        print("✅ TC-004 PASSED: Invalid - Duplicate USN")
    
    def test_invalid_registration_duplicate_username(self, client):
        """TC-005: Invalid - Duplicate Username"""
        # Register first user
        client.post('/api/register', json={
            'fullname': 'First User',
            'username': 'duplicateuser',
            'usn': 'UNIQUE001',
            'password': 'pass123'
        })
        
        # Try to register with same username
        response = client.post('/api/register', json={
            'fullname': 'Second User',
            'username': 'duplicateuser',
            'usn': 'UNIQUE002',
            'password': 'pass123'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        print("✅ TC-005 PASSED: Invalid - Duplicate Username")
    
    def test_invalid_registration_missing_fields(self, client):
        """TC-006: Invalid - Missing required fields"""
        response = client.post('/api/register', json={
            'fullname': 'Incomplete User',
            'username': 'incomplete'
            # Missing usn and password
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        print("✅ TC-006 PASSED: Invalid - Missing Fields")
    
    def test_invalid_login_wrong_password(self, client):
        """TC-007: Invalid - Wrong password"""
        # Register user
        client.post('/api/register', json={
            'fullname': 'Password User',
            'username': 'passuser',
            'usn': 'PASS001',
            'password': 'correctpassword'
        })
        
        # Try login with wrong password
        response = client.post('/api/login', json={
            'usn': 'PASS001',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] == False
        print("✅ TC-007 PASSED: Invalid - Wrong Password")
    
    def test_invalid_login_nonexistent_user(self, client):
        """TC-008: Invalid - Nonexistent user"""
        response = client.post('/api/login', json={
            'usn': 'NONEXISTENT',
            'password': 'password'
        })
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] == False
        print("✅ TC-008 PASSED: Invalid - Nonexistent User")


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])