import os
import json
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.selenium import synthetics_logger as logger
from aws_synthetics.common import synthetics_common as common


def handler(event, context):
    url = os.environ["TARGET_URL"]

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    driver = syn_webdriver.Chrome()
    driver.set_page_load_timeout(30)

    try:
        logger.info(f"Navigating to {url}")

        # Better step visibility in CloudWatch Synthetics
        common.execute_step("load_page", lambda: driver.get(url))

        # Use final URL in case of redirects (CloudFront/ALB etc.)
        final_url = driver.current_url
        logger.info(f"Final URL: {final_url}")

        raw_response = syn_webdriver.get_http_response(final_url)
        logger.info(f"Raw response type: {type(raw_response)}")
        logger.info(f"Raw response: {raw_response}")

        if not raw_response:
            raise RuntimeError(f"No HTTP response captured for {final_url}")

        # 🔧 Handle string vs dict (fixes your exact error)
        if isinstance(raw_response, str):
            response = json.loads(raw_response)
        else:
            response = raw_response

        status_code = response.get("statusCode")
        logger.info(f"HTTP status code: {status_code}")

        if status_code is None:
            raise RuntimeError("Status code not present in response")

        # ❌ Fail canary on bad status (this will trigger your alarm)
        if status_code >= 400:
            raise RuntimeError(f"Canary failed: HTTP {status_code} for {final_url}")

        title = driver.title or ""
        logger.info(f"Page loaded successfully. Title='{title}'")

    finally:
        driver.quit()
