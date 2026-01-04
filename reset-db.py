from app import create_app, db
import app.models # Ensure models are loaded

app = create_app()
with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    print("✅ Database Reset Successfully!")