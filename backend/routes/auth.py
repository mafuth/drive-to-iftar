from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import database, models
from libs import security
from libs.settings import settings
from pydantic import BaseModel
import httpx
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

class ZitadelLoginRequest(BaseModel):
    code: str

class UserResponse(BaseModel):
    id: int
    username: str | None
    email: str | None
    profile_photo: str | None
    score: int
    access_token: str
    is_guest: bool
    rank: int | None = None

def get_user_rank(db: Session, user_id: int, score: int) -> int:
    # Rank is 1 + count of *non-guest* users with strictly higher score
    higher_scores = db.query(models.User).filter(
        models.User.score > score,
        models.User.is_guest == False
    ).count()
    return higher_scores + 1

class UsernameUpdateRequest(BaseModel):
    username: str

@router.post("/guest", response_model=UserResponse)
async def guest_login(db: Session = Depends(database.get_db)):
    # Create a unique guest user
    guest_uuid = str(uuid.uuid4())[:8]
    username = f"Guest_{guest_uuid}"
    
    user = models.User(
        email=None,
        username=username,
        is_guest=True,
        profile_photo=None
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token = security.create_access_token(data={"sub": str(user.id)})
    
    # Guest rank is roughly based on 0 score, but let's calculate it accurately
    # rank = get_user_rank(db, user.id, user.score) 
    # User requested no rank for guests
    
    return {
        "id": user.id,
        "username": f"{user.username}#{user.id}",
        "email": None,
        "profile_photo": None,
        "score": 0,
        "access_token": access_token,
        "is_guest": True,
        "rank": None
    }

@router.post("/zitadel", response_model=UserResponse)
async def zitadel_login(request: ZitadelLoginRequest, db: Session = Depends(database.get_db)):
    # Exchange code for token
    token_url = f"{settings.ZITADEL_BASE_URL}/oauth/v2/token"
    data = {
        "code": request.code,
        "client_id": settings.ZITADEL_CLIENT_ID,
        "client_secret": settings.ZITADEL_CLIENT_SECRET,
        "redirect_uri": settings.ZITADEL_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        if response.status_code != 200:
             print(f"Token Exchange Failed: {response.text}")
             raise HTTPException(status_code=400, detail="Invalid Zitadel Code")
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        # Get User Info
        user_info_url = f"{settings.ZITADEL_BASE_URL}/oidc/v1/userinfo"
        user_info_response = await client.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"})
        if user_info_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        user_info = user_info_response.json()
        
        # Zitadel UserInfo fields
        print(f"DEBUG: Zitadel UserInfo: {user_info}")
        
        email = user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Identity provider did not return an email address.")
            
        zitadel_id = user_info.get("sub")
        picture = user_info.get("picture")
        
        # Try to find a username
        # Reference: username=user_info.get('preferred_username', user_info['email'].split('@')[0])
        username_claim = user_info.get("preferred_username")
        if not username_claim:
             username_claim = email.split("@")[0]
             
        # Check if user exists
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user:
            # Create new user
            user = models.User(
                email=email,
                oauth_id=zitadel_id,
                profile_photo=picture,
                username=username_claim,
                is_guest=False
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"DEBUG: Created new user {user.username} ({user.email})")
        else:
            # Update profile photo and ensuring consistency
            updated = False
            if user.profile_photo != picture and picture:
                user.profile_photo = picture
                updated = True
            
            # Update username if it was missing? 
            # Ideally we don't overwrite if they changed it, but if it's null we should.
            if not user.username:
                user.username = username_claim
                updated = True
                
            if updated:
                db.commit()
                db.refresh(user)
            print(f"DEBUG: Logged in existing user {user.username} ({user.email})")
        
        # Create JWT
        access_token = security.create_access_token(data={"sub": str(user.id)})
        
        rank = get_user_rank(db, user.id, user.score)
        
        return {
            "id": user.id,
            "username": f"{user.username}#{user.id}",
            "email": user.email,
            "profile_photo": user.profile_photo,
            "score": user.score,
            "access_token": access_token,
            "is_guest": user.is_guest,
            "rank": rank
        }

@router.put("/username", response_model=UserResponse)
async def update_username(request: UsernameUpdateRequest, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(database.get_db)):
    if current_user.username and not current_user.is_guest:
        raise HTTPException(status_code=400, detail="Username already set")
    
    # Uniqueness check removed to allow duplicate usernames
    # existing = db.query(models.User).filter(models.User.username == request.username).first()
    # if existing:
    #     raise HTTPException(status_code=400, detail="Username taken")
        
    current_user.username = request.username
    db.commit()
    db.refresh(current_user)
    
    # Re-issue token? Not strictly necessary if token checks ID.
    access_token = security.create_access_token(data={"sub": str(current_user.id)})

    rank = get_user_rank(db, current_user.id, current_user.score)

    return {
        "id": current_user.id,
        "username": f"{current_user.username}#{current_user.id}",
        "email": current_user.email,
        "profile_photo": current_user.profile_photo,
        "score": current_user.score,
        "access_token": access_token,
        "is_guest": current_user.is_guest,
        "rank": rank
    }

@router.get("/config")
async def get_auth_config():
    return {
        "issuer": settings.ZITADEL_BASE_URL,
        "client_id": settings.ZITADEL_CLIENT_ID,
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: models.User = Depends(security.get_current_user), db: Session = Depends(database.get_db)):
    rank = None
    if not current_user.is_guest:
        rank = get_user_rank(db, current_user.id, current_user.score)
        
    return {
            "id": current_user.id,
            "username": f"{current_user.username}#{current_user.id}",
            "email": current_user.email,
            "profile_photo": current_user.profile_photo,
            "score": current_user.score,
            "access_token": "", # Not needed for verification check endpoint usually
            "is_guest": current_user.is_guest,
            "rank": rank
        }
