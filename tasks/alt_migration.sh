#!/bin/sh
set -e -o pipefail

echo "Beginning alt migration"

python manage.py build_sitemaps
# migrate_all_alt_text_to_images
echo "Task completed successfully."
