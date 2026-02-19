from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from database import database, models
from libs import security, websocket_manager, daily_challenge
from libs.settings import settings
from pydantic import BaseModel
import random
import uuid
import json

router = APIRouter(prefix="/game", tags=["game"])

@router.get("/config")
async def get_game_config():
    # Return a fresh config for single player with a random seed
    config = settings.GAME_CONFIG.copy()
    config["world"] = config["world"].copy()
    config["world"]["seed"] = str(uuid.uuid4())
    return config

@router.post("/start/single")
async def start_single_player(config: dict = None, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(database.get_db)):
    # Use provided config or default
    if not config or not config.get("world"):
       config = await get_game_config()
       
    # Create Session strictly for 1 player (Private)
    session = models.MultiplayerSession(
        host_id=current_user.id,
        max_players=1,
        game_seed=str(uuid.uuid4()),
        status="started" # Immediately started, so no one else can join via "waiting" check
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # config seed should match session seed
    config["world"]["seed"] = session.game_seed
    config["is_multiplayer"] = False # Logic tweak: It IS technically a session, but UI treats as single? 
                                     # Actually, better to set True so WS logic works, but maybe keep UI clean.
                                     # Let's keep strict "is_multiplayer": False for UI HUD differences if any.

    # Create Race
    race = models.Race(
        name=f"Single Player Race {current_user.username}",
        config=config,
        car_index=0
    )
    db.add(race)
    db.commit()
    db.refresh(race)
    
    # Create Game (Participant) - Auto-join host
    game = models.Game(
        user_id=current_user.id,
        race_id=race.id,
        multiplayer_session_id=session.id, # Link to session
        car_index=0
    )
    db.add(game)
    db.commit()
    
    return {
        "status": "started", 
        "race_id": race.id, 
        "session_id": str(session.id), # Return session_id for WS connection
        "config": config
    }

class CreateLobbyRequest(BaseModel):
    max_players: int = 5

class LobbyResponse(BaseModel):
    session_id: str
    host_id: int
    players: list

@router.post("/lobby", response_model=LobbyResponse)
async def create_lobby(request: CreateLobbyRequest, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(database.get_db)):
    # Create Session directly (Race created at start)
    session = models.MultiplayerSession(
        host_id=current_user.id,
        max_players=request.max_players,
        game_seed=str(uuid.uuid4())
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Add Host as first participant (Game)
    game = models.Game(
        user_id=current_user.id,
        multiplayer_session_id=session.id,
        car_index=0 # Host default
    )
    db.add(game)
    db.commit()
    
    # Return full lobby info
    players = [{"id": g.user.id, "username": f"{g.user.username}#{g.user.id}"} for g in session.games if g.user]
    return {
        "session_id": str(session.id),
        "host_id": session.host_id,
        "players": players
    }

class JoinLobbyRequest(BaseModel):
    car_index: int = 0

@router.post("/lobby/{session_id}/join", response_model=LobbyResponse)
async def join_lobby(session_id: int, request: JoinLobbyRequest, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(database.get_db)):
    session = db.query(models.MultiplayerSession).filter(models.MultiplayerSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Strict checks as requested
    if session.status != "waiting":
         raise HTTPException(status_code=400, detail="Game already started or finished")

    # Count CURRENT players (reliable check)
    player_count = db.query(models.Game).filter(models.Game.multiplayer_session_id == session.id).count()
    if player_count >= session.max_players:
        raise HTTPException(status_code=400, detail="Lobby is full")

    # Check if already joined
    game = db.query(models.Game).filter(
        models.Game.multiplayer_session_id == session.id,
        models.Game.user_id == current_user.id
    ).first()
    
    if not game:
        # Join
        game = models.Game(
            user_id=current_user.id,
            multiplayer_session_id=session.id,
            car_index=request.car_index
        )
        db.add(game)
        db.commit()
        db.refresh(session)
    else:
        # Update car_index if already in lobby
        game.car_index = request.car_index
        db.commit()
    
    # Return full lobby info
    players_data = [{"id": g.user.id, "username": f"{g.user.username}#{g.user.id}"} for g in session.games if g.user]
    
    # Notify others via WebSocket
    await websocket_manager.manager.broadcast({
        "type": "lobby_update",
        "players": players_data
    }, str(session.id))
    
    return {
        "session_id": str(session.id),
        "host_id": session.host_id,
        "players": players_data
    }

async def _start_session_game(session: models.MultiplayerSession, db: Session):
    session.status = "started"
    # Generate final seed
    session.game_seed = str(uuid.uuid4())
    
    import copy
    config = copy.deepcopy(settings.GAME_CONFIG)
    config["world"]["seed"] = session.game_seed
    config["is_multiplayer"] = True
    
    # Scale lanes to player count, but keep at least the default for variety
    num_players = len(session.games)
    max_lanes = max(settings.GAME_CONFIG["lanes"]["maxLanes"], num_players)
    config["lanes"]["maxLanes"] = max_lanes
    
    # Randomize lanes (1-based index) for all players
    available_lanes = list(range(1, max_lanes + 1))
    random.shuffle(available_lanes)
    
    lane_map = {}
    for i, game in enumerate(session.games):
        # Assign lane
        assigned = available_lanes[i % len(available_lanes)]
        game.assigned_lane = assigned
        game.score = 0
        game.finished_at = None
        lane_map[str(game.user_id)] = assigned
        
    # Start car in one of the assigned lanes (e.g. Host's)
    config["player"]["initialLane"] = lane_map.get(str(session.host_id), 1)
    
    # Create Race now
    race = models.Race(
        name=f"Race for Session {session.id}",
        config=config,
        car_index=0
    )
    db.add(race)
    db.flush() # Get race ID
    
    # Link games to this race
    for game in session.games:
        game.race_id = race.id
        
    db.commit()
    
    # Broadcast Start
    await websocket_manager.manager.broadcast({
        "type": "game_start",
        "race_id": race.id,
        "config": config,
        "seed": session.game_seed,
        "lane_assignments": lane_map
    }, str(session.id))
    
    return race.id

@router.post("/lobby/{session_id}/start")
async def start_game(session_id: int, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(database.get_db)):
    session = db.query(models.MultiplayerSession).filter(models.MultiplayerSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only host can start game")
        
    race_id = await _start_session_game(session, db)
    return {"status": "started", "race_id": race_id}

@router.post("/lobby/{session_id}/retry")
async def retry_lobby(session_id: int, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(database.get_db)):
    session = db.query(models.MultiplayerSession).filter(models.MultiplayerSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only host can retry game")
        
    race_id = await _start_session_game(session, db)
    return {"status": "started", "race_id": race_id}

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, db: Session = Depends(database.get_db)):
    # Don't accept yet, manager.connect will do it
    token = websocket.query_params.get("token")
    if not token:
        await websocket.accept() # Accept just to close with code
        await websocket.close(code=4003, reason="Missing token")
        return
        
    user = security.get_user_from_token(token, db)
    if not user:
        await websocket.accept()
        await websocket.close(code=4003, reason="Invalid token")
        return
        
    # Check if user joined this session
    try:
        s_id = int(session_id)
    except ValueError:
        await websocket.accept()
        await websocket.close(code=4000, reason="Invalid session ID")
        return

    joined_game = db.query(models.Game).filter(
        models.Game.multiplayer_session_id == s_id,
        models.Game.user_id == user.id
    ).first()
    
    if not joined_game:
        await websocket.accept()
        await websocket.close(code=4003, reason="User not in this session")
        return
    
    await websocket_manager.manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Re-broadcast to others
            message["user_id"] = user.id
            await websocket_manager.manager.broadcast(message, session_id, exclude=websocket)
            
            # Persist 'collect' events
            if message.get("type") == "collect":
                amount = message.get("amount", 1)
                success, msg = daily_challenge.increment_dates(db, user, amount)
                if not success:
                    print(f"WS Collect Error for {user.username}: {msg}")
            
    except WebSocketDisconnect:
        websocket_manager.manager.disconnect(websocket, session_id)
        # Notify others of disconnection
        await websocket_manager.manager.broadcast({"type": "player_disconnected", "id": user.id}, session_id)



@router.get("/leaderboard")
async def get_leaderboard(db: Session = Depends(database.get_db)):
    users = db.query(models.User).order_by(models.User.score.desc()).limit(settings.LEADERBOARD_LIMIT).all()
    return [{"id": u.id, "username": f"{u.username}#{u.id}", "score": u.score, "photo": u.profile_photo} for u in users]

class ScoreSubmission(BaseModel):
    score: int

@router.post("/{race_id}/score")
async def submit_score(race_id: int, submission: ScoreSubmission, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(database.get_db)):
    # Find the game record
    # race_id here is actually session_id in current flow context? 
    # Frontend might pass session_id or race_id. 
    # Let's assume it passes the Race ID returned in start_game.
    
    # Actually, models.Game links to race_id.
    
    game = db.query(models.Game).filter(
        models.Game.race_id == race_id,
        models.Game.user_id == current_user.id
    ).first()
    
    if not game:
        # Fallback: create a new Game record if missing
        game = models.Game(
            user_id=current_user.id,
            race_id=race_id if race_id > 0 else None,
            score=submission.score
        )
        db.add(game)
    else:
        game.score = submission.score
        game.finished_at = func.now()
    
    # Update Race Status to finished
    race = db.query(models.Race).filter(models.Race.id == race_id).first()
    if race:
        race.status = "finished"
    
    # Update Multiplayer Session status if applicable
    if game and game.multiplayer_session_id:
        session = db.query(models.MultiplayerSession).filter(models.MultiplayerSession.id == game.multiplayer_session_id).first()
        if session:
            session.status = "ended"
    
    # Update User High Score
    if submission.score > current_user.score:
        current_user.score = submission.score
        
    db.commit()
    
    return {"status": "success", "new_high_score": current_user.score}



@router.get("/challenge/status")
async def get_challenge_status(current_user: models.User = Depends(security.get_current_user)):
    return daily_challenge.get_status(current_user)

class CollectDateRequest(BaseModel):
    count: int = 1

@router.post("/challenge/collect")
async def collect_date(request: CollectDateRequest, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(database.get_db)):
    success, message = daily_challenge.increment_dates(db, current_user, request.count)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"status": "success", "collected": current_user.dates_collected_today}

@router.get("/challenge/leaderboard")
async def get_challenge_leaderboard(db: Session = Depends(database.get_db)):
    return daily_challenge.get_daily_leaderboard(db)

