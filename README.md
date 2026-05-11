<div align="center">

<img src="https://i.ibb.co/rKM4mfnx/x.jpg" width="60%" />

# ⚡ Ether Userbot System
**The Next-Gen Modular Telegram Framework**

![Stars](https://img.shields.io/github/stars/LearningBotsOfficial/Ether)
![Forks](https://img.shields.io/github/forks/LearningBotsOfficial/Ether)

[![License](https://img.shields.io/github/license/LearningBotsOfficial/Ether?style=for-the-badge&color=94a3b8)](LICENSE)

<p align="center">
  <b>Ether</b> is a high-performance, modular Telegram userbot architecture built with <b>Telethon</b> + <b>MongoDB</b>. Designed for developers who prioritize security, speed, and clean code.
</p>


---

</div>

## 🛡️ Why Ether is Safe?

**Zero String Session Reliance**

Unlike traditional userbots that require risky "String Sessions" generated via third-party  bots, Ether utilizes a **native authentication flow**.

* **Self-Hosted Sovereignty:** Deploy on your own VPS. Your credentials never leave your environment.
* **Direct-to-Telegram Login:** Use the `/login` command to trigger an official Telegram OTP/2FA flow directly to your device.
* **Encrypted Local Storage:** Session data is stored securely on *your* server, not in a cloud database or a developer's logs.
* **No Middleware Risks:** No Replit, no Heroku logs, and no external session string generators.

---

## ⭐ Features

* **🛡️ Secure Auth:** Native login system (No String Session required)
* **⚡ Hybrid Engine:** Leverages Telethon (Userbot) and Bot API simultaneously
* **🔐 Privacy First:** Full 2FA support and local session management
* **📦 Plugin Architecture:** Easily drop new `.py` scripts into the `plugins/` folder
* **👉 There are many more features — visit the plugins folder or deploy to explore all.**

---

---
<br>

<div align="center">

<a href="https://render.com/deploy?repo=https://github.com/LearningBotsOfficial/Ether">
  <img src="https://render.com/images/deploy-to-render-button.svg" width="170">
</a>

<br>


</div>

<details>

<summary align="center">

  ` 🚀 Render Deployment Guide`

</summary>

---

### 1️⃣ Collect Required Details

| Variable | Description |
|---|---|
| API_ID | Telegram API ID |
| API_HASH | Telegram API Hash |
| BOT_TOKEN | BotFather Bot Token |
| OWNER_ID | Your Telegram Numeric ID |
| MONGO_URI | MongoDB Connection URI |

### Required Links

- https://my.telegram.org
- https://t.me/BotFather
- https://mongodb.com

---

### 2️⃣ Fork Repository

- ⭐ Star the repository
- 🍴 Fork Ether to your GitHub account

---

### 3️⃣ Deploy to Render

Click the **Deploy to Render** button.

Then:

- Login to Render
- Connect GitHub
- Select your forked Ether repository

---

### 4️⃣ Configure Render

#### Recommended Plan

- Free Plan

---

### Fill in Start Command

```bash
python main.py
```

---

## Add Environment Variables

| Key | Value |
|---|---|
| API_ID | Your Telegram API ID |
| API_HASH | Your Telegram API Hash |
| BOT_TOKEN | Your Bot Token |
| OWNER_ID | Your Telegram User ID |
| MONGO_URI | MongoDB URI |
| WEB_SERVICE | true |

---

After adding all variables:

✅ Click **Create Web Service**

⏳ Deployment usually takes around **1–2 minutes**

---

### 5️⃣ Final Telegram Setup

Open **@BotFather**

- Send `/mybots`
- Select your bot
- Open **Bot Settings**
- Enable **Inline Mode**

---

Then open your deployed bot and run:

```bash
/login
```

Complete the login process:

- Phone Number Verification
- OTP Verification
- 2FA Password (if enabled)

---

## ✅ Deployment Complete

Use:

```bash
.help
```

to see all available commands.



</details>

---

<br>

<div align="center">

<a href="https://justrunmy.app/">
  <img src="https://img.shields.io/badge/Deploy%20Now-JustRunMyApp-5865F2?style=for-the-badge">
</a>

</div>

<br>

<details>

<summary align="center">

`🚀 JustRunMyApp Deployment Guide`

</summary>

---

# 1️⃣ Collect Required Details

| Variable | Description |
|---|---|
| API_ID | Telegram API ID |
| API_HASH | Telegram API Hash |
| BOT_TOKEN | BotFather Bot Token |
| OWNER_ID | Your Telegram Numeric ID |
| MONGO_URI | MongoDB Connection URI |

---

# 2️⃣ Fork & Download Repository

- ⭐ Star Ether
- 🍴 Fork the repository
- 📦 Download repository ZIP

---

# 3️⃣ Upload ZIP File

- Login to JustRunMyApp
- Upload the ZIP file
- Wait for processing
- Fill all required environment variables

⏳ Deployment usually takes around **1–2 minutes**

---

# 4️⃣ Final Telegram Setup

Open **@BotFather**

- Send `/mybots`
- Select your bot
- Open **Bot Settings**
- Enable **Inline Mode**

---

Then open your deployed bot and run:

```bash
/login
```

Complete:

- Phone Number Verification
- OTP Verification
- 2FA Password (if enabled)

---

# ✅ Deployment Complete

Use:

```bash
.help
```

to see all available commands.

---

</details>

---

# ☁️ Deploy on VPS

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv git screen -y

# Clone repository
git clone https://github.com/LearningBotsOfficial/Ether.git

# Open project folder
cd Ether

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Create environment file
nano .env

# Start screen session
screen -S ether

# Start Ether
python main.py

# Detach screen session:
# CTRL + A then D
```

---

## 🤝 Community & Support

<p align="center">
  <a href="https://t.me/Ether_Update">
    <img src="https://img.shields.io/badge/🚀%20Ether%20Userbot-Official%20Channel-5865F2?style=for-the-badge&logo=telegram">
  </a>
  <a href="https://t.me/EtherSupport">
    <img src="https://img.shields.io/badge/💬%20Ether%20Support-Get%20Help-2ECC71?style=for-the-badge&logo=telegram">
  </a>
</p>

<p align="center">
  <a href="https://t.me/LearningBotsNetwork">
    <img src="https://img.shields.io/badge/📢%20Learning%20Bots-Updates%20%26%20Ecosystem-F39C12?style=for-the-badge&logo=telegram">
  </a>
</p>

---

## ⚠️ License & Terms

Ether is source-available software developed by **LearningBotsOfficial**.

By using, modifying, or sharing this project, you agree to the following terms:

- Original credits to **LearningBotsOfficial** must remain intact.
- Any public fork or modified version must provide proper attribution to:
  **LearningBotsOfficial/Ether**
- Reselling this project or distributing paid/public clones is prohibited.
- Republishing this project under another name without permission is prohibited.
- Personal and private modifications are allowed.
- Use this software responsibly and follow Telegram's Terms of Service.

Failure to follow these terms may result in permission being revoked.

© 2026 LearningBotsOfficial. All rights reserved.


---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by [LearningBotsOfficial](https://github.com/LearningBotsOfficial)**

[⬆ Back to Top](#-ether-userbot-system)

</div>
