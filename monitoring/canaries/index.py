import os
import json
import urllib.request
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.selenium import synthetics_logger as logger

import boto3


import urllib.error

def _preflight(url, token):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "IrelandIE-Canary/1.0",
            "x-canary-token": token,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            logger.info(f"Preflight OK: {resp.getcode()} -> {resp.geturl()}")
            return resp.getcode(), resp.geturl()
    except urllib.error.HTTPError as e:
        body = e.read(300).decode("utf-8", errors="replace")
        logger.error(f"Preflight FAIL: HTTP {e.code} for {url}. body_head={body!r}")
        raise


def _get_canary_token():
    ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "eu-west-1"))
    resp = ssm.get_parameter(
        Name="canary_token",
        WithDecryption=True
    )
    return resp["Parameter"]["Value"]


def _get_status_with_urllib(url, auth_token):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "x-canary-token": auth_token,
        }
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

    try:
        status_code, resolved_url = _get_status_with_urllib(url, auth_token)
        logger.info(f"urllib status_code={status_code}, resolved_url={resolved_url}")

        if int(status_code) >= 400:
            raise RuntimeError(f"Canary failed: HTTP {status_code} for {url}")

        logger.info(f"Page OK.")

    finally:
        logger.info("Health check finished.")
