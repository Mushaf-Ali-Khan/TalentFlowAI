import os
import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/talentflow")
os.environ.setdefault("CELERY_DATABASE_URL", "postgresql://user:pass@localhost:5432/talentflow")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("CLERK_SECRET_KEY", "test")
os.environ.setdefault("CLERK_PUBLISHABLE_KEY", "test")
os.environ.setdefault("R2_ACCOUNT_ID", "test")
os.environ.setdefault("R2_ACCESS_KEY_ID", "test")
os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("R2_BUCKET_NAME", "test")
os.environ.setdefault("R2_PUBLIC_URL", "https://r2.example.com")
os.environ.setdefault("EMBEDDING_MODEL_PATH", "BAAI/bge-m3")
os.environ.setdefault("EMBEDDING_MODEL_VERSION", "bge-m3-v1.0")
os.environ.setdefault("MAX_BATCH_FILES", "100")
os.environ.setdefault("MAX_FILE_SIZE_MB", "10")
os.environ.setdefault("AUTO_REJECT_THRESHOLD", "0.20")
os.environ.setdefault("JWT_CACHE_TTL_SECONDS", "300")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("SECRET_KEY", "dev-secret")

# Mock database and redis init/close functions for unit tests to avoid real connections
import app.core.database
import app.core.redis

async def dummy_async_func(*args, **kwargs):
    pass

app.core.database.init_db = dummy_async_func
app.core.database.close_db = dummy_async_func
app.core.redis.init_redis = dummy_async_func
app.core.redis.close_redis = dummy_async_func

from app.config import settings

from app.models.base import Base

# We will use an in-memory sqlite or a test postgres database.
# For async tests, let's just use the configured DATABASE_URL but we would normally use a test DB.
# For this example, we assume DATABASE_URL points to a local test DB.

ENABLE_DB_TESTS = os.getenv("ENABLE_DB_TESTS", "false").lower() == "true"

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    if not ENABLE_DB_TESTS:
        yield
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    if not ENABLE_DB_TESTS:
        pytest.skip("Database tests disabled. Set ENABLE_DB_TESTS=true to run.")
    async with async_session() as session:
        yield session

@pytest.fixture
def mock_llm_factory():
    def _factory(return_data=None):
        class MockLLM:
            async def generate(self, *args, **kwargs):
                return return_data
        return MockLLM()
    return _factory

@pytest.fixture
def fixture_candidate_profile():
    return {
        "name": "Tony Stark",
        "email": "tony@starkindustries.com",
        "phone": "555-0199",
        "location": "Malibu, CA",
        "skills": [
            {"name": "Python", "years_experience": 10.0, "proficiency": "expert"}
        ],
        "experience": [
            {
                "company": "Stark Industries",
                "title": "CEO",
                "start_date": "2008-05-02",
                "end_date": None,
                "is_current": True,
                "achievements": ["Built Iron Man suit in a cave"]
            }
        ],
        "education": [],
        "certifications": [],
        "languages": ["English"],
        "total_years_experience": 10.0,
        "seniority_level": "executive",
        "extraction_confidence": 0.99,
        "needs_manual_review": False
    }
