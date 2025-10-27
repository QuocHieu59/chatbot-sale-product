from connection.postgresql import Base, engine
from models.user import User
import logging

# Tạo các bảng trong DB (nếu chưa có)
logger = logging.getLogger(__name__)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized.")
