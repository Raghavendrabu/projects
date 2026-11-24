import pytest
from selenium.webdriver.common.by import By

def test_registration_success(ui):
    """TC_REG_001: Register a new user, skip photo upload, verify redirection to homepage"""
    ui.navigate_to("register.html")
    
    # Enter registration details
    ui.write("#fullname", "Selenium Test User")
    ui.write("#username", "selenium_test_user")
    ui.write("#usn", "SELREG001")
    ui.write("#password", "password123")
    
    # Submit the form
    ui.click("button[type='submit']")
    
    # Verify we are redirected to setup_photo.html
    assert ui.wait_for_url_to_contain("setup_photo.html")
    
    # Click Skip for now button
    ui.click(".btn-secondary")
    
    # Verify redirected to homepage (index page)
    # The URL can be just "/" or the base url without file path
    assert ui.wait_for_url_to_contain("/")
    
    # Verify profile photo placeholder is visible in story ring
    # and "Your story" text exists, confirming we are logged in and on feed page.
    your_story_element = ui.find_visible("#storiesContainer p")
    assert "Your story" in your_story_element.text


def test_registration_duplicate(ui):
    """TC_REG_002: Attempt registration with a duplicate USN and handle error alert"""
    # Register first user
    ui.navigate_to("register.html")
    ui.write("#fullname", "First User")
    ui.write("#username", "first_user")
    ui.write("#usn", "SELREG_DUP")
    ui.write("#password", "password123")
    ui.click("button[type='submit']")
    
    # Skip photo setup
    assert ui.wait_for_url_to_contain("setup_photo.html")
    ui.click(".btn-secondary")
    assert ui.wait_for_url_to_contain("/")
    
    # Clear local storage to log out
    ui.driver.execute_script("localStorage.clear();")
    
    # Attempt to register again with same USN
    ui.navigate_to("register.html")
    ui.write("#fullname", "Second User")
    ui.write("#username", "second_user")
    ui.write("#usn", "SELREG_DUP")  # Same USN
    ui.write("#password", "password123")
    ui.click("button[type='submit']")
    
    # Check for the alert dialog displaying the duplicate error
    alert_text = ui.get_alert_text()
    assert alert_text is not None
    assert "exists" in alert_text.lower() or "already" in alert_text.lower()
    
    # Verify we are still on register.html
    assert "register.html" in ui.driver.current_url


def test_registration_validation(ui):
    """TC_REG_003: Check HTML5 required inputs validation (form shouldn't submit if blank)"""
    ui.navigate_to("register.html")
    
    # Click register directly with empty fields
    ui.click("button[type='submit']")
    
    # Since inputs are required, the form will not submit and we will stay on register.html
    # Also verify there is no alert
    alert_text = ui.get_alert_text(timeout=1)
    assert alert_text is None
    assert "register.html" in ui.driver.current_url
