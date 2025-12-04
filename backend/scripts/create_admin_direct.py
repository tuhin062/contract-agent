"""
Script to create an admin user directly in the database.
Run this after running migrations.

Usage:
    python scripts/create_admin_direct.py

This will create an admin user with:
    Email: admin@contractagent.com
    Password: Admin123!
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.models.user import User, UserRole
from app.core.security import get_password_hash


def create_admin():
    """Create admin user directly."""
    # Create database connection
    engine = create_engine(str(settings.DATABASE_URL))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Check if admin already exists
        email = "admin@contractagent.com"
        existing = db.query(User).filter(User.email == email).first()
        
        if existing:
            print(f"Admin user already exists: {email}")
            print(f"ID: {existing.id}")
            print(f"Role: {existing.role}")
            return
        
        # Create admin user
        admin = User(
            email=email,
            name="System Administrator",
            password_hash=get_password_hash("Admin123!"),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("=" * 50)
        print("Admin user created successfully!")
        print("=" * 50)
        print(f"Email: {email}")
        print(f"Password: Admin123!")
        print(f"ID: {admin.id}")
        print(f"Role: {admin.role}")
        print("=" * 50)
        print("IMPORTANT: Change this password immediately in production!")
        print("=" * 50)
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
