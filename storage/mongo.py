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

from pymongo import AsyncMongoClient
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
            logger.warning("MongoDB URI not configured, running without DB")
            return False
        
        try:
            self.client = AsyncMongoClient(
                Config.MONGO_URI,
                serverSelectionTimeoutMS=5000
            )
            
            # Verify connection
            await self.client.admin.command("ping")
            
            self.db = self.client[Config.DB_NAME]
            logger.info(f"Connected to MongoDB ({Config.DB_NAME})")
            return True
            
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            return False
    
    async def close(self) -> None:
        if self.client:
            await self.client.close()
            logger.info("MongoDB connection closed")
    
    # Collection accessors
    @property
    def dm_users(self):
        return self.db["dm_users"] if self.db else None
    
    @property
    def dm_config(self):
        return self.db["dm_config"] if self.db else None
    
    @property
    def settings(self):
        return self.db["settings"] if self.db else None
    
    @property
    def shortcuts(self):
        return self.db["shortcuts"] if self.db else None


    @property
    def dm_shield(self):
        return self.db["dm_shield"] if self.db else None
 
# Global instance
ether_db = EtherMongo()