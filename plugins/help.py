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
from config.config import Config
from utils.logger import get_logger
from core.bot import bot

logger = get_logger("EtherHelp")


def setup(ether, db, owner_id):
    
    @ether.on(events.NewMessage(pattern=r"^\.help$", outgoing=True))
    async def help_handler(event):
        user = event.sender_id
        if user != Config.OWNER_ID:
            return
        
        bot_username = Config.BOT_USERNAME
        if not bot_username:
            await event.reply(
                "<blockquote>"
                "🔥 <b>Ether Help</b>\n\n"
                "<code>.commands</code> - List all commands\n"
                "<code>.ping</code> - Check latency\n"
                "<code>.shortcut &lt;name&gt;</code> - Save shortcut\n"
                "<code>.get &lt;name&gt;</code> - Get shortcut\n"
                "<code>.setwelcome</code> - Set welcome\n"
                "<code>.allow</code> - Allow user\n"
                "<code>.disallow</code> - Disallow user\n\n"
                "<i>Add BOT_USERNAME to .env for button UI.</i>"
                "</blockquote>",
                parse_mode="html"
            )
            return
        
        try:
            await event.delete()
            
            results = await ether.inline_query(bot_username, "help")
            
            if results:
                await results[0].click(event.chat_id)
            else:
                await event.respond(
                    "<blockquote>"
                    "🔥 <b>Ether Help</b>\n\n"
                    "<code>.commands</code> - List all commands\n"
                    "<code>.ping</code> - Check latency\n"
                    "<code>.shortcut &lt;name&gt;</code> - Save shortcut\n"
                    "<code>.get &lt;name&gt;</code> - Get shortcut\n"
                    "<code>.setwelcome</code> - Set welcome\n"
                    "<code>.allow</code> - Allow user\n\n"
                    "<i>Bot inline query failed.</i>"
                    "</blockquote>",
                    parse_mode="html"
                )
        except Exception as e:
            logger.error(f"Inline help failed: {e}")
            await event.respond(
                "<blockquote>"
                "🔥 <b>Ether Help</b>\n\n"
                "<code>.commands</code> - List all commands\n"
                "<code>.ping</code> - Check latency\n"
                "<code>.shortcut &lt;name&gt;</code> - Save shortcut\n"
                "<code>.get &lt;name&gt;</code> - Get shortcut\n"
                "<code>.setwelcome</code> - Set welcome\n"
                "<code>.allow</code> - Allow user\n"
                "<code>.disallow</code> - Disallow user"
                "</blockquote>",
                parse_mode="html"
            )
    
    logger.info("Help plugin loaded (inline mode)")
