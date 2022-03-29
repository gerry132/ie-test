#!/bin/bash


python3 manage.py migrate --fake

if $( python3 manage.py migrate  --noinput > /dev/null ); then
    echo "Migrations run successfully"
else
echo "Migrations failed. Please check logs."
    exit 1
fi

init_username="system_admin"
init_password="password1234!"

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='"$init_username"').exists() or User.objects.create_superuser('"$init_username"', password='"$init_password"');" | python3 manage.py shell

gunicorn -b :8000 --keep-alive 60 --workers 3 app.wsgi --log-level error --access-logfile - --error-logfile -

exit 1
