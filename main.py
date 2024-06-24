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
        return {"error": f"WebDriver initialization failed: {str(e)}"}

    driver.set_page_load_timeout(120)

    try:
        driver = webdriver.Chrome(options=options)
        print("WebDriver initialized successfully")
    except Exception as e:
        return {"error": f"WebDriver initialization failed: {str(e)}"}

    driver.set_page_load_timeout(120)

    try:
        print(f"Attempting to load URL: {url}")
        driver.get(url)
        print(f"Loaded URL: {driver.current_url}")

        # Capture page source for debugging
        page_source = driver.page_source
        print(f"Page source length: {len(page_source)}")

        wait = WebDriverWait(driver, 30)
        try:
            post = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-ad-preview="message"]')))
            print("Found post element")
            content = post.text
            print(f"Found post content: {content[:100]}...")
        except TimeoutException:
            return {"error": "Timeout waiting for post content"}
        except Exception as e:
            return {"error": f"Error finding post content: {str(e)}"}

        post_id_match = re.search(r'"post_id":"(\d+)"', page_source)
        if post_id_match:
            post_id = post_id_match.group(1)
            page_name = url.split('/')[-1]
            post_url = f"https://www.facebook.com/{page_name}/posts/{post_id}"
            print(f"Constructed post URL: {post_url}")
        else:
            return {"error": "Couldn't find post ID in page source"}

        if content or post_url:
            return {
                'content': content,
                'url': post_url
            }
        else:
            return {"error": "Failed to find both content and URL"}

    except Exception as e:
        return {"error": f"General scraping error: {str(e)}"}
    finally:
        driver.quit()
        print("Driver quit")

@app.route('/latest_post', methods=['GET'])
def get_latest_post():
    url = 'https://www.facebook.com/LGRIDofficial'
    result = scrape_latest_post(url)
    if 'error' in result:
        return jsonify({"error": "Failed to scrape the latest post", "details": result['error']}), 404
    return jsonify(result)

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