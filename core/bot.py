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

import time
import psutil
import random
import os
import asyncio
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    FloodWaitError
)
from config.config import Config
from config.channels import get_channel_list, get_channels
from utils.logger import get_logger
from services.dm_shield_service import DMShieldService
from core.user_client import EtherUserClient
from storage.mongo import ether_db

logger = get_logger("EtherBot")

bot = TelegramClient('bot', Config.API_ID, Config.API_HASH)
bot.parse_mode = 'html'
 
def owner_only(func):
    async def wrapper(event):
        if event.sender_id != Config.OWNER_ID:
            if isinstance(event, events.CallbackQuery.Event):
                await event.answer("❌ This feature is for the owner only. Host your own bot to use it!", alert=True)
            elif isinstance(event, events.InlineQuery.Event):
                await event.answer([], switch_pm="❌ Access Denied", switch_pm_param="unauthorized")
            elif event.is_private:
                # We'll handle public /start separately, so this is for other private msgs
                if not event.text.startswith(("/start", "/id")):
                    await event.reply("<blockquote>❌ <b>Access Denied</b>\n\nThis is a private instance of Ether Userbot. Please host your own to access full features.</blockquote>", buttons=[Button.url("📁 Get Source", "https://github.com/LearningBotsOfficial/Ether")])
            return
        return await func(event)
    return wrapper

# Store login state temporarily
login_state = {}
userbot_client = None
userbot_wrapper = None
plugin_loader = None

HELP_DATA = {
    "text": "<blockquote><b>Ether Userbot Help</b></blockquote>",
    "buttons": None
}

WELCOME_DATA = {
    "text": None,
    "image": None,
    "buttons": None
}

SHORTCUT_DATA = {}


main_buttons = [
    [
        Button.inline("DM Protection", b"help_dm"),
        Button.inline("Shortcuts", b"help_shortcut")
    ],
    [
        Button.inline("TagAll", b"help_tagall"),
        Button.inline("Fonts", b"help_fonts")
    ],
    [
        Button.inline("DM Shield", b"help_shield"),
    ],
    [
        Button.inline("Ping System", b"help_ping"),
        Button.inline("System Info", b"help_system")
    ],
    [
        Button.inline("Auto-Reply", b"help_auto"),
        Button.inline("Privacy & Logs", b"help_privacy")
    ]
]


HELP_DATA["buttons"] = main_buttons

# ============================================

@bot.on(events.InlineQuery)
@owner_only
async def inline_help(event):
    builder = event.builder
    
    if event.text == "help":
        
        result = builder.article(
            id="help_menu",
            title="Ether Help Menu",
            description="Click to see help with buttons",
            text="<blockquote><b>Ether Userbot Help</b>\n\nSelect a feature below:</blockquote>",
            buttons=main_buttons
        )
        
        await event.answer([result], cache_time=0)
        logger.info(f"Inline help for user {event.sender_id}")

# ============================================

    elif event.text == "welcome":
        logger.info(f"Welcome inline query from user {event.sender_id}")
        if WELCOME_DATA["text"]:
            try:
                
                buttons = None
                if WELCOME_DATA["buttons"]:
                    logger.info(f"Reconstructing {len(WELCOME_DATA['buttons'])} button rows")
                    button_rows = []
                    for i, row in enumerate(WELCOME_DATA["buttons"]):
                        row_buttons = []
                        logger.info(f"Processing row {i}: {type(row)} - {row}")
                        for btn in row:
                            logger.info(f"Processing button: {type(btn)} - {btn}")
                            if isinstance(btn, dict):
                                if btn.get("type") == "url":
                                    row_buttons.append(Button.url(btn["text"], btn["url"]))
                                    logger.info(f"Added URL button: {btn['text']}")
                                elif btn.get("type") == "callback":
                                    data = btn["data"]
                                    if isinstance(data, str):
                                        data = data.encode('utf-8')
                                    elif not isinstance(data, bytes):
                                        data = str(data).encode('utf-8')
                                    row_buttons.append(Button.inline(btn["text"], data))
                                    logger.info(f"Added inline button: {btn['text']}")
                            else:
                                logger.warning(f"Unexpected button type: {type(btn)}")
                        if row_buttons:
                            button_rows.append(row_buttons)
                            logger.info(f"Added row with {len(row_buttons)} buttons")
                    
                    if button_rows:
                        buttons = button_rows
                        logger.info(f"Total button rows: {len(button_rows)}")
                
                
                if WELCOME_DATA["image"]:
                    result = builder.photo(
                        file=WELCOME_DATA["image"],
                        id="welcome_msg",
                        text=WELCOME_DATA["text"],
                        buttons=buttons
                    )
                else:
                    result = builder.article(
                        id="welcome_msg",
                        title="Welcome Message",
                        description="DM Protection Welcome",
                        text=WELCOME_DATA["text"],
                        buttons=buttons
                    )
                
                await event.answer([result], cache_time=0)
            except Exception as e:
                logger.error(f"Failed to create welcome inline result: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            logger.warning(f"WELCOME_DATA is empty, cannot answer inline query")

# ============================================

    elif event.text.startswith("shortcut:"):
        shortcut_name = event.text.replace("shortcut:", "").lower()
        
        if shortcut_name in SHORTCUT_DATA:
            try:
                shortcut = SHORTCUT_DATA[shortcut_name]
                
                
                buttons = None
                if shortcut.get("buttons"):
                    button_rows = []
                    for i, row in enumerate(shortcut["buttons"]):
                        row_buttons = []
                        for btn in row:
                            if isinstance(btn, dict):
                                if btn.get("type") == "url":
                                    row_buttons.append(Button.url(btn["text"], btn["url"]))
                                    logger.info(f"Added URL button: {btn['text']}")
                                elif btn.get("type") == "callback":
                                    data = btn["data"]
                                    if isinstance(data, str):
                                        data = data.encode('utf-8')
                                    elif not isinstance(data, bytes):
                                        data = str(data).encode('utf-8')
                                    row_buttons.append(Button.inline(btn["text"], data))
                                    logger.info(f"Added inline button: {btn['text']}")
                        if row_buttons:
                            button_rows.append(row_buttons)
                    
                    if button_rows:
                        buttons = button_rows
                
                text = shortcut.get("text", "")
                image = shortcut.get("image")
                
                
                if image:
                    result = builder.photo(
                        file=image,
                        id=f"shortcut_{shortcut_name}",
                        text=text,
                        buttons=buttons
                    )
                else:
                    result = builder.article(
                        id=f"shortcut_{shortcut_name}",
                        title=f"Shortcut: {shortcut_name}",
                        description="Saved shortcut content",
                        text=text,
                        buttons=buttons
                    )
                
                await event.answer([result], cache_time=0)
            except Exception as e:
                logger.error(f"Failed to create shortcut inline result: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            logger.warning(f"Shortcut '{shortcut_name}' not found in SHORTCUT_DATA")

# ============================================

    elif event.text.startswith("fonts:"):
        try:
            text = event.text.replace("fonts:", "", 1)

            result_text = "<b>Font Styles</b>\n\n"

            for key in FONT_MAPS:
                styled = apply_font(text, key)
                result_text += f"{key} -> <code>{styled}</code>\n"

            buttons = [
                [
                    Button.inline("Style", f"font_style:{text}".encode()),
                    Button.inline("Mix", f"font_mix:{text}".encode())
                ]
            ]

            result = builder.article(
                id="font_preview",
                title="Font Styles",
                description="Preview styled text",
                text=result_text,
                buttons=buttons
            )

            await event.answer([result], cache_time=0)

        except Exception as e:
            logger.error(f"Font inline error: {e}")

# ============================================

    elif event.text == "alive":
        bot_info = Config.BOT_MENTION or "Bot"
        
        # Calculate Uptime
        uptime_seconds = int(time.time() - Config.START_TIME)
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime = f"{days}d {hours}h {minutes}m {seconds}s"
        
        # System Stats
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        result = builder.photo(
            file="assets/ether_logo.png",
            text=(
                "<b>Ether Userbot is Alive</b>\n\n"
                "<blockquote>"
                f"Client: {bot_info}\n"
                "Status: ONLINE\n"
                f"Uptime: {uptime}\n"
                f"CPU: {cpu}%\n"
                f"RAM: {ram}%\n"
                f"Disk: {disk}%\n"
                "Telethon: CONNECTED\n"
                "Database: STABLE\n"
                "</blockquote>\n\n"
                "<i>All systems operational</i>"
            ),
            buttons=[
                [
                    Button.url("Repository", "https://github.com/LearningBotsOfficial/Ether")
                ]
            ]
        )

        await event.answer([result], cache_time=0)
    
    

# ============================================
# Callback Handlers
# ============================================

@bot.on(events.CallbackQuery(data=b"help_back"))
@owner_only
async def cb_back(event):
    await event.edit(
        "<blockquote><b>Ether Userbot Help</b>\n\nSelect a feature below:</blockquote>",
        buttons=main_buttons
    )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_dm"))
@owner_only
async def cb_dm(event):
    await event.edit(
        "<blockquote>"
        "<b>DM Protection System</b>\n\n"
        "<b>Overview:</b>\n"
        "When someone messages you:\n"
        "• First message → Welcome message sent\n"
        "• Follow-ups → Warning counter (max 3)\n"
        "• After max warnings → Auto block\n\n"
        "Only users you <code>.allow</code> can message freely.\n\n"
        "<b>Commands:</b>\n"
        "<code>.setwelcome</code> - Set welcome message with buttons\n"
        "<code>.clearwelcome</code> - Remove welcome message\n"
        "<code>.allow</code> - Allow user (in their DM)\n"
        "<code>.disallow</code> - Disallow user (in their DM)\n"
        "<code>.setwarn &lt;number&gt;</code> - Set max warnings\n\n"
        "<b>Warning System:</b>\n"
        "Users who aren't allowed get:\n"
        "• Welcome on 1st message\n"
        "• Warning X/N on follow-ups\n"
        "• <b>Auto-block</b> at max warnings\n\n"
        "Use <code>.setwarn &lt;number&gt;</code> to change limit"
        "</blockquote>",
        buttons=[[Button.inline("Back", b"help_back")]]
    )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_shortcut"))
@owner_only
async def cb_shortcut(event):
    await event.edit(
        "<blockquote>"
        "<b>Shortcuts System</b>\n\n"
        "<b>Overview:</b>\n"
        "Save messages, images, and buttons with custom names for quick access.\n"
        "• <b>Text:</b> Save formatted text with bold, italic, code\n"
        "• <b>Images:</b> Save photos with captions\n"
        "• <b>Buttons:</b> Save inline buttons (URL & callback)\n\n"
        "Perfect for welcome messages, announcements, or frequently sent content.\n\n"
        "<b>Commands:</b>\n"
        "<code>.shortcut &lt;name&gt;</code> - Save content (reply to message)\n"
        "<code>.get &lt;name&gt;</code> - Retrieve and send shortcut\n"
        "<code>.delshortcut &lt;name&gt;</code> - Delete a shortcut\n"
        "<code>.shortcuts</code> - List all saved shortcuts\n\n"
        "<b>Tips:</b>\n"
        "• Reply to a message with <code>.shortcut mychannel</code> to save\n"
        "• Use <code>.get mychannel</code> to send it anywhere\n"
        "• Reply to a message with <code>.get mychannel</code> to send to that chat\n"
        "• Names are case-insensitive (MyChannel = mychannel)\n"
        "• Button format: <code>[Button.url('Text', 'URL')]</code>\n"
        "• Button format: <code>[Button.inline('Text', 'data')]</code>"
        "</blockquote>",
        buttons=[[Button.inline("Back", b"help_back")]]
    )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_tagall"))
@owner_only
async def cb_tagall(event):
    await event.edit(
        "<blockquote>"
        "<b>TagAll</b>\n\n"
        "Mention group members in small batches with delay to avoid spam and limits.\n\n"
        
        "<b>Commands:</b>\n"
        "• <code>.tagall &lt;msg&gt;</code>\n"
        "• <code>.gmtag &lt;msg&gt;</code> (Morning greeting)\n"
        "• <code>.gntag &lt;msg&gt;</code> (Night greeting)\n\n"
        
        "<b>Examples:</b>\n"
        "• <code>.tagall Wake up!</code>\n"
        "• <code>.gmtag</code> (Uses 'Good Morning!')\n"
        "• <code>.gntag sleep tight</code>\n\n"
        
        "<b>Tips:</b>\n"
        "• Works only in groups\n"
        "• Skips bots & deleted users\n"
        "• Use <code>.tagstop</code> or <code>.&lt;cmd&gt; stop</code> to cancel"
        "</blockquote>",
        
        buttons=[[Button.inline("Back", b"help_back")]]
    )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_ping"))
@owner_only
async def cb_ping(event):
    await event.edit(
        "<blockquote>"
        "<b>Ping System</b>\n\n"
        "<b>Overview:</b>\n"
        "The ping command measures how quickly the userbot responds.\n"
        "Lower = better.\n\n"
        "<b>Commands:</b>\n"
        "<code>.ping</code> - Check response time\n\n"
        "Returns time in milliseconds."
        "</blockquote>",
        buttons=[[Button.inline("Back", b"help_back")]]
    )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_system"))
@owner_only
async def cb_system(event):
    await event.edit(
        "<blockquote>"
        "<b>System Management</b>\n\n"
        "• <code>.ping</code> - Check latency\n"
        "• <code>.alive</code> - Check system status\n"
        "• <code>.restart</code> - Reboot Ether\n"
        "• <code>.afk</code> - Go away silently\n"
        "• <code>.status</code> - Check away duration\n"
        "• <code>.id</code> - Get chat/user IDs"
        "</blockquote>",
        buttons=[[Button.inline("Back", b"help_back")]]
    )


# ============================================

@bot.on(events.CallbackQuery(data=b"help_privacy"))
@owner_only
async def cb_privacy(event):
    await event.edit(
        "<blockquote>"
        "<b>Privacy & Protection</b>\n\n"
        "<b>Anti-Flood:</b>\n"
        "Automatically blocks users who spam your DMs.\n"
        "• <code>.antiflood on</code> - Enable protection\n"
        "• <code>.antiflood off</code> - Disable protection\n\n"
        "<b>Auto-Read:</b>\n"
        "Marks all incoming DMs as read immediately.\n"
        "• <code>.autoread on</code> - Enable blue ticks\n"
        "• <code>.autoread off</code> - Disable blue ticks\n\n"
        "<b>Self-Destruct:</b>\n"
        "• <code>.sd &lt;secs&gt; &lt;text&gt;</code> - Send vanishing text"
        "</blockquote>",
        buttons=[[Button.inline("Back", b"help_back")]]
    )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_fonts"))
@owner_only
async def cb_fonts(event):
    await event.edit(
        "<blockquote>"
        "<b>Fonts & Styles System</b>\n\n"
        "<b>Overview:</b>\n"
        "Convert normal text into stylish fonts and modern effects.\n"
        "Includes aesthetic, glitch, hacker, and decorative styles.\n\n"
        
        "<b>Command:</b>\n"
        "<code>.fonts &lt;text&gt;</code>\n\n"
        
        "<b>Example:</b>\n"
        "<code>.fonts hello world</code>\n\n"
        
        "<b>Features:</b>\n"
        "• 10+ Unicode font styles\n"
        "• Aesthetic & vaporwave text\n"
        "• Glitch & hacker effects\n"
        "• Mix styles randomly\n"
        "• Interactive buttons (Style / Mix / Cool)\n\n"
        
        "<b>Tips:</b>\n"
        "• Works in any chat\n"
        "• Use for bios, captions, branding\n"
        "• Combine with shortcuts for fast reuse"
        "</blockquote>",
        
        buttons=[[Button.inline("Back", b"help_back")]]
    )

# ============================================

@bot.on(events.CallbackQuery(pattern=b"font_.*"))
@owner_only
async def font_callbacks(event):

    data = event.data.decode()

    if data.startswith("font_style:"):
        text = data.split(":", 1)[1]

        result = (
            "<blockquote>"
            f"<code>{text}</code>\n"
            f"<code>{apply_font(text,'2')}</code>\n"
            f"<code>{apply_font(text,'3')}</code>"
            "</blockquote>"
        )

        await event.edit(result)

    elif data.startswith("font_mix:"):
        text = data.split(":", 1)[1]

        mixed = ""
        for char in text:
            if char.isalpha():
                font = random.choice(list(FONT_MAPS.keys()))
                mixed += char.lower().translate(FONT_MAPS[font])
            else:
                mixed += char

        await event.edit(
            "<blockquote>"
            "<b>Mixed Style</b>\n\n"
            f"<code>{mixed}</code>"
            "</blockquote>"
        )

# ============================================

@bot.on(events.CallbackQuery(data=b"help_shield"))
@owner_only
async def cb_shield(event):

    await event.edit(
        "<blockquote>"
        "<b>DM Shield System</b>\n\n"
        
        "<b>Overview:</b>\n"
        "Automatically protects your DM from unwanted messages.\n\n"
        
        "<b>What it blocks:</b>\n"
        "• Links (t.me, https, tg://)\n"
        "• Usernames (@spam tags)\n\n"
        
        "<b>Commands:</b>\n"
        "<code>.shield</code> - Open control panel\n"
        "<code>.shield on</code> - Enable system\n"
        "<code>.shield off</code> - Disable system\n"
        "<code>.shield link</code> - link filter\n"
        "<code>.shield user</code> - username filter\n"
        "<code>.shield allow</code> - Reply to whitelist user\n"
        "<code>.shield disallow</code> - Reply to remove whitelist\n"
        "<code>.shield status</code> - Show system status\n\n"
        
        "<b>Tip:</b>\n"
        "Use allow system to whitelist trusted users."
        "</blockquote>",
        
        buttons=[[Button.inline("Back", b"help_back")]]
    )

# ============================================
# Bot Welcome
# ============================================

BOT_WELCOME_TEXT = (
    "<blockquote>"
    "<b>Ether Userbot</b>\n\n"
    "A fast, modern Telegram userbot built for automation and control.\n\n"
    "<b>Security:</b> 99% safe — no need to generate session strings from unknown sources.\n"
    "For full transparency, check the source code below.\n\n"
    "Manage Telegram like a pro."
    "</blockquote>"
)

BOT_WELCOME_IMAGE = "assets/ether_logo.png"

bot_dm_buttons = [
    [
        Button.url("Updates", "https://t.me/Ether_Update"),
        Button.url("Support Group", "https://t.me/EtherSupport")
    ],
    [Button.url("Source Code", "https://github.com/LearningBotsOfficial/Ether")],
]

# ============================================
# Bot Start Handler
# ============================================

@bot.on(events.NewMessage(pattern=r"^/start$", incoming=True, func=lambda e: e.is_private))
async def bot_start_handler(event):
    if event.sender_id != Config.OWNER_ID:
        await event.reply(
            "<blockquote><b>Welcome to Ether Userbot</b>\n\n"
            "This is a private instance of Ether. If you want your own powerful userbot, click the button below to get the source code and host it yourself!</blockquote>",
            buttons=[
                [Button.url("Source", "https://github.com/LearningBotsOfficial/Ether")],
                [Button.url("Updates", "https://t.me/Ether_Update"), Button.url("Support", "https://t.me/Ether_Support")]
            ]
        )
        return

    try:
        await bot.send_file(
            event.chat_id,
            file=BOT_WELCOME_IMAGE,
            caption=BOT_WELCOME_TEXT,
            buttons=bot_dm_buttons
        )

    except Exception as e:
        logger.error(f"Bot /start reply failed: {e}", exc_info=True)

        try:
            await bot.send_message(
                event.chat_id,
                BOT_WELCOME_TEXT,
                buttons=bot_dm_buttons
            )
            logger.info(f"Bot /start fallback sent to user {event.sender_id}")
        except Exception as e2:
            logger.error(f"Bot /start fallback failed: {e2}", exc_info=True)


# ============================================
# Bot Login Handler
# ============================================

@bot.on(events.NewMessage(pattern=r"^/id$", incoming=True))
async def bot_id_handler(event):
    await event.reply(f"<blockquote><b>Your ID:</b> <code>{event.sender_id}</code>\n<b>Chat ID:</b> <code>{event.chat_id}</code></blockquote>")

# ============================================
# Administrative Commands (Owner Only)
# ============================================

@bot.on(events.NewMessage(pattern=r"^/login$", incoming=True, func=lambda e: e.is_private))
@owner_only
async def bot_login_handler(event):
    if event.sender_id != Config.OWNER_ID:
        await event.reply("<blockquote><b>Access Denied:</b> This command is only for the admin.</blockquote>")
        return
    
    if userbot_client is None:
        await event.reply("<blockquote><b>System Error:</b> Userbot client not initialized. Please restart the bot.</blockquote>")
        return
    
    login_state[Config.OWNER_ID] = {"step": "phone"}
    
    await event.reply(
        "<blockquote>"
        "<b>Ether Login System</b>\n\n"
        "Please enter your phone number with country code.\n\n"
        "<i>Example: +9198*****</i>\n\n"
        "Send /cancel to abort."
        "</blockquote>"
    )
    logger.info(f"Login initiated by owner {Config.OWNER_ID}")


# ============================================
# Bot Cancel Handler
# ============================================

@bot.on(events.NewMessage(pattern=r"^/cancel$", incoming=True, func=lambda e: e.is_private))
@owner_only
async def bot_cancel_handler(event):
    if event.sender_id != Config.OWNER_ID:
        return
    
    if Config.OWNER_ID in login_state:
        del login_state[Config.OWNER_ID]
        await event.reply("<blockquote><b>Session Action:</b> Login cancelled.</blockquote>")


# ============================================
# Bot Restart Handler
# ============================================

@bot.on(events.NewMessage(pattern=r"^/restart$", incoming=True, func=lambda e: e.is_private))
@owner_only
async def bot_restart_handler(event):
    if event.sender_id != Config.OWNER_ID:
        return
        
    await event.reply("<blockquote><b>System Restart Initiated</b>\n\nThe bot is restarting now...</blockquote>")
    
    # Give it a moment
    await asyncio.sleep(2)
    
    import sys
    import os
    logger.info("Restarting system via Bot UI /restart command")
    os.execv(sys.executable, [sys.executable] + sys.argv)


# ============================================
# Bot Login Flow Handler
# ============================================

@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
@owner_only
async def bot_login_flow_handler(event):
    global userbot_client, userbot_wrapper
    
    if event.sender_id != Config.OWNER_ID:
        return
    
    if Config.OWNER_ID not in login_state:
        return
    
    if userbot_client is None:
        await event.reply("❌ Userbot client not initialized.")
        return
    
    state = login_state[Config.OWNER_ID]
    text = event.text.strip()
    
    if text.startswith("/"):
        return
    
    if state["step"] == "phone":
        phone = text
        
        try:
            # Ensure client is connected
            if not userbot_client.is_connected():
                await userbot_client.connect()
                logger.info("Userbot client connected for login")
            
            result = await userbot_client.send_code_request(phone)
            state["step"] = "otp"
            state["phone"] = phone
            state["phone_code_hash"] = result.phone_code_hash
            
            await event.reply(
                f"<blockquote>"
                f"📩 Send OTP with spaces (e.g. 1 2 3 4 5)\n\n"
                "Send /cancel to abort."
                "</blockquote>"
            )
            logger.info(f"OTP sent to {phone}")
        except FloodWaitError as e:
            del login_state[Config.OWNER_ID]
            await event.reply(f"<blockquote>⏳ <b>Flood Wait</b>\n\nPlease wait {e.seconds} seconds before trying again.</blockquote>")
            logger.warning(f"Flood wait: {e.seconds}s")
        except Exception as e:
            del login_state[Config.OWNER_ID]
            await event.reply(f"<blockquote>❌ <b>Error</b>\n\nFailed to send OTP: {str(e)}</blockquote>")
            logger.error(f"OTP send error: {e}")
    
    elif state["step"] == "otp":
        code = text
        
        try:
            # Ensure client is connected
            if not userbot_client.is_connected():
                await userbot_client.connect()
            
            await userbot_client.sign_in(
                phone=state["phone"],
                code=code,
                phone_code_hash=state["phone_code_hash"]
            )
            
            del login_state[Config.OWNER_ID]
            
            await asyncio.sleep(1)
            # Capture session string BEFORE disconnecting so it isn't lost
            _saved_session = userbot_client.session.save() if userbot_client.session else None
            await userbot_client.disconnect()
            
            if userbot_wrapper:
                # Re-initialize with the authenticated session string
                userbot_client = userbot_wrapper.init_client(_saved_session)
                await userbot_client.connect()
                logger.info("Userbot client recreated and reconnected after login")
            else:
                await userbot_client.connect()
                logger.info("Userbot client reconnected after login (no wrapper)")
            
            # Verify authorization
            is_authorized = await userbot_client.is_user_authorized()
            if is_authorized:
                me = await userbot_client.get_me()
                Config.OWNER_NAME = me.first_name
                Config.OWNER_USERNAME = me.username
                Config.OWNER_MENTION = f"<a href='tg://user?id={me.id}'>{me.first_name}</a>"
                logger.info(f"Userbot session verified as authorized: {Config.OWNER_NAME} (@{me.username})")
            else:
                logger.warning("Userbot session not authorized after reconnection")
            
            # Auto-join official channels
            try:
                channels = get_channels()
                joined_count = 0
                for name, link in channels.items():
                    try:
                        # Extract channel username from link
                        username = link.split('/')[-1]
                        await userbot_client(JoinChannelRequest(username))
                        joined_count += 1
                        logger.info(f"Joined channel: {name} ({username})")
                        await asyncio.sleep(1)  # Rate limit
                    except Exception as e:
                        logger.warning(f"Could not join {name}: {e}")
                if joined_count > 0:
                    logger.info(f"Successfully joined {joined_count} official channels")
            except Exception as e:
                logger.error(f"Channel auto-join failed: {e}")
            
            await event.reply(
                "<blockquote>"
                "✅ <b>Login Successful!</b>\n\n"
                "Your session has been created.\n"
                "The userbot has been reconnected.\n"
                "Joined official channels automatically.\n\n"
                "You can now use all commands."
                "</blockquote>"
            )
            logger.info("Login successful")

            # ── Persist Session to MongoDB ────────────────────────────────────
            try:
                if userbot_wrapper:
                    session_str = userbot_wrapper.get_session_string()
                    if session_str:
                        await ether_db.save_session(Config.SESSION_NAME, session_str)
                        logger.info("Session: SAVED to database after OTP login.")
            except Exception as db_err:
                logger.warning(f"Session save failed (non-critical): {db_err}")
            # ─────────────────────────────────────────────────────────────────
        except SessionPasswordNeededError:
            state["step"] = "2fa"
            await event.reply(
                "<blockquote>"
                "🔐 <b>2FA Required</b>\n\n"
                "Please enter your two-factor authentication password.\n\n"
                "Send /cancel to abort."
                "</blockquote>"
            )
            logger.info("2FA required")
        except PhoneCodeInvalidError:
            del login_state[Config.OWNER_ID]
            await event.reply("<blockquote>❌ <b>Invalid Code</b>\n\nThe OTP you entered is incorrect. Please try /login again.</blockquote>")
            logger.warning("Invalid OTP entered")
        except PhoneCodeExpiredError:
            del login_state[Config.OWNER_ID]
            await event.reply("<blockquote>❌ <b>Code Expired</b>\n\nThe OTP has expired. Please try /login again.</blockquote>")
            logger.warning("OTP expired")
        except Exception as e:
            del login_state[Config.OWNER_ID]
            await event.reply(f"<blockquote>❌ <b>Error</b>\n\nFailed to verify OTP: {str(e)}</blockquote>")
            logger.error(f"OTP verify error: {e}")
    
    elif state["step"] == "2fa":
        password = text
        
        try:
            # Ensure client is connected
            if not userbot_client.is_connected():
                await userbot_client.connect()
                logger.info("Userbot client reconnected for 2FA verification")
            
            await userbot_client.sign_in(password=password)
            
            del login_state[Config.OWNER_ID]
            
            await asyncio.sleep(1)
            # Capture session string BEFORE disconnecting so it isn't lost
            _saved_session = userbot_client.session.save() if userbot_client.session else None
            await userbot_client.disconnect()
            
            if userbot_wrapper:
                # Re-initialize with the authenticated session string
                userbot_client = userbot_wrapper.init_client(_saved_session)
                await userbot_client.connect()
                logger.info("Userbot client recreated and reconnected after 2FA login")
            else:
                await userbot_client.connect()
                logger.info("Userbot client reconnected after 2FA login (no wrapper)")
            
            is_authorized = await userbot_client.is_user_authorized()
            if is_authorized:
                me = await userbot_client.get_me()
                Config.OWNER_NAME = me.first_name
                Config.OWNER_USERNAME = me.username
                Config.OWNER_MENTION = f"<a href='tg://user?id={me.id}'>{me.first_name}</a>"
                logger.info(f"Userbot session verified as authorized (2FA): {Config.OWNER_NAME} (@{me.username})")
            else:
                logger.warning("Userbot session not authorized after 2FA reconnection")
            
            # Auto-join official channels (2FA login)
            try:
                channels = get_channels()
                joined_count = 0
                for name, link in channels.items():
                    try:
                        username = link.split('/')[-1]
                        await userbot_client(JoinChannelRequest(username))
                        joined_count += 1
                        logger.info(f"Joined channel: {name} ({username})")
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.warning(f"Could not join {name}: {e}")
                if joined_count > 0:
                    logger.info(f"Successfully joined {joined_count} official channels (2FA)")
            except Exception as e:
                logger.error(f"Channel auto-join failed (2FA): {e}")
            
            await event.reply(
                "<blockquote>"
                "✅ <b>Login Successful!</b>\n\n"
                "Your session has been created with 2FA.\n"
                "The userbot has been reconnected.\n"
                "You can now use all commands."
                "</blockquote>"
            )
            logger.info("2FA login successful")

            # ── Persist Session to MongoDB ────────────────────────────────────
            try:
                if userbot_wrapper:
                    session_str = userbot_wrapper.get_session_string()
                    if session_str:
                        await ether_db.save_session(Config.SESSION_NAME, session_str)
                        logger.info("Session: SAVED to database after 2FA login.")
            except Exception as db_err:
                logger.warning(f"Session save failed (non-critical): {db_err}")
            # ─────────────────────────────────────────────────────────────────
        except Exception as e:
            del login_state[Config.OWNER_ID]
            await event.reply(f"<blockquote>❌ <b>Error</b>\n\nFailed to verify 2FA: {str(e)}</blockquote>")
            logger.error(f"2FA verify error: {e}")

# ============================================
# Remove Command
# ============================================

@bot.on(events.NewMessage(pattern=r"^/remove$", incoming=True, func=lambda e: e.is_private))
async def bot_remove_handler(event):
    if event.sender_id != Config.OWNER_ID:
        await event.reply("<blockquote><b>Access Denied:</b> This command is only for the admin.</blockquote>")
        return
    
    session_file = f"{Config.SESSION_NAME}.session"
    session_journal = f"{Config.SESSION_NAME}.session-journal"
    
    deleted = False
    
    # First, attempt to cleanly log out which removes the session on Telegram's end
    # and safely deletes the local .session file without lock issues.
    if userbot_client and userbot_client.is_connected():
        try:
            await userbot_client.log_out()
            logger.info("Userbot logged out successfully")
            deleted = True
        except Exception as e:
            logger.error(f"Failed to log out userbot cleanly: {e}")
            # Fallback: disconnect and manually delete
            try:
                await userbot_client.disconnect()
            except Exception:
                pass
    
    # Fallback to manual file removal if log_out failed or client wasn't connected
    if not deleted and os.path.exists(session_file):
        try:
            os.remove(session_file)
            deleted = True
            logger.info(f"Session file removed manually: {session_file}")
        except Exception as e:
            logger.error(f"Failed to remove session file: {e}")
    
    if os.path.exists(session_journal):
        try:
            os.remove(session_journal)
            logger.info(f"Session journal removed: {session_journal}")
        except Exception as e:
            logger.error(f"Failed to remove session journal: {e}")
    
    # ── Clear session from MongoDB ────────────────────────────────────────────
    try:
        if ether_db.db is not None:
            await ether_db.db.sessions.delete_one({"name": Config.SESSION_NAME})
            logger.info("Session: DELETED from database.")
    except Exception as db_err:
        logger.warning(f"Session DB delete failed (non-critical): {db_err}")
    # ─────────────────────────────────────────────────────────────────────────
    
    if deleted:
        await event.reply(
            "🗑️ <b>Session Removed</b>\n\n"
            "Your session has been deleted from disk and database.\n"
            "Use /login to create a new session."
        )
    else:
        await event.reply(
            "ℹ️ <b>No Session Found</b>\n\n"
            "No session file exists to remove."
        )


def set_userbot_client(client, wrapper=None):
    global userbot_client, userbot_wrapper
    userbot_client = client
    userbot_wrapper = wrapper
    logger.info("Userbot client reference set for login")


def set_plugin_loader(loader):
    global plugin_loader
    plugin_loader = loader
    logger.info("Plugin loader reference set for login")


# ============================================
# Font Utilities
# ============================================

FONT_MAPS = {
    "1": str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"),
    "2": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃"),
    "3": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"),
    "4": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"),
    "5": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣"),
    "6": str.maketrans("abcdefghijklmnopqrstuvwxyz", "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"),
    "7": str.maketrans("abcdefghijklmnopqrstuvwxyz", "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"),
    "8": str.maketrans("abcdefghijklmnopqrstuvwxyz", "αв¢∂єƒgнιנкℓмησρզяѕтυνωχуz"),
    "9": str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ"),
    "10": str.maketrans("abcdefghijklmnopqrstuvwxyz", "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"),
}

def apply_font(text, font_key):
    return text.lower().translate(FONT_MAPS[font_key])


# ============================================

@bot.on(events.CallbackQuery(data=b"help_auto"))
@owner_only
async def cb_auto(event):
    await event.edit(
        "<blockquote>"
        "<b>Auto-Reply System</b>\n\n"
        "<b>Auto-Reply:</b>\n"
        "The bot can automatically respond to specific keywords in DMs.\n"
        "• <code>.autoreply \"trigger\" | response</code> - Add text\n"
        "• <code>.autoreply trigger</code> (reply to a message) - Save media/post\n"
        "• <code>.delreply trigger</code> - Remove\n"
        "• <code>.replies</code> - List all active triggers\n\n"
        "<b>Scheduler:</b>\n"
        "Send messages after a specific delay.\n"
        "• <code>.schedule &lt;secs&gt; | &lt;text&gt;</code>\n\n"
        "<b>Example:</b>\n"
        "<code>.autoreply \"hello world\" | Hey there!</code>"
        "</blockquote>",
        buttons=[[Button.inline("Back", b"help_back")]]
    )

# ============================================
# Bot Class
# ============================================

class EtherBot:
    
    def __init__(self):
        self.token = Config.BOT_TOKEN
        self._running = False
    
    async def start(self) -> None:
        """Connect the bot to Telegram (non-blocking — does NOT run the event loop)."""
        if not Config.BOT_TOKEN:
            logger.warning("No BOT_TOKEN - bot features disabled")
            return
        
        try:
            logger.info(f"Attempting to start bot with token: {self.token[:20]}...")
            await asyncio.wait_for(bot.start(bot_token=self.token), timeout=30)
            logger.info("Bot connected successfully")
        except asyncio.TimeoutError:
            logger.error("Bot connection timed out after 30 seconds")
        except Exception as e:
            logger.error(f"Bot start error: {e}", exc_info=True)

    async def get_me(self):
        return await bot.get_me()

    async def run(self) -> None:
        """Keep the bot alive — call this after start()."""
        try:
            await bot.run_until_disconnected()
        except Exception as e:
            logger.error(f"Bot run error: {e}", exc_info=True)
    
    async def stop(self) -> None:
        await bot.disconnect()
        logger.info("Bot stopped")


async def send_log(text: str, buttons=None):
    """Sends a notification log to the owner via the Bot UI."""
    if not Config.BOT_TOKEN or not Config.OWNER_ID:
        return
    try:
        await bot.send_message(Config.OWNER_ID, text, buttons=buttons)
    except Exception as e:
        logger.error(f"Failed to send log to owner: {e}")


ether_bot = EtherBot()
