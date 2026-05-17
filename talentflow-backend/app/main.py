from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.middleware import RequestContextMiddleware
from app.core.exceptions import TalentFlowException, talentflow_exception_handler, global_exception_handler
import app.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # init DB pool, Redis, embedding model
    print("Starting up...")
    yield
    print("Shutting down...")

app = FastAPI(title="TalentFlow AI", version="0.1.0", lifespan=lifespan)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Should be tightened in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(TalentFlowException, talentflow_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Mount API routers
from app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}
