from app import app
from models import db, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

with app.app_context():

    # CHECK EXISTING ADMIN

    existing_admin = User.query.filter_by(
        email="admin@gmail.com"
    ).first()

    if existing_admin:

        print("Admin already exists")

    else:

        hashed_password = bcrypt.generate_password_hash(
            "admin123"
        ).decode('utf-8')

        admin = User(

            fullname="Main Admin",

            email="admin@gmail.com",

            password=hashed_password,

            role="admin"
        )

        db.session.add(admin)

        db.session.commit()

        print("Admin Created Successfully")