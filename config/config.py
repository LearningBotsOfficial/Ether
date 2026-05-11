# =============================================================================
#  Ether Userbot System
#
#  Project Name:  Ether
#  Author:        LearningBotsOfficial
#
#  Repository:    https://github.com/LearningBotsOfficial/Ether
#
#  Support:       https://t.me/Ether_Support
#  Channel:       https://t.me/Ether_Update
#
#  License:       Open Source (Keep Credits)
#
#  IMPORTANT:
#    • If you copy, fork, or reuse this project or any part of it,
#      you MUST retain original credits.
#    • Proper attribution to Ether project is required.
#
#  Thank you for respecting open-source development.
# =============================================================================

from dotenv import load_dotenv
import os

load_dotenv()


class Config:

    API_ID: int = int(os.getenv("API_ID", 0))
    API_HASH: str = os.getenv("API_HASH", "")
    OWNER_ID: int = int(os.getenv("OWNER_ID", 0))
    
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "")  # Auto-fetched if not set
    
    SESSION_NAME: str = os.getenv("SESSION_NAME", "etheruserbot")
    SESSION_DIR: str = os.getenv("SESSION_DIR", "sessions")

    MONGO_URI: str = os.getenv("MONGO_URI", "")
    DB_NAME: str = os.getenv("DB_NAME", "Ether")
    
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Dm Protection Settings
    DM_MAX_WARNS: int = int(os.getenv("DM_MAX_WARNS", "3"))
    
    # Web Service
    WEB_SERVICE: bool = os.getenv("WEB_SERVICE", "false").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8080"))
    
    @classmethod
    def validate(cls) -> None:
        missing = []
        
        if not cls.API_ID:
            missing.append("API_ID")
        if not cls.API_HASH:
            missing.append("API_HASH")
        if not cls.OWNER_ID:
            missing.append("OWNER_ID")
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )


# Validate on import
Config.validate()
