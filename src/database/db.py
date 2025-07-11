from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+psycopg2://ultimate_user:ultimate_password@172.28.0.2:5432/ultimate_db"

class DatabaseManager:
  def __init__(cls, database_url):
    cls.database_url = database_url
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

db_manager = DatabaseManager(DATABASE_URL)