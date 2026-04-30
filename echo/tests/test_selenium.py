import os
import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_SELENIUM") != "1",
    reason="Set RUN_SELENIUM=1 and run a live server to execute Selenium tests."
)

from selenium import webdriver
from selenium.webdriver.common.by import By

BASE_URL = os.environ.get("LIVE_SERVER_URL", "http://127.0.0.1:5000")

@pytest.fixture()
def browser():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

def test_homepage_loads(browser):
    browser.get(BASE_URL)
    assert "Echo Escape" in browser.title

def test_register_link_visible(browser):
    browser.get(BASE_URL)
    assert browser.find_element(By.LINK_TEXT, "Register")

def test_login_page_loads(browser):
    browser.get(BASE_URL + "/login")
    assert "Login" in browser.page_source

def test_leaderboard_page_loads(browser):
    browser.get(BASE_URL + "/leaderboard")
    assert "Leaderboard" in browser.page_source

def test_game_requires_login(browser):
    browser.get(BASE_URL + "/game")
    assert "Login" in browser.page_source or "login" in browser.current_url.lower()

def test_register_form_has_username(browser):
    browser.get(BASE_URL + "/register")
    assert browser.find_element(By.NAME, "username")
