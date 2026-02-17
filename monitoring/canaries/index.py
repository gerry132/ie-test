import os
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.selenium import synthetics_logger as logger


def handler(event, context):
    url = os.environ["TARGET_URL"]

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    driver = syn_webdriver.Chrome()
    driver.set_page_load_timeout(30)

    try:
        logger.info(f"Navigating to {url}")
        driver.get(url)

        response = syn_webdriver.get_http_response()

        if response is None:
            raise RuntimeError("No HTTP response captured by canary")

        status_code = response.get("statusCode")
        logger.info(f"HTTP status code: {status_code}")

        if status_code >= 400:
            raise RuntimeError(f"Canary failed: HTTP {status_code} for {url}")

        title = driver.title or ""
        logger.info(f"Loaded {url}, title='{title}'")

    finally:
        driver.quit()
