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

app = Flask(__name__)

def scrape_latest_post(url):
    print("Starting scrape_latest_post function")
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome"
    print("Chrome options set up")

    try:
        driver = webdriver.Chrome(options=options)
        print("WebDriver initialized successfully")
    except Exception as e:
        print(f"Error initializing WebDriver: {str(e)}")
        return None

    driver.set_page_load_timeout(120)

    try:
        print(f"Attempting to load URL: {url}")
        driver.get(url)
        print(f"Loaded URL: {driver.current_url}")

        wait = WebDriverWait(driver, 30)
        try:
            post = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-ad-preview="message"]')))
            print("Found post element")
            try:
                see_more = post.find_element(By.XPATH, ".//div[contains(text(), 'See more')]")
                driver.execute_script("arguments[0].click();", see_more)
                print("Clicked 'See more' button")
                time.sleep(2)
            except NoSuchElementException:
                print("No 'See more' button found. The post might already be fully expanded.")

            content = post.text
            print(f"Found post content: {content[:100]}...")
        except TimeoutException:
            print("Timeout waiting for post content")
            content = None

        post_url = None
        page_source = driver.page_source

        post_id_match = re.search(r'"post_id":"(\d+)"', page_source)
        if post_id_match:
            post_id = post_id_match.group(1)
            page_name = url.split('/')[-1]
            post_url = f"https://www.facebook.com/{page_name}/posts/{post_id}"
            print(f"Constructed post URL: {post_url}")
        else:
            print("Couldn't find post ID in page source")

        if content or post_url:
            return {
                'content': content,
                'url': post_url
            }
        else:
            print("Failed to find both content and URL")
            return None

    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return None
    finally:
        driver.quit()
        print("Driver quit")

@app.route('/latest_post', methods=['GET'])
def get_latest_post():
    url = 'https://www.facebook.com/LGRIDofficial'
    try:
        result = scrape_latest_post(url)
        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Failed to scrape the latest post", "details": "No content or URL found"}), 404
    except Exception as e:
        return jsonify({"error": "Exception occurred", "details": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "Facebook Scraper API is running. Use /latest_post to get the latest post."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)