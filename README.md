# E.D.I.T.H — Personal AI Operating System

**Even Dead, I'm The Hero**

A personal AI OS built around a single-file HTML dashboard that syncs live data from Notion, Outlook Calendar, and other sources. Dark amber/gold HUD aesthetic inspired by Tony Stark's E.D.I.T.H glasses from Spider-Man: Far From Home.

---

## Dashboard

10-tab HUD served via a local Python server (`edith_server.py`). Run the server first, then open `http://localhost:5000` in a browser.

| Tab | What it shows |
|---|---|
| Overview | Morning brief, stat cards, today's calendar, task preview, content pipeline mini, deadlines |
| Tasks | Full task list with priority/status filters, live completion toggle, quick-add form |
| Calendar | 14-day Outlook calendar with ALL / THIS WEEK / TODAY filter |
| KPI | Weekly KPI tracker with inline logging (click to edit) |
| Projects | Active projects with progress bars |
| Agents | AI agent status panel — Scout, Atlas, Muse |
| Pipeline | Content pipeline (Idea → Scripting → Filming → Editing → Posted) |
| Content | Full content view |
| Research | Study hub / research tracker |
| Food | Saved restaurants & cafes — status, would return, notes, Maps link |

---

## How to Run

**1. Start the server**
```bash
cd edith_skills
python edith_server.py
```

**2. Open the dashboard**

Go to `http://localhost:5000` in your browser.

**3. Keep data live (optional)**
```bash
python edith_sync.py --watch        # sync every 5 minutes
python edith_sync.py --watch --interval 600   # custom interval (seconds)
```

---

## How Sync Works

```bash
python edith_sync.py
```

Queries 6 Notion databases in parallel, fetches the Outlook ICS feed, builds HTML for each dashboard section, then rewrites the file using `<!-- INJECT:TAG:START/END -->` markers so each section updates independently.

**Injected sections per sync:**
`TASKS` · `PROJECTS` · `KPI` · `CONTENT` · `RESEARCH` · `FOOD` · `CONTENT_MINI` · `DEADLINES` · `PIPELINE_HEALTH` · `TASKS_FULL` · `KPI_FULL` · `PROJECTS_FULL` · `CALENDAR` · `OVERVIEW_CALENDAR`

---

## Module Layout

```
E.D.I.T.H/
├── edith-command-center.html      # Dashboard HTML shell (slim — no inline CSS/JS)
├── edith_static/
│   ├── edith.css                  # All dashboard styles
│   └── edith.js                   # All dashboard JS
├── edith_skills/
│   ├── edith_sync.py              # Orchestrator: Notion queries + ICS fetch + inject
│   ├── edith_builders.py          # HTML builders for every dashboard section
│   ├── edith_calendar.py          # ICS fetch (Outlook-compatible), parse, calendar HTML
│   ├── edith_food.py              # Food Places HTML builder
│   ├── edith_server.py            # stdlib HTTP server — serves dashboard + Notion write-back API
│   ├── edith_agents.py            # AI agents — Orchestrator, Scout, Atlas, Muse
│   ├── .env.example               # Environment variable template
│   └── SETUP.md                   # Setup guide
└── edith_voice_agent/
    └── SETUP.md
```

> Telegram bot, Notion write actions, and notification logic are in a private repository.

---

## edith_server.py

Local stdlib HTTP server (no Flask). Key endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Serves the dashboard HTML |
| `/static/*` | GET | Serves CSS + JS from `edith_static/` |
| `/api/status` | GET | Alive check + last sync timestamp |
| `/api/sync` | POST | Triggers `edith_sync.py` subprocess |
| `/api/task/complete` | POST | PATCHes Notion task to Done |
| `/api/task/create` | POST | Creates new task in Notion |
| `/api/kpi/log` | POST | Logs KPI value to Notion |
| `/api/pomodoro/log` | POST | Logs Pomodoro session to Notion |

---

## edith_agents.py

AI agent layer. Runs locally via LM Studio or falls back to Claude API.

- `Orchestrator` — routes messages to the right agent
- `Scout` — web research, article summarisation
- `Atlas` — CS/AI study companion, explain concepts, quiz mode (reads Obsidian vault)
- `Muse` — content ideas, captions, reel scripts

**Mode system:**

| Mode | Active agents |
|---|---|
| `active` | Scout, Atlas, Muse |
| `focus` | Scout, Atlas |
| `overnight` | None (dormant) |
| `standby` | None (dormant) |

Run via CLI: `python edith_agents.py`

---

## edith_builders.py

Builds HTML for every section from raw Notion API responses. Key functions:

- `build_tasks` / `build_tasks_full` — task cards with priority badges and overdue detection
- `build_projects` / `build_projects_full` — project cards with progress bars
- `build_kpi` / `build_kpi_full` — KPI tracker with weekly grid and progress bars
- `build_content` / `build_content_mini` — content pipeline cards by status
- `build_research` — research/study hub entries
- `build_deadlines` — upcoming project deadlines
- `build_pipeline_health` — project health summary
- `compute_brief` — derives morning brief stats (priorities, tasks due, deadlines, active projects)

---

## edith_food.py

Builds HTML for the Food Places tab from Notion page data.

- `build_food_tab` — food place cards with status badges, cuisine emoji, would-return indicator, notes snippet, Maps link button
- `build_food_stats` — returns stats dict (total, visited, want_to_try, regulars, would_return) for Overview use

---

## edith_calendar.py

- `_fetch_ics(url)` — fetches Outlook ICS with browser User-Agent (required to bypass Office 365 bot detection)
- `_parse_ics_events(ics_text, days_ahead)` — parses VEVENT blocks, deduplicates events across subscribed calendars
- `build_calendar(ics_text)` — 14-day calendar HTML with `data-date` attributes for JS filtering
- `build_overview_calendar(ics_text)` — compact today-only event list for the Overview card

---

## Notion Databases

| Database | Purpose |
|---|---|
| Task Manager | Personal tasks with priority, status, category, due date |
| Projects | Active projects with progress %, status, deadlines |
| KPI Digest | Weekly KPI tracking across life areas |
| Content Pipeline | Content ideas through to posted |
| Study Hub / Research | Research topics and study notes |
| Food Places | Saved restaurants & cafes with Maps links |

---

## Setup

**1. Clone and install dependencies**
```bash
git clone <repo>
cd E.D.I.T.H/edith_skills
pip install -r requirements.txt
```

**2. Configure environment**
```bash
cp .env.example .env
# Fill in your keys
```

**3. Start the server**
```bash
python edith_server.py
```

**4. Open dashboard**

Go to `http://localhost:5000`

---

## Environment Variables

See `edith_skills/.env.example` for the full list. Core variables:

| Variable | Required for |
|---|---|
| `NOTION_TOKEN` | All Notion sync |
| `OUTLOOK_ICS_URL` | Calendar tab + Overview calendar card |
| `ANTHROPIC_API_KEY` | Agent fallback (Claude API) |
| `TELEGRAM_BOT_TOKEN` | Telegram bot (private repo) |
| `DISCORD_WEBHOOK_URL` | Online/offline notifications (private repo) |
| `OBSIDIAN_VAULT` | Atlas knowledge base (`E:/Brain`) |

---

## Roadmap

- [x] AI Agents — Scout, Atlas, Muse + Orchestrator (`edith_agents.py`)
- [x] Agent mode switching — Active / Focus / Overnight / Standby
- [ ] Local inference via LM Studio — `unsloth/functiongemma-270m-it-GGUF` (Orchestrator) + `qwen/qwen3.5-9b` (agents)
- [ ] Telegram → Agents wiring (all messages routed through Orchestrator)
- [ ] Obsidian vault integration — Atlas reads from `E:/Brain`
- [ ] Live Agents tab on dashboard

---

*Built by Ban · CS/AI Year 2 @ APU*
