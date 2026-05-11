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
import re

from services.shortcut_service import ShortcutService
from utils.parser import parse_links
from utils.logger import get_logger
from config.config import Config
from core.bot import bot, SHORTCUT_DATA

logger = get_logger("EtherShortcut")


def setup(ether, db, owner_id):
    shortcut_service = ShortcutService(db)

# ============================================
# Load Shortcuts Data
# ============================================
    
    async def load_shortcuts_data():
        try:
            if db is None:
                return
            
            shortcuts_collection = db["shortcuts"]
            cursor = shortcuts_collection.find({"owner_id": owner_id})
            shortcuts = await cursor.to_list(length=None)
            
            for shortcut in shortcuts:
                name = shortcut.get("name", "").lower()
                if name:
                    SHORTCUT_DATA[name] = {
                        "text": shortcut.get("text", ""),
                        "image": shortcut.get("image"),
                        "file": shortcut.get("file"),
                        "media_type": shortcut.get("media_type"),
                        "buttons": shortcut.get("buttons")
                    }
                    
        except Exception as e:
            logger.error(f"Failed to load shortcuts data: {e}")
    
    import asyncio
    asyncio.create_task(load_shortcuts_data())


# ============================================
# Shortcut Command
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.shortcut (\w+)$", outgoing=True))
    async def shortcut_handler(event):
        if event.sender_id != owner_id:
            return
        
        name = event.pattern_match.group(1)
        
        if not event.is_reply:
            await event.reply(
                "<blockquote>"
                "⚠️ Reply to the message you want to save as a shortcut.\n\n"
                "📝 <b>Supported Formatting:</b>\n"
                "• <b>Bold:</b> Use <code>**text**</code> or <code>__text__</code>\n"
                "• <i>Italic:</i> Use <code>__text__</code>\n"
                "• <code>Code:</code> Use <code>`text`</code>\n\n"
                "📎 <b>Supported Media:</b>\n"
                "• Images (photos)\n"
                "• Audio files\n"
                "• Videos\n"
                "• Documents/Files (ZIP, PDF, etc.)\n"
                "• Voice notes\n"
                "• Stickers\n\n"
                "📌 <b>Button Format:</b>\n"
                "<code>[Button.url('Button Text', 'https://example.com')]</code>\n"
                "💡 <b>Tip:</b> Include button code in your message text."
                "</blockquote>",
                parse_mode="html"
            )
            return
        
        msg = await event.get_reply_message()
        
        image_path = None
        file_path = None
        media_type = None
        
        # Handle different media types
        if msg.photo:
            try:
                image_path = await msg.download_media(file=f"media/shortcut_{name}.jpg")
                media_type = "photo"
            except Exception as e:
                logger.error(f"Failed to download shortcut image: {e}")
        elif msg.audio:
            try:
                file_path = await msg.download_media(file=f"media/shortcut_{name}_audio")
                media_type = "audio"
            except Exception as e:
                logger.error(f"Failed to download shortcut audio: {e}")
        elif msg.video:
            try:
                file_path = await msg.download_media(file=f"media/shortcut_{name}_video")
                media_type = "video"
            except Exception as e:
                logger.error(f"Failed to download shortcut video: {e}")
        elif msg.document:
            try:
                file_path = await msg.download_media(file=f"media/shortcut_{name}_file")
                media_type = "document"
            except Exception as e:
                logger.error(f"Failed to download shortcut file: {e}")
        elif msg.voice:
            try:
                file_path = await msg.download_media(file=f"media/shortcut_{name}_voice")
                media_type = "voice"
            except Exception as e:
                logger.error(f"Failed to download shortcut voice: {e}")
        elif msg.sticker:
            try:
                file_path = await msg.download_media(file=f"media/shortcut_{name}_sticker")
                media_type = "sticker"
            except Exception as e:
                logger.error(f"Failed to download shortcut sticker: {e}")
        
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
            await shortcut_service.save_shortcut(owner_id, name, parsed_text, image_path, buttons, file_path, media_type)
            
            SHORTCUT_DATA[name.lower()] = {
                "text": parsed_text,
                "image": image_path,
                "file": file_path,
                "media_type": media_type,
                "buttons": buttons
            }
            
            response = f"✅ Shortcut '{name}' saved."
            if image_path:
                response += "\n📷 Image included."
            if file_path:
                response += f"\n📎 {media_type or 'File'} included."
            if buttons:
                response += f"\n🔘 {len(buttons)} button rows included."
            await event.edit(response)
        except Exception as e:
            logger.error(f"Failed to save shortcut: {e}")
            await event.edit("❌ Failed to save shortcut.")


# ============================================
# Get Shortcut Command
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.get (\w+)$", outgoing=True))
    async def get_shortcut_handler(event):
        if event.sender_id != owner_id:
            return
        
        name = event.pattern_match.group(1)
        
        shortcut = await shortcut_service.get_shortcut(owner_id, name)
        
        if not shortcut:
            await event.reply(f"<blockquote>❌ Shortcut '{name}' not found.</blockquote>", parse_mode="html")
            return
        
        text = shortcut.get("text", "")
        image = shortcut.get("image")
        file_path = shortcut.get("file")
        media_type = shortcut.get("media_type")
        buttons = shortcut.get("buttons")
        
        async def send_shortcut_message(text: str, target_chat=None) -> None:
            try:
                chat_id = target_chat or event.chat_id
                bot_username = Config.BOT_USERNAME
                
                if bot_username and buttons:
                    
                    try:
                        results = await ether.inline_query(bot_username, f"shortcut:{name.lower()}")
                        
                        if results:
                            await results[0].click(chat_id)
                            return
                    except Exception as inline_err:
                        logger.error(f"Inline query failed: {inline_err}")
                
                # Handle different media types when sending
                if image:
                    await ether.send_file(chat_id, file=image, caption=text, parse_mode="html")
                elif file_path and media_type:
                    if media_type == "audio":
                        await ether.send_file(chat_id, file=file_path, caption=text, parse_mode="html")
                    elif media_type == "video":
                        await ether.send_file(chat_id, file=file_path, caption=text, parse_mode="html")
                    elif media_type == "document":
                        await ether.send_file(chat_id, file=file_path, caption=text, parse_mode="html")
                    elif media_type == "voice":
                        await ether.send_file(chat_id, file=file_path, caption=text, parse_mode="html", voice_note=True)
                    elif media_type == "sticker":
                        await ether.send_file(chat_id, file=file_path)
                    else:
                        await ether.send_file(chat_id, file=file_path, caption=text, parse_mode="html")
                else:
                    await ether.send_message(chat_id, text, parse_mode="html")
            except Exception as e:
                logger.error(f"Failed to send shortcut: {e}")
        
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            target_chat = reply_msg.chat_id
            await send_shortcut_message(text, target_chat)
            await event.edit(f"✅ Shortcut '{name}' sent.")
        else:
            await send_shortcut_message(text)
            await event.edit(f"✅ Shortcut '{name}' sent.")


# ============================================
# Delete Shortcut Command
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.delshortcut (\w+)$", outgoing=True))
    async def del_shortcut_handler(event):
        if event.sender_id != owner_id:
            return
        
        name = event.pattern_match.group(1)
        
        deleted = await shortcut_service.delete_shortcut(owner_id, name)
        
        if deleted:
            if name.lower() in SHORTCUT_DATA:
                del SHORTCUT_DATA[name.lower()]
            
            await event.edit(f"🗑️ Shortcut '{name}' deleted.")
        else:
            await event.edit(f"❌ Shortcut '{name}' not found.")

    
# ============================================
# List Shortcuts Command
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.shortcuts$", outgoing=True))
    async def list_shortcuts_handler(event):
        if event.sender_id != owner_id:
            return
        
        shortcuts = await shortcut_service.list_shortcuts(owner_id)
        
        if not shortcuts:
            await event.reply("<blockquote>📭 No shortcuts saved yet.\n\nUse .shortcut <name> to save one.</blockquote>", parse_mode="html")
        else:
            shortcut_list = "\n".join(f"• <code>{s}</code>" for s in shortcuts)
            await event.reply(f"<blockquote>📋 <b>Your Shortcuts:</b>\n\n{shortcut_list}\n\n<i>Total: {len(shortcuts)}</i></blockquote>", parse_mode="html")
