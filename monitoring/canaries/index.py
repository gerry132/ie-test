import os
import json
import urllib.request
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.selenium import synthetics_logger as logger

import boto3
import os

def _get_canary_token():
    ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "eu-west-1"))
    resp = ssm.get_parameter(
        Name=os.environ["canary_token"],
        WithDecryption=True
    )
    return resp["Parameter"]["Value"]


def _parse_http_response(raw):
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        s = raw.strip()
        if not s or s.lower() == "none":
            return None
        try:
            obj = json.loads(s)
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _get_status_with_urllib(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.getcode(), resp.geturl()


def handler(event, context):
    auth_token = _get_canary_token()
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
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd(
            "Network.setExtraHTTPHeaders",
            {
                "headers": {
                    "x-canary-token": auth_token,
                    "User-Agent": "IrelandIE-Canary/1.0"
                }
            },
        )
        final_url = driver.current_url
        logger.info(f"Final URL after redirects: {final_url}")

        raw = syn_webdriver.get_http_response(final_url)
        logger.info(f"Raw http response: {raw!r}")

        resp = _parse_http_response(raw)
        status_code = resp.get("statusCode") if resp else None

        if status_code is None:
            logger.info("Falling back to urllib for status code")
            status_code, resolved_url = _get_status_with_urllib(final_url)
            logger.info(f"urllib status_code={status_code}, resolved_url={resolved_url}")

        if int(status_code) >= 400:
            raise RuntimeError(f"Canary failed: HTTP {status_code} for {final_url}")

        title = driver.title or ""
        logger.info(f"Page OK. Title='{title}'")

    finally:
        driver.quit()
