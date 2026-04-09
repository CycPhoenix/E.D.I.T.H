# E.D.I.T.H — Personal AI Operating System

**Even Dead, I'm The Hero**

A personal AI OS built for day-to-day life management — tasks, projects, content pipeline, calendar, research, and KPIs — all synced from Notion into a single amber/gold HUD dashboard. Inspired by Tony Stark's E.D.I.T.H glasses from Spider-Man: Far From Home.

---

## What It Does

- **Live Dashboard** — single-file HTML command centre with 5 tabs: Overview, Agents, Pipeline, Content, Research
- **Notion Sync** — pulls live data from Notion databases and injects it into the dashboard
- **Outlook Calendar** — fetches ICS feed and renders a 14-day calendar with day filtering
- **Telegram Bot** — natural language interface to manage tasks, log content, run briefs, and trigger sync via chat or voice
- **Discord Notifications** — posts system status (online/offline) to a Discord channel via webhook
- **Voice Input** — transcribes voice messages through the Telegram bot using ElevenLabs

---

## Stack

| Layer | Tech |
|---|---|
| Dashboard | Vanilla HTML/CSS/JS (single file, no build step) |
| Backend | Python 3.10+ |
| Data | Notion API |
| Calendar | Outlook ICS (Office 365) |
| Bot | Telegram Bot API |
| AI | Anthropic Claude API (intent parsing, morning brief) |
| Voice | ElevenLabs STT |
| Notifications | Discord Webhooks |

---

## Project Structure

```
E.D.I.T.H/
├── edith-command-center.html   # Main dashboard (open in browser)
├── edith_skills/
│   ├── edith_sync.py           # Orchestrator — pulls Notion data, injects into dashboard
│   ├── edith_builders.py       # HTML section builders for each dashboard component
│   ├── edith_calendar.py       # ICS fetch, parse, and calendar HTML builder
│   ├── .env.example            # Environment variable template
│   └── SETUP.md                # Setup guide
└── edith_voice_agent/
    └── SETUP.md
```

> The Telegram bot, Notion action handlers, and notification logic are kept in a private repository.

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/E.D.I.T.H.git
cd E.D.I.T.H
```

**2. Install dependencies**
```bash
cd edith_skills
pip install python-dotenv anthropic requests
```

**3. Configure environment**
```bash
cp .env.example .env
# Fill in your API keys and database IDs
```

**4. Run a sync**
```bash
python edith_sync.py
```

**5. Open the dashboard**

Open `edith-command-center.html` in your browser. That's it — no server needed.

---

## How Sync Works

```
edith_sync.py
    ├── Queries all Notion databases (Tasks, Projects, KPIs, Content, Research)
    ├── Fetches Outlook ICS calendar feed
    ├── Builds HTML for each dashboard section via edith_builders.py
    └── Injects HTML between <!-- INJECT:TAG:START/END --> markers in the dashboard
```

The dashboard uses inject markers so sync can update any section independently without touching the rest of the file.

---

## Environment Variables

See `.env.example` for the full list. You'll need:
- Anthropic API key
- Notion API key + database IDs (Tasks, Projects, KPIs, Content, Research)
- Telegram bot token + your chat ID
- Discord webhook URL
- Outlook ICS URL (Settings → Calendar → Shared calendars → Publish → copy the `.ics` link)
- ElevenLabs API key + voice ID (optional, for voice input)

---

## Roadmap

- [ ] AI Agents (Scout, Muse, Atlas) — local inference via LM Studio on Mac Mini
- [ ] Agent mode switching (Active / Focus / Overnight / Standby)
- [ ] Orchestrator layer for natural language agent routing

---

*Built by Ban — CS/AI Year 2 @ APU*
