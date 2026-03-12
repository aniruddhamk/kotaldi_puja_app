from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./kotaldi_puja.db"
# If deploying to a system where local SQLite files don't persist well, 
# typically we would switch to PostgreSQL. SQLite is fine for our Render free tier 
# if we attach a persistent disk, otherwise data resets on each deploy.
# For Kotaldi, we'll configure it straightforwardly.

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
