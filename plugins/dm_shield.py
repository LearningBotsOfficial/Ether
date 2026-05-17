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

from telethon import events
from utils.logger import get_logger
from services.dm_shield_service import DMShieldService
from services.dm_service import DMService
from config.config import Config

logger = get_logger("DMShield")


def setup(ether, db, owner_id):

    shield = DMShieldService(db)
    dm_service = DMService(db)
# ============================================
# Dm filter
# ============================================
    @ether.on(events.NewMessage(incoming=True))
    async def dm_filter(event):
    
        if not event.is_private:
            return
    
        if event.sender_id == owner_id:
            return

        # Skip bots
        if event.sender and getattr(event.sender, 'bot', False):
            return
        try:
            sender = await event.get_sender()
            if sender and getattr(sender, 'bot', False):
                return
        except Exception:
            pass
    
        settings = await shield.get(owner_id)
    
        # 🔥 DEBUG (remove later if needed)
        logger.info(f"DM CHECK FROM: {event.sender_id}")
        logger.info(f"SETTINGS: {settings}")
    
        if not settings.get("enabled"):
            return
    
        # Check if sender is in allowed list (whitelist) via DMService
        user = await dm_service.get_user(event.sender_id)
        if user and user.get("allowed"):
            logger.info(f"User {event.sender_id} is allowed, skipping filter")
            return

        # Block unauthorized media from unknown users
        if event.message.media and not (user and user.get("message_count", 0) > 2):
            try:
                await event.delete()
                logger.info(f"Shield: Deleted unauthorized media from {event.sender_id}")
            except Exception as e:
                logger.error(f"DM media delete failed: {e}")
            return
    
        text = event.raw_text or ""
    
        block = False
    
        if settings.get("link") and shield.has_link(text):
            block = True
    
        if settings.get("username") and shield.has_username(text):
            block = True
    
        if block:
            try:
                await event.delete()
                logger.info(f"Deleted DM from {event.sender_id}")
            except Exception as e:
                logger.error(f"DM delete failed: {e}")

# ============================================
# Shield Allow
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.shield allow$", outgoing=True))
    async def shield_allow(event):
    
        if event.sender_id != owner_id:
            return
    
        user_id = None
        if event.is_reply:
            reply = await event.get_reply_message()
            user_id = reply.sender_id
        elif event.is_private:
            user_id = event.chat_id
            
        if not user_id or user_id == owner_id:
            return
    
        user = await dm_service.get_user(user_id)
    
        if user and user.get("allowed"):
            await event.reply(f"<blockquote><b>Identity Status:</b> User {user_id} is already in the allowed list.</blockquote>")
            return
        
        await dm_service.allow_user(user_id)
    
        await event.reply(f"<blockquote><b>Access Granted:</b> User {user_id} is now ALLOWED in DM Shield</blockquote>")
    
# ============================================
# Shield Disallow
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.shield disallow$", outgoing=True))
    async def shield_disallow(event):
    
        if event.sender_id != owner_id:
            return
    
        user_id = None
        if event.is_reply:
            reply = await event.get_reply_message()
            user_id = reply.sender_id
        elif event.is_private:
            user_id = event.chat_id
            
        if not user_id or user_id == owner_id:
            return
    
        user = await dm_service.get_user(user_id)
    
        if not user or not user.get("allowed"):
            await event.reply(f"<blockquote><b>Identity Status:</b> User {user_id} is not in the allowed list.</blockquote>")
            return
        
        await dm_service.disallow_user(user_id, owner_id)
    
        await event.reply(f"<blockquote><b>Access Revoked:</b> User {user_id} is now REMOVED from allowed list</blockquote>")
    
    
# ============================================
# Shield Help
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.shield$", outgoing=True))
    async def shield_help(event):

        if event.sender_id != owner_id:
            return

        settings = await shield.get(owner_id)
        allowed = settings.get("allowed", [])

        msg = (
            "<blockquote>"
            "<b>DM Shield System</b>\n\n"
            "<b>Status:</b>\n"
            f"Shield: {'ON' if settings.get('enabled') else 'OFF'}\n"
            f"Links: {'ACTIVE' if settings.get('link') else 'INACTIVE'}\n"
            f"Usernames: {'ACTIVE' if settings.get('username') else 'INACTIVE'}\n"
            f"Allowed Users: {len(allowed)}\n\n"
            "<b>Commands:</b>\n"
            "<code>.shield on</code>\n"
            "<code>.shield off</code>\n"
            "<code>.shield allow</code>\n"
            "<code>.shield disallow</code>\n"
            "<code>.shield link</code>\n"
            "<code>.shield user</code>\n"
            "<code>.shield status</code>"
            "</blockquote>"
        )

        await event.reply(msg)

# ============================================
# Shield On
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.shield on$", outgoing=True))
    async def shield_on(event):

        if event.sender_id != owner_id:
            return

        settings = await shield.get(owner_id)
        settings["enabled"] = True
        await shield.save(owner_id, settings)

        await event.reply("<blockquote><b>DM Shield:</b> ENABLED</blockquote>")


# ============================================
# Shield Off
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.shield off$", outgoing=True))
    async def shield_off(event):

        if event.sender_id != owner_id:
            return

        settings = await shield.get(owner_id)
        settings["enabled"] = False
        await shield.save(owner_id, settings)

        await event.reply("<blockquote><b>DM Shield:</b> DISABLED</blockquote>")


# ============================================
# Shield Link
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.shield link$", outgoing=True))
    async def shield_link(event):

        if event.sender_id != owner_id:
            return

        settings = await shield.get(owner_id)
        settings["link"] = not settings.get("link", False)
        await shield.save(owner_id, settings)

        await event.reply(
            f"<blockquote><b>Link Filter:</b> {'ENABLED' if settings['link'] else 'DISABLED'}</blockquote>",
        )


# ============================================
# Shield User
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.shield user$", outgoing=True))
    async def shield_user(event):

        if event.sender_id != owner_id:
            return

        settings = await shield.get(owner_id)
        settings["username"] = not settings.get("username", False)
        await shield.save(owner_id, settings)

        await event.reply(
            f"<blockquote><b>Username Filter:</b> {'ENABLED' if settings['username'] else 'DISABLED'}</blockquote>",
        )


# ============================================
# Shield Status
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.shield status$", outgoing=True))
    async def shield_status(event):

        if event.sender_id != owner_id:
            return

        settings = await shield.get(owner_id)

        await event.reply(
            "<blockquote>"
            "<b>Shield Status</b>\n\n"
            f"Shield: {'ON' if settings.get('enabled') else 'OFF'}\n"
            f"Links: {'ACTIVE' if settings.get('link') else 'INACTIVE'}\n"
            f"Usernames: {'ACTIVE' if settings.get('username') else 'INACTIVE'}"
            "</blockquote>",
        )
