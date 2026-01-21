#!/bin/sh
set -e -o pipefail

echo "Building sitemaps"

python manage.py build_sitemaps

echo "Task completed successfully."
