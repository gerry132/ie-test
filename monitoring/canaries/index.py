import os
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.selenium import synthetics_logger as logger


def handler(event, context):
    url = os.environ["TARGET_URL"]

    # Fix invalid argument issue (your logs showed uat.ireland.ie)
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    driver = syn_webdriver.Chrome()
    driver.set_page_load_timeout(30)

    try:
        logger.info(f"Navigating to {url}")
        driver.get(url)

        # ✅ Correct usage: must pass URL
        response = syn_webdriver.get_http_response(url)

        if not response:
            raise RuntimeError(f"No HTTP response captured for {url}")

        status_code = response.get("statusCode")
        logger.info(f"HTTP status code for {url}: {status_code}")

        # ❌ Fail the canary properly
        if status_code >= 400:
            raise RuntimeError(f"Canary failed: HTTP {status_code} for {url}")

        title = driver.title or ""
        logger.info(f"Loaded {url}, title='{title}'")

    finally:
        driver.quit()
