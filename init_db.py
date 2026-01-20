import sys
from app import create_app, db

def initialize_database():
    """Drops existing tables and creates new ones based on the models."""
    app = create_app()
    
    with app.app_context():
        try:
            print("--- Database Initialization Started ---")
            
            # 1. Clear existing data (Optional: remove if you want to persist data)
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

if __name__ == "__main__":
    initialize_database()