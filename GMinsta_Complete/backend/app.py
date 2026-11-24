from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from database import db
from bson import ObjectId
from datetime import datetime, timedelta
from functools import wraps
import bcrypt
import jwt
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config.from_object(Config)
CORS(app)

# Connect to database
mongodb = db.connect(app.config)

# ============ HELPER FUNCTIONS ============

def generate_token(usn, username):
    payload = {
        'usn': usn,
        'username': username,
        'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA'],
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authentication token missing'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.usn = payload['usn']
        request.username = payload['username']
        return f(*args, **kwargs)
    return decorated

def time_ago(dt):
    """Convert datetime to 'X ago' format"""
    if not dt:
        return "Just now"
    diff = datetime.utcnow() - dt
    if diff.days > 7:
        return dt.strftime('%b %d')
    elif diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600}h ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60}m ago"
    else:
        return "Just now"

def create_notification(user_usn, from_usn, from_name, type, post_id=None):
    """Create a notification for a user"""
    notification = {
        'user_id': user_usn,
        'from_usn': from_usn,
        'from_name': from_name,
        'type': type,
        'post_id': post_id,
        'is_read': False,
        'created_at': datetime.utcnow()
    }
    if 'notifications' not in mongodb.list_collection_names():
        mongodb.create_collection('notifications')
    mongodb.notifications.insert_one(notification)

# ============ FRONTEND ROUTES ============

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    return send_from_directory('../frontend', path)

# ============ AUTH API ============

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    fullname = data.get('fullname', '').strip()
    username = data.get('username', '').strip()
    usn = data.get('usn', '').strip()
    password = data.get('password', '')
    
    if not usn or not password or not username:
        return jsonify({'success': False, 'error': 'All fields required'}), 400
    
    existing = mongodb.users.find_one({'$or': [{'usn': usn}, {'username': username}]})
    if existing:
        return jsonify({'success': False, 'error': 'USN or Username already exists'}), 400
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    user = {
        'fullname': fullname,
        'username': username,
        'usn': usn,
        'password': hashed.decode('utf-8'),
        'profilePhoto': None,
        'bio': '',
        'followers': [],
        'following': [],
        'isPrivate': False,
        'created_at': datetime.utcnow()
    }
    
    result = mongodb.users.insert_one(user)
    token = generate_token(usn, username)
    
    user['_id'] = str(result.inserted_id)
    user.pop('password', None)
    
    return jsonify({
        'success': True,
        'token': token,
        'user': user
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    usn = data.get('usn', '').strip()
    password = data.get('password', '')
    
    user = mongodb.users.find_one({'usn': usn})
    if not user:
        return jsonify({'success': False, 'error': 'Invalid USN or password'}), 401
    
    if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'success': False, 'error': 'Invalid USN or password'}), 401
    
    token = generate_token(user['usn'], user['username'])
    user['_id'] = str(user['_id'])
    user.pop('password', None)
    
    return jsonify({
        'success': True,
        'token': token,
        'user': user
    }), 200

@app.route('/api/verify', methods=['GET'])
@token_required
def verify():
    user = mongodb.users.find_one({'usn': request.usn})
    if not user:
        return jsonify({'success': False}), 401
    user['_id'] = str(user['_id'])
    user.pop('password', None)
    return jsonify({'success': True, 'user': user}), 200

# ============ USER API ============

@app.route('/api/users/me', methods=['GET'])
@token_required
def get_current_user():
    user = mongodb.users.find_one({'usn': request.usn})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user['_id'] = str(user['_id'])
    user.pop('password', None)
    # Make sure all fields are included
    return jsonify({
        'usn': user['usn'],
        'username': user['username'],
        'fullname': user.get('fullname', ''),
        'bio': user.get('bio', ''),
        'profilePhoto': user.get('profilePhoto'),
        'followers': user.get('followers', []),
        'following': user.get('following', []),
        'isPrivate': user.get('isPrivate', False),
        'posts_count': user.get('posts_count', 0),
        'created_at': user.get('created_at')
    }), 200

@app.route('/api/users/<usn>', methods=['GET'])
@token_required
def get_user(usn):
    user = mongodb.users.find_one({'usn': usn})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    current_user = mongodb.users.find_one({'usn': request.usn})
    is_following = request.usn in user.get('followers', [])
    
    user['_id'] = str(user['_id'])
    user.pop('password', None)
    
    return jsonify({
        'user': user,
        'is_following': is_following,
        'is_own_profile': request.usn == usn
    }), 200

@app.route('/api/users/<usn>/follow', methods=['POST'])
@token_required
def follow_user(usn):
    if usn == request.usn:
        return jsonify({'success': False, 'error': 'Cannot follow yourself'}), 400
    
    # Check if already following
    current_user = mongodb.users.find_one({'usn': request.usn})
    if usn in current_user.get('following', []):
        return jsonify({'success': False, 'error': 'Already following'}), 400
    
    mongodb.users.update_one({'usn': request.usn}, {'$push': {'following': usn}})
    mongodb.users.update_one({'usn': usn}, {'$push': {'followers': request.usn}})
    
    # Create notification
    create_notification(usn, request.usn, request.username, 'follow')
    
    return jsonify({'success': True}), 200

@app.route('/api/users/<usn>/unfollow', methods=['DELETE'])
@token_required
def unfollow_user(usn):
    mongodb.users.update_one({'usn': request.usn}, {'$pull': {'following': usn}})
    mongodb.users.update_one({'usn': usn}, {'$pull': {'followers': request.usn}})
    
    return jsonify({'success': True}), 200

@app.route('/api/users/profile', methods=['PUT'])
@token_required
def update_profile():
    data = request.get_json()
    update_data = {}
    
    if 'profilePhoto' in data:
        update_data['profilePhoto'] = data['profilePhoto']
    if 'bio' in data:
        update_data['bio'] = data['bio']
    if 'isPrivate' in data:
        update_data['isPrivate'] = data['isPrivate']
    
    if update_data:
        mongodb.users.update_one({'usn': request.usn}, {'$set': update_data})
    
    return jsonify({'success': True}), 200

# ============ POSTS API ============

@app.route('/api/posts', methods=['POST'])
@token_required
def create_post():
    data = request.get_json()
    
    post = {
        'id': str(ObjectId()),
        'authorUsn': request.usn,
        'authorName': request.username,
        'authorPhoto': data.get('authorPhoto', ''),
        'image': data.get('image'),
        'caption': data.get('caption', ''),
        'type': data.get('type', 'post'),
        'likes': [],
        'comments': [],
        'shares': 0,
        'timestamp': datetime.utcnow(),
        'created_at': datetime.utcnow()
    }
    
    mongodb.posts.insert_one(post)
    return jsonify({'success': True, 'post_id': post['id']}), 201

@app.route('/api/posts', methods=['GET'])
@token_required
def get_posts():
    user = mongodb.users.find_one({'usn': request.usn})
    following = user.get('following', [])
    following.append(request.usn)
    
    posts = list(mongodb.posts.find({
        'authorUsn': {'$in': following}
    }).sort('created_at', -1))
    
    for post in posts:
        post['_id'] = str(post['_id'])
        post['liked_by_user'] = request.usn in post.get('likes', [])
    
    return jsonify({'posts': posts}), 200

@app.route('/api/posts/user/<usn>', methods=['GET'])
@token_required
def get_user_posts(usn):
    posts = list(mongodb.posts.find({'authorUsn': usn}).sort('created_at', -1))
    for post in posts:
        post['_id'] = str(post['_id'])
    return jsonify({'posts': posts}), 200

@app.route('/api/posts/<post_id>/like', methods=['POST'])
@token_required
def like_post(post_id):
    post = mongodb.posts.find_one({'id': post_id})
    if not post:
        return jsonify({'success': False, 'error': 'Post not found'}), 404
    
    if request.usn in post.get('likes', []):
        mongodb.posts.update_one({'id': post_id}, {'$pull': {'likes': request.usn}})
    else:
        mongodb.posts.update_one({'id': post_id}, {'$push': {'likes': request.usn}})
        # Create notification for post owner
        if post['authorUsn'] != request.usn:
            create_notification(post['authorUsn'], request.usn, request.username, 'like', post_id)
    
    return jsonify({'success': True}), 200

@app.route('/api/posts/<post_id>/comment', methods=['POST'])
@token_required
def add_comment(post_id):
    data = request.get_json()
    comment = {
        'usn': request.usn,
        'username': request.username,
        'text': data.get('text'),
        'timestamp': datetime.utcnow()
    }
    
    mongodb.posts.update_one({'id': post_id}, {'$push': {'comments': comment}})
    
    # Create notification for post owner
    post = mongodb.posts.find_one({'id': post_id})
    if post and post['authorUsn'] != request.usn:
        create_notification(post['authorUsn'], request.usn, request.username, 'comment', post_id)
    
    return jsonify({'success': True, 'comment': comment}), 200

@app.route('/api/posts/<post_id>', methods=['DELETE'])
@token_required
def delete_post(post_id):
    post = mongodb.posts.find_one({'id': post_id})
    if not post or post['authorUsn'] != request.usn:
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
    
    mongodb.posts.delete_one({'id': post_id})
    return jsonify({'success': True}), 200

# ============ STORIES API ============

@app.route('/api/stories', methods=['POST'])
@token_required
def create_story():
    data = request.get_json()
    
    story = {
        'id': str(ObjectId()),
        'authorUsn': request.usn,
        'authorName': request.username,
        'authorPhoto': data.get('authorPhoto', ''),
        'image': data.get('image'),
        'caption': data.get('caption', ''),
        'timestamp': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(hours=24)
    }
    
    mongodb.stories.insert_one(story)
    return jsonify({'success': True, 'story_id': story['id']}), 201

@app.route('/api/stories', methods=['GET'])
@token_required
def get_stories():
    user = mongodb.users.find_one({'usn': request.usn})
    following = user.get('following', [])
    following.append(request.usn)
    
    stories = list(mongodb.stories.find({
        'authorUsn': {'$in': following},
        'expires_at': {'$gt': datetime.utcnow()}
    }).sort('timestamp', -1))
    
    for story in stories:
        story['_id'] = str(story['_id'])
    
    return jsonify({'stories': stories}), 200

# ============ MESSAGES API ============

@app.route('/api/messages', methods=['GET'])
@token_required
def get_messages():
    messages = list(mongodb.messages.find({
        '$or': [
            {'fromUsn': request.usn},
            {'toUsn': request.usn}
        ]
    }).sort('timestamp', 1))
    
    for msg in messages:
        msg['_id'] = str(msg['_id'])
    
    return jsonify({'messages': messages}), 200

@app.route('/api/messages', methods=['POST'])
@token_required
def send_message():
    data = request.get_json()
    
    message = {
        'id': str(ObjectId()),
        'fromUsn': request.usn,
        'fromName': request.username,
        'toUsn': data.get('toUsn'),
        'text': data.get('text'),
        'timestamp': datetime.utcnow()
    }
    
    mongodb.messages.insert_one(message)
    return jsonify({'success': True, 'message': message}), 201

# ============ SEARCH API ============

@app.route('/api/search', methods=['GET'])
@token_required
def search():
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify({'users': []}), 200
    
    users = list(mongodb.users.find({
        '$or': [
            {'username': {'$regex': query, '$options': 'i'}},
            {'fullname': {'$regex': query, '$options': 'i'}}
        ],
        'usn': {'$ne': request.usn}
    }).limit(20))
    
    for user in users:
        user['_id'] = str(user['_id'])
        user.pop('password', None)
    
    return jsonify({'users': users}), 200

# ============ NOTIFICATIONS API ============

@app.route('/api/notifications', methods=['GET'])
@token_required
def get_notifications():
    notifications = list(mongodb.notifications.find({
        'user_id': request.usn
    }).sort('created_at', -1).limit(50))
    
    result = []
    for n in notifications:
        from_user = mongodb.users.find_one({'usn': n['from_usn']})
        result.append({
            'id': str(n['_id']),
            'type': n['type'],
            'from_username': from_user['username'] if from_user else 'unknown',
            'from_avatar': from_user.get('profilePhoto') if from_user else None,
            'is_read': n.get('is_read', False),
            'created_ago': time_ago(n['created_at'])
        })
    
    return jsonify({'notifications': result}), 200

@app.route('/api/notifications/unread/count', methods=['GET'])
@token_required
def get_unread_count():
    count = mongodb.notifications.count_documents({
        'user_id': request.usn,
        'is_read': False
    })
    return jsonify({'count': count}), 200

@app.route('/api/notifications/mark-all-read', methods=['POST'])
@token_required
def mark_all_read():
    mongodb.notifications.update_many(
        {'user_id': request.usn, 'is_read': False},
        {'$set': {'is_read': True}}
    )
    return jsonify({'success': True}), 200
# ============ ADD THESE MISSING ENDPOINTS ============

@app.route('/api/users/<usn>/posts', methods=['GET'])
@token_required
def get_user_posts_by_usn(usn):
    """Get posts by user USN - FIXED for profile page"""
    posts = list(mongodb.posts.find({'authorUsn': usn}).sort('created_at', -1))
    for post in posts:
        post['_id'] = str(post['_id'])
    return jsonify({'posts': posts}), 200

@app.route('/api/users/username/<username>', methods=['GET'])
@token_required
def get_user_by_username(username):
    """Get user by username - for profile viewing"""
    user = mongodb.users.find_one({'username': username})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    current_user = mongodb.users.find_one({'usn': request.usn})
    is_following = request.usn in user.get('followers', [])
    
    user['_id'] = str(user['_id'])
    user.pop('password', None)
    
    return jsonify({
        'user': user,
        'is_following': is_following,
        'is_own_profile': request.usn == user['usn']
    }), 200

@app.route('/api/users/update-profile', methods=['POST'])
@token_required
def update_profile_full():
    """Update profile including bio and profile picture - FIXED"""
    data = request.get_json()
    
    update_data = {}
    if 'bio' in data:
        update_data['bio'] = data['bio']
    if 'profilePhoto' in data:
        update_data['profilePhoto'] = data['profilePhoto']
    
    if update_data:
        mongodb.users.update_one({'usn': request.usn}, {'$set': update_data})
        
        # Return updated user
        updated_user = mongodb.users.find_one({'usn': request.usn})
        updated_user['_id'] = str(updated_user['_id'])
        updated_user.pop('password', None)
        return jsonify({'success': True, 'user': updated_user}), 200
    
    return jsonify({'success': False, 'error': 'No data to update'}), 400

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 GMinsta Backend is running!")
    print("📍 Backend API: http://localhost:5000")
    print("📍 Frontend: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)