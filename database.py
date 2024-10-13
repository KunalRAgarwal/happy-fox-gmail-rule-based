from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime

DATABASE_URL = 'sqlite:///emails.db'
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    message_id = Column(String, unique=True)
    sender = Column(String)
    subject = Column(String)
    message_snippet = Column(String)
    received_datetime = Column(DateTime)
    is_read = Column(Boolean)
    labels = Column(String)

Base.metadata.create_all(engine)