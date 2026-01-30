#!/bin/sh
set -e -o pipefail

echo "Beginning alt migration"

python manage.py migrate_all_alt_text_to_images

# migrate_all_alt_text_to_images
echo "Task completed successfully."
