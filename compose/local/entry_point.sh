#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."
    echo "HOST: $SQL_HOST"
    echo "PORT: $SQL_PORT"
    while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi


#python manage.py reset_db --noinput

#python manage.py makemigrations
#python manage.py migrate
#python manage.py clean_duplicate_history --auto
#python manage.py collectstatic --no-input

#python manage.py create_test_org

exec "$@"
