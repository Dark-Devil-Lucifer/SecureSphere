import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from backend.config.database import SessionLocal
from backend.models.user import User
from backend.utils.auth import hash_password


load_dotenv()


users = [
    {
        "username": "admin",
        "email": "admin@securesphere.local",
        "password": os.getenv("SECURESPHERE_ADMIN_PASSWORD"),
        "full_name": "SecureSphere Administrator",
        "role": "ADMIN",
    },
    {
        "username": "analyst",
        "email": "analyst@securesphere.local",
        "password": os.getenv("SECURESPHERE_ANALYST_PASSWORD"),
        "full_name": "Security Analyst",
        "role": "SECURITY_ANALYST",
    },
    {
        "username": "viewer",
        "email": "viewer@securesphere.local",
        "password": os.getenv("SECURESPHERE_VIEWER_PASSWORD"),
        "full_name": "Management Viewer",
        "role": "VIEWER",
    },
]


def create_users():

    missing = [
        user["username"]
        for user in users
        if not user["password"]
    ]

    if missing:
        raise RuntimeError(
            "Missing password environment variables for: "
            + ", ".join(missing)
        )

    db: Session = SessionLocal()

    try:

        for user_data in users:

            existing_user = (
                db.query(User)
                .filter(
                    User.username == user_data["username"]
                )
                .first()
            )

            if existing_user:

                print(
                    f"User '{user_data['username']}' "
                    "already exists."
                )

                continue

            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=hash_password(
                    user_data["password"]
                ),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True,
            )

            db.add(user)

        db.commit()

        print("User creation completed.")

    except Exception as error:

        db.rollback()

        print("Error creating users:")
        print(error)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    create_users()
