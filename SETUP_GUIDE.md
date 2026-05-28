# 🧑‍🎓 Beginner Setup Guide (Zero Coding Knowledge Required)

This guide assumes you have **never installed anything for development** in your life. Follow it line-by-line. Whenever you see a black box, that is a **command** you must paste into a tool called the *terminal* (also called *command prompt* on Windows).

---

## 0. Mental model: what we're installing and why

| Tool | Why we need it | Install once? |
|---|---|---|
| **Git** | Downloads code from GitHub | Yes |
| **Node.js v20+** | Runs the website (frontend) | Yes |
| **Python 3.11** | Runs the AI server (backend) | Yes |
| **Docker Desktop** | Lets us run everything with ONE command | Yes |
| **VS Code** | The text editor where you'll see code | Yes |

---

## 1. Install the tools

### Windows

1. **Git** → https://git-scm.com/download/win → download → install with all defaults.
2. **Node.js (LTS, v20+)** → https://nodejs.org → click the green LTS button → run installer.
3. **Python 3.11** → https://www.python.org/downloads/ → ⚠️ on the FIRST install screen, **tick the box "Add Python to PATH"**, then click Install Now.
4. **Docker Desktop** → https://www.docker.com/products/docker-desktop/ → install → restart computer → open Docker Desktop and wait until the whale icon at the bottom-left turns green.
5. **VS Code** → https://code.visualstudio.com → install with all defaults.

### macOS

```bash
# install Homebrew first if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install git node python@3.11
brew install --cask docker visual-studio-code
```

Open Docker Desktop once so it asks for permissions.

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y git curl python3.11 python3.11-venv python3-pip
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
# Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER && newgrp docker
sudo snap install --classic code
```

---

## 2. Verify everything is installed

Open your terminal:
- Windows: press `Win` → type **PowerShell** → Enter
- macOS: press `Cmd + Space` → type **Terminal** → Enter
- Linux: `Ctrl + Alt + T`

Paste these one at a time and press Enter. Each must print a version number, NOT "command not found".

```bash
git --version
node --version
npm --version
python --version
docker --version
```

If any of them fail → re-install that tool.

---

## 3. Download this project from GitHub

Pick a comfortable place on your computer (e.g. `Documents`):

```bash
cd ~/Documents
git clone https://github.com/yashonaath-06/AI-Powered-Interview-Preparation-Platform.git
cd AI-Powered-Interview-Preparation-Platform
```

You should now see files like `README.md`, `docker-compose.yml`, `backend/`, `frontend/`.

---

## 4. Create your secrets file

The project ships with a **template** called `.env.example`. You make a real copy named `.env`:

```bash
# macOS / Linux
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

Open `.env` in VS Code and **change `JWT_SECRET`** to any long random string.
You can leave the AI keys (`GROQ_API_KEY`, `OPENAI_API_KEY`) blank — we have free fallbacks.

> 💡 If later you want even better AI quality, get a **free** Groq key at https://console.groq.com (no credit card required) and paste it.

---

## 5. (Easiest) Run everything with Docker

Make sure Docker Desktop is running (whale icon green), then:

```bash
docker compose up --build
```

The first run takes ~5-10 minutes (it downloads images and installs everything).
When you see logs from `interview_frontend` saying `ready - started server on 0.0.0.0:3000`, open your browser to:

- 🌐 **Website:** http://localhost:3000
- 📖 **API docs:** http://localhost:8000/docs

To stop: press `Ctrl + C` in the terminal, or run `docker compose down`.

---

## 6. (Manual mode) Run frontend & backend separately

Open **two** terminals.

### Terminal 1 — Backend

```bash
cd backend
python -m venv .venv
# activate the virtual environment:
#   macOS/Linux:
source .venv/bin/activate
#   Windows PowerShell:
.\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see `Application startup complete.` Visit http://localhost:8000/docs.

### Terminal 2 — Frontend

```bash
cd frontend
cp .env.local.example .env.local       # (Windows: Copy-Item)
npm install
npm run dev
```

Visit http://localhost:3000.

---

## 7. Common errors & fixes

| Error | Meaning | Fix |
|---|---|---|
| `'python' is not recognized` | Python wasn't added to PATH on Windows | Re-run installer, tick "Add to PATH" |
| `EACCES` on Linux when running docker | User not in docker group | `sudo usermod -aG docker $USER`, log out, log back in |
| `port 3000 already in use` | Another app is using the port | `npx kill-port 3000` or change port in `package.json` |
| `port 8000 already in use` | Same idea | Stop the other process or change the port in the `uvicorn` command |
| `psycopg2` install fails | Missing Postgres dev headers | Use Docker mode instead (Section 5) |
| Browser says "blocked" for camera/mic | Browser permissions | Click the lock icon next to URL → allow camera and mic |

---

## 8. What to do next

You're set up! From here:
1. Read `README.md` and `ARCHITECTURE.md`.
2. Watch the agent build features phase by phase.
3. Each phase comes as its own pull-request on GitHub — review and merge it.

Welcome to your final-year project. 🚀
