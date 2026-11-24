"""
Test Suite - Posts CRUD Operations
Tests MongoDB $push and $pull operators for likes/comments
"""
import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import db
from bson import ObjectId

@pytest.fixture
def auth_client():
    """Create authenticated test client"""
    app.config['TESTING'] = True
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/'
    app.config['DB_NAME'] = 'gminsta_test'
    
    with app.test_client() as client:
        with app.app_context():
            # Clear database
            db.db.users.delete_many({})
            db.db.posts.delete_many({})
            
            # Create test user and get token
            client.post('/api/register', json={
                'fullname': 'Post Tester',
                'username': 'posttester',
                'usn': 'POST001',
                'password': 'testpass'
            })
            
            login_resp = client.post('/api/login', json={
                'usn': 'POST001',
                'password': 'testpass'
            })
            token = json.loads(login_resp.data)['token']
            
            # Set auth header
            client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
            
        yield client


class TestPosts:
    """Test post CRUD operations with MongoDB operators"""
    
    def test_create_post(self, auth_client):
        """TC-009: Valid - Create a new post"""
        response = auth_client.post('/api/posts', json={
            'image': 'https://example.com/test.jpg',
            'caption': 'Test post caption',
            'type': 'post'
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'post_id' in data
        print("✅ TC-009 PASSED: Create Post")
    
    def test_get_posts_feed(self, auth_client):
        """TC-010: Valid - Get posts feed"""
        # Create a post first
        auth_client.post('/api/posts', json={
            'image': 'https://example.com/feed.jpg',
            'caption': 'Feed post'
        })
        
        response = auth_client.get('/api/posts')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'posts' in data
        print("✅ TC-010 PASSED: Get Posts Feed")
    
    def test_like_post_with_push(self, auth_client):
        """TC-011: Valid - Like a post using $push operator"""
        # Create post
        create_resp = auth_client.post('/api/posts', json={
            'image': 'https://example.com/like-test.jpg',
            'caption': 'Test like'
        })
        post_id = json.loads(create_resp.data)['post_id']
        
        # Like the post
        response = auth_client.post(f'/api/posts/{post_id}/like')
        assert response.status_code == 200
        
        # Verify like was added
        from database import db
        post = db.db.posts.find_one({'id': post_id})
        assert len(post['likes']) == 1
        print("✅ TC-011 PASSED: Like Post with $push")
    
    def test_unlike_post_with_pull(self, auth_client):
        """TC-012: Valid - Unlike a post using $pull operator"""
        # Create post
        create_resp = auth_client.post('/api/posts', json={
            'image': 'https://example.com/unlike-test.jpg',
            'caption': 'Test unlike'
        })
        post_id = json.loads(create_resp.data)['post_id']
        
        # Like then unlike
        auth_client.post(f'/api/posts/{post_id}/like')
        response = auth_client.post(f'/api/posts/{post_id}/like')  # Toggle to unlike
        
        assert response.status_code == 200
        
        # Verify like was removed
        from database import db
        post = db.db.posts.find_one({'id': post_id})
        assert len(post['likes']) == 0
        print("✅ TC-012 PASSED: Unlike Post with $pull")
    
    def test_add_comment_with_push(self, auth_client):
        """TC-013: Valid - Add comment using $push operator"""
        # Create post
        create_resp = auth_client.post('/api/posts', json={
            'image': 'https://example.com/comment-test.jpg',
            'caption': 'Test comment'
        })
        post_id = json.loads(create_resp.data)['post_id']
        
        # Add comment
        response = auth_client.post(f'/api/posts/{post_id}/comment', json={
            'text': 'This is a great post!'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        # Verify comment was added
        from database import db
        post = db.db.posts.find_one({'id': post_id})
        assert len(post['comments']) == 1
        assert post['comments'][0]['text'] == 'This is a great post!'
        print("✅ TC-013 PASSED: Add Comment with $push")
    
    def test_get_user_posts(self, auth_client):
        """TC-014: Valid - Get posts by specific user"""
        # Create a post
        auth_client.post('/api/posts', json={
            'image': 'https://example.com/userpost.jpg',
            'caption': 'User post'
        })
        
        response = auth_client.get('/api/posts/user/POST001')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'posts' in data
        print("✅ TC-014 PASSED: Get User Posts")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])