import os
import json
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.selenium import synthetics_logger as logger


def handler(event, context):
    url = os.environ.get("TARGET_URL", "").strip()
    if not url:
        raise RuntimeError("TARGET_URL environment variable is not set")

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    driver = syn_webdriver.Chrome()
    driver.set_page_load_timeout(30)

    try:
        logger.info(f"Navigating to {url}")
        driver.get(url)

        final_url = driver.current_url
        logger.info(f"Final URL: {final_url}")

        raw = syn_webdriver.get_http_response(final_url)
        logger.info(f"HTTP response raw type={type(raw)} raw={raw}")

        if not raw:
            raise RuntimeError(f"No HTTP response captured for {final_url}")

        # get_http_response sometimes returns a JSON string in this runtime
        response = json.loads(raw) if isinstance(raw, str) else raw

        status_code = response.get("statusCode")
        logger.info(f"HTTP status code: {status_code}")

        if status_code is None:
            raise RuntimeError(f"No statusCode in http response for {final_url}: {response}")

        if int(status_code) >= 400:
            raise RuntimeError(f"Canary failed: HTTP {status_code} for {final_url}")

        title = driver.title or ""
        logger.info(f"Loaded OK. title='{title}'")

    finally:
        driver.quit()
