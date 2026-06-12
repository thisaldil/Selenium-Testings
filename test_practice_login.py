# test_practice_login.py

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ── Credentials (these are public — the site gives them to you) ─────────────
LOGIN_URL = "https://practicetestautomation.com/practice-test-login/"
USERNAME  = "student"
PASSWORD  = "Password123"

# ── Fixture ──────────────────────────────────────────────────────────────────
@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")   # full screen so you can watch
    # options.add_argument("--headless")         # ← uncomment to hide the browser
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    yield driver
    driver.quit()

# ── Test 1: Successful login ─────────────────────────────────────────────────
def test_successful_login(browser):
    wait = WebDriverWait(browser, 10)

    browser.get(LOGIN_URL)

    # Type username
    browser.find_element(By.ID, "username").send_keys(USERNAME)

    # Type password
    browser.find_element(By.ID, "password").send_keys(PASSWORD)

    # Click the Login button
    browser.find_element(By.ID, "submit").click()

    # After login, page should say "Congratulations"
    success_msg = wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert "Congratulations" in success_msg.text
    print("✅ Login successful!")

# ── Test 2: Wrong username ───────────────────────────────────────────────────
def test_wrong_username(browser):
    wait = WebDriverWait(browser, 10)

    browser.get(LOGIN_URL)
    browser.find_element(By.ID, "username").send_keys("wronguser")
    browser.find_element(By.ID, "password").send_keys(PASSWORD)
    browser.find_element(By.ID, "submit").click()

    error = wait.until(
        EC.visibility_of_element_located((By.ID, "error"))
    )
    assert "Your username is invalid!" in error.text
    print("✅ Wrong username correctly rejected")

# ── Test 3: Wrong password ───────────────────────────────────────────────────
def test_wrong_password(browser):
    wait = WebDriverWait(browser, 10)

    browser.get(LOGIN_URL)
    browser.find_element(By.ID, "username").send_keys(USERNAME)
    browser.find_element(By.ID, "password").send_keys("wrongpass")
    browser.find_element(By.ID, "submit").click()

    error = wait.until(
        EC.visibility_of_element_located((By.ID, "error"))
    )
    assert "Your password is invalid!" in error.text
    print("✅ Wrong password correctly rejected")

# ── Test 4: Empty fields ─────────────────────────────────────────────────────
def test_empty_fields(browser):
    wait = WebDriverWait(browser, 10)

    browser.get(LOGIN_URL)
    browser.find_element(By.ID, "submit").click()

    error = wait.until(
        EC.visibility_of_element_located((By.ID, "error"))
    )
    assert error.is_displayed()
    print("✅ Empty form correctly blocked")

# ── Test 5: Logout after login ───────────────────────────────────────────────
def test_logout_after_login(browser):
    wait = WebDriverWait(browser, 10)

    browser.get(LOGIN_URL)
    browser.find_element(By.ID, "username").send_keys(USERNAME)
    browser.find_element(By.ID, "password").send_keys(PASSWORD)
    browser.find_element(By.ID, "submit").click()

    # Wait for the logout button to appear
    logout_btn = wait.until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Log out"))
    )
    logout_btn.click()

    # Should be back on the login page
    wait.until(EC.presence_of_element_located((By.ID, "username")))
    assert "practice-test-login" in browser.current_url
    print("✅ Logout successful!")