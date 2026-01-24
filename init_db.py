import sys
from argparse import ArgumentParser

from app import create_app, db

def initialize_database(drop_all):
    """Drops existing tables and creates new ones based on the models."""
    app = create_app()
    
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
            
        except Exception as e:
            print(f"❌ Error during initialization: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    parser = ArgumentParser(description="Initialize the database.")
    parser.add_argument("--drop-all", action="store_true", help="Drop all existing tables before creating new ones.", default=False)
    args = parser.parse_args()
    initialize_database(drop_all=args.drop_all)

if __name__ == "__main__":
    main()