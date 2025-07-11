import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = f"postgresql+psycopg2://{os.environ.get("DATABASE_USER")}:{os.environ.get("DATABASE_PASSWORD")}@172.28.0.2:5432/{os.environ.get("DATABASE_NAME")}"

class DatabaseManager:
  def __init__(cls):
    cls.database_url = DATABASE_URL
    cls.engine = create_engine(cls.database_url)
    cls.SessionLocal = sessionmaker(bind=cls.engine)
    cls.Base = declarative_base()

  def get_db(cls):
      
    db = cls.SessionLocal()
    try:
        yield db
    finally:
        db.close()

  def create_all_tables(cls):
      
    cls.Base.metadata.create_all(bind=cls.engine)

db_manager = DatabaseManager()