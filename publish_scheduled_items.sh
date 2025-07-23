#!/bin/sh
set -e -o pipefail

echo "Publishing scheduled items"
python manage.py publish_scheduled

echo "Task completed successfully."
