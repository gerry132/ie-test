import os
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.selenium import synthetics_logger as logger


def handler(event, context):
    url = os.environ["TARGET_URL"]

    driver = syn_webdriver.Chrome()
    driver.get(url)

    title = driver.title or ""
    logger.info(f"Loaded {url}, title='{title}'")

    driver.quit()
