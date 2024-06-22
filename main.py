from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import chromedriver_autoinstaller
import re
import time

app = Flask(__name__)

def scrape_latest_post(url):
    chromedriver_autoinstaller.install()
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Add these lines to specify the path to the Chrome executable
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        print(f"Loaded URL: {driver.current_url}")

        wait = WebDriverWait(driver, 20)
        try:
            post = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-ad-preview="message"]')))
            
            try:
                see_more = post.find_element(By.XPATH, ".//div[contains(text(), 'Lihat selengkapnya')]")
                driver.execute_script("arguments[0].click();", see_more)
                time.sleep(2)
            except NoSuchElementException:
                print("No 'Lihat selengkapnya' button found. The post might already be fully expanded.")

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

    finally:
        driver.quit()

@app.route('/latest_post', methods=['GET'])
def get_latest_post():
    url = 'https://www.facebook.com/LGRIDofficial'
    result = scrape_latest_post(url)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Failed to scrape the latest post"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
