# E.D.I.T.H — Personal AI Operating System

**Even Dead, I'm The Hero**

A personal AI OS built around a single-file HTML dashboard that syncs live data from Notion, Outlook Calendar, and other sources. Dark amber/gold HUD aesthetic inspired by Tony Stark's E.D.I.T.H glasses from Spider-Man: Far From Home.

---

## Dashboard

`edith-command-center.html` — open directly in a browser, no server needed.

7 tabs, all data-driven via Notion sync:

| Tab | What it shows |
|---|---|
| Overview | Morning brief, stat cards, today's calendar, task preview, content pipeline mini, deadlines |
| Calendar | 14-day Outlook calendar with ALL / THIS WEEK / TODAY filter |
| Tasks | Full task list with priority/status filters and live completion toggle |
| Pipeline | Active projects with progress bars + KPI tracker |
| Content | Full content pipeline (Idea → Scripting → Filming → Editing → Posted) |
| Research | Study hub / research tracker |
| Food | Saved restaurants & cafes — status, would return, notes, Maps link |
| Agents | Agent status panel (in development) |

---

## How Sync Works

```
python edith_sync.py
```

Queries 5 Notion databases in parallel, fetches the Outlook ICS feed, builds HTML for each dashboard section, then rewrites the file using `<!-- INJECT:TAG:START/END -->` markers so each section updates independently.

**11 injected sections per sync:**
`TASKS` · `PROJECTS` · `KPI` · `CONTENT` · `RESEARCH` · `FOOD` · `CONTENT_MINI` · `DEADLINES` · `PIPELINE_HEALTH` · `TASKS_FULL` · `KPI_FULL` · `PROJECTS_FULL` · `CALENDAR` · `OVERVIEW_CALENDAR`

**Stat counters** (tasks done/total, active projects, content in progress, avg project progress, due badges) are updated via element ID injection alongside the HTML sections.

```bash
python edith_sync.py              # sync once
python edith_sync.py --watch      # sync every 5 minutes
python edith_sync.py --watch --interval 600   # custom interval (seconds)
```

---

## Module Layout

```
E.D.I.T.H/
├── edith-command-center.html      # Dashboard — open in browser
├── edith_skills/
│   ├── edith_sync.py              # Orchestrator: Notion queries + ICS fetch + inject
│   ├── edith_builders.py          # HTML builders for every dashboard section
│   ├── edith_calendar.py          # ICS fetch (Outlook-compatible), parse, calendar HTML
│   ├── .env.example               # Environment variable template
│   └── SETUP.md                   # Setup guide
└── edith_voice_agent/
    └── SETUP.md
```

> Telegram bot, Notion write actions, Discord/voice notification logic, and voice agent are in a private repository.

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

Builds HTML for the Food Places tab from Notion page data. Key functions:

- `build_food_tab` — food place cards with status badges, cuisine emoji, would-return indicator, notes snippet, Maps link button
- `build_food_stats` — returns stats dict (total, visited, want_to_try, regulars, would_return) for optional Overview use

Shared helpers: `prop()` (safe Notion property extractor), `strip_emoji()`, `norm_pct()`, `update_id()`, `esc()`.

---

## edith_calendar.py

- `_fetch_ics(url)` — fetches Outlook ICS with browser User-Agent (required to bypass Office 365 bot detection), validates `BEGIN:VCALENDAR` in response
- `_parse_ics_events(ics_text, days_ahead)` — parses VEVENT blocks into event dicts, deduplicates events that appear across multiple subscribed calendars (same title + time = one entry)
- `build_calendar(ics_text)` — 14-day calendar HTML with `data-date` attributes for JS filtering
- `build_overview_calendar(ics_text)` — compact today-only event list for the Overview card

---

## Notion Databases

| Database | Purpose |
|---|---|
| Task Manager | Personal tasks with priority, status, category, due date |
| Projects | Active projects with progress %, status, deadlines |
| KPI Digest | Weekly KPI tracking across life areas |
| Content Pipeline | Content ideas through to posted (Idea → Scripting → Filming → Editing → Posted) |
| Study Hub / Research | Research topics and study notes |

---

## Setup

**1. Install dependencies**
```bash
cd edith_skills
pip install python-dotenv anthropic requests
```

**2. Configure environment**
```bash
cp .env.example .env
# Fill in your keys
```

**3. Run sync**
```bash
python edith_sync.py
```

**4. Open dashboard**

Open `edith-command-center.html` in a browser. Run `--watch` in a background terminal to keep it live.

---

## Environment Variables

See `edith_skills/.env.example` for the full list. Core variables:

| Variable | Required for |
|---|---|
| `NOTION_TOKEN` | All Notion sync |
| `OUTLOOK_ICS_URL` | Calendar tab + Overview calendar card |
| `ANTHROPIC_API_KEY` | Telegram bot intent parsing + morning brief |
| `TELEGRAM_BOT_TOKEN` | Telegram bot (private repo) |
| `DISCORD_WEBHOOK_URL` | Online/offline status notifications (private repo) |
| `ELEVENLABS_API_KEY` | Voice transcription (private repo) |

---

## Roadmap

- [ ] AI Agents — Scout (research), Muse (content), Atlas (study)
- [ ] Orchestrator layer for natural language agent routing
- [ ] Local inference via LM Studio on Mac Mini (replacing Claude API for agent tasks)
- [ ] Agent mode switching — Active / Focus / Overnight / Standby

---

*Built by Ban · CS/AI Year 2 @ APU*
