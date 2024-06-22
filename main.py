from flask import Flask, jsonify
from playwright.sync_api import sync_playwright
import re

app = Flask(__name__)

def scrape_latest_post(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url)
            print(f"Loaded URL: {page.url}")

            post_selector = 'div[data-ad-preview="message"]'
            post = page.wait_for_selector(post_selector, timeout=20000)

            # Try to click "See More" if it exists
            try:
                see_more = post.locator("text=Lihat selengkapnya")
                see_more.click()
                page.wait_for_timeout(2000)  # Wait for content to expand
            except:
                print("No 'Lihat selengkapnya' button found. The post might already be fully expanded.")

            content = post.text_content()
            print(f"Found post content: {content[:100]}...")

            post_url = None
            page_source = page.content()

            # Look for the post ID in the page source
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
            browser.close()

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
