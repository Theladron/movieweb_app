import os
import sys

from sqlalchemy import inspect

from datamanager.sqlite_data_manager import db

basedir = os.path.abspath(os.path.dirname(__file__))


def validate_database(app):
    """Validates the database by checking the file path and file itself. Exits the program and links
    to the setup file if filepath or database missing / corrupt"""
    db_path = os.path.join(basedir, 'data', 'movies.db')

    if not os.path.isfile(db_path):
        print("❌ Database not found. Please run db_setup.py to create the database.")
        sys.exit(1)

    with app.app_context():
        inspector = inspect(db.engine)

        expected_tables = {
            'user': {'id', 'name'},
            'movie': {'id', 'title', 'release_year', 'poster', 'director', 'rating'},
            'user_movies': {'id', 'user_id', 'movie_id'},
        }

        actual_tables = set(inspector.get_table_names())
        missing_tables = set(expected_tables.keys()) - actual_tables
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}.")
            print("Please delete the database and rerun db_setup.py.")
            sys.exit(1)

        for table, expected_cols in expected_tables.items():
            actual_cols = {col["name"] for col in inspector.get_columns(table)}
            if expected_cols != actual_cols:
                print(f"❌ Table '{table}' has incorrect columns.")
                print(f"Expected: {expected_cols}")
                print(f"Found:    {actual_cols}")
                print("Please delete the database and rerun db_setup.py.")
                sys.exit(1)

    print("✅ Database validated successfully.")
