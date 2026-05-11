import asyncio
import sys
import time
import os
import signal
import psutil

try:
    import uvloop # type: ignore
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
from utils.task_helper import safe_run

logger = get_logger("EtherMain")

# Global variables
plugin_loader = None
Config.START_TIME = time.time()
LOCK_FILE = "ether.lock"
shutdown_event = asyncio.Event()

def check_instance():
    """Prevent multiple instances from running simultaneously."""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                old_pid = int(f.read().strip())
            
            if psutil.pid_exists(old_pid):
                # Check if it's actually an Ether process (optional but safer)
                proc = psutil.Process(old_pid)
                if old_pid != os.getpid():
                    logger.critical(f"System: MULTI-INSTANCE DETECTED (PID: {old_pid} is already running)")
                    print(f"\n[!] Ether is already running (PID: {old_pid}).")
                    print("[!] Please stop the existing instance before starting a new one.\n")
                    sys.exit(1)
        except (ValueError, psutil.NoSuchProcess):
            # Stale lock file
            os.remove(LOCK_FILE)

def acquire_lock():
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    logger.info(f"System: Lock acquired (PID: {os.getpid()})")

def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
        logger.info("System: Lock released")

def signal_handler(sig, frame):
    logger.warning(f"System: Received signal {sig}, initiating graceful shutdown...")
    shutdown_event.set()

async def run_userbot():
    global plugin_loader
    client_wrapper = EtherUserClient()

    # Connect to database
    db_connected = await ether_db.connect()
    if not db_connected:
        logger.warning("Database: DISCONNECTED (Running in limited mode)")
    else:
        logger.info(f"Database: CONNECTED ({Config.DB_NAME})")
    
    while not shutdown_event.is_set():
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
            # If not authorized, don't run the client loop. 
            # Instead, wait for a few seconds and check again.
            try:
                # Wait for shutdown or just sleep
                done, pending = await asyncio.wait(
                    [asyncio.sleep(30), shutdown_event.wait()],
                    return_when=asyncio.FIRST_COMPLETED
                )
                for task in pending:
                    task.cancel()
                
                if shutdown_event.is_set():
                    break
                continue # Re-check status
            except Exception:
                await asyncio.sleep(5)
                continue
        else:
            try:
                me = await client.get_me()
                if me:
                    Config.OWNER_NAME = me.first_name
                    Config.OWNER_USERNAME = me.username
                    Config.OWNER_MENTION = f"<a href='tg://user?id={me.id}'>{me.first_name}</a>"
                    logger.info(f"Session: AUTHORIZED (User: {Config.OWNER_NAME})")
            except Exception as e:
                logger.error(f"Failed to fetch user details: {e}")
        
        set_userbot_client(client, client_wrapper)
        
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
        
        logger.info("Userbot: RUNNING (Awaiting commands)")
        
        try:
            # Wait for disconnection or shutdown signal
            done, pending = await asyncio.wait(
                [client.run_until_disconnected(), shutdown_event.wait()],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            for task in pending:
                task.cancel()
                
            if shutdown_event.is_set():
                logger.info("Userbot: Shutdown signal received, exiting loop...")
                break
                
        except Exception as e:
            # If we get "The key is not registered in the system", it means the session was logged out
            if "The key is not registered" in str(e):
                logger.error("Userbot: Session has been logged out or is invalid.")
                # We can't do much except re-check status in the next loop iteration
            else:
                logger.error(f"Userbot execution error: {e}")
            await asyncio.sleep(5)
        
        logger.info("Userbot: Loop exited. Re-evaluating client state...")
        await asyncio.sleep(1)

async def init_bot_identity():
    if not Config.BOT_TOKEN:
        return
    await ether_bot.start()
    me = await ether_bot.get_me()
    Config.BOT_USERNAME = me.username
    Config.BOT_MENTION = f"@{me.username}"
    logger.info(f"Bot UI: IDENTITY FETCHED (@{me.username})")

async def run_bot():
    if not Config.BOT_TOKEN:
        return
    logger.info("Bot UI: RUNNING")
    
    # We use wait to handle shutdown event alongside bot.run()
    try:
        done, pending = await asyncio.wait(
            [ether_bot.run(), shutdown_event.wait()],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
    except Exception as e:
        logger.error(f"Bot UI error: {e}")

async def startup():
    setup_logger()
    check_instance()
    acquire_lock()
    
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
    
    if not validate_integrity():
        logger.critical("CORE INTEGRITY VIOLATION DETECTED")
        release_lock()
        sys.exit(1)
    
    logger.info("Core integrity check: PASSED")
    
    tasks = []
    
    if Config.WEB_SERVICE:
        web_task = safe_run(run_web_service(), name="WebService")
        tasks.append(web_task)
        await asyncio.sleep(1)
    
    if Config.BOT_TOKEN:
        try:
            await init_bot_identity()
        except Exception as e:
            logger.error(f"Bot Identity: FAILED ({e})")
    
    userbot_task = safe_run(run_userbot(), name="UserbotCore")
    tasks.append(userbot_task)
    
    if Config.BOT_TOKEN:
        bot_task = safe_run(run_bot(), name="BotUI")
        tasks.append(bot_task)
    
    # Wait until shutdown signal
    await shutdown_event.wait()
    logger.info("System: Shutdown initiated, cleaning up tasks...")
    
    for task in tasks:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

async def shutdown():
    logger.info("System: PERFOMING FINAL CLEANUP")
    
    # Disconnect Userbot
    try:
        client_wrapper = EtherUserClient()
        await client_wrapper.disconnect()
    except Exception:
        pass
        
    # Stop Bot UI
    try:
        await ether_bot.stop()
    except Exception:
        pass
        
    # Close DB
    try:
        await ether_db.close()
    except Exception:
        pass
        
    release_lock()
    logger.info("System: OFFLINE")

def main():
    if Config.WEB_SERVICE and uvloop:
        uvloop.install()
    
    # Setup signal handlers
    if sys.platform != "win32":
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, signal_handler)
    else:
        # On Windows, signal handling is limited
        signal.signal(signal.SIGINT, signal_handler)
            
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        try:
            # We need a new loop for shutdown if the previous one is closed
            asyncio.run(shutdown())
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            release_lock() # Emergency release
        
        sys.exit(0)

if __name__ == "__main__":
    main()
    main()