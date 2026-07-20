#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> Upgrading pip..."
pip install --upgrade pip

echo "==> Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
elif [ -f "bookshop/requirements.txt" ]; then
    pip install -r bookshop/requirements.txt
fi

echo "==> Collecting static files..."
if [ -f "bookshop/manage.py" ]; then
    python bookshop/manage.py collectstatic --no-input
else
    python manage.py collectstatic --no-input
fi

echo "==> Applying database migrations..."
if [ -f "bookshop/manage.py" ]; then
    python bookshop/manage.py migrate
else
    python manage.py migrate
fi

echo "==> Production build completed successfully!"
