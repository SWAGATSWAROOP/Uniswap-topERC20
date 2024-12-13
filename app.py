from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


app = Flask(__name__)


@app.route('/extract-tokens', methods=["GET"])
def extract_tokens():
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    chrome_options.add_argument("--no-sandbox")  # Required for running in Docker
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Disable automation flags
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36"
    )

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # Override `navigator.webdriver` to avoid detection
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            """
        },
    )

    # Open the dynamic webpage
    driver.get("https://app.uniswap.org/explore/tokens/ethereum")

    # Wait for the main content to load (adjust timeout as needed)
    try:
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sc-jGKxIK.dvVXlr"))
        )
    except Exception as e:
        print(f"Error loading page: {e}")
        driver.quit()
        return jsonify({"error": "Could not load content"}), 500

    # Extract the page source
    html = driver.page_source

    # Close the Selenium browser
    driver.quit()

    # Parse the HTML with Beautiful Soup
    soup = BeautifulSoup(html, "html.parser")

    # Find all tokens by searching for spans with the given data-testid
    a_tags = soup.find_all("span", {"data-testid": "token-name"})

    # Extract token names
    tokens = [a_tag.text.strip() for a_tag in a_tags if a_tag.text.strip()]

    # Return extracted token names as JSON
    return jsonify({"tokens": tokens, "count": len(tokens)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
