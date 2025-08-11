import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

from main import app, get_db
from models import Base

load_dotenv()
TEST_DB_URL = os.getenv("TEST_DB_URL")

if not TEST_DB_URL:
    raise ValueError("URL is not there in .env file...")


engine = create_engine(TEST_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind = engine)

def override_db():
    try:
        db = SessionLocal()
        yield db
    
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        yield db
    
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(db_session : Session):
    with TestClient(app) as c:
        yield c