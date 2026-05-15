<div align="center">

<img src="https://i.ibb.co/rKM4mfnx/x.jpg" width="100%" alt="Ether Banner" />

# Ether Userbot System
**The Next-Gen Modular Telegram Framework**

[![GitHub Stars](https://img.shields.io/github/stars/LearningBotsOfficial/Ether?style=for-the-badge&logo=github&color=FFD700)](https://github.com/LearningBotsOfficial/Ether/stargazers) [![GitHub Forks](https://img.shields.io/github/forks/LearningBotsOfficial/Ether?style=for-the-badge&logo=github&color=94a3b8)](https://github.com/LearningBotsOfficial/Ether/network/members) [![GitHub Issues](https://img.shields.io/github/issues/LearningBotsOfficial/Ether?style=for-the-badge&color=F34F29)](https://github.com/LearningBotsOfficial/Ether/issues) [![GitHub Repo Size](https://img.shields.io/github/repo-size/LearningBotsOfficial/Ether?style=for-the-badge&color=5865F2)](https://github.com/LearningBotsOfficial/Ether)
<br>
[![Total Visits](https://hits.dwyl.com/LearningBotsOfficial/Ether.svg?style=for-the-badge&color=2ECC71)](https://hits.dwyl.com/LearningBotsOfficial/Ether) [![License](https://img.shields.io/github/license/LearningBotsOfficial/Ether?style=for-the-badge&color=94a3b8)](LICENSE) [![Python Version](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/) [![Last Commit](https://img.shields.io/github/last-commit/LearningBotsOfficial/Ether?style=for-the-badge&color=8E44AD)](https://github.com/LearningBotsOfficial/Ether/commits/main)

<p align="center">
  <b>Ether</b> is a high-performance, modular Telegram userbot architecture built with <b>Telethon</b> and <b>PyMongo Async</b>. Designed for developers who prioritize <b>security</b>, <b>sovereignty</b>, and <b>scalability</b>.
</p>

---

## Repository Statistics

<p align="center">
  <img src="https://metrics.lecoq.io/LearningBotsOfficial?template=classic&base=header,activity,community,repositories,metadata&languages=1&languages.limit=8&languages.threshold=0%25&theme=radical" width="100%" alt="GitHub Metrics" />
</p>

<p align="center">
  <img src="https://github-profile-trophy.vercel.app/?username=LearningBotsOfficial&theme=tokyonight&margin-w=15&no-bg=true" alt="GitHub Trophies" />
</p>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=LearningBotsOfficial&repo=Ether&theme=tokyo-night&bg_color=1a1b27&color=73daca&line=73daca&point=f7768e&area=true&hide_border=true" width="100%" alt="Activity Graph" />

---

[Features](#key-features) • [Structure](#repository-structure) • [Configuration](#configuration) • [Deployment](#deployment-options) • [Commands](#command-reference) • [Development](#plugin-development) • [Contributors](#contributors)

---

</div>

## Sovereignty & Security

Ether is engineered to eliminate the most common security risks in the userbot ecosystem.

*   **Zero String Session Reliance**: No third-party bots or risky session generators. Ether uses the official Telegram native authentication flow.
*   **Direct Auth**: Use the `/login` command to trigger an official Telegram OTP/2FA flow directly to your device.
*   **Encrypted Storage**: Your session data is stored securely on *your* server. It never touches a developer's database or public logs.
*   **No Middleware Risks**: Your credentials remain private. No Replit, no external middleware, just direct communication with Telegram servers.

---

## Key Features

*   **Hybrid Engine**: Orchestrates Telethon (Userbot) and Telegram Bot API concurrently for maximum flexibility.
*   **Plug-and-Play**: Drop any `.py` script into the `plugins/` directory to instantly extend functionality.
*   **Native Async**: Fully asynchronous architecture powered by `pymongo` native async drivers for high-concurrency handling.
*   **Health Monitoring**: Integrated FastAPI heartbeat service for 100% uptime on cloud providers.
*   **Containerized**: Production-ready Docker configuration for seamless local or cloud orchestration.

---

## Repository Structure

Ether follows a clean, modular directory structure for scalability and ease of development.

```text
Ether/
├── assets/             # Static media and branding
├── config/             # Environment and global configuration
├── core/               # The engine: Userbot, Bot API, and Loader
├── logs/               # Persistent system and session logs
├── plugins/            # Add-on functionality (.py files)
├── services/           # Logic layers for database interactions
├── storage/            # MongoDB connection management
├── utils/              # Shared helpers and logging tools
├── main.py             # Main entry point for the hybrid system
└── web_service.py      # FastAPI heartbeat service
```

---

## Tech Stack & Dependencies

Ether is built on a modern, high-performance stack designed for low latency and high concurrency.

| Technology | Purpose |
| :--- | :--- |
| [Python 3.11+](https://www.python.org/) | Core programming language |
| [Telethon](https://docs.telethon.dev/) | MTProto library for Telegram User & Bot API interaction |
| [PyMongo Async](https://www.mongodb.com/docs/drivers/pymongo/) | Native asynchronous driver for MongoDB |
| [FastAPI](https://fastapi.tiangolo.com/) | High-performance web framework for health monitoring |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server for production-grade web service |
| [uv](https://github.com/astral-sh/uv) | Ultra-fast Python package installer and resolver |
| [Docker](https://www.docker.com/) | Containerization and environment isolation |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variable management |

---

## Configuration

> [!CAUTION]
> **Security Warning:** Never expose your environment variables or upload your `.env` file to public repositories. Anyone with access to your `API_ID`, `API_HASH`, or `BOT_TOKEN` can take full control of your account. Use your hosting provider's dashboard to set these variables securely.

Ether uses environment variables for configuration. These can be set in a `.env` file for local deployment or in your cloud provider's dashboard.

| Variable | Requirement | Description |
| :--- | :--- | :--- |
| `API_ID` | Required | Your Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Required | Your Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | Required | Your Bot Token from [@BotFather](https://t.me/BotFather) |
| `OWNER_ID` | Required | Your numeric Telegram User ID |
| `MONGO_URI` | Required | MongoDB Atlas connection string |
| `BOT_USERNAME` | Required | Your Bot's username (without @) |
| `DB_NAME` | Optional | Database name (Default: `Ether`) |
| `DEBUG` | Optional | Set to `true` for verbose logging (Default: `false`) |
| `WEB_SERVICE` | Optional | Set to `true` for cloud keep-alive services |
| `PORT` | Optional | Port for the web service (Default: `8080`) |

---

## Deployment Options

Ether is designed to be deployed anywhere. Choose the platform that fits your needs.

<div align="center">

| [**Render**](https://render.com) | [**Heroku**](https://heroku.com) | [**JustRunMyApp**](https://justrunmy.app) |
| :---: | :---: | :---: |
| [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/LearningBotsOfficial/Ether) | [![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy/?template=https://github.com/LearningBotsOfficial/Ether) | [![Deploy to JustRunMyApp](https://img.shields.io/badge/Deploy%20Now-JustRunMyApp-5865F2?style=for-the-badge&logo=rocket)](https://justrunmy.app/) |

</div>

### Quick Start Guides

#### 1. Cloud Hosting (Render - Recommended)
Render provides the most stable environment for Ether with native Docker support.
1.  **Fork** this repository to your own GitHub account.
2.  Click the **Deploy to Render** button above.
3.  Connect your GitHub account and select the forked repository.
4.  Configure the **Environment Variables** (see [Configuration](#configuration)).
    *   **Crucial:** Ensure `WEB_SERVICE` is set to `true` to prevent the service from sleeping.
5.  Render will automatically build and deploy the container.

---

### Keep-Alive & Automation (Cloud)

Cloud providers like Render often put free-tier apps to "sleep" after inactivity. Use these tools to ensure Ether stays online 24/7.

#### UptimeRobot (Keep-Alive)
To prevent Render from sleeping, set up a monitor to ping your bot's URL:
1.  Go to [UptimeRobot](https://uptimerobot.com/) and create a free account.
2.  Click **Add New Monitor**.
3.  **Monitor Type**: `HTTP(s)`
4.  **Friendly Name**: `Ether Userbot`
5.  **URL**: Your Render app URL (e.g., `https://your-app.onrender.com/`)
6.  **Monitoring Interval**: Every `5 minutes`.
7.  Click **Create Monitor**.

#### Cron-job.org (Scheduled Tasks)
If you need to trigger specific bot actions or ensure the web service remains active via external triggers:
1.  Create an account at [Cron-job.org](https://cron-job.org/).
2.  Create a **New Cronjob**.
3.  **URL**: Your Render app URL.
4.  **Schedule**: Every 5 or 10 minutes.
5.  This acts as a secondary heart-beat for your bot.

---

#### 2. Heroku Deployment
Ideal for users familiar with the Heroku ecosystem.
1.  Click the **Deploy to Heroku** button above.
2.  Enter a unique app name and fill in the required environment variables.
3.  Once the build finishes, go to the **Resources** tab.
4.  **Important:** Turn off the `web` dyno and turn **ON** the `worker` dyno.
5.  Render will automatically build and deploy the container.

---

#### 3. JustRunMyApp (One-Click)
A simple, zero-config deployment platform.
1.  Click the **Deploy Now** button for JustRunMyApp above.
2.  Paste the repository URL: `https://github.com/LearningBotsOfficial/Ether`
3.  Follow the on-screen prompts to set your Environment Variables.
4.  Launch the app and wait for the status to show "Running".

#### 4. Docker Deployment (Local / VPS)
The preferred method for developers and privacy-focused users.
```bash
# 1. Clone the repository
git clone https://github.com/LearningBotsOfficial/Ether.git && cd Ether

# 2. Create and configure your .env file
cp .env.example .env
nano .env

# 3. Build and launch with Docker Compose
docker-compose up -d --build
```
> [!TIP]
> Using Docker Compose handles the health checks and automatic restarts for you.

#### 5. Manual Setup (Linux / VPS)
For advanced users who want full control over the environment.
```bash
# Update system & install git
sudo apt update && sudo apt install git -y

# Install uv (Recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup project
git clone https://github.com/LearningBotsOfficial/Ether.git && cd Ether
uv sync

# Run the bot
uv run main.py
```

---

### Post-Deployment: Authentication

Unlike traditional userbots, Ether doesn't use risky "String Sessions". Follow these steps to authorize your account:

1.  Open your bot on Telegram (the one created via `@BotFather`).
2.  Send the `/login` command.
3.  The bot will prompt you for your phone number.
4.  Enter the OTP sent by Telegram (and your 2FA password if enabled).
5.  **Success!** Your session is now securely stored in your own MongoDB database.

---

## Command Reference

Ether provides a suite of professional tools. All userbot commands are prefixed with `.` by default.

### Account & Session
| Command | Action | Platform |
| :--- | :--- | :--- |
| `/login` | Starts the native Telegram OTP/2FA login flow. | Official Bot |
| `/restart` | Restarts the bot instance to apply changes. | Official Bot |

### System & Utility
| Command | Description |
| :--- | :--- |
| `.alive` | View system status, uptime, and version info. |
| `.ping` | Check the current latency between Ether and Telegram. |
| `.help` | Open the interactive help menu (Inline Support). |
| `.commands` | Displays a full list of all loaded plugin commands. |

### Privacy & DM Shield
| Command | Description |
| :--- | :--- |
| `.allow` | Approves a user to message you in DMs. |
| `.disallow` | Revokes a user's permission and enables the shield. |
| `.setwelcome` | Sets a custom welcome message for new DM users (Reply). |
| `.clearwelcome` | Resets the DM welcome message to default. |
| `.setwarn <n>` | Set max warnings before a user is auto-blocked. |

### Shortcuts & Management
| Command | Description |
| :--- | :--- |
| `.shortcut <name>` | Save the replied message as a permanent shortcut. |
| `.get <name>` | Retrieve and send a saved shortcut. |
| `.delshortcut <n>` | Delete a specific shortcut by its name. |
| `.shortcuts` | List all your saved shortcuts and snips. |
| `.tagall <msg>` | Mention all members in a group safely. |
| `.fonts <text>` | Transform text into stylish mathematical fonts. |

---

## Plugin Development

Ether is built to be modular. You can add new features by creating a `.py` file in the `plugins/` directory. Each plugin must implement a `setup` function.

### The Setup Function
```python
def setup(ether, db, owner_id):
    """
    ether: The Telethon TelegramClient instance.
    db: The MongoDB motor database instance.
    owner_id: The numeric ID of the bot owner.
    """
```

### Pro Plugin Example: `notes.py`
This example shows how to use the database to save and retrieve simple notes.

```python
from telethon import events

def setup(ether, db, owner_id):
    # Collection reference
    notes = db["notes"]

    @ether.on(events.NewMessage(pattern=r"^\.save (\w+) (.+)$", outgoing=True))
    async def save_note(event):
        if event.sender_id != owner_id: return
        
        name = event.pattern_match.group(1)
        text = event.pattern_match.group(2)
        
        await notes.update_one(
            {"name": name}, 
            {"$set": {"content": text}}, 
            upsert=True
        )
        await event.edit(f"Note '{name}' saved successfully.")

    @ether.on(events.NewMessage(pattern=r"^\.getnote (\w+)$", outgoing=True))
    async def get_note(event):
        if event.sender_id != owner_id: return
        
        name = event.pattern_match.group(1)
        note = await notes.find_one({"name": name})
        
        if note:
            await event.edit(f"**Note {name}:**\n{note['content']}")
        else:
            await event.edit("Note not found.")
```

---

## Community & Support

Get help, report bugs, and stay updated with the latest plugins and features from the Ether ecosystem.

| Platform | Purpose | Link |
| :--- | :--- | :--- |
| **Telegram Channel** | Announcements, version releases, and security patches. | [Join Channel](https://t.me/Ether_Update) |
| **Telegram Group** | Community support, plugin troubleshooting, and general chat. | [Join Support](https://t.me/Ether_Support) |
| **Developer Network** | Collaboration with the LearningBotsOfficial ecosystem. | [Join Network](https://t.me/LearningBotsNetwork) |

> [!NOTE]
> For technical bug reports and detailed feature requests, please use the [GitHub Issues](https://github.com/LearningBotsOfficial/Ether/issues) tracker.

---

## Contributors

We appreciate the support and contributions from our amazing community.

<a href="https://github.com/LearningBotsOfficial/Ether/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=LearningBotsOfficial/Ether" />
</a>

---

## Terms of Use & Licensing

Ether is a professional open-source framework. By utilizing this software, you agree to the following:

*   **Attribution**: Original credits to **LearningBotsOfficial** must remain intact in all files.
*   **Forks**: Public forks must link back to the original repository.
*   **Commercial Use**: Reselling this project or distributing paid clones is strictly prohibited.
*   **Liability**: Use this software responsibly. We are not responsible for any account bans or misuse.

© 2026 [LearningBotsOfficial](https://github.com/LearningBotsOfficial). All rights reserved. Licensed under the [MIT License](LICENSE).

<div align="center">

**Made with love for the Open Source Community by [LearningBotsOfficial](https://github.com/LearningBotsOfficial)**

[Back to Top](#ether-userbot-system)

</div>
