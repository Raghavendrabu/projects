import pytest
import bcrypt
from datetime import datetime
from database import db

def register_user_direct(usn, username, password):
    """Helper to insert a user directly into MongoDB for testing"""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = {
        'fullname': 'Login Tester',
        'username': username,
        'usn': usn,
        'password': hashed,
        'profilePhoto': None,
        'bio': 'I am a tester',
        'followers': [],
        'following': [],
        'isPrivate': False,
        'created_at': datetime.utcnow()
    }
    db.db.users.insert_one(user)

def test_login_success(ui):
    """TC_LOG_001: Log in with valid credentials, verify redirect to home page and feed load"""
    # Programmatically register the test user
    register_user_direct("SELLOG001", "logintester", "password123")
    
    # Go to login page
    ui.navigate_to("login.html")
    
    # Enter credentials
    ui.write("#usn", "SELLOG001")
    ui.write("#password", "password123")
    
    # Submit
    ui.click("button[type='submit']")
    
    # Verify we redirect to homepage
    assert ui.wait_for_url_to_contain("/")
    
    # Verify feed page elements
    logo = ui.find_visible(".logo")
    assert "GMInsta" in logo.text


def test_login_invalid_password(ui):
    """TC_LOG_002: Attempt login with incorrect password and verify alert message"""
    register_user_direct("SELLOG002", "logintester2", "password123")
    
    ui.navigate_to("login.html")
    ui.write("#usn", "SELLOG002")
    ui.write("#password", "wrongpassword")
    ui.click("button[type='submit']")
    
    # Verify alert text
    alert_text = ui.get_alert_text()
    assert alert_text is not None
    assert "invalid" in alert_text.lower() or "wrong" in alert_text.lower()
    
    # Verify we stay on login page
    assert "login.html" in ui.driver.current_url


def test_login_nonexistent_user(ui):
    """TC_LOG_003: Attempt login with a non-existent user and verify alert message"""
    ui.navigate_to("login.html")
    ui.write("#usn", "NOT_EXIST_USN")
    ui.write("#password", "somepassword")
    ui.click("button[type='submit']")
    
    # Verify alert text
    alert_text = ui.get_alert_text()
    assert alert_text is not None
    assert "invalid" in alert_text.lower() or "wrong" in alert_text.lower()
    
    # Verify we stay on login page
    assert "login.html" in ui.driver.current_url
