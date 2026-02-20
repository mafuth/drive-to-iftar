from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from database import models
from libs.settings import settings

# Challenge Window: Configurable
CHALLENGE_START_HOUR = settings.DATES_START_HOUR
CHALLENGE_END_HOUR = settings.DATES_END_HOUR

def get_today_challenge_date() -> str | None:
    """Returns YYYY-MM-DD if current time is within 05:00 - 18:00 window."""
    # Maldives is UTC+5
    now = datetime.utcnow() + timedelta(hours=5)
    if CHALLENGE_START_HOUR <= now.hour < CHALLENGE_END_HOUR:
        return now.strftime("%Y-%m-%d")
    return None

from libs.settings import settings

def get_daily_target(date_str: str, user_score: int = 0) -> int:
    """
    Returns deterministic random target for the given date, scaled by user score.
    Base target is random between MIN and MAX.
    Difficulty modifier: +1 target for every 5000 points of score.
    """
    seed = f"daily_dates_{date_str}"
    rng = random.Random(seed)
    
    base_target = rng.randint(settings.DATES_MIN_TARGET, settings.DATES_MAX_TARGET)
    
    # Scale based on score (Higher score = Harder challenge)
    # Example: 10,000 score -> +2 dates
    difficulty_mod = user_score // 5000
    
    final_target = base_target + difficulty_mod
    
    # Optional: Cap it at some reasonable upper limit if needed, or let it grow indefinitely?
    # User asked for "random amount ... each user gets different amounts ... higher score more they have to collect"
    # The RNG seed is date-based, so all users get same BASE target.
    # But difficulty_mod makes it different per user.
    
    return final_target

def check_and_apply_penalty(db: Session, user: models.User):
    """
    Checks if user failed the previous valid challenge day.
    If so, resets score to 0.
    Should be called on login/session validation.
    """
    # Maldives is UTC+5
    now = datetime.utcnow() + timedelta(hours=5)
    
    # Determine the 'last completed challenge day' that implies a check
    # If now < 5AM, then yesterday's window is closed and should be checked.
    # If now >= 18PM, then today's window is closed and should be checked.
    # If now is inside window, we can't check TODAY yet, but we must have passed YESTERDAY.
    
    if now.hour < CHALLENGE_START_HOUR:
        # Before window opens, verify yesterday
        check_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    elif now.hour >= CHALLENGE_END_HOUR:
        # After window closes, verify today
        check_date = now.strftime("%Y-%m-%d")
    else:
        # During window, verify yesterday (since today is still ongoing)
        check_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    # If user has no history, new user, no penalty.
    if not user.last_challenge_date:
        return

    # If user's last attempt is strictly older than check_date, they missed the check_date entirely.
    if user.last_challenge_date < check_date:
        reset_score(db, user)
        # Advance last_challenge_date to prevent repeated resets for the same miss?
        # Actually, if they log in multiple times, we don't want to keep resetting if they score 0.
        # But score becomes 0, so resetting 0 to 0 is fine.
        return

    # If user played on check_date, did they meet the target?
    # If user played on check_date, did they meet the target?
    if user.last_challenge_date == check_date:
        today_str = now.strftime("%Y-%m-%d")
        
        # Only check if data is reliable:
        # 1. Checking TODAY (Window closed evening check) -> Data intact.
        # 2. Checking YESTERDAY but dates > 0 -> Server missed midnight wipe, data intact.
        # If Checking YESTERDAY and dates == 0 -> Assume Midnight Wipe handled it. Skip.
        
        should_check = False
        if check_date == today_str:
            should_check = True
        elif user.dates_collected_today > 0:
            should_check = True
            
        if should_check:
            target = get_daily_target(check_date, user.score)
            if user.dates_collected_today < target:
                reset_score(db, user)

def reset_score(db: Session, user: models.User):
    if user.score > 0:
        print(f"Applying penalty to {user.username}: Score reset from {user.score} to 0")
        user.score = 0
        db.commit()

def increment_dates(db: Session, user: models.User, count: int = 1):
    """Increments dates collected if window is open."""
    today = get_today_challenge_date()
    if not today:
        return False, "Challenge window closed (5AM - 6PM)"

    if user.last_challenge_date != today:
        # Initialize for new day
        user.dates_collected_today = 0
        user.last_challenge_date = today
    
    user.dates_collected_today += count
    db.commit()
    user.dates_collected_today += count
    db.commit()
    return True, "Date collected"

def reset_daily_collection(db: Session):
    """Resets dates_collected_today to 0 for ALL users. Called at midnight."""
    print("Background Monitor: Running daily reset and penalty check...")
    
    # 1. Identify "Yesterday" (The day that just ended)
    # 1 second ago it was yesterday.
    now_mvt = datetime.utcnow() + timedelta(hours=5)
    yesterday_str = (now_mvt - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 2. Check players who played yesterday but failed
    # We only care about users whose last_challenge_date WAS yesterday.
    # If it was older, they are handled by "missed day" logic on login.
    users_played_yesterday = db.query(models.User).filter(
        models.User.last_challenge_date == yesterday_str
    ).all()

    for user in users_played_yesterday:
        target = get_daily_target(yesterday_str, user.score)
        if user.dates_collected_today < target:
             print(f"Midnight Check: {user.username} failed challenge ({user.dates_collected_today}/{target}). Resetting score.")
             user.score = 0
    
    db.commit()

    # 3. Wipe daily collection for EVERYONE
    db.query(models.User).update({models.User.dates_collected_today: 0})
    db.commit()

def get_status(user: models.User):
    today = get_today_challenge_date()
    
    # If window is closed, show info for "Next" or "Results"?
    # If closed, is_active = False.
    
    target = 0
    collected = 0
    
    if today:
        target = get_daily_target(today, user.score)
        if user.last_challenge_date == today:
            collected = user.dates_collected_today
        else:
            collected = 0
        active = True
    else:
        # Show specific message? 
        # For now just inactive.
        active = False
        
    return {
        "active": active,
        "target": target,
        "collected": collected,
        "window": f"{CHALLENGE_START_HOUR:02d}:00 - {CHALLENGE_END_HOUR:02d}:00"
    }

def get_daily_leaderboard(db: Session, limit: int = 3):
    today = get_today_challenge_date()
    if not today:
        # If window is closed, show leaderboard for TODAY (results so far)
        # Or if "closed" means "night before next day", we still show results for the day that just passed?
        # Logic: get_today_challenge_date returns None if outside window. 
        # But we still want to see the leaderboard for the "active" or "just finished" day.
        
        # Simple fallback: use current date (even if outside window)
        now = datetime.utcnow() + timedelta(hours=5)
        today = now.strftime("%Y-%m-%d")
        
    # Query users who have collected dates today, ordered by count desc
    results = db.query(models.User).filter(
        models.User.last_challenge_date == today,
        models.User.dates_collected_today > 0
    ).order_by(models.User.dates_collected_today.desc()).limit(limit).all()
    
    return [
        {
            "username": f"{u.username}#{u.id}" if u.username else f"User #{u.id}",
            "dates": u.dates_collected_today,
            "photo": u.profile_photo
        }
        for u in results
    ]
