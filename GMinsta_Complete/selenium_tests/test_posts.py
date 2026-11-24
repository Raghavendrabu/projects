import pytest
import bcrypt
from datetime import datetime
from database import db
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

# Base64 for a tiny 1x1 transparent PNG image
TINY_PNG_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

def register_and_login(ui, usn, username, password):
    """Helper to register user directly and log them in via the UI"""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = {
        'fullname': 'Post Tester',
        'username': username,
        'usn': usn,
        'password': hashed,
        'profilePhoto': None,
        'bio': 'Post testing user',
        'followers': [],
        'following': [],
        'isPrivate': False,
        'created_at': datetime.utcnow()
    }
    db.db.users.insert_one(user)
    
    # Login via UI
    ui.navigate_to("login.html")
    ui.write("#usn", usn)
    ui.write("#password", password)
    ui.click("button[type='submit']")
    ui.find_visible("#storiesContainer")


def test_create_and_verify_post(ui):
    """TC_PST_001: Log in, go to post creation, upload image, add caption, share, and verify in feed"""
    register_and_login(ui, "SELPST001", "posttester", "password123")
    
    # Click the square-plus icon in bottom navigation to go to post.html
    ui.navigate_to("post.html")
    assert ui.wait_for_url_to_contain("post.html")
    
    # Upload the image using JS injection
    ui.upload_image("#fileInput", TINY_PNG_BASE64)
    
    # Write caption
    caption_text = "This is a selenium automated test post! #awesome"
    ui.write("#captionInput", caption_text)
    
    # Click share in header
    ui.click(".header .share")
    
    # Verify redirected back to feed homepage
    ui.find_visible("#feedContainer")
    
    # Wait for the post to load on the feed
    feed_post = ui.find_visible(".post")
    assert feed_post is not None
    
    # Verify post author and caption
    caption_element = ui.find_visible(".post .caption")
    assert "posttester" in caption_element.text
    assert caption_text in caption_element.text


def test_like_post(ui):
    """TC_PST_002: Like a post and verify the like count updates"""
    register_and_login(ui, "SELPST002", "liketester", "password123")
    
    # Create a post first
    ui.navigate_to("post.html")
    ui.upload_image("#fileInput", TINY_PNG_BASE64)
    ui.write("#captionInput", "Like testing post")
    ui.click(".header .share")
    ui.find_visible("#feedContainer")
    
    # Verify initial likes (0 likes or no likes text)
    likes_elem = ui.find_visible(".post .likes")
    assert "0 likes" in likes_elem.text
    
    # Click the like heart button
    ui.click(".post .like-btn")
    
    # Wait and verify likes count updates to 1 (handling stale references on feed reload)
    def check_likes(d):
        try:
            element = d.find_element(By.CSS_SELECTOR, ".post .likes")
            return "1 likes" in element.text
        except StaleElementReferenceException:
            return False
            
    ui.wait.until(check_likes)
    
    # Verify like button icon has solid class
    like_btn = ui.find(".post .like-btn")
    assert "fa-solid" in like_btn.get_attribute("class")


def test_comment_on_post(ui):
    """TC_PST_003: Comment on a post and verify the comment is listed in the modal"""
    register_and_login(ui, "SELPST003", "commenttester", "password123")
    
    # Create a post
    ui.navigate_to("post.html")
    ui.upload_image("#fileInput", TINY_PNG_BASE64)
    ui.write("#captionInput", "Comment testing post")
    ui.click(".header .share")
    ui.find_visible("#feedContainer")
    
    # Click comment button to open modal
    ui.click(".post .fa-comment")
    
    # Verify comment modal is displayed
    modal = ui.find_visible("#commentModal")
    assert modal.is_displayed()
    
    # Write a comment and post it
    comment_text = "Automation comment here!"
    ui.write("#commentInput", comment_text)
    ui.click(".comment-input-area button")
    
    # The frontend closes the comment modal automatically when postComment() completes.
    # Wait for the comment modal to be closed first.
    ui.wait.until(lambda d: not d.find_element(By.ID, "commentModal").is_displayed())
    
    # Reopen the comment modal to verify the comment has been added
    ui.click(".post .fa-comment")
    
    # Verify comment appears in list
    comments_list = ui.find_visible("#commentsList")
    assert "commenttester" in comments_list.text
    assert comment_text in comments_list.text
    
    # Close comment modal
    ui.click(".modal-header .fa-xmark")
    
    # Verify modal is hidden
    ui.wait.until(lambda d: not d.find_element(By.ID, "commentModal").is_displayed())
