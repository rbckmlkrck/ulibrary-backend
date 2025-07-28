# Copyright (C) 2025 Raul Berrios
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#!/bin/sh

# This script is executed when the Docker container starts.
# It prepares the database and then executes the main container command.

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready.
# A simple sleep is used here for demonstration. In production, you might
# use a more robust script like wait-for-it.sh.
echo "Waiting for database..."
# Wait 15 seconds to ensure the database is up and running.
sleep 15

# Run Django management commands
echo "Applying database migrations..."
python manage.py migrate

echo "Creating superuser..."
# This command uses a Python script to create a superuser non-interactively.
# It checks if the user already exists to make the script idempotent.
python manage.py shell <<EOF
import os
from library.models import User
if not User.objects.filter(username='admin').exists():
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    if not password:
        raise ValueError("DJANGO_SUPERUSER_PASSWORD environment variable not set")
    User.objects.create_superuser('admin', 'admin@example.com', password)
    print(f'Superuser "admin" created.')
else:
    print('Superuser "admin" already exists.')
EOF

echo "Seeding database with initial data..."
python manage.py seed_data --clear

echo "Collecting static files..."
# The --noinput flag prevents any interactive prompts, and --clear removes old files.
python manage.py collectstatic --noinput --clear

echo "Database setup complete. Starting server."

# Execute the main command provided to the container (e.g., gunicorn)
exec "$@"