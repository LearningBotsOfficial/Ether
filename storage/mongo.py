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

from motor.motor_asyncio import AsyncIOMotorClient
from config.config import Config
from utils.logger import get_logger

logger = get_logger("EtherMongo")

# ============================================
# MongoDB Connection
# ============================================

class EtherMongo:
    
    def __init__(self):
        self.client: AsyncMongoClient = None
        self.db = None
    
    async def connect(self) -> bool:
        if not Config.MONGO_URI:
            logger.warning("Database: URI MISSING (Running without persistence)")
            return False
        
        try:
            self.client = AsyncMongoClient(
                Config.MONGO_URI,
                serverSelectionTimeoutMS=5000,
                retryWrites=True,
                maxPoolSize=50
            )
            
            # Verify connection
            await self.client.admin.command("ping")
            
            self.db = self.client[Config.DB_NAME]
            logger.info(f"Database: CONNECTED ({Config.DB_NAME})")
            
            # Initialize Indexes for Performance
            await self.ensure_indexes()
            
            return True
            
        except Exception as e:
            logger.error(f"Database: CONNECTION FAILED ({e})")
            self.client = None
            self.db = None
            return False

    async def ensure_indexes(self):
        """Creates indexes to ensure lightning-fast lookups."""
        if self.db is None:
            return
        try:
            # Autoreplies: Trigger lookup
            await self.db.autoreplies.create_index("trigger", unique=True)
            # Shortcuts: Name lookup
            await self.db.shortcuts.create_index("name", unique=True)
            # DM Shield: User ID lookup
            await self.db.dm_shield.create_index("user_id", unique=True)
            # Sessions: Name lookup (fast session bootstrap on startup)
            await self.db.sessions.create_index("name", unique=True)
            logger.info("Database: INDEXES SYNCHRONIZED")
        except Exception as e:
            logger.error(f"Database: INDEX ERROR ({e})")

    async def is_healthy(self) -> bool:
        """Runtime health check for the DB connection."""
        if not self.client:
            return False
        try:
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False
    
    async def close(self) -> None:
        if self.client:
            await self.client.close()
            logger.info("MongoDB connection closed")
    
    # Collection accessors
    @property
    def dm_users(self):
        return self.db["dm_users"] if self.db is not None else None
    
    @property
    def dm_config(self):
        return self.db["dm_config"] if self.db is not None else None
    
    @property
    def settings(self):
        return self.db["settings"] if self.db is not None else None
    
    @property
    def shortcuts(self):
        return self.db["shortcuts"] if self.db is not None else None


    @property
    def dm_shield(self):
        return self.db["dm_shield"] if self.db is not None else None

    @property
    def messages(self):
        return self.db["messages"] if self.db is not None else None

    @property
    def autoreplies(self):
        return self.db["autoreplies"] if self.db is not None else None

    @property
    def sessions(self):
        return self.db["sessions"] if self.db is not None else None

    async def get_session(self, name: str) -> str:
        """Retrieves a session string from DB."""
        if self.db is None: return None
        doc = await self.db.sessions.find_one({"name": name})
        return doc.get("session") if doc else None

    async def save_session(self, name: str, session: str):
        """Saves a session string to DB securely."""
        if self.db is None: return
        await self.db.sessions.update_one(
            {"name": name},
            {"$set": {"session": session}},
            upsert=True
        )
 
# Global instance
ether_db = EtherMongo()
