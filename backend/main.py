from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes import auth, game
from database import models
from libs.logger import setup_logging, shutdown_logging
from libs.settings import settings
from libs.background_tasks import start_challenge_monitor

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    
    # Debug: Print current time and challenge status
    from libs import daily_challenge
    from datetime import datetime, timedelta
    now_maldives = datetime.utcnow() + timedelta(hours=5)
    print(f"DEBUG: Server UTC Time: {datetime.utcnow()}")
    print(f"DEBUG: Maldives Time: {now_maldives}")
    print(f"DEBUG: Challenge Date: {daily_challenge.get_today_challenge_date()}")
    print(f"DEBUG: Start Hour: {daily_challenge.CHALLENGE_START_HOUR}, End Hour: {daily_challenge.CHALLENGE_END_HOUR}")
    
    start_challenge_monitor()
    print("started challenge monitor")
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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Welcome to Dash Multiplayer Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
