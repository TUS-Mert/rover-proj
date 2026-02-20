from ast import Name
import sys
import os
from argparse import ArgumentParser
import bcrypt
import dotenv

from flask_bcrypt import Bcrypt

from app.models import User
from app import create_app, db


dotenv.load_dotenv()
def initialize_database(drop_all: bool = False):
    """Drops existing tables and creates new ones based on the models."""
    app = create_app()
    bcrypt = Bcrypt()
    with app.app_context():
        try:
            print("--- Database Initialization Started ---")

            # 1. Clear existing data (Optional: remove if you want to persist data)
            if drop_all:
                print("Dropping all existing tables...")
                db.drop_all()

            # 2. Create tables based on models/ definitions
            print("Creating new tables...")
            db.create_all()

            print("✅ Database successfully initialized!")
            print(f"Tables created: {db.metadata.tables.keys()}")

            user = User(email="admin@admin.com", password=bcrypt.generate_password_hash(os.getenv("POSTGRES_PASSWORD")))
            db.session.add(user)
            db.session.commit()

        except Exception as e:
            print(f"❌ Error during initialization: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    parser = ArgumentParser(description="Initialize the database.")
    parser.add_argument(
        "--drop-all",
        action="store_true",
        help="Drop all existing tables before creating new ones.",
        default=False,
    )
    args = parser.parse_args()
    initialize_database(drop_all=args.drop_all)


if __name__ == "__main__":
    main()
