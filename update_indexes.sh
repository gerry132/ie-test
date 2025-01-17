#!/bin/sh
set -e -o pipefail

# OpenSearch index update
python manage.py update_index
