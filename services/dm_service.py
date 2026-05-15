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

from typing import Optional, Dict, Any, List

# ============================================
# DM Service Class
# ============================================

class DMService:
    
    def __init__(self, db):
        self.users = db["dm_users"] if db is not None else None
        self.config = db["dm_config"] if db is not None else None
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        if self.users is None:
            return None
        return await self.users.find_one({"user_id": user_id})
    
    async def create_user(self, user_id: int) -> None:
        if self.users is None:
            return
        
        existing = await self.get_user(user_id)
        if existing:
            return
        
        from config.config import Config
        await self.users.insert_one({
            "user_id": user_id,
            "allowed": False,
            "warns": 0,
            "max_warns": Config.DM_MAX_WARNS,
            "blocked": False,
            "message_count": 0
        })
    
    async def allow_user(self, user_id: int) -> None:
        if self.users is None:
            return
        
        await self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "allowed": True,
                    "warns": 0,
                    "blocked": False
                }
            },
            upsert=True
        )
    
    async def disallow_user(self, user_id: int, owner_id: int = None) -> None:
        if self.users is None:
            return
        
        max_warns = None
        if owner_id and self.config is not None:
            config = await self.config.find_one({"owner_id": owner_id})
            if config and config.get("max_warns"):
                max_warns = config["max_warns"]
        
        update_data = {
            "allowed": False,
            "warns": 0
        }
        
        if max_warns:
            update_data["max_warns"] = max_warns
        
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": update_data},
            upsert=True
        )
    
    async def increment_warn(self, user_id: int) -> int:
        if self.users is None:
            return 0
        
        result = await self.users.find_one_and_update(
            {"user_id": user_id},
            {"$inc": {"warns": 1}},
            upsert=True,
            return_document=True
        )
        return result.get("warns", 1) if result else 1
    
    async def set_global_max_warns(self, owner_id: int, max_warns: int) -> None:
        if self.config is None:
            return
        
        await self.config.update_one(
            {"owner_id": owner_id},
            {"$set": {"max_warns": max_warns}},
            upsert=True
        )
    
    async def get_max_warns(self, user_id: int, owner_id: int) -> int:
        if self.config is not None:
            config = await self.config.find_one({"owner_id": owner_id})
            if config and config.get("max_warns"):
                return config["max_warns"]
        
        from config.config import Config
        return Config.DM_MAX_WARNS
    
    async def block_user(self, user_id: int) -> None:
        if self.users is None:
            return
        
        await self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "blocked": True,
                    "allowed": False,
                    "unblock_at": None # Permanent
                }
            },
            upsert=True
        )

    async def temp_block_user(self, user_id: int, duration_secs: int) -> None:
        if self.users is None:
            return
        
        import time
        unblock_at = time.time() + duration_secs
        
        await self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "blocked": True,
                    "allowed": False,
                    "unblock_at": unblock_at
                }
            },
            upsert=True
        )
    
    async def increment_message_count(self, user_id: int) -> None:
        if self.users is None:
            return
        
        await self.users.update_one(
            {"user_id": user_id},
            {"$inc": {"message_count": 1}},
            upsert=True
        )
    
    async def get_welcome(self, owner_id: int) -> Dict[str, Any]:
        if self.config is None:
            return {"text": "", "image": None, "buttons": None, "media_type": None}
        
        result = await self.config.find_one({"owner_id": owner_id})
        return result or {"text": "", "image": None, "buttons": None, "media_type": None}
    
    async def set_welcome(self, owner_id: int, text: str, image: Optional[str] = None, buttons: Optional[List[Dict[str, str]]] = None, media_type: Optional[str] = None) -> None:
        if self.config is None:
            return
        
        data = {"text": text}
        if image:
            data["image"] = image
        else:
            data["image"] = None
            
        if buttons:
            data["buttons"] = buttons
        else:
            data["buttons"] = None
        
        if media_type:
            data["media_type"] = media_type
        else:
            data["media_type"] = "photo"
        
        await self.config.update_one(
            {"owner_id": owner_id},
            {"$set": data},
            upsert=True
        )
    
    async def delete_welcome(self, owner_id: int) -> None:
        if self.config is None:
            return
        
        await self.config.delete_one({"owner_id": owner_id})
