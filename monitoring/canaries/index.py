import os
import json
import requests
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.selenium import synthetics_logger as logger


def _parse_http_response(raw):
    """
    Synthetics get_http_response() may return:
      - dict
      - JSON string
      - empty string
      - 'None'
      - other non-JSON strings
    Return a dict or None.
    """
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        s = raw.strip()
        if not s or s.lower() == "none":
            return None
        # Try JSON
        try:
            obj = json.loads(s)
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            return None
    return None


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
        logger.info(f"get_http_response raw type={type(raw)} raw={raw!r}")

        resp = _parse_http_response(raw)

        status_code = None
        if resp:
            status_code = resp.get("statusCode")

        # ✅ Fallback: use requests to get a reliable status code
        if status_code is None:
            logger.info("No statusCode from get_http_response; falling back to requests.get()")
            r = requests.get(final_url, timeout=20, allow_redirects=True)
            status_code = r.status_code
            logger.info(f"requests status_code={status_code} final_url={r.url}")

        if int(status_code) >= 400:
            raise RuntimeError(f"Canary failed: HTTP {status_code} for {final_url}")

        title = driver.title or ""
        logger.info(f"Loaded OK. title='{title}'")

    finally:
        driver.quit()
