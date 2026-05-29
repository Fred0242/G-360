#!/bin/sh

echo "Attente de PostgreSQL..."

while ! nc -z db 5432; do
    sleep 1
done

echo "PostgreSQL est prêt !"

python manage.py migrate
exec "$@"
