#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput

gunicorn core.asgi:application --worker-class uvicorn.workers.UvicornWorker --workers 5 --bind 0.0.0.0:8000 --timeout 200
