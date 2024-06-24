from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import time
import os
import json

app = Flask(__name__)

def initialize_webdriver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-infobars')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome"
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver

def load_cookies(driver):
    cookies_json = os.environ.get('FACEBOOK_COOKIES')
    if not cookies_json:
        raise ValueError("Facebook cookies not found in environment variables")
    
    cookies = json.loads(cookies_json)
    driver.get("https://www.facebook.com")
    for cookie in cookies:
        driver.add_cookie(cookie)
    return driver

def scrape_post_url(driver, page_url):
    driver.get(page_url)
    wait = WebDriverWait(driver, 20)
    try:
        post = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-ad-preview="message"]')))
        print("Found post element")
        
        # Get the post URL
        post_id_match = re.search(r'"post_id":"(\d+)"', driver.page_source)
        if post_id_match:
            post_id = post_id_match.group(1)
            page_name = page_url.split('/')[-1]
            post_url = f"https://www.facebook.com/{page_name}/posts/{post_id}"
            print(f"Constructed post URL: {post_url}")
            return post_url
        else:
            raise ValueError("Couldn't find post ID in page source")
    except TimeoutException:
        raise TimeoutException("Timeout waiting for post element")
    except NoSuchElementException:
        raise NoSuchElementException("Post element not found")

def scrape_post_content(driver, post_url):
    driver.get(post_url)
    wait = WebDriverWait(driver, 20)
    try:
        post = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-ad-preview="message"]')))
        print("Found post content element")
        
        try:
            see_more = post.find_element(By.XPATH, ".//div[contains(text(), 'See more')]")
            driver.execute_script("arguments[0].click();", see_more)
        except NoSuchElementException:
            print("No 'See more' button found. The post might already be fully expanded.")
        
        content = post.text
        print(f"Found post content: {content[:100]}...")
        return content
    except TimeoutException:
        raise TimeoutException("Timeout waiting for post content")
    except NoSuchElementException:
        raise NoSuchElementException("Post content element not found")

@app.route('/latest_post', methods=['GET'])
def get_latest_post():
    url = 'https://www.facebook.com/LGRIDofficial'
    try:
        driver = initialize_webdriver()
        driver = load_cookies(driver)
        post_url = scrape_post_url(driver, url)
        post_content = scrape_post_content(driver, post_url)
        return jsonify({'content': post_content, 'url': post_url})
    except Exception as e:
        return jsonify({"error": "Failed to scrape the latest post", "details": str(e)}), 404
    finally:
        driver.quit()

@app.route('/test', methods=['GET'])
def test_selenium():
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome"
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.example.com")
        title = driver.title
        driver.quit()
        return jsonify({"status": "success", "title": title})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/', methods=['GET'])
def home():
    return "Facebook Scraper API is running. Use /latest_post to get the latest post."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
