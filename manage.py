#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def setup_mysql():
    if os.getenv('USE_LOCAL_DB') == 'True':
        return

    import MySQLdb

    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')

    try:
        db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password)
        cursor: MySQLdb.cursors.BaseCursor = db.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def automigrate(execute_from_command_line, AUTO_MIGRATE=False):
    if 'runserver' not in sys.argv:
        return

    if not AUTO_MIGRATE:
        return

    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growskit.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    from dotenv import load_dotenv

    load_dotenv()

    setup_mysql()
    automigrate(execute_from_command_line, os.getenv('AUTO_MIGRATE') == 'True')

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
