from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes import auth, game
from database import models
from libs.logger import setup_logging, shutdown_logging
from libs.settings import settings

from alembic.config import Config
from alembic import command

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run database migrations
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Database migrations applied successfully.")
    except Exception as e:
        print(f"Error applying database migrations: {e}")

    setup_logging()
    yield
    shutdown_logging()

app = FastAPI(title="Dash Multiplayer Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(game.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Dash Multiplayer Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
