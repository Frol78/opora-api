import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app as fastapi_app
from app.models.user import User  # noqa: F401  нужно, чтобы таблица users попала в Base.metadata

# Отдельная база в памяти только для тестов. Настоящий opora.db не трогаем.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False)


@pytest.fixture()
def client():
    # Каждый тест получает чистую базу: создаём таблицы, после теста удаляем
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Подменяем настоящий get_db на тестовый
    fastapi_app.dependency_overrides[get_db] = override_get_db

    yield TestClient(fastapi_app)

    fastapi_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
