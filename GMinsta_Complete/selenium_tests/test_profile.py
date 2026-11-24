import pytest
import bcrypt
from datetime import datetime
from database import db
from selenium.webdriver.common.by import By

def register_and_login(ui, usn, username, password):
    """Helper to register user directly and log them in via the UI"""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = {
        'fullname': 'Profile Tester',
        'username': username,
        'usn': usn,
        'password': hashed,
        'profilePhoto': None,
        'bio': 'Initial Bio',
        'followers': [],
        'following': [],
        'isPrivate': False,
        'created_at': datetime.utcnow()
    }
    db.db.users.insert_one(user)
    
    ui.navigate_to("login.html")
    ui.write("#usn", usn)
    ui.write("#password", password)
    ui.click("button[type='submit']")
    ui.find_visible("#storiesContainer")


def test_edit_bio(ui):
    """TC_PRF_001: Go to profile page, open edit bio modal, update bio, and verify it updates in the UI"""
    register_and_login(ui, "SELPRF001", "profiletester", "password123")
    
    # Navigate to profile page
    ui.navigate_to("profile.html")
    assert ui.wait_for_url_to_contain("profile.html")
    
    # Assert initial bio
    bio_element = ui.find_visible("#profileBio")
    assert "Initial Bio" in bio_element.text
    
    # Click Edit Profile button
    ui.click(".edit-profile-btn")
    
    # Wait for modal to be visible
    bio_modal = ui.find_visible("#bioModal")
    assert bio_modal.is_displayed()
    
    # Change the bio text
    new_bio = "Hello! This is my brand new Selenium automated bio."
    ui.write("#bioInput", new_bio)
    
    # Save the bio
    ui.click("#bioModal button[onclick='saveBio()']")
    
    # Handle the success alert dialog
    alert_text = ui.get_alert_text()
    assert alert_text is not None
    assert "success" in alert_text.lower()
    
    # Check that modal is hidden
    ui.wait.until(lambda d: not d.find_element(By.ID, "bioModal").is_displayed())
    
    # Check that UI updated with the new bio
    assert new_bio in ui.find_visible("#profileBio").text


def test_toggle_privacy(ui):
    """TC_PRF_002: Click settings menu, toggle account privacy, handle alert, and check toggle status text"""
    register_and_login(ui, "SELPRF002", "profiletester2", "password123")
    
    # Navigate to profile
    ui.navigate_to("profile.html")
    assert ui.wait_for_url_to_contain("profile.html")
    
    # Verify initial privacy text is OFF
    privacy_status = ui.find("#privacyStatus")
    assert "OFF" in privacy_status.get_attribute("textContent")
    
    # Click hamburger menu (fa-bars icon)
    ui.click(".header .fa-bars")
    
    # Verify dropdown menu is visible
    dropdown = ui.find_visible("#dropdownMenu")
    assert dropdown.is_displayed()
    
    # Click Private Account option
    ui.click("#dropdownMenu div[onclick='togglePrivacy()']")
    
    # Handle privacy change alert
    alert_text = ui.get_alert_text()
    assert alert_text is not None
    assert "private" in alert_text.lower()
    
    # Check that privacy text is now ON
    privacy_status = ui.find("#privacyStatus")
    assert "ON" in privacy_status.get_attribute("textContent")


def test_logout(ui):
    """TC_PRF_003: Click settings menu, click logout, and verify redirect to login page"""
    register_and_login(ui, "SELPRF003", "profiletester3", "password123")
    
    ui.navigate_to("profile.html")
    assert ui.wait_for_url_to_contain("profile.html")
    
    # Open settings menu
    ui.click(".header .fa-bars")
    ui.find_visible("#dropdownMenu")
    
    # Click Logout
    ui.click("#dropdownMenu div[onclick='logout()']")
    
    # Verify redirected to login.html
    assert ui.wait_for_url_to_contain("login.html")
    
    # Verify localStorage is cleared
    token = ui.driver.execute_script("return localStorage.getItem('gminsta_token');")
    assert token is None
