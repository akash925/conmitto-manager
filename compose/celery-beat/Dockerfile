FROM python:3.7

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV $ENV
ENV DOCKER_CONTAINER=1
ENV SQL_HOST $SQL_HOST
ENV DB_NAME $SQL_DATABASE
ENV DB_USER $SQL_USER
ENV DB_PW $SQL_PASSWORD
ENV CONMITTO_EMAIL_PASS $CONMITTO_EMAIL_PASS

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client netcat iputils-ping gdal-bin \
    && rm -rf /var/lib/apt/lists/*


RUN mkdir -p /app/api
WORKDIR /app/api

COPY requirements.txt .

RUN pip install -r requirements.txt

# Server
EXPOSE 8000
STOPSIGNAL SIGINT
#ENTRYPOINT [, ]
ENTRYPOINT ["/app/api/compose/celery-beat/entry_point.sh"]

#CMD ["python","/app/api/manage.py", "runserver", "0.0.0.0:8000"]
