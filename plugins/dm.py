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

import re
import os

from telethon import events, Button
from telethon.extensions import html
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.types import (
    DocumentAttributeAnimated,
    KeyboardButtonUrl,
    KeyboardButtonCallback,
)

from services.dm_service import DMService
from utils.parser import parse_links
from utils.logger import get_logger
from config.config import Config
from core.bot import bot, WELCOME_DATA

logger = get_logger("EtherDM")

# ============================================
# Markdown → HTML Converter
# ============================================

def md_to_html(text: str) -> str:
    """Convert Telegram-style Markdown to HTML for storage and rendering.
    Supports: > blockquote, **bold**, __bold__, _italic_, *italic*, `code`, ~~strike~~
    """
    lines = text.split('\n')
    result_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Handle blockquote: lines starting with "> " or bare ">"
        if line.startswith('> ') or line.strip() == '>':
            bq_lines = []
            while i < len(lines) and (lines[i].startswith('> ') or lines[i].strip() == '>'):
                bq_lines.append(lines[i][2:] if lines[i].startswith('> ') else '')
                i += 1
            inner = '\n'.join(bq_lines)
            result_lines.append(f"<blockquote>{inner}</blockquote>")
        else:
            result_lines.append(line)
            i += 1

    text = '\n'.join(result_lines)

    # Bold: **text** or __text__ (must run before italic to avoid conflicts)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text, flags=re.DOTALL)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text, flags=re.DOTALL)
    # Italic: _text_ (not preceded/followed by word chars or underscores)
    text = re.sub(r'(?<![_\w])_([^_\n]+)_(?![_\w])', r'<i>\1</i>', text)
    # Italic: *text* (single asterisk, not double)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    # Inline code: `text`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Strikethrough: ~~text~~
    text = re.sub(r'~~(.+?)~~', r'<s>\1</s>', text)

    return text


# ============================================
# Default Welcome Content
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

BUTTON_PATTERN = r"\[Button\.(url|inline)\(['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]\)\]"


# ============================================
# Setup
# ============================================

def setup(ether, db, owner_id):

    dm_service = DMService(db)
    max_warns = Config.DM_MAX_WARNS

    async def load_welcome_data():
        try:
            welcome_config = await dm_service.get_welcome(owner_id)
            if welcome_config.get("text"):
                WELCOME_DATA["text"] = welcome_config["text"]
                
                # Check if the saved image file exists (important for Heroku/Docker restarts)
                img = welcome_config.get("image")
                if img and os.path.exists(img):
                    WELCOME_DATA["image"] = img
                else:
                    WELCOME_DATA["image"] = DEFAULT_WELCOME_IMAGE
                
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
        await event.edit("<blockquote>✅ User allowed.</blockquote>")

    @ether.on(events.NewMessage(pattern=r"^\.disallow$", outgoing=True))
    async def disallow_handler(event):
        if event.sender_id != owner_id:
            return

        if not event.is_private:
            await event.edit("<blockquote>❌ Use in private chat.</blockquote>")
            return

        user_id = event.chat_id
        await dm_service.disallow_user(user_id, owner_id)
        await event.edit("<blockquote>🚫 User disallowed.</blockquote>")


# ============================================
# Set Welcome Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.setwelcome(?:\s+([\s\S]*))?$", outgoing=True))
    async def setwelcome_handler(event):
        if event.sender_id != owner_id:
            return

        custom_text = (event.pattern_match.group(1) or "").strip()
        msg = await event.get_reply_message() if event.is_reply else None

        # If no direct text AND no reply → show help
        if not custom_text and msg is None:
            await event.reply(
                "<blockquote>"
                "⚠️ <b>How to use .setwelcome:</b>\n\n"
                "<b>Option 1 — Inline text:</b>\n"
                "<code>.setwelcome > Your welcome text here</code>\n\n"
                "<b>Option 2 — Reply to a message:</b>\n"
                "Reply to any text/photo/video with <code>.setwelcome</code>\n\n"
                "📝 <b>Supported Markdown:</b>\n"
                "• <code>> text</code> → Blockquote\n"
                "• <code>**text**</code> → <b>Bold</b>\n"
                "• <code>_text_</code> → <i>Italic</i>\n"
                "• <code>`text`</code> → <code>Code</code>\n"
                "• <code>~~text~~</code> → <s>Strike</s>\n\n"
                "📌 <b>Button format:</b>\n"
                "<code>[Button.url('Label', 'https://example.com')]</code>"
                "</blockquote>"
            )
            return

        # --- Media extraction (only if replying to a message) ---
        image_path = None
        media_type = "photo"
        os.makedirs("media", exist_ok=True)

        if msg is not None:
            if msg.photo:
                try:
                    image_path = await msg.download_media(file="media/welcome.jpg")
                    media_type = "photo"
                except Exception as e:
                    logger.error(f"Failed to download welcome image: {e}")
            elif msg.video:
                try:
                    image_path = await msg.download_media(file="media/welcome.mp4")
                    if msg.document and any(
                        isinstance(a, DocumentAttributeAnimated) for a in msg.document.attributes
                    ):
                        media_type = "gif"
                    else:
                        media_type = "video"
                except Exception as e:
                    logger.error(f"Failed to download welcome media: {e}")
            elif msg.document and msg.document.mime_type and any(
                msg.document.mime_type.startswith(t) for t in ['image/', 'video/']
            ):
                try:
                    ext = ".jpg" if msg.document.mime_type.startswith('image/') else ".mp4"
                    image_path = await msg.download_media(file=f"media/welcome{ext}")
                    media_type = "photo" if ext == ".jpg" else "video"
                except Exception as e:
                    logger.error(f"Failed to download welcome document: {e}")

        # --- Text extraction ---
        if custom_text:
            # Always use md_to_html() for inline custom text.
            # Reason: html.unparse() HTML-escapes plain-text portions (> → &gt;)
            # and Telegram client entities may use <strong> instead of <b>.
            # Our md_to_html() converts raw Markdown symbols directly to clean HTML.
            parsed_text = md_to_html(custom_text)
        elif msg is not None:
            # Text came from the replied message
            raw = msg.text or msg.caption or ""
            if msg.entities:
                parsed_text = html.unparse(raw, msg.entities)
            elif msg.caption_entities:
                parsed_text = html.unparse(raw, msg.caption_entities)
            else:
                parsed_text = raw
        else:
            parsed_text = ""

        # --- Button extraction ---
        # Keep a copy of the text before stripping button syntax
        raw_text_for_buttons = parsed_text
        # Remove button syntax from the stored welcome text
        parsed_text = re.sub(r'\[Button\.(url|inline)\([^\]]+\)\]', '', parsed_text).strip()

        buttons = None

        # First: try to get buttons from the replied message's reply_markup
        if msg is not None and msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
            button_rows = []
            for row in msg.reply_markup.rows:
                row_buttons = []
                for btn in row.buttons:
                    if isinstance(btn, KeyboardButtonUrl):
                        row_buttons.append({"text": btn.text, "url": btn.url, "type": "url"})
                    elif isinstance(btn, KeyboardButtonCallback):
                        row_buttons.append({"text": btn.text, "data": btn.data.decode(), "type": "callback"})
                if row_buttons:
                    button_rows.append(row_buttons)
            if button_rows:
                buttons = button_rows

        # Second: try to parse buttons from inline syntax in the text
        if not buttons:
            matches = re.findall(BUTTON_PATTERN, raw_text_for_buttons)
            if matches:
                button_rows = []
                for line in raw_text_for_buttons.split('\n'):
                    line_buttons = []
                    for btn_type, btn_text, btn_value in re.findall(BUTTON_PATTERN, line):
                        if btn_type == 'url':
                            line_buttons.append({"text": btn_text, "url": btn_value, "type": "url"})
                        elif btn_type == 'inline':
                            line_buttons.append({"text": btn_text, "data": btn_value, "type": "callback"})
                    if line_buttons:
                        button_rows.append(line_buttons)
                if button_rows:
                    buttons = button_rows

        # --- Save to DB and update in-memory cache ---
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
                response += f"\n🔘 {len(buttons)} button row(s) included."
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

        await event.edit("<blockquote>🗑️ Welcome message cleared.</blockquote>")


# ============================================
# DM Handler (Incoming Messages)
# ============================================

    @ether.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def dm_handler(event):

        logger.info(f"DM PROTECTION CHECK FROM: {event.sender_id}")

        # Skip bots
        if event.sender and getattr(event.sender, 'bot', False):
            return
        try:
            sender = await event.get_sender()
            if sender and getattr(sender, 'bot', False):
                return
        except Exception:
            pass

        # Skip owner's own messages
        if event.sender_id == owner_id:
            return

        # Skip if DB not ready
        if db is None:
            return

        user_id = event.sender_id

        user = await dm_service.get_user(user_id)
        welcome_config = await dm_service.get_welcome(owner_id)

        welcome_text = welcome_config.get("text") or DEFAULT_WELCOME_TEXT
        
        # Check if saved media exists on disk
        saved_image = welcome_config.get("image")
        if saved_image and os.path.exists(saved_image):
            welcome_image = saved_image
        else:
            welcome_image = DEFAULT_WELCOME_IMAGE
            
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

                # Fallback: send directly
                if welcome_image:
                    await event.respond(file=welcome_image, message=text, parse_mode='html')
                else:
                    await event.respond(text, parse_mode='html')
            except Exception as e:
                logger.error(f"Failed to send welcome: {e}")

        if not user:
            await dm_service.create_user(user_id)
            user = await dm_service.get_user(user_id)

        if user:
            if user.get("blocked"):
                try:
                    await ether(BlockRequest(user_id))
                except Exception as e:
                    logger.error(f"Block error for {user_id}: {e}")
                return

            if user.get("allowed"):
                await dm_service.increment_message_count(user_id)
                return

        # Increment warning count
        warns = await dm_service.increment_warn(user_id)
        max_warns = await dm_service.get_max_warns(user_id, owner_id)

        # Block if max warns exceeded
        if warns >= max_warns:
            await dm_service.block_user(user_id)
            try:
                await ether(BlockRequest(user_id))
            except Exception as e:
                logger.error(f"Block error for {user_id}: {e}")
            await event.respond("<blockquote>⛔ <b>You have been blocked</b> for spamming.</blockquote>", parse_mode='html')
            return

        # Append warning message to the welcome text
        warning_msg = f"\n\n⚠️ <b>Warning {warns}/{max_warns}:</b> Please wait for a reply. Spamming will result in a block."
        if "</blockquote>" in welcome_text:
            final_text = welcome_text.replace("</blockquote>", f"{warning_msg}</blockquote>")
        else:
            final_text = welcome_text + warning_msg

        await send_welcome(final_text)
