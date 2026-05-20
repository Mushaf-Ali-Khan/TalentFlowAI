import asyncio
import logging
import threading
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI engine (bound to uvicorn's event loop — works fine for web requests)
# ---------------------------------------------------------------------------

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def init_db() -> None:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))

async def close_db() -> None:
    await engine.dispose()


# ---------------------------------------------------------------------------
# Worker-safe session factory for Celery tasks.
# asyncio.run() and run_coroutine_threadsafe() use different event loops than
# uvicorn, so the module-level engine's connection pool becomes unusable.
# This factory creates a fresh engine per-loop so connections stay valid.
# ---------------------------------------------------------------------------

_worker_engines: dict[int, tuple] = {}  # loop_id -> (engine, sessionmaker)
_worker_lock = threading.Lock()


def get_worker_session_factory() -> async_sessionmaker:
    """
    Return an async_sessionmaker that is safe to use from Celery workers.
    Creates a separate engine per event loop to avoid 'Event loop is closed' errors.
    """
    loop = None
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        pass

    loop_id = id(loop) if loop else 0

    with _worker_lock:
        if loop_id not in _worker_engines:
            eng = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=5,
                pool_recycle=300,
            )
            sf = async_sessionmaker(eng, expire_on_commit=False, class_=AsyncSession)
            _worker_engines[loop_id] = (eng, sf)
            logger.info(f"Created worker DB engine for loop {loop_id}")
        return _worker_engines[loop_id][1]
