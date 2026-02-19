import time
import threading
from sqlalchemy.orm import Session
from database import models
from database.database import SessionLocal
from libs import daily_challenge
import traceback

def monitor_loop():
    """
    Background thread loop.
    Checks user scores periodically and resets them if they failed the daily challenge.
    Also handles Daily Reset at 00:00.
    """
    print("Background Challenge Monitor: Started")
    
    # Initialize last checked date
    # Maldives is UTC+5
    from datetime import datetime, timedelta
    last_checked_date = (datetime.utcnow() + timedelta(hours=5)).date()
    
    while True:
        try:
            # Create a new session for this check
            db: Session = SessionLocal()
            try:
                # 1. Check for New Day (Midnight Reset)
                now_maldives = datetime.utcnow() + timedelta(hours=5)
                current_date = now_maldives.date()
                
                if current_date > last_checked_date:
                    print(f"Background Monitor: New Day Detected ({current_date}). Triggering reset...")
                    daily_challenge.reset_daily_collection(db)
                    last_checked_date = current_date
                
                # 2. Penalty Check (Existing Logic)
                # Query all users with a score > 0
                users = db.query(models.User).filter(models.User.score > 0).all()
                
                for user in users:
                    daily_challenge.check_and_apply_penalty(db, user)
                    
            except Exception as e:
                print(f"Background Monitor Error: {e}")
                traceback.print_exc()
            finally:
                db.close()
                
            # Wait for 60 seconds before next check
            time.sleep(60)
            
        except Exception as e:
            print(f"Critical Background Monitor Error: {e}")
            time.sleep(60) # Wait and retry

def start_challenge_monitor():
    """Starts the background monitor thread."""
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
