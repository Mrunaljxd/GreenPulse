from app import app, db
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

with app.app_context():
    with db.engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE user_plant ADD COLUMN custom_name TEXT;'))
            print("Added column 'custom_name'")
        except (OperationalError, ProgrammingError):
            print("Column 'custom_name' already exists or cannot be added")

        try:
            conn.execute(text('ALTER TABLE user_plant ADD COLUMN rejected BOOLEAN DEFAULT 0;'))
            print("Added column 'rejected'")
        except (OperationalError, ProgrammingError):
            print("Column 'rejected' already exists or cannot be added")



