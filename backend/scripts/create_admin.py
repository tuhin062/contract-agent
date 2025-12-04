"""
Script to create an admin user for initial setup.
Run this after setting up the database.
"""
import sys
from pathlib import Path

# Add app to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.user import User, UserRole
from app.core.security import get_password_hash
from app.db.crud.user import get_user_by_email


def create_admin_user(
    email: str = "admin@contractagent.com",
    password: str = "admin123",
    name: str = "Admin User"
):
    """
    Create an admin user.
    
    Args:
        email: Admin email
        password: Admin password
        name: Admin name
    """
    db: Session = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_user = get_user_by_email(db, email)
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            return
        
        # Create admin user
        admin_user = User(
            email=email,
            name=name,
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Role: {admin_user.role.value}")
        print(f"   ID: {admin_user.id}")
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument("--email", default="admin@contractagent.com", help="Admin email")
    parser.add_argument("--password", default="admin123", help="Admin password")
    parser.add_argument("--name", default="Admin User", help="Admin name")
    
    args = parser.parse_args()
    
    create_admin_user(
        email=args.email,
        password=args.password,
        name=args.name
    )
