# test_saucedemo_checkout.py
#
# Practice site: https://www.saucedemo.com
# Login:   standard_user / secret_sauce
#
# This suite breaks the e-commerce "transaction" flow into separate tests:
#   1. Login
#   2. Add item(s) to cart
#   3. Cart contents are correct
#   4. Checkout - fill shipping info
#   5. Order summary - validate price calculations (the "check clearance" step)
#   6. Complete order - confirmation message
#
# Each test is INDEPENDENT - it starts fresh from the login page and
# performs whatever steps are needed to reach the state it's testing.
# This is the standard pattern: tests should never depend on each other.

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://www.saucedemo.com"
USERNAME = "standard_user"
PASSWORD = "secret_sauce"


# ── Fixture: fresh browser per test ─────────────────────────────────────────
@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    yield driver
    driver.quit()


# ── Helper: log in (used by every test except the login test itself) ───────
def login(browser, wait):
    browser.get(BASE_URL)
    browser.find_element(By.ID, "user-name").send_keys(USERNAME)
    browser.find_element(By.ID, "password").send_keys(PASSWORD)
    browser.find_element(By.ID, "login-button").click()
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "inventory_list")))


# ── Test 1: Login ────────────────────────────────────────────────────────────
def test_login(browser):
    wait = WebDriverWait(browser, 10)

    browser.get(BASE_URL)
    browser.find_element(By.ID, "user-name").send_keys(USERNAME)
    browser.find_element(By.ID, "password").send_keys(PASSWORD)
    browser.find_element(By.ID, "login-button").click()

    # After login we land on the products page
    wait.until(EC.url_contains("inventory.html"))
    title = browser.find_element(By.CLASS_NAME, "title")
    assert title.text == "Products"
    print("✅ Login successful, landed on Products page")


# ── Test 2: Add item to cart ─────────────────────────────────────────────────
def test_add_item_to_cart(browser):
    wait = WebDriverWait(browser, 10)
    login(browser, wait)

    # Add "Sauce Labs Backpack" to cart
    browser.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()

    # The cart icon badge should now show "1"
    cart_badge = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "shopping_cart_badge"))
    )
    assert cart_badge.text == "1"
    print("✅ Item added, cart badge shows 1")


# ── Test 3: Cart contents are correct ────────────────────────────────────────
def test_cart_contents(browser):
    wait = WebDriverWait(browser, 10)
    login(browser, wait)

    # Add two items
    browser.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    browser.find_element(By.ID, "add-to-cart-sauce-labs-bike-light").click()

    # Go to cart
    browser.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(EC.url_contains("cart.html"))

    # Check both items are listed
    item_names = browser.find_elements(By.CLASS_NAME, "inventory_item_name")
    names_text = [item.text for item in item_names]

    assert "Sauce Labs Backpack" in names_text
    assert "Sauce Labs Bike Light" in names_text
    assert len(names_text) == 2
    print(f"✅ Cart contains correct items: {names_text}")


# ── Test 4: Checkout - fill shipping info ────────────────────────────────────
def test_checkout_information_form(browser):
    wait = WebDriverWait(browser, 10)
    login(browser, wait)

    # Add an item and go to cart
    browser.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    browser.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(EC.url_contains("cart.html"))

    # Click "Checkout"
    browser.find_element(By.ID, "checkout").click()
    wait.until(EC.url_contains("checkout-step-one.html"))

    # Fill in shipping info
    browser.find_element(By.ID, "first-name").send_keys("Thisal")
    browser.find_element(By.ID, "last-name").send_keys("Tester")
    browser.find_element(By.ID, "postal-code").send_keys("10100")
    browser.find_element(By.ID, "continue").click()

    # Should move to step two (overview page)
    wait.until(EC.url_contains("checkout-step-two.html"))
    assert "checkout-step-two" in browser.current_url
    print("✅ Checkout info accepted, moved to order overview")


# ── Test 5: Order summary - price validation ─────────────────────────────────
def test_order_summary_price_calculation(browser):
    wait = WebDriverWait(browser, 10)
    login(browser, wait)

    # Add two known-price items
    browser.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()   # $29.99
    browser.find_element(By.ID, "add-to-cart-sauce-labs-bike-light").click()  # $9.99

    browser.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(EC.url_contains("cart.html"))

    browser.find_element(By.ID, "checkout").click()
    wait.until(EC.url_contains("checkout-step-one.html"))

    browser.find_element(By.ID, "first-name").send_keys("Thisal")
    browser.find_element(By.ID, "last-name").send_keys("Tester")
    browser.find_element(By.ID, "postal-code").send_keys("10100")
    browser.find_element(By.ID, "continue").click()
    wait.until(EC.url_contains("checkout-step-two.html"))

    # Read individual item prices from the summary
    price_elements = browser.find_elements(By.CLASS_NAME, "inventory_item_price")
    prices = [float(p.text.replace("$", "")) for p in price_elements]
    expected_subtotal = round(sum(prices), 2)

    # Read the displayed subtotal ("Item total: $39.98")
    subtotal_text = browser.find_element(By.CLASS_NAME, "summary_subtotal_label").text
    displayed_subtotal = float(subtotal_text.replace("Item total: $", ""))

    assert displayed_subtotal == expected_subtotal, (
        f"Mismatch! Items sum to {expected_subtotal}, "
        f"but page shows {displayed_subtotal}"
    )

    # Bonus check: total = subtotal + tax
    tax_text = browser.find_element(By.CLASS_NAME, "summary_tax_label").text
    tax = float(tax_text.replace("Tax: $", ""))

    total_text = browser.find_element(By.CLASS_NAME, "summary_total_label").text
    total = float(total_text.replace("Total: $", ""))

    expected_total = round(displayed_subtotal + tax, 2)
    assert total == expected_total, (
        f"Total mismatch! Expected {expected_total}, page shows {total}"
    )

    print(f"✅ Prices verified: items={prices}, subtotal={displayed_subtotal}, "
          f"tax={tax}, total={total}")


# ── Test 6: Complete the order - confirmation ────────────────────────────────
def test_complete_order(browser):
    wait = WebDriverWait(browser, 10)
    login(browser, wait)

    browser.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    browser.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(EC.url_contains("cart.html"))

    browser.find_element(By.ID, "checkout").click()
    wait.until(EC.url_contains("checkout-step-one.html"))

    browser.find_element(By.ID, "first-name").send_keys("Thisal")
    browser.find_element(By.ID, "last-name").send_keys("Tester")
    browser.find_element(By.ID, "postal-code").send_keys("10100")
    browser.find_element(By.ID, "continue").click()
    wait.until(EC.url_contains("checkout-step-two.html"))

    # Click "Finish"
    browser.find_element(By.ID, "finish").click()

    # Should land on the complete page with a thank-you message
    wait.until(EC.url_contains("checkout-complete.html"))
    complete_header = browser.find_element(By.CLASS_NAME, "complete-header")
    assert complete_header.text == "Thank you for your order!"
    print("✅ Order completed successfully - confirmation shown")