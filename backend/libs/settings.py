import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "Dash Multiplayer Backend"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3000
    
    # Zitadel OAuth
    ZITADEL_BASE_URL: str = os.getenv("ZITADEL_BASE_URL", "https://login.example.com") # Default or example
    ZITADEL_CLIENT_ID: str = os.getenv("ZITADEL_CLIENT_ID", "")
    ZITADEL_CLIENT_SECRET: str = os.getenv("ZITADEL_CLIENT_SECRET", "")
    ZITADEL_REDIRECT_URI: str = os.getenv("ZITADEL_REDIRECT_URI", "http://localhost:5173") # Frontend callback
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        origin.strip() for origin in os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",") if origin.strip()
    ]
    
    
    
    # Game Config
    LEADERBOARD_LIMIT: int = int(os.getenv("LEADERBOARD_LIMIT", 10))

    # Daily Challenge Config
    DATES_MIN_TARGET: int = int(os.getenv("DATES_MIN_TARGET", 10))
    DATES_MAX_TARGET: int = int(os.getenv("DATES_MAX_TARGET", 100))
    DATES_START_HOUR: int = int(os.getenv("DATES_START_HOUR", 1))
    DATES_END_HOUR: int = int(os.getenv("DATES_END_HOUR", 24))
    
    GAME_CONFIG: dict = {
        "world": {
            "tileLength": 30,
            "seed": "default_seed", # Will be overwritten/generated
            "numTiles": 12,
            "roadScale": [1.5, 3, 6],
            "roadRotation": [0, 1.57079632679, 0], # Math.PI / 2
            "fog": {
                "color": "#000816",
                "near": 30,
                "far": 300
            },
            "curvature": -0.0003,
            "sky": {
                "dynamic": False,
                "defaultTime": 13,
                "day": {
                    "fog": "#87ceeb",
                    "ambient": "#99ccff",
                    "directional": "#fff5e6",
                    "intensity": 2.0
                },
                "sunset": {
                    "fog": "#ff7b39",
                    "ambient": "#4a4a8a",
                    "directional": "#ffaa33",
                    "intensity": 3.0
                },
                "night": {
                    "fog": "#000816",
                    "ambient": "#151530",
                    "directional": "#88aaff",
                    "intensity": 0.8
                }
            },
            "sidewalk": {
                "width": 200,
                "height": 1,
                "offset": 57.5,
                "segments": 50,
                "color": {
                    "city": "#ffffff",
                    "nature": "#7eff3d",
                    "bridge": "#00ffff"
                }
            },
            "ground": {
                "width": 1000,
                "height": 40,
                "yOffset": -35.5,
                "segments": 40,
                "color": {
                    "city": "#ffffff",
                    "nature": "#7eff3d",
                    "bridge": "#00ffff"
                }
            }
        },
        "zones": {
            "segmentLength": 40,
            "sequence": ["city", "suburbs", "industrial", "bridge", "nature"],
            "zoneTransitionGap": 5,
            "bridge": {
                "waterColor": "#00ffff",
                "boats": {
                    "density": 0.05,
                    "offset": 15,
                    "offsetVariance": 16,
                    "scale": {"min": 1, "max": 2},
                    "yOffset": -0.8,
                    "bobbing": {
                        "amplitude": 0.15,
                        "speed": 1.5
                    }
                }
            },
            "nature": {
                "scale": {"min": 10, "max": 12},
                "density": 0.8,
                "offsetVariance": 15
            }
        },
        "lanes": {
            "width": 4.5,
            "maxLanes": 3
        },
        "player": {
            "scale": 2.2,
            "speed": {
                "initial": 20,
                "increment": 0.5,
                "max": 50
            },
            "initialLane": 2, # Center lane for 3 lanes (1-based: 1, 2, 3)
            "laneChangeSpeed": 10,
            "bankingIntensity": 0.2,
            "jumpHeight": 0,
            "camera": {
                "position": [0, 15, 27],
                "fov": 70,
                "lookAt": [0, 0, -10]
            },
            "hitbox": {"width": 4, "height": 2, "depth": 4},
            "nitro": {
                "duration": 5000,
                "speedBoost": 50,
                "flyHeight": 5,
                "flySpeed": 500,
                "tiltNitro": 0.1,
                "tiltEnding": -0.15,
                "watermelonThreshold": 5
            },
            "scoreMultiplier": 0.2
        },
        "buildings": {
            "offset": 30,
            "scale": {"min": 12, "max": 22},
            "spawnChance": 1.0
        },
        "lights": {
            "offset": 8,
            "scale": 10,
            "spawnChance": 0.3,
            "spawnInterval": 100,
            "rotation": [0, 3.14159, 0] # Math.PI
        },
        "obstacles": {
            "scale": 2.2,
            "spawnDistance": -250,
            "rotation": [0, 3.14159, 0],
            "hitbox": {"width": 4, "height": 2, "depth": 4},
            "proximitySoundDistance": 6,
            "spawn": {
                "initialDelay": 2500,
                "minDelay": 1000,
                "decreaseFactor": 40
            }
        },
        "collectibles": {
            "scale": 3,
            "hitbox": {"width": 3, "height": 3, "depth": 3},
            "spawnDistance": -250,
            "spawn": {
                "interval": 1000,
                "chance": 0.1
            },
            "points": 100
        },
        "dates": {
            "scale": 3,
            "hitbox": {"width": 2, "height": 2, "depth": 2},
            "spawnDistance": -250,
            "spawn": {
                "interval": 800,
                "chance": 0.15
            },
            "points": 50,
            "target": 10,
            "startHour": DATES_START_HOUR,
            "endHour": DATES_END_HOUR
        },
        "menus": {
            "start": {
                "camera": {
                    "position": [6, 1.2, 0],
                    "lookAt": [0, 0.8, 0],
                    "fov": 45
                },
                "car": {
                    "position": [0, 0, 1.5],
                    "rotation": [0, -1.570796, 0]
                },
                "character": {
                    "position": [0, 0, 1.5],
                    "rotation": [0, 0.523599, 0],
                    "scale": 1.9
                }
            },
            "gameover": {
                "groupOffset": [0, 0, 5],
                "car": {
                    "position": [0, 0.5, -2],
                    "rotation": [0.392699, 3.92699, 0.261799]
                },
                "character": {
                    "position": [2, 0, -2],
                    "rotation": [0, -0.785398, 0],
                    "scale": 2
                }
            }
        },
        "development": {
            "collisionEnabled": True,
            "devMode": False,
            "showHitboxes": False
        }
    }

settings = Settings()
