#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."
    while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --noinput

python manage.py reset_db --noinput
#python manage.py sqlflush | python manage.py dbshell
##exit;
#python manage.py makemigrations
python manage.py migrate
#python manage.py collectstatic --no-input
#python manage.py initadmin
#python manage.py create_test_org

#python manage.py migrate --database=test_conmitto-test
#python manage.py migrate --settings=config.settings.unittest
#python manage.py test --settings=config.settings.unittest

exec "$@"
