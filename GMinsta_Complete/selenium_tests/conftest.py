import os
import sys
import time
import pytest
import threading
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import NoSuchElementException

# Set up paths so we can import the backend code
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set test environment variable BEFORE importing app to use the test database
os.environ['DB_NAME'] = 'gminsta_selenium_test'
os.environ['TESTING'] = 'true'

# pyrefly: ignore [missing-import]
from app import app as flask_app
# pyrefly: ignore [missing-import]
from database import db

# Clean up database collections helper
def clear_db_collections():
    print(f"\n[DB_DEBUG] db.db is: {db.db}")
    if db.db is not None:
        user_count_before = db.db.users.count_documents({})
        db.db.users.delete_many({})
        user_count_after = db.db.users.count_documents({})
        print(f"[DB_DEBUG] Users count before: {user_count_before}, after: {user_count_after}")
        db.db.posts.delete_many({})
        db.db.stories.delete_many({})
        db.db.messages.delete_many({})
        db.db.notifications.delete_many({})

def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", default=False, help="Run browser in headless mode")
    parser.addoption("--browser", action="store", default="chrome", help="Browser to run: chrome or edge")

# Session-scoped fixture to start the Flask app in the background
@pytest.fixture(scope="session", autouse=True)
def server_url():
    port = 5005
    flask_app.config['TESTING'] = True
    flask_app.config['DB_NAME'] = 'gminsta_selenium_test'
    
    # Run the server in a separate daemon thread
    def run_server():
        # debug=False and use_reloader=False are required to run inside a thread
        flask_app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
        
    thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()
    
    # Allow the server a moment to start
    time.sleep(1.5)
    
    url = f"http://127.0.0.1:{port}"
    yield url

# Session-scoped fixture to clear db at start and end of the test session
@pytest.fixture(scope="session", autouse=True)
def clean_db():
    clear_db_collections()
    yield
    clear_db_collections()

# Function-scoped fixture to set up Selenium webdriver
@pytest.fixture(scope="function")
def driver(request):
    headless = request.config.getoption("--headless")
    browser = request.config.getoption("--browser").lower()
    
    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,800")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)
    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,800")
        options.add_argument("--disable-gpu")
        driver = webdriver.Edge(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser}")
        
    driver.implicitly_wait(3)
    
    yield driver
    
    driver.quit()

# UI Helper Class to handle waits and interactions cleanly
class GMInstaUI:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 8, ignored_exceptions=(NoSuchElementException, AttributeError))

    def navigate_to(self, path=""):
        self.driver.get(f"{self.base_url}/{path}")

    def find(self, selector, by=By.CSS_SELECTOR):
        return self.wait.until(EC.presence_of_element_located((by, selector)))

    def find_visible(self, selector, by=By.CSS_SELECTOR):
        return self.wait.until(EC.visibility_of_element_located((by, selector)))

    def find_all(self, selector, by=By.CSS_SELECTOR):
        # returns lists, doesn't need to throw if empty, but wait for at least one if we expect it
        return self.driver.find_elements(by, selector)

    def click(self, selector, by=By.CSS_SELECTOR):
        element = self.wait.until(EC.element_to_be_clickable((by, selector)))
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)
        return element

    def write(self, selector, text, by=By.CSS_SELECTOR):
        element = self.find_visible(selector, by)
        element.clear()
        element.send_keys(text)
        return element

    def get_alert_text(self, timeout=5):
        try:
            alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            text = alert.text
            alert.accept()
            return text
        except:
            return None

    def wait_for_url_to_contain(self, text):
        return self.wait.until(EC.url_contains(text))

    def upload_image(self, selector, image_base64, by=By.CSS_SELECTOR):
        """Uploads an image via JavaScript by injecting it into the file input.
        This avoids registry MIME-type resolution issues in headless browsers on Windows.
        """
        element = self.find(selector, by)
        element_id = element.get_attribute("id")
        if not element_id:
            element_id = "temp_file_input_id"
            self.driver.execute_script(f"arguments[0].setAttribute('id', '{element_id}');", element)
            
        js_script = f"""
        const base64Str = "{image_base64}";
        const byteCharacters = atob(base64Str.includes(",") ? base64Str.split(",")[1] : base64Str);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {{
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }}
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], {{ type: "image/png" }});
        const file = new File([blob], "test.png", {{ type: "image/png" }});
        
        const fileInput = document.getElementById("{element_id}");
        const container = new DataTransfer();
        container.items.add(file);
        fileInput.files = container.files;
        fileInput.dispatchEvent(new Event('change'));
        """
        self.driver.execute_script(js_script)

# UI Helper Fixture
@pytest.fixture(scope="function")
def ui(driver, server_url):
    return GMInstaUI(driver, server_url)

# Pytest hook to capture screenshots on test failure
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    # We only look at failures during the actual test run (call phase)
    if rep.when == "call" and rep.failed:
        try:
            if "driver" in item.funcargs:
                driver = item.funcargs["driver"]
                screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)
                
                # Make safe file name
                test_name = item.name.replace("[", "_").replace("]", "_")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(screenshots_dir, f"fail_{test_name}_{timestamp}.png")
                
                driver.save_screenshot(screenshot_path)
                print(f"\n[SCREENSHOT] Test failed. Screenshot saved to: {screenshot_path}")
        except Exception as e:
            print(f"\n[WARNING] Failed to take screenshot: {e}")
