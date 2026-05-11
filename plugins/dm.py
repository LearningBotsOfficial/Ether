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
    "👋 Hello!\n\n"
    "You've just reached Ether Userbot ⚡️\n\n"
    "This DM is protected to prevent spam and unwanted messages.\n\n"
    "⭐️ What you can do:\n\n"
    "• Wait for approval\n"
    "• Use buttons below for support\n\n"
    "🕔 You'll be reviewed soon. Stay patient."
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
        except Exception as e:
            logger.error(f"Failed to load welcome data: {e}")
    
    import asyncio
    asyncio.create_task(load_welcome_data())

# ============================================
# Allow Command
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.allow$", outgoing=True))
    async def allow_handler(event):
        if event.sender_id != owner_id:
            return
        
        if not event.is_private:
            await event.edit("<blockquote>❌ Use in private chat.</blockquote>", parse_mode="html")
            return
        
        user_id = event.chat_id
        await dm_service.allow_user(user_id)
        await event.edit(f"✅ User allowed.")
    
    @ether.on(events.NewMessage(pattern=r"^\.disallow$", outgoing=True))
    async def disallow_handler(event):
        if event.sender_id != owner_id:
            return
        
        if not event.is_private:
            await event.edit("<blockquote>❌ Use in private chat.</blockquote>", parse_mode="html")
            return
        
        user_id = event.chat_id
        await dm_service.disallow_user(user_id, owner_id)
        await event.edit(f"🚫 User disallowed.")
    

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
                parse_mode="html"
            )
            return
        
        msg = await event.get_reply_message()
        
        image_path = None
        if msg.photo:
            try:
                image_path = await msg.download_media(file="media/welcome.jpg")
            except Exception as e:
                logger.error(f"Failed to download welcome image: {e}")
        
        raw_text = msg.text or ""
        parsed_text = parse_links(raw_text)
        
        parsed_text = re.sub(r'\[Button\.(url|inline)\([^\]]+\)\]', '', parsed_text).strip()
        
        parsed_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', parsed_text)
        parsed_text = re.sub(r'__(.+?)__', r'<i>\1</i>', parsed_text)
        parsed_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', parsed_text)
        
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
            await dm_service.set_welcome(owner_id, parsed_text, image_path, buttons)
            
            WELCOME_DATA["text"] = parsed_text
            WELCOME_DATA["image"] = image_path
            WELCOME_DATA["buttons"] = buttons
            
            response = "✅ Welcome message saved."
            if image_path:
                response += "\n📷 Image included."
            if buttons:
                response += f"\n🔘 {len(buttons)} button rows included."
            await event.edit(response)
        except Exception as e:
            logger.error(f"Failed to save welcome: {e}")
            await event.edit("<blockquote>❌ Failed to save welcome message.</blockquote>", parse_mode="html")
    

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
        
        await event.edit("🗑️ Welcome message cleared.")

# ============================================
# Set Warn Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.setwarn (\d+)$", outgoing=True))
    async def setwarn_handler(event):
        if event.sender_id != owner_id:
            return
        
        max_warns = int(event.pattern_match.group(1))
        
        await dm_service.set_global_max_warns(owner_id, max_warns)
        await event.edit(f"<blockquote>⚠️ Global max warnings set to {max_warns}.</blockquote>", parse_mode="html")
    
    @ether.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def dm_handler(event):

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
        
        async def send_welcome(text: str) -> None:
            try:
                bot_username = Config.BOT_USERNAME
                if bot_username and welcome_buttons:
                    
                    WELCOME_DATA["text"] = text
                    WELCOME_DATA["buttons"] = welcome_buttons
                    
                    try:
                        results = await ether.inline_query(bot_username, "welcome")
                        
                        if results:
                            await results[0].click(event.chat_id)
                            return
                    except Exception as inline_err:
                        logger.error(f"Inline query failed: {inline_err}")
                if welcome_image:
                    await event.respond(file=welcome_image, message=text, parse_mode="html")
                else:
                    await event.respond(text, parse_mode="html")
            except Exception as e:
                logger.error(f"Failed to send welcome: {e}")
        
        if not user:
            await dm_service.create_user(user_id)
            await send_welcome(welcome_text)
            return
        
        if user.get("blocked"):
            try:
                await event.reply("<blockquote>⛔ You are blocked from contacting this user.</blockquote>", parse_mode="html")
                await ether(BlockRequest(user_id))
            except Exception as e:
                logger.error(f"Block error for {user_id}: {e}")
            return
        
        if user.get("allowed"):
            await dm_service.increment_message_count(user_id)
            return
        
        warns = await dm_service.increment_warn(user_id)
        user_max_warns = await dm_service.get_max_warns(user_id, owner_id)
        
        if warns >= user_max_warns:
            await dm_service.block_user(user_id)
            
            try:
                await send_welcome(f"{welcome_text}\n\n⛔ <b>You have been blocked after {warns} warnings.</b>")
                await ether(BlockRequest(user_id))
            except Exception as e:
                logger.error(f"Auto-block failed for {user_id}: {e}")
        else:
            await send_welcome(f"{welcome_text}\n\n⚠️ <b>Warning {warns}/{user_max_warns}</b>\n<i>Continued messaging will result in a block.</i>")
    
