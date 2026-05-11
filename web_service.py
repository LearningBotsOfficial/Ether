import asyncio
from fastapi import FastAPI
import uvicorn
from config.config import Config
from utils.logger import get_logger

logger = get_logger("EtherWeb")

app = FastAPI(title="Ether Userbot", description="Keep-alive web service for Ether Userbot")

@app.get("/")
async def root():
    return {"status": "alive", "bot": "Ether Userbot", "version": "2.0"}

async def run_web_service():
    if not Config.WEB_SERVICE:
        logger.info("Web service is disabled via config.")
        return
        
    logger.info(f"Starting web service on port {Config.PORT}...")
    
    config = uvicorn.Config(
        app=app, 
        host="0.0.0.0", 
        port=Config.PORT, 
        log_level="warning"
    )
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except asyncio.CancelledError:
        logger.warning("Web service cancelled and shutting down.")
