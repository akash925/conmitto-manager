#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."
    while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

echo "reset_db"
python manage.py reset_db --noinput
echo "makemigrations..."
python manage.py makemigrations
echo "migrate..."
python manage.py migrate
echo "collectstatic..."
python manage.py collectstatic --no-input
echo "initadmin..."
python manage.py initadmin
echo "create test org..."
python manage.py create_test_org

exec "$@"
