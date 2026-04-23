# E.D.I.T.H — Work In Progress

**Last updated:** April 23, 2026

All planned features and improvements. Pick one → write a plan → build.

---

## 🤖 AI Agents
> Waiting on Mac Mini arrival before starting

- [ ] `edith_skills/edith_agents.py` — base `Agent` class + Orchestrator routing layer
- [ ] **Scout** — web research agent (first to build)
- [ ] **Atlas** — study companion (explain CS/AI, quiz mode, paper breakdown)
- [ ] **Muse** — content ideas, captions, reel scripts from Notion content pipeline
- [ ] LM Studio swap: Claude API → local Qwen 2.5 32B Q4 (`localhost:1234`)
- [ ] Mode switching system: Active / Focus / Overnight / Standby

---

## 📊 Dashboard Interactivity
> Dashboard is currently read-only — all data flows Notion → HTML, never back

- [ ] Click-to-complete tasks in dashboard → instant Notion write-back
- [ ] Inline KPI logging — type new value directly in KPI tab, saves to Notion
- [ ] Quick-add task form in Tasks tab → creates Notion entry without opening Notion

---

## 🔔 Sync Notifications
- [ ] HUD toast popup when `edith_sync.py` finishes ("✅ Synced · 3s ago")
- [ ] Auto-sync countdown in header (live timer to next sync in watch mode)
- [ ] Error badge on affected tab if Notion query fails

---

## ⌨️ Keyboard Navigation
- [ ] `1`–`9` / `0` keys switch tabs
- [ ] `/` opens global search across all tabs
- [ ] `r` triggers manual sync (calls `edith_sync.py` via local server or file watch)

---

## 📱 Mobile Polish
- [ ] Hamburger nav for screens < 768px
- [ ] Swipe left/right to change tabs (touch events)
- [ ] Compact single-column card layout on portrait

---

## ⏱ Study / Pomodoro Timer
> Useful for CS Year 2 semester work

- [ ] HUD-styled focus timer (25/5 Pomodoro or custom) in Overview tab
- [ ] Link timer to a Study Hub topic — logs session time to Notion
- [ ] Session history in Study Hub tab

---

## ✨ Animation & Transitions — Phase 2
> Phase 1 done: scanlines, glitch, stagger, progress bars, count-up, boot sequence

- [ ] **Tab slide direction** — slide left/right based on tab index order (not just fade)
- [ ] **Clock digit flip** — flip card animation on clock seconds tick
- [ ] **Card hover lift** — `translateY(-3px)` + glow intensify on `.food-card`, `.project-full-card`, `.stat-card`
- [ ] **Header sweep** — single bright amber line sweeps across header every ~20s
- [ ] **Corner bracket draw-in** — HUD corner brackets animate in (draw stroke) on page load
- [ ] **Ripple on nav tabs** — material-style click ripple on tab button press
- [ ] **Data flash on sync** — injected sections briefly flash amber highlight when sync rewrites them
- [ ] **Morning brief typewriter** — `.brief-message` text types out character by character on load
- [ ] **Agent pulse rings** — expanding ring animation around online agent status dots
- [ ] **Progress bar shimmer** — shimmer highlight sweeps left→right across filled `.prog-fill` bars

---

## 🍜 Food Saver — Private Steps Remaining
> Public parts done. Private repo steps still needed.

- [ ] Create `🍜 Food Places` Notion DB (manual) → copy ID → add `NOTION_FOOD_DB` to `.env`
- [ ] `edith_notion.py`: add `add_food_place()`, `search_food_place()`, `update_food_place()`
- [ ] `edith_telegram_bot.py`: `add_food` / `edit_food` / `list_food` intents + inline keyboard flow
- [ ] Run `python edith_sync.py` to confirm `INJECT:FOOD` markers populate

---

## ✅ Completed
- [x] E.D.I.T.H dashboard — 10-tab HUD (Overview, Tasks, Calendar, KPI, Projects, Agents, Pipeline, Content, Research, Food)
- [x] Notion → Dashboard sync (`edith_sync.py` + `edith_builders.py`)
- [x] Outlook ICS calendar sync + filter buttons (ALL / THIS WEEK / TODAY)
- [x] Duplicate event deduplication
- [x] GitHub repo setup + `.gitignore` + `.env.example`
- [x] Food Saver — public parts (`edith_food.py`, dashboard tab, CSS, inject markers)
- [x] Animation Phase 1 — scanlines, logo glitch, progress bar fill, card stagger, count-up, boot sequence
