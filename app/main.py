import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import admission, asset, staff, academic, auth, student

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Schema is managed by Alembic migrations (see alembic/), not created
    # here - run `alembic upgrade head` before starting the app.
    worker_task = asyncio.create_task(admission.admission_worker())
    yield
    worker_task.cancel()

app = FastAPI(title="BrainiacsLMSV1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admission.router)
app.include_router(asset.router)
app.include_router(staff.router)
app.include_router(academic.router)
app.include_router(auth.router)
app.include_router(student.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to BrainiacsLMSV1 API"}
