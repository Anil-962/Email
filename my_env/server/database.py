from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Set up SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"

# Create the engine with thread restriction off (specific to SQLite)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Connect a localized session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base for the SQLAlchemy Object Models
Base = declarative_base()

# FastAPI dependency generator tool to yield and cleanly close the connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
