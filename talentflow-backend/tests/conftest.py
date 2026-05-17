import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings
from app.models.base import Base

# We will use an in-memory sqlite or a test postgres database.
# For async tests, let's just use the configured DATABASE_URL but we would normally use a test DB.
# For this example, we assume DATABASE_URL points to a local test DB.

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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
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
