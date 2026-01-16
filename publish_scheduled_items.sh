#!/bin/sh
set -e -o pipefail

echo "Publishing scheduled items"
python manage.py publish_scheduled
python manage.py build_sitemaps

echo "Task completed successfully."
