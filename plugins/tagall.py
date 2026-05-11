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

from telethon import events, errors
import asyncio
import random
from utils.logger import get_logger

logger = get_logger("EtherTagAll")

# Process tracking is now handled via MongoDB

GM_GREETINGS = [
    "Good Morning! Have a blessed day.",
    "Subah bakhair! Kaise hain aap?",
    "Morning! Chai nasta hua?",
    "Good Morning! Hope you slept well.",
    "Rise and shine! Utho jaldi.",
    "Assalam-o-Alaikum, Good Morning!",
    "Good morning! Aaj ka kya plan hai?",
    "Have a productive morning!",
    "Subha ho gayi! Have a great one.",
    "Good Morning Ji! Sab thik?"
]

GN_GREETINGS = [
    "Good Night! Sleep tight.",
    "Shab bakhair! Milte hain kal.",
    "Good Night! Sweet dreams.",
    "So jao, thak gaye hoge aaj.",
    "Good night! Subah jaldi uthna hai.",
    "Allah Hafiz, Good Night!",
    "Nighty night! Take rest.",
    "You did well today, Good Night!",
    "Kal milte hain, so jao ab.",
    "Good Night Ji! Khayal rakhiyega."
]

def setup(ether, db, owner_id):

    BATCH_SIZE = 1          # 1 user per message
    DELAY = 1.5             # slight adjustment for single tags
    
    # MongoDB collection for process tracking
    if db is not None:
        tag_col = db["tag_tasks"]

# ============================================
# Universal Tag Handler
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.(tagall|gmtag|gntag|tagstop)(?:(?:\s+)(.+))?$", outgoing=True))
    async def universal_tag_handler(event):
        if event.sender_id != owner_id:
            return
        
        if not event.is_group:
            await event.edit("<blockquote><b>Command Error:</b> This command works only in groups.</blockquote>")
            return

        cmd = event.pattern_match.group(1).lower()
        arg = event.pattern_match.group(2)
        chat_id = event.chat_id
        
        # Check for stop command
        if cmd == "tagstop" or (arg and arg.lower() == "stop"):
            await tag_col.update_one({"chat_id": chat_id}, {"$set": {"active": False}})
            msg = "Tagging Process" if cmd == "tagstop" else cmd.capitalize()
            await event.edit(f"<blockquote><b>Action Success:</b> {msg} has been terminated.</blockquote>")
            return

        # Determine mode
        use_random = not bool(arg)
        if cmd == "gmtag":
            label = "Morning Tag"
            message = arg
        elif cmd == "gntag":
            label = "Night Tag"
            message = arg
        else:
            label = "TagAll"
            message = arg or "Hey everyone!"
            use_random = False
        
        # Check active status in DB
        current = await tag_col.find_one({"chat_id": chat_id})
        if current and current.get("active"):
            await event.edit(f"<blockquote><b>Process Error:</b> A tagging process is already running.</blockquote>")
            return

        await event.delete()
        status_msg = await ether.send_message(
            chat_id, 
            f"<blockquote><b>Starting {label}...</b>\n<i>Use <code>.{cmd} stop</code> to cancel.</i></blockquote>"
        )
        
        # Set active in DB
        await tag_col.update_one({"chat_id": chat_id}, {"$set": {"active": True}}, upsert=True)
        
        try:
            users = []
            async for user in ether.iter_participants(chat_id):
                if user.bot or user.deleted:
                    continue
                users.append(user)
            
            if not users:
                await status_msg.edit("<blockquote><b>Process Error:</b> No eligible users found.</blockquote>")
                return

            total = len(users)
            sent = 0
            
            for i in range(0, total, BATCH_SIZE):
                # Check DB for cancellation
                current_status = await tag_col.find_one({"chat_id": chat_id})
                if not current_status or not current_status.get("active"):
                    break
                
                batch = users[i:i + BATCH_SIZE]
                
                if use_random:
                    greetings = GM_GREETINGS if cmd == "gmtag" else GN_GREETINGS
                    greeting = random.choice(greetings)
                    user = batch[0]
                    name = user.first_name or "User"
                    tag_text = f"{greeting} <a href='tg://user?id={user.id}'>{name}</a>"
                else:
                    user = batch[0]
                    name = user.first_name or "User"
                    tag_text = f"{message} <a href='tg://user?id={user.id}'>{name}</a>"
                
                try:
                    await ether.send_message(chat_id, tag_text)
                    sent += len(batch)
                except errors.FloodWaitError as e:
                    logger.warning(f"FloodWait: Sleeping for {e.seconds}s")
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    logger.error(f"Tag error: {e}")
                
                await asyncio.sleep(DELAY)
            
            result_text = f"<blockquote><b>{label} Completed</b>\nTagged: {sent} users</blockquote>"
            
            # Check if it was stopped
            final_status = await tag_col.find_one({"chat_id": chat_id})
            if not final_status or not final_status.get("active"):
                result_text = f"<blockquote><b>{label} Stopped</b>\nTagged: {sent} users</blockquote>"
            
            await ether.send_message(chat_id, result_text)
            
        finally:
            await tag_col.update_one({"chat_id": chat_id}, {"$set": {"active": False}})
            try:
                await status_msg.delete()
            except:
                pass

    logger.info("Enhanced TagAll plugin loaded")
