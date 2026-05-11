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
import time
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
Config.START_TIME = time.time()


async def run_userbot():
    global plugin_loader
    client_wrapper = EtherUserClient()

    # Connect to database
    db_connected = await ether_db.connect()
    if not db_connected:
        logger.warning("Database: DISCONNECTED (Running in limited mode)")
    else:
        logger.info(f"Database: CONNECTED ({Config.DB_NAME})")
    
    while True:
        # Initialize/get the current client
        client = client_wrapper.get_client()
        
        if not client.is_connected():
            logger.info("Userbot: CONNECTING...")
            connected = await client_wrapper.connect()
            if not connected:
                logger.error("Connection: FAILED. Retrying in 10s...")
                await asyncio.sleep(10)
                continue

        # Check authorization
        is_authorized = await client_wrapper.is_authorized()
        
        if not is_authorized:
            logger.warning("Session: UNAUTHORIZED (Waiting for /login via Bot UI)")
        else:
            # Auto-fetch user details for authorized sessions
            try:
                me = await client.get_me()
                if me:
                    Config.OWNER_NAME = me.first_name
                    Config.OWNER_USERNAME = me.username
                    Config.OWNER_MENTION = f"<a href='tg://user?id={me.id}'>{me.first_name}</a>"
                    logger.info(f"Session: AUTHORIZED (User: {Config.OWNER_NAME})")
            except Exception as e:
                logger.error(f"Failed to fetch user details: {e}")
        
        # Share the current client with the Bot UI
        set_userbot_client(client, client_wrapper)
        
        # (Re)load plugins for this client instance
        # We reload if the client instance has changed OR if it just became authorized
        should_reload = not plugin_loader or plugin_loader.client != client
        
        if should_reload and is_authorized:
            logger.info(f"Plugins: (Re)loading for {'new ' if plugin_loader else ''}authorized client instance...")
            loader = PluginLoader(
                client=client,
                db=ether_db.db,
                owner_id=Config.OWNER_ID
            )
            loader.load_all()
            plugin_loader = loader
            set_plugin_loader(loader)
            
            stats = loader.get_stats()
            logger.info(f"Plugins: LOADED ({stats['total']} modules active)")
        elif not is_authorized:
            logger.info("Plugins: Skipping load (Waiting for authorization)")
        
        logger.info("Userbot: RUNNING (Awaiting commands)")
        
        try:
            # This blocks until the client is disconnected (e.g., by the login flow in bot.py)
            await client.run_until_disconnected()
        except Exception as e:
            logger.error(f"Userbot execution error: {e}")
            await asyncio.sleep(5)
        
        # If we reach here, the client was disconnected. 
        # The loop will restart, get the new client (if any), and resume.
        logger.info("Userbot: Loop exited. Re-evaluating client state...")
        await asyncio.sleep(1)


async def init_bot_identity():
    if not Config.BOT_TOKEN:
        return
    
    # Connect the bot and fetch its identity (non-blocking — does NOT run the loop)
    await ether_bot.start()
    me = await ether_bot.get_me()
    Config.BOT_USERNAME = me.username
    Config.BOT_MENTION = f"@{me.username}"
    logger.info(f"Bot UI: IDENTITY FETCHED (@{me.username})")


async def run_bot():
    if not Config.BOT_TOKEN:
        return
    
    # Keep the bot alive — ether_bot.start() was already called in init_bot_identity
    logger.info("Bot UI: RUNNING")
    await ether_bot.run()


async def startup():
    setup_logger()
    
    print("\n" + "=" * 60)
    print("    ______ _   _                      ")
    print("   |  ____| | | |                     ")
    print("   | |__  | |_| |__   ___ _ __        ")
    print("   |  __| | __| '_ \\ / _ \\ '__|       ")
    print("   | |____| |_| | | |  __/ |          ")
    print("   |______|\\__|_| |_|\\___|_|          ")
    print("\n      Hybrid Automation System v2.0   ")
    print("=" * 60 + "\n")
    
    logger.info("Initializing Ether Hybrid System...")
    
    # Validate channels file integrity
    if not validate_integrity():
        logger.critical("CORE INTEGRITY VIOLATION DETECTED")
        print("\n" + "!" * 60)
        print(" SECURITY ALERT: core/channels.py has been modified.")
        print(" Bot startup aborted to protect system integrity.")
        print("!" * 60 + "\n")
        sys.exit(1)
    
    logger.info("Core integrity check: PASSED")
    
    tasks = []
    
    # 1. Start web service FIRST so Render sees an open port immediately
    if Config.WEB_SERVICE:
        web_task = asyncio.create_task(run_web_service())
        tasks.append(web_task)
        # Give it a moment to bind the port before proceeding
        await asyncio.sleep(1)
    
    # 2. Fetch bot identity (sequential, fast)
    if Config.BOT_TOKEN:
        try:
            await init_bot_identity()
        except Exception as e:
            logger.error(f"Bot Identity: FAILED ({e})")
    
    # 3. Start userbot and bot UI as concurrent tasks
    userbot_task = asyncio.create_task(run_userbot())
    tasks.append(userbot_task)
    
    if Config.BOT_TOKEN:
        bot_task = asyncio.create_task(run_bot())
        tasks.append(bot_task)
    
    # 4. Keep alive — wait for all tasks (any failure is logged, not fatal)
    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        logger.error(f"System: CRITICAL FAILURE ({e})")
    finally:
        # Cleanup all remaining tasks on exit
        for task in tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


async def shutdown():
    logger.info("System: SHUTTING DOWN")
    await ether_bot.stop()
    await ether_db.close()
    logger.info("System: OFFLINE")


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