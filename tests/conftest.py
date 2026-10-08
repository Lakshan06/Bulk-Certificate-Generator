import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.config import settings

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session(monkeypatch):
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    monkeypatch.setattr("app.services.generator.SessionLocal", TestingSessionLocal)
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session, tmp_path):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    original_output_dir = settings.output_dir
    settings.output_dir = tmp_path
    
    yield TestClient(app)
    
    del app.dependency_overrides[get_db]
    settings.output_dir = original_output_dir
