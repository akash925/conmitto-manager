FROM mdillon/postgis:11

# Custom initialization scripts
COPY create_db.sh /docker-entrypoint-initdb.d/20-create_db.sh
#COPY schema.sql /schema.sql
#COPY data.sql /data.sql

RUN chmod +x /docker-entrypoint-initdb.d/20-create_db.sh