"""
Quick script to verify and reset admin credentials
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.user import User, UserRole
from app.core.security import get_password_hash

def reset_admin():
    db: Session = SessionLocal()
    
    try:
        # Find admin user
        admin = db.query(User).filter(User.email == "admin@contractagent.com").first()
        
        if admin:
            # Reset password
            admin.password_hash = get_password_hash("admin123")
            admin.is_active = True
            db.commit()
            print("✅ Admin password reset to: admin123")
            print(f"   Email: {admin.email}")
            print(f"   Role: {admin.role}")
        else:
            # Create new admin
            admin = User(
                email="admin@contractagent.com",
                name="Admin User",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✅ New admin user created!")
            print("   Email: admin@contractagent.com")
            print("   Password: admin123")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
