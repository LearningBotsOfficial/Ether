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
from config.config import Config
from utils.logger import get_logger

logger = get_logger("EtherAlive")


def setup(ether, db, owner_id):
    ALIVE_IMAGE = "assets/ether_logo.png"

    @ether.on(events.NewMessage(pattern=r"^\.alive$", outgoing=True))
    async def alive_handler(event):
        if event.sender_id != owner_id:
            return

        bot_username = Config.BOT_USERNAME
        if not bot_username:
            await event.reply("❌ BOT_USERNAME not fetched yet. Please wait.")
            return

        try:
            await event.delete()
            results = await ether.inline_query(bot_username, "alive")

            if results:
                await results[0].click(event.chat_id)
            else:
                await event.respond("❌ Inline failed: no result returned.")

        except Exception as e:
            logger.error(f"Alive error: {e}")
            await event.respond("❌ Alive failed.")