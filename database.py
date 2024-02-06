from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLAchemy_DATABASE_URL = "postgresql://elmo:kochamkotki@172.22.0.2/automatyczna_ewidencja"
engine = create_engine(SQLAchemy_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
