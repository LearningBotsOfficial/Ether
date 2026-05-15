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

from telethon import events, Button
from telethon.tl.functions.contacts import BlockRequest
import re

from services.dm_service import DMService
from utils.parser import parse_links
from utils.logger import get_logger
from config.config import Config
from core.bot import bot, WELCOME_DATA

logger = get_logger("EtherDM")

# ============================================
# Default Welcome Text
# ============================================

DEFAULT_WELCOME_TEXT = (
    "<blockquote>"
    "👋 <b>Welcome!</b>\n\n"
    "You have reached my private inbox. I am currently unavailable.\n\n"
    "<i>Please leave your message and I will get back to you as soon as possible.</i>\n\n"
    "🛡 <b>Protected by Ether</b>"
    "</blockquote>"
)

DEFAULT_WELCOME_IMAGE = "assets/ether_logo.png"

DEFAULT_WELCOME_BUTTONS = [
    [{"text": "Userbot Repo", "url": "https://github.com/LearningBotsOfficial/Ether", "type": "url"}]
]


def setup(ether, db, owner_id):
    
    dm_service = DMService(db)
    max_warns = Config.DM_MAX_WARNS
    
    async def load_welcome_data():
        try:
            welcome_config = await dm_service.get_welcome(owner_id)
            if welcome_config.get("text"):
                WELCOME_DATA["text"] = welcome_config["text"]
                WELCOME_DATA["image"] = welcome_config.get("image")
                WELCOME_DATA["buttons"] = welcome_config.get("buttons")
                WELCOME_DATA["media_type"] = welcome_config.get("media_type", "photo")
        except Exception as e:
            logger.error(f"Failed to load welcome data: {e}")
    
    from utils.task_helper import safe_run
    safe_run(load_welcome_data(), name="LoadWelcomeData")

# ============================================
# Allow Command
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.allow$", outgoing=True))
    async def allow_handler(event):
        if event.sender_id != owner_id:
            return
        
        if not event.is_private:
            await event.edit("<blockquote>❌ Use in private chat.</blockquote>")
            return
        
        user_id = event.chat_id
        await dm_service.allow_user(user_id)
        await event.edit(f"<blockquote>✅ User allowed.</blockquote>")
    
    @ether.on(events.NewMessage(pattern=r"^\.disallow$", outgoing=True))
    async def disallow_handler(event):
        if event.sender_id != owner_id:
            return
        
        if not event.is_private:
            await event.edit("<blockquote>❌ Use in private chat.</blockquote>")
            return
        
        user_id = event.chat_id
        await dm_service.disallow_user(user_id, owner_id)
        await event.edit(f"<blockquote>🚫 User disallowed.</blockquote>")
    

# ============================================
# Set Welcome Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.setwelcome$", outgoing=True))
    async def setwelcome_handler(event):
        if event.sender_id != owner_id:
            return
        
        if not event.is_reply:
            await event.reply(
                "<blockquote>"
                "⚠️ Reply to the message you want as welcome text.\n\n"
                "📝 <b>Supported Formatting:</b>\n"
                "• <b>Bold:</b> Use <code>**text**</code> or <code>__text__</code>\n"
                "• <i>Italic:</i> Use <code>__text__</code>\n"
                "• <code>Code:</code> Use <code>`text`</code>\n"
                "• Images (photos)\n\n"
                "📌 <b>Button Format:</b>\n"
                "<code>[Button.url('Button Text', 'https://example.com')]</code>\n"
                "💡 <b>Tip:</b> Include button code in your message text."
                "</blockquote>",
                
            )
            return
        
        msg = await event.get_reply_message()
        
        image_path = None
        media_type = "photo"
        if msg.photo:
            try:
                image_path = await msg.download_media(file="media/welcome.jpg")
                media_type = "photo"
            except Exception as e:
                logger.error(f"Failed to download welcome image: {e}")
        elif msg.video:
            try:
                image_path = await msg.download_media(file="media/welcome.mp4")
                media_type = "video"
            except Exception as e:
                logger.error(f"Failed to download welcome video: {e}")
        elif msg.gif:
            try:
                image_path = await msg.download_media(file="media/welcome.mp4")
                media_type = "gif"
            except Exception as e:
                logger.error(f"Failed to download welcome gif: {e}")
        elif msg.document and any(msg.document.mime_type.startswith(t) for t in ['image/', 'video/']):
            try:
                ext = ".jpg" if msg.document.mime_type.startswith('image/') else ".mp4"
                image_path = await msg.download_media(file=f"media/welcome{ext}")
                media_type = "photo" if ext == ".jpg" else "video"
            except Exception as e:
                logger.error(f"Failed to download welcome document: {e}")
        
        from telethon.extensions import html
        if msg.entities:
            parsed_text = html.unparse(msg.text, msg.entities)
        else:
            parsed_text = msg.text or ""
        
        parsed_text = re.sub(r'\[Button\.(url|inline)\([^\]]+\)\]', '', parsed_text).strip()
        
        buttons = None
        
        if msg.reply_markup:
            from telethon.tl.types import KeyboardButtonRow, KeyboardButtonUrl, KeyboardButtonCallback
            
            button_rows = []
            if hasattr(msg.reply_markup, 'rows'):
                for row in msg.reply_markup.rows:
                    row_buttons = []
                    for btn in row.buttons:
                        if isinstance(btn, KeyboardButtonUrl):
                            row_buttons.append({"text": btn.text, "url": btn.url, "type": "url"})
                        elif isinstance(btn, KeyboardButtonCallback):
                            row_buttons.append({"text": btn.text, "data": btn.data.decode(), "type": "callback"})
                    if row_buttons:
                        button_rows.append(row)
            
            if button_rows:
                buttons = button_rows
        
        if not buttons:
            text_content = msg.text or ""
            
            button_pattern = r"\[Button\.(url|inline)\(['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]\)\]"
            matches = re.findall(button_pattern, text_content)
            
            
            if matches:
                lines = text_content.split('\n')
                button_rows = []
                
                for line in lines:
                    line_buttons = []
                    line_matches = re.findall(button_pattern, line)
                    
                    for match in line_matches:
                        btn_type = match[0]
                        text = match[1]
                        value = match[2]
                        
                        if btn_type == 'url':
                            line_buttons.append({"text": text, "url": value, "type": "url"})
                        elif btn_type == 'inline':
                            if value.startswith('b') and len(value) > 1:
                                value = value[1:]
                            line_buttons.append({"text": text, "data": value, "type": "callback"})
                    
                    if line_buttons:
                        button_rows.append(line_buttons)
                
                if button_rows:
                    buttons = button_rows
        
        try:
            await dm_service.set_welcome(owner_id, parsed_text, image_path, buttons, media_type)
            
            WELCOME_DATA["text"] = parsed_text
            WELCOME_DATA["image"] = image_path
            WELCOME_DATA["buttons"] = buttons
            WELCOME_DATA["media_type"] = media_type
            
            response = "<blockquote>✅ Welcome message saved."
            if image_path:
                response += f"\n📷 {media_type.capitalize()} included."
            if buttons:
                response += f"\n🔘 {len(buttons)} button rows included."
            response += "</blockquote>"
            await event.edit(response)
        except Exception as e:
            logger.error(f"Failed to save welcome: {e}")
            await event.edit("<blockquote>❌ Failed to save welcome message.</blockquote>")
    

# ============================================
# Clear Welcome Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.clearwelcome$", outgoing=True))
    async def clearwelcome_handler(event):
        if event.sender_id != owner_id:
            return
        
        await dm_service.delete_welcome(owner_id)
        
        WELCOME_DATA["text"] = None
        WELCOME_DATA["image"] = None
        WELCOME_DATA["buttons"] = None
        WELCOME_DATA["media_type"] = "photo"
        
        await event.edit("🗑️ Welcome message cleared.")

    
    @ether.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def dm_handler(event):
        
        # 🔥 DEBUG LOG
        logger.info(f"DM PROTECTION CHECK FROM: {event.sender_id}")

        # Check if sender is a bot - skip all processing for bots
        if event.sender and event.sender.bot:
            return
        
        # Additional bot check using sender_id if sender object is not available
        try:
            sender = await event.get_sender()
            if sender and hasattr(sender, 'bot') and sender.bot:
                return
        except:
            pass

        if event.sender_id == owner_id:
            return
        
        if db is None:
            return
        
        user_id = event.sender_id
        
        user = await dm_service.get_user(user_id)
        welcome_config = await dm_service.get_welcome(owner_id)
        
        welcome_text = welcome_config.get("text") or DEFAULT_WELCOME_TEXT
        welcome_image = welcome_config.get("image") or DEFAULT_WELCOME_IMAGE
        welcome_buttons = welcome_config.get("buttons") or DEFAULT_WELCOME_BUTTONS
        welcome_media_type = welcome_config.get("media_type") or "photo"
        
        async def send_welcome(text: str) -> None:
            try:
                bot_username = Config.BOT_USERNAME
                if bot_username and welcome_buttons:
                    
                    WELCOME_DATA["text"] = text
                    WELCOME_DATA["buttons"] = welcome_buttons
                    WELCOME_DATA["image"] = welcome_image
                    WELCOME_DATA["media_type"] = welcome_media_type
                    
                    try:
                        results = await ether.inline_query(bot_username, "welcome")
                        
                        if results:
                            await results[0].click(event.chat_id)
                            return
                    except Exception as inline_err:
                        logger.error(f"Inline query failed: {inline_err}")
                if welcome_image:
                    await event.respond(file=welcome_image, message=text)
                else:
                    await event.respond(text)
            except Exception as e:
                logger.error(f"Failed to send welcome: {e}")
        
        if not user:
            await dm_service.create_user(user_id)
        else:
            if user.get("blocked"):
                try:
                    await ether(BlockRequest(user_id))
                except Exception as e:
                    logger.error(f"Block error for {user_id}: {e}")
                return
            
            if user.get("allowed"):
                await dm_service.increment_message_count(user_id)
                return

        # If they reach here, they are not allowed/blocked yet.
        # Send welcome message every time as requested.
        await send_welcome(welcome_text)
    
