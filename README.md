# Coda → BKMS Attendance Automation

This project automates attendance tracking for BAPS Kishore sabhas. It pulls attendance data from a **Coda-based roster** and syncs it to the **BKMS (BAPS Kishore Management System)** portal — eliminating all manual entry.

The UI has two tabs, each running a separate bot:

| Tab | Bot | What it does |
|-----|-----|--------------|
| **Attendance Bot** | `bkms.py` | Reads Coda attendance and marks it in BKMS |
| **User Update Bot** | `bkms_user_update.py` | Bulk-updates user profiles in BKMS (e.g. Saturday Sabha checkbox) |

---

## Tech Stack

- **Frontend:** React + MUI (dark theme)
- **Backend:** FastAPI + Uvicorn
- **Automation:** Selenium WebDriver (Chrome)
- **Data:** Coda API, Pandas
- **Messaging:** Telegram Bot API

---

## Running Locally

### 1. Install dependencies

**macOS / Linux**
```sh
chmod +x install_dependencies.sh
./install_dependencies.sh
```

**Windows**
```bat
install_dependencies.bat
```

### 2. Configure environment variables

Copy and fill in both `.env` files (see [Environment Variables](#environment-variables) below).

### 3. Start the backend

Run from the **project root** (not inside `backend/`):

```sh
PYTHONPATH=. uvicorn backend.index:app --reload --port 8002
```

The API will be available at **`http://localhost:8002`**.

### 4. Start the frontend

```sh
cd ui
npm start
```

Open **`http://localhost:3000`** in your browser.

---

## Free Coda Button Setup

If you want a Coda button to trigger the bot and open Chrome for CAPTCHA on a user's own Mac, that Mac must run the backend locally. Coda does not open Chrome directly. The flow is:

1. Coda Pack sends a request to the user's public ngrok URL.
2. ngrok forwards the request to the local FastAPI backend on that Mac.
3. The backend starts Selenium.
4. Chrome opens on that same Mac.

### First-Time Setup

Do these steps once on each Mac that should run the bot.

1. Clone this repo.
2. Fill in `backend/.env` with the BKMS, Coda, and Telegram values.
3. Reserve a free ngrok domain at:

```text
https://dashboard.ngrok.com/domains
```

4. Run:

```sh
chmod +x setup_and_run_mac.sh
./setup_and_run_mac.sh
```

During setup you may be prompted for:

- your ngrok authtoken
- your reserved ngrok domain
- a `BOT_TRIGGER_TOKEN` for Coda

When setup finishes, you will have:

- a public URL such as `https://your-domain.ngrok-free.dev`
- a trigger token saved in `backend/.env`
- a running local backend
- a running ngrok tunnel

### Daily Use

After first-time setup, use these commands:

1. Start everything:

```sh
bash local_bot.sh
```

2. Check local backend health:

```sh
bash local_bot.sh health-local
```

Expected response:

```json
{"status":"ok"}
```

3. Check public ngrok health:

```sh
bash local_bot.sh health
```

4. Trigger a real test run:

```sh
bash local_bot.sh test-run "2026-04-12" "Sunday K1" "Yes" "No" "Yes"
```

5. Stop everything:

```sh
bash local_bot.sh stop
```

### Connect The Coda Pack

In the Pack connection screen, use:

- Endpoint URL: `https://YOUR_DOMAIN`
- Token: `YOUR_BOT_TRIGGER_TOKEN`

The Pack will call:

```text
POST https://YOUR_DOMAIN/run-bot
```

with a request body like:

```json
{
  "date": "2026-04-12",
  "group": "Sunday K1",
  "sabhaHeld": "Yes",
  "p2Guju": "No",
  "prepCycleDone": "Yes"
}
```

Other supported endpoints:

- `/run-bot-stream`
- `/run-goshthi`
- `/run-goshthi-stream`
- `/run-user-update`
- `/run-user-update-stream`

### Important Limitations

- The Mac must be powered on and logged in.
- Chrome opens on the Mac running the backend, not on the device that clicked the Coda button.
- This is free, but it is not a true cloud-hosted browser automation flow.

---

## Using the App

### Attendance Bot tab

1. Select the **date** — choose from the 4 pre-computed Sundays (2 weeks ago, last week, this Sunday, next Sunday).
2. Select the **sabha group** — Saturday K1, Saturday K2, Sunday K1, or Sunday K2.
3. Answer **Was Sabha Held?** If Yes, answer the two follow-up questions.
4. Click **Run Bot**.
5. A Chrome window opens and auto-fills your BKMS credentials. **Solve the CAPTCHA within 60 seconds** (a countdown timer is shown). Do NOT click Sign In yourself — the bot does it after the countdown.
6. The bot marks attendance in BKMS and a Telegram notification is sent on success.

### User Update Bot tab

1. Paste **User IDs** (one per line) into the text area.
2. Click **Run Bot**.
3. A Chrome window opens and auto-fills BKMS credentials. **Solve the CAPTCHA within 60 seconds**.
4. The bot searches each user ID, opens their profile, ticks the Saturday Sabha checkbox (if not already ticked), and saves.
5. Real-time logs stream into the page as each user is processed.
6. Known validation errors (missing student type, missing parent email) are handled automatically. Any unknown error halts the bot and is shown in the log.

---

## Environment Variables

### Backend — `backend/.env`

```env
# Telegram — main notification group
MAIN_GROUP_TELEGRAM_TOKEN=
MAIN_GROUP_TELEGRAM_CHAT_ID=

# Telegram — per-group channels (used by scheduled poll workflows)
SAT_K1_TELEGRAM_TOKEN=
SAT_K1_TELEGRAM_CHAT_ID=
SAT_K2_TELEGRAM_TOKEN=
SAT_K2_TELEGRAM_CHAT_ID=
SUN_K1_TELEGRAM_TOKEN=
SUN_K1_TELEGRAM_CHAT_ID=
SUN_K2_TELEGRAM_TOKEN=
SUN_K2_TELEGRAM_CHAT_ID=

# Coda API
CODA_API_KEY=
CODA_DOC_ID=

# Coda table IDs (one per sabha group)
SATURDAY_K1_TABLE_ID=
SATURDAY_K2_TABLE_ID=
SUNDAY_K1_TABLE_ID=
SUNDAY_K2_TABLE_ID=

# BKMS login credentials
BKMS_ID=
BKMS_EMAIL=
BKMS_PASSWORD=
BKMS_ACCESS_TYPE=Regional
```

### Frontend — `ui/.env`

```env
REACT_APP_API_URL=http://localhost:8002
REACT_APP_VALID_EMAIL=
REACT_APP_VALID_PASSWORD=
```

> Both the **Attendance Bot** and **User Update Bot** tabs are always enabled. No additional env vars are needed to unlock them.

> **Contact Vraj for the actual values of all `.env` variables.**

---

## Running Tests

### Backend — 100% coverage required

```sh
# From project root
CODA_API_KEY=test python3 -m pytest --cov=backend --cov-report=term-missing -q
```

### Frontend — 100% coverage required

```sh
cd ui
npm run test:ci
```

---

## Scheduled Telegram Polls

Two GitHub Actions workflows send weekly Telegram polls to each sabha group asking kishores to mark their own attendance:

| Workflow | Schedule | Prefix |
|----------|----------|--------|
| `sat_polls.yml` | Every Saturday | `SAT_` |
| `sun_polls.yml` | Every Sunday | `SUN_` |

These run automatically in CI. The relevant Telegram tokens/chat IDs are stored as GitHub repository secrets matching the `SAT_*` / `SUN_*` env var names above.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/run-bot` | Run the Attendance Bot for a given group/date |
| `POST` | `/run-user-update-stream` | Stream real-time logs from the User Update Bot (SSE) |

---

## Collaboration Guidelines

- **Branching:** All branches must start with `feature/`, e.g. `feature/improve-telegram-alert`.
- **Testing:** All changes must be tested locally before opening a PR.
- **Pull Request checklist:**
  - Brief summary of changes
  - Screenshot or short video of the feature working
  - Screenshot showing **100% coverage** for both backend and frontend

---

## Project Setup Reference

### macOS / Linux — quick start

```sh
cd /path/to/coda-to-bkms

# Install everything
chmod +x install_dependencies.sh && ./install_dependencies.sh

# Terminal 1 — backend (port 8002)
PYTHONPATH=. uvicorn backend.index:app --reload --port 8002

# Terminal 2 — frontend
cd ui && npm start
```

### Windows — quick start

```bat
cd path\to\coda-to-bkms
install_dependencies.bat

:: Terminal 1 — backend (port 8002)
set PYTHONPATH=.
uvicorn backend.index:app --reload --port 8002

:: Terminal 2 — frontend
cd ui
npm start
```

Open **`http://localhost:3000`** once both servers are running.
