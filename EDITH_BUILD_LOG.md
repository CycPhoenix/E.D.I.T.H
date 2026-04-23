# 🕶️ E.D.I.T.H OS — Build Log
**Date:** 29 March 2026
**Session:** Full system build from scratch
**Builder:** Claude (Cowork mode)

---

## What Was Built

E.D.I.T.H (Even Dead, I'm The Hero) — a personal AI Operating System inspired by Mau Pan's AI OS concept, custom-built for Ban. Dark amber/gold HUD aesthetic inspired by Tony Stark's E.D.I.T.H glasses from Spider-Man: Far From Home.

---

## System Components

### 1. 🖥️ Command Center Dashboard
**File:** `edith-command-center.html`
**Open:** Double-click the file in your browser.

A fully interactive single-file HTML dashboard with:
- Live clock, countdown timer, and sync timer
- 5 fully functional navigation tabs: Overview · Agents · Pipeline · Content · Research
- Task checkboxes that auto-sort (done tasks sink to the bottom)
- Empty state messages for all sections
- Scanline + grid overlay HUD aesthetic
- **Notion sync injection points** — run `edith_sync.py` to populate with real data

---

### 2. 🗄️ Notion OS (7 Live Databases)
All databases are live in your Notion workspace.

| Database | Notion URL | ID |
|---|---|---|
| 🏠 Hub Page (E.D.I.T.H Command Center) | https://www.notion.so/331ceab05e6d81a49590d2c85439b958 | — |
| 📋 Task Manager | https://www.notion.so/903584e20e7645ef92487d9bb44fcc5a | `903584e20e7645ef92487d9bb44fcc5a` |
| 🚀 Projects | https://www.notion.so/0c2fa008b3aa4d5195e17ec11d9ffa36 | `0c2fa008b3aa4d5195e17ec11d9ffa36` |
| 📊 KPI Digest | https://www.notion.so/7339d0186ba44062b9de72e771131fad | `7339d0186ba44062b9de72e771131fad` |
| 🎬 Content Pipeline | https://www.notion.so/448f9f35c8c7441a9683f72fb13a2650 | `448f9f35c8c7441a9683f72fb13a2650` |
| 📚 Study Hub | https://www.notion.so/0d96b2834ff8466ca67e04d4a1f6b984 | `0d96b2834ff8466ca67e04d4a1f6b984` |
| 🤝 Client Onboarding | https://www.notion.so/05bc936c8aef4dccbbce9ebd60e34909 | `05bc936c8aef4dccbbce9ebd60e34909` |

---

### 3. 🛠️ Skills Toolkit
**Folder:** `edith_skills/`
**Main file:** `edith_skills.py`

Python CLI with 7 AI-powered skills:

```bash
python edith_skills.py brief      # Morning brief — daily summary
python edith_skills.py email      # Draft an email in your tone
python edith_skills.py notes      # Summarise meeting notes
python edith_skills.py research   # Research any topic via web + Claude
python edith_skills.py tasks      # Add/view tasks in Notion
python edith_skills.py calendar   # View/add Google Calendar events
python edith_skills.py kpi        # Log + view weekly KPIs
```

---

### 4. 🔄 Notion → Dashboard Sync
**File:** `edith_skills/edith_sync.py`

Pulls live data from all 5 Notion databases and injects it into the dashboard HTML.

```bash
python edith_sync.py              # Sync once
python edith_sync.py --watch      # Auto-sync every 5 minutes
python edith_sync.py --watch --interval 600   # Every 10 minutes
```

Sections synced: Tasks · Projects · KPI · Content · Research

---

### 5. 🍜 Food Saver
**Files:** `edith_skills/edith_food.py` (new public), `edith_skills/edith_sync.py` (updated), `edith-command-center.html` (updated), `edith_skills/.env.example` (updated)

Track restaurants and cafes via Telegram, stored in a `🍜 Food Places` Notion database, synced to a new Food tab on the dashboard.

- **Dashboard tab:** Food grid with status filter (All / Visited / Want to Try / Regulars), cuisine emoji, would-return indicator, notes snippet, Maps link button
- **Sync:** `INJECT:FOOD` markers — add `NOTION_FOOD_DB` to `.env` to enable
- **Telegram (private):** `add_food` intent (inline button flow for Status/Cuisine/Would Return + free-text notes), `edit_food` intent, `list_food` intent
- **Notion schema:** Name · Google Maps URL · Cuisine · Status · Would Return · Notes · Date Visited

> Step 6 (edith_notion.py) and Step 7 (edith_telegram_bot.py) are private — implement per FOOD_SAVER_PLAN.md.

---

### 6. 🎤 Voice Agent
**Folder:** `edith_voice_agent/`
**Main file:** `edith_voice_agent.py`

Powered by Vapi (phone infrastructure) + ElevenLabs (voice clone).

```bash
python edith_voice_agent.py setup      # First-time setup wizard
python edith_voice_agent.py clone      # Clone your voice
python edith_voice_agent.py deploy     # Deploy the assistant
python edith_voice_agent.py call +66XXXXXXXXX   # Make an outbound call
python edith_voice_agent.py voicemail +66XXXXXXXXX  # Drop a voicemail
python edith_voice_agent.py logs       # View recent call transcripts
python edith_voice_agent.py status     # Check agent status
```

---

## Environment Setup

### `.env` file (in `edith_skills/` folder)

```env
ANTHROPIC_API_KEY=your_key_here
NOTION_TOKEN=your_notion_integration_token
NOTION_TASK_DB=903584e20e7645ef92487d9bb44fcc5a
NOTION_KPI_DB=7339d0186ba44062b9de72e771131fad
NOTION_PROJECT_DB=0c2fa008b3aa4d5195e17ec11d9ffa36
NOTION_CONTENT_DB=448f9f35c8c7441a9683f72fb13a2650
NOTION_RESEARCH_DB=0d96b2834ff8466ca67e04d4a1f6b984
SERPER_API_KEY=your_key_here
GCAL_CREDS_FILE=credentials.json
```

### Keys still needed
| Key | Where to get it | Priority |
|---|---|---|
| `NOTION_TOKEN` | notion.so/my-integrations | 🔴 Critical |
| `ANTHROPIC_API_KEY` | console.anthropic.com | 🔴 Critical |
| `SERPER_API_KEY` | serper.dev | 🟡 For research skill |
| `VAPI_API_KEY` | vapi.ai | 🟡 For voice agent |
| `ELEVENLABS_API_KEY` | elevenlabs.io | 🟡 For voice cloning |
| `GCAL_CREDS_FILE` | Google Cloud Console | 🟢 Optional |

---

## Activation Checklist

- [ ] Copy all files to `C:\Users\banbr\Documents\Claude\Projects\E.D.I.T.H`
- [ ] Run `cp .env.template .env` and fill in API keys
- [ ] Go to notion.so/my-integrations → create integration → copy token → paste as `NOTION_TOKEN`
- [ ] In Notion, share all 6 databases with your integration
- [ ] Run `pip install anthropic python-dotenv google-api-python-client google-auth-oauthlib requests`
- [ ] Run `python edith_sync.py` to pull live Notion data into the dashboard
- [ ] Open `edith-command-center.html` in browser
- [ ] Run `python edith_voice_agent.py setup` to configure the voice agent
- [ ] ⚡ E.D.I.T.H is online

---

## File Structure

```
E.D.I.T.H/
├── edith-command-center.html        ← Main dashboard (open in browser)
├── edith_skills/
│   ├── edith_skills.py              ← 7-skill Python CLI
│   ├── edith_sync.py                ← Notion → Dashboard sync
│   ├── .env.template                ← Copy to .env and fill in keys
│   ├── .env                         ← Your actual keys (DO NOT share)
│   └── SETUP.md                     ← Full setup guide
└── edith_voice_agent/
    ├── edith_voice_agent.py         ← Voice agent CLI
    ├── .env.template
    └── SETUP.md
```

---

## Security Reminders
- Never share API keys in chat or commit them to Git
- Add `.env` to your `.gitignore` if you version control this project
- If a key is ever exposed, revoke it immediately at the provider's dashboard

---

*Built with Claude Cowork mode · March 2026*
