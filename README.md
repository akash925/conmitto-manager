# API Documentation

## Library Documentation Links
https://django-extensions.readthedocs.io/en/latest/

Django Channels Rest Framework
https://github.com/hishnash/djangochannelsrestframework

Django Scheduler 
https://github.com/tejasjadhav/django-scheduler

### Migration Troubleshooting Tips
For LOCAL database problems only, you can use the `manage.py reset_db` command to completely reset the database

To delete all migration files:
```bash
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
```

Sometimes `--fake-inital`  can be helpful too.
```bash
python manage.py makemigrations
python manage.py migrate --fake-initial
```

### Running Tests
To run the backend tests, simply run the following command while the docker backend is running

```
docker exec $(docker ps -aqf "name=django_server") python manage.py test --settings=config.settings.unittest
```

If a specific test suite is desired to run, just append the path to the app to the end of that command,
such as `api.assets.asset`

### Celery

```bash
celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
celery worker -A config --loglevel=debug --concurrency=4
```

### Updating Requirements

For any new pip modules added, add to the `requirements.in` file.

Then run:
```bash
pip-compile --output-file requirements.txt requirements.in
```


### Testing with Django Shell
Using the django-extensions shell plus, you can quickly get to a Django shell with all model imports.
```bash
 ./scripts/docker_api_shell.sh 
# python manage.py shell_plus
# Shell Plus Model Imports

```

## Docker and testing tips

If using pycharm to run tests with the manage.py console, canceling can leave the test database created and will hang on that next time you run the tests.
To fix:
run this command inside the dev_db container

```bash
psql -U conmitto -c "DROP DATABASE IF EXISTS test_conmitto;"
```


 
 
