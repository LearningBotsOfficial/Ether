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

import asyncio
import sys
import os

try:
    import uvloop
except ImportError:
    uvloop = None

from core.user_client import EtherUserClient
from core.bot import ether_bot, set_userbot_client, set_plugin_loader
from core.loader import PluginLoader
from storage.mongo import ether_db
from config.config import Config
from config.channels import validate_integrity
from utils.logger import setup_logger, get_logger
from web_service import run_web_service

logger = get_logger("EtherMain")

# Global loader for plugin reloading after login
plugin_loader = None


async def run_userbot():

    # Connect to database
    db_connected = await ether_db.connect()
    if not db_connected:
        logger.warning("Running without database - some features disabled")
    
    # Check session file existence
    session_file = f"{Config.SESSION_NAME}.session"
    session_exists = os.path.exists(session_file)
    logger.info(f"Session file check: {session_file} - {'EXISTS' if session_exists else 'NOT FOUND'}")
    
    # Initialize Telegram client
    client_wrapper = EtherUserClient()
    logger.info("Initializing Telegram client...")
    
    connected = await client_wrapper.connect()
    
    if not connected:
        logger.error("Failed to connect to Telegram")
        return
    
    logger.info("Telegram client connected successfully")
    
    # Check authorization
    is_authorized = await client_wrapper.is_authorized()
    logger.info(f"Session authorization check: {'AUTHORIZED' if is_authorized else 'NOT AUTHORIZED'}")
    
    if not is_authorized:
        logger.warning("Session not authorized. Use /login command to authenticate.")
        logger.info("Userbot running in unauthenticated mode - login required")
    else:
        # Auto-fetch user details
        client = client_wrapper.get_client()
        me = await client.get_me()
        logger.info(f"Userbot session authorized: {me.first_name} (@{me.username})")
    
    # Get raw client for plugin loading
    client = client_wrapper.get_client()
    
    # Set userbot client reference for bot login
    set_userbot_client(client, client_wrapper)
    
    # Load all plugins
    global plugin_loader
    loader = PluginLoader(
        client=client,
        db=ether_db.db,
        owner_id=Config.OWNER_ID
    )
    loader.load_all()
    plugin_loader = loader
    
    # Set plugin loader reference for bot to reload after login
    set_plugin_loader(loader)
    
    stats = loader.get_stats()
    logger.info(f"Loaded {stats['total']} plugins: {stats['plugins']}")
    logger.info("Userbot running")
    
    await client.run_until_disconnected()


async def run_bot():
    if not Config.BOT_TOKEN:
        logger.info("No BOT_TOKEN - bot UI disabled")
        return
    
    logger.info("Bot Ui starting...")
    await ether_bot.start()
    
    # Auto-fetch bot details
    me = await ether_bot.get_me()
    Config.BOT_USERNAME = me.username
    logger.info(f"Bot started as @{me.username} ({me.first_name})")


async def startup():
    setup_logger()
    logger.info("=" * 50)
    logger.info("Ether Hybrid System Starting")
    logger.info("=" * 50)
    
    # Validate channels file integrity
    if not validate_integrity():
        logger.error("=" * 50)
        logger.error("SECURITY VIOLATION DETECTED")
        logger.error("The channels.py file has been modified.")
        logger.error("Unauthorized modification detected.")
        logger.error("Bot will not start to protect integrity.")
        logger.error("=" * 50)
        print("\n" + "=" * 50)
        print("SECURITY VIOLATION DETECTED")
        print("The channels.py file has been modified.")
        print("Unauthorized modification detected.")
        print("Bot will not start to protect integrity.")
        print("=" * 50 + "\n")
        sys.exit(1)
    
    logger.info("Channels file integrity validated successfully")
    
    # Start bot first - it should always run for /login
    bot_task = asyncio.create_task(run_bot())
    
    # Start userbot in background - may fail if session is invalid
    userbot_task = asyncio.create_task(run_userbot())
    
    # Start web service if enabled
    if Config.WEB_SERVICE:
        web_task = asyncio.create_task(run_web_service())
    
    # Wait for bot to finish (it should run indefinitely)
    try:
        await bot_task
    except Exception as e:
        logger.error(f"Bot task failed: {e}", exc_info=True)
    finally:
        # Cancel userbot if bot stops
        if not userbot_task.done():
            userbot_task.cancel()
            try:
                await userbot_task
            except asyncio.CancelledError:
                pass
                
        # Cancel web service if running
        if Config.WEB_SERVICE and 'web_task' in locals() and not web_task.done():
            web_task.cancel()
            try:
                await web_task
            except asyncio.CancelledError:
                pass


async def shutdown():
    logger.info("Shutting down...")
    await ether_bot.stop()
    await ether_db.close()


def main():
    if Config.WEB_SERVICE and uvloop:
        uvloop.install()
            
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        try:
            asyncio.run(shutdown())
        except Exception:
            pass


if __name__ == "__main__":
    main()