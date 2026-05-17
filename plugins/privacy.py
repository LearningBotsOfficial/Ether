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

from telethon import events, functions, Button
from utils.logger import get_logger
from config.config import Config
from core.bot import send_log
from services.dm_service import DMService
from services.dm_shield_service import DMShieldService
import time
import asyncio

logger = get_logger("PrivacyPlugin")


def setup(ether, db, owner_id):

    dm_service = DMService(db)
    shield_service = DMShieldService(db)


    # 2. Advanced Anti-Spam System (Moved to dm_shield.py)

    # 3. Privacy Commands

    # 4. Background Unblocker Task
    async def unblock_task():
        """Periodically checks and unblocks users whose temp ban expired."""
        if db is None:
            return
            
        while True:
            try:
                now = time.time()
                # Find users where unblock_at is in the past
                expired_users = db.dm_users.find({"blocked": True, "unblock_at": {"$lte": now, "$ne": None}})
                
                async for user in expired_users:
                    uid = user["user_id"]
                    try:
                        await ether(functions.contacts.UnblockRequest(id=uid))
                        await db.dm_users.update_one({"user_id": uid}, {"$set": {"blocked": False, "unblock_at": None}})
                        logger.info(f"UnblockTask: Automatically unblocked user {uid}")
                        await send_log(f"<blockquote><b>SYSTEM LOG: Auto-Unblock</b>\n\nUser <code>{uid}</code> has been restored after temporary ban.</blockquote>")
                    except Exception as ue:
                        logger.error(f"UnblockTask error for {uid}: {ue}")
                
            except Exception as e:
                logger.error(f"UnblockTask general error: {e}")
            
            await asyncio.sleep(300) # Check every 5 minutes

    from utils.task_helper import safe_run
    safe_run(unblock_task(), name="AutoUnblocker")

    logger.info("Privacy plugin loaded (Temp-ban active)")
