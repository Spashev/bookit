# CRM DEPLOY

## Project setup
```
make install
```

### Run migrations
```
make migrate
```

### Make migrations
```
make makemigrations
```

### Start crm
```
make start
```

### Stop crm
```
make stop
```

### Go to bash
```
make shell
```

### Remove containers
```
make destroy
```

### Collect static
```
make collectstatic
```

### Start celery
```
make celery
```

Swagger [swagger](http://localhost:8000/swagger/).<br>
Redoc [docs](http://localhost:8000/swagger/redoc/).

### Certbot
```
docker-compose run --rm --entrypoint "\
certbot certonly --webroot -w /var/www/certbot \
  --email s.nurken92@gmail.com \
  -d bookit.kz \
  --rsa-key-size 2048 \
  --agree-tos \
  --force-renewal" certbot -v
```

### DB connection
```
SHOW max_connections;
SHOW shared_buffers;

ALTER SYSTEM SET max_connections = 99999;
ALTER SYSTEM SET shared_buffers = '2GB';
```