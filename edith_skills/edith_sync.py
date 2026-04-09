#!/usr/bin/env python3
"""
E.D.I.T.H Sync — Pulls live data from Notion and stamps it into the
dashboard HTML so it always reflects reality.

Usage:
    python edith_sync.py              # sync once
    python edith_sync.py --watch      # sync every 5 minutes (Ctrl+C to stop)

Module layout:
    edith_sync.py       ← this file (orchestrator + Notion queries + inject)
    edith_builders.py   ← all HTML section builders + shared helpers
    edith_calendar.py   ← ICS fetch/parse + calendar HTML builders
"""

import os, json, re, time, argparse, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# Explicit path so this works regardless of cwd (e.g. when called from the bot)
load_dotenv(Path(__file__).parent / ".env")

from edith_builders import (
    prop, strip_emoji, norm_pct, update_id, compute_brief,
    build_tasks, build_projects, build_kpi, build_content,
    build_research, build_tasks_full, build_kpi_full,
    build_projects_full, build_content_mini,
    build_deadlines, build_pipeline_health,
)
from edith_calendar import _fetch_ics, build_calendar, build_overview_calendar

# ── CONFIG ────────────────────────────────────────────────────────────────────
NOTION_TOKEN    = os.getenv("NOTION_TOKEN", "")
TASK_DB         = os.getenv("NOTION_TASK_DB",    "903584e20e7645ef92487d9bb44fcc5a")
PROJECT_DB      = os.getenv("NOTION_PROJECT_DB", "0c2fa008b3aa4d5195e17ec11d9ffa36")
KPI_DB          = os.getenv("NOTION_KPI_DB",     "7339d0186ba44062b9de72e771131fad")
CONTENT_DB      = os.getenv("NOTION_CONTENT_DB", "448f9f35c8c7441a9683f72fb13a2650")
RESEARCH_DB     = os.getenv("NOTION_RESEARCH_DB","0d96b2834ff8466ca67e04d4a1f6b984")
OUTLOOK_ICS_URL = os.getenv("OUTLOOK_ICS_URL",  "")

DASHBOARD = Path(__file__).parent.parent / "edith-command-center.html"
HEADERS   = {
    "Authorization":  f"Bearer {NOTION_TOKEN}",
    "Content-Type":   "application/json",
    "Notion-Version": "2022-06-28",
}


# ── NOTION QUERY ──────────────────────────────────────────────────────────────

def notion_query(db_id: str) -> list:
    """Query a Notion database and return all pages."""
    url  = f"https://api.notion.com/v1/databases/{db_id}/query"
    body = json.dumps({"page_size": 50}).encode()
    req  = urllib.request.Request(url, data=body, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()).get("results", [])
    except urllib.error.HTTPError as e:
        print(f"  ⚠  Notion query failed for {db_id}: {e.code} {e.reason}")
        return []


# ── HTML INJECTION ────────────────────────────────────────────────────────────

def inject(html: str, tag: str, content: str) -> str:
    """Replace everything between <!-- INJECT:TAG:START --> and END markers."""
    pattern = rf"<!-- INJECT:{tag}:START -->.*?<!-- INJECT:{tag}:END -->"
    matched = []
    def replacer(m):
        matched.append(True)
        return f"<!-- INJECT:{tag}:START -->\n{content}\n        <!-- INJECT:{tag}:END -->"
    new_html = re.sub(pattern, replacer, html, flags=re.DOTALL)
    if not matched:
        print(f"  ⚠  INJECT:{tag} markers not found in dashboard HTML — skipping.")
    return new_html


# ── MAIN SYNC ─────────────────────────────────────────────────────────────────

def sync():
    if not NOTION_TOKEN:
        print("❌  NOTION_TOKEN not set. Add it to your .env file.")
        return False

    if not DASHBOARD.exists():
        print(f"❌  Dashboard not found at: {DASHBOARD}")
        return False

    print(f"🔄  Syncing Notion → E.D.I.T.H dashboard...")
    ts = datetime.now().strftime("%H:%M:%S")

    # ── Fetch Notion data ──
    tasks    = notion_query(TASK_DB)
    projects = notion_query(PROJECT_DB)
    kpis     = notion_query(KPI_DB)
    content  = notion_query(CONTENT_DB)
    research = notion_query(RESEARCH_DB)

    print(f"   ↳ {len(tasks)} tasks · {len(projects)} projects · {len(kpis)} KPIs · {len(content)} content · {len(research)} research")

    # ── Derived stats ──
    priorities, tasks_due, deadlines, active_projects = compute_brief(tasks, projects)
    done_tasks    = sum(1 for p in tasks if strip_emoji(str(prop(p,"Status",fallback=""))).lower() in ("done","complete","completed") or prop(p,"Done",fallback=False))
    total_tasks   = len(tasks)
    pending_tasks = total_tasks - done_tasks
    high_tasks    = sum(1 for p in tasks if strip_emoji(str(prop(p,"Priority",fallback=""))).lower() == "high"
                        and strip_emoji(str(prop(p,"Status",fallback=""))).lower() not in ("done","complete","completed"))
    def _cstatus(p): return strip_emoji(str(prop(p,"Status",fallback=""))).lower()
    cnt_ideas   = sum(1 for p in content if _cstatus(p) == "idea")
    cnt_prod    = sum(1 for p in content if _cstatus(p) in ("scripting","filming","editing"))
    posted      = sum(1 for p in content if _cstatus(p) == "posted")
    in_progress = sum(1 for p in content if _cstatus(p) not in ("posted",""))
    avg_progress = round(sum(norm_pct(prop(p,"Progress",fallback=0)) for p in projects) / max(len(projects),1), 1) if projects else 0

    html = DASHBOARD.read_text(encoding="utf-8")

    # ── Section injections ──
    html = inject(html, "TASKS",           build_tasks(tasks))
    html = inject(html, "PROJECTS",        build_projects(projects))
    html = inject(html, "KPI",             build_kpi(kpis))
    html = inject(html, "CONTENT",         build_content(content))
    html = inject(html, "RESEARCH",        build_research(research))
    html = inject(html, "CONTENT_MINI",    build_content_mini(content))
    html = inject(html, "DEADLINES",       build_deadlines(projects))
    html = inject(html, "PIPELINE_HEALTH", build_pipeline_health(projects))
    html = inject(html, "TASKS_FULL",      build_tasks_full(tasks))
    html = inject(html, "KPI_FULL",        build_kpi_full(kpis))
    html = inject(html, "PROJECTS_FULL",   build_projects_full(projects))

    # ── Calendar — fetch ICS once, share between both calendar sections ──
    if OUTLOOK_ICS_URL:
        print(f"  📅  ICS URL loaded (length {len(OUTLOOK_ICS_URL)}, starts: {OUTLOOK_ICS_URL[:40]}...)")
    else:
        print("  ⚠  OUTLOOK_ICS_URL is empty — check .env is loading correctly")
    ics_text = _fetch_ics(OUTLOOK_ICS_URL) if OUTLOOK_ICS_URL else ""
    cal_html = build_calendar(ics_text)
    if cal_html:
        html = inject(html, "CALENDAR", cal_html)
    html = inject(html, "OVERVIEW_CALENDAR", build_overview_calendar(ics_text))

    # ── Brief numbers ──
    html = update_id(html, "brief-priorities", str(priorities))
    html = update_id(html, "brief-tasks-due",  str(tasks_due))
    html = update_id(html, "brief-agents",     "4")
    _pri_text = f'{priorities} {"priority" if priorities == 1 else "priorities"}'
    _dl_text  = f'{deadlines} {"deadline" if deadlines == 1 else "deadlines"}'
    html = re.sub(r'(<span id="brief-priorities-text">)[^<]*(</span>)',
                  lambda m: f"{m.group(1)}{_pri_text}{m.group(2)}", html)
    html = re.sub(r'(<span id="brief-deadlines-text">)[^<]*(</span>)',
                  lambda m: f"{m.group(1)}{_dl_text}{m.group(2)}", html)

    # ── Overview stat cards ──
    html = update_id(html, "stat-tasks",    f"{done_tasks}/{total_tasks}")
    html = update_id(html, "stat-projects", str(active_projects))
    html = update_id(html, "stat-content",  str(in_progress))
    html = update_id(html, "overall-pct",   f"{avg_progress}%")

    # ── Task badge ──
    due_badge = (f"{tasks_due} DUE TODAY" if tasks_due
                 else f"{high_tasks} HIGH PRIORITY" if high_tasks
                 else f"{pending_tasks} PENDING")
    html = update_id(html, "tasks-due-badge", due_badge)

    # ── Content tab stats ──
    html = update_id(html, "cnt-ideas",  str(cnt_ideas))
    html = update_id(html, "cnt-prod",   str(cnt_prod))
    html = update_id(html, "cnt-posted", str(posted))
    html = update_id(html, "cnt-total",  str(len(content)))

    # ── Subtitles ──
    html = re.sub(
        r'(<div[^>]+id="content-header-sub"[^>]*>)[^<]*(</div>)',
        lambda m: f'{m.group(1)}{len(content)} pieces tracked · {posted} posted · {in_progress} in progress{m.group(2)}',
        html
    )
    deadline_word = "deadline" if deadlines == 1 else "deadlines"
    html = re.sub(
        r'(<div[^>]+id="pipeline-header-sub"[^>]*>)[^<]*(</div>)',
        lambda m: f'{m.group(1)}{active_projects} active projects · {deadlines} {deadline_word} this week{m.group(2)}',
        html
    )

    DASHBOARD.write_text(html, encoding="utf-8")
    print(f"✅  Dashboard fully synced at {ts}")
    print(f"   {priorities} priorities · {tasks_due} tasks due · {deadlines} deadlines · {active_projects} projects active")
    return True


def main():
    parser = argparse.ArgumentParser(description="E.D.I.T.H Notion sync")
    parser.add_argument("--watch",    action="store_true", help="Sync every 5 minutes")
    parser.add_argument("--interval", type=int, default=300, help="Watch interval in seconds (default 300)")
    args = parser.parse_args()

    if args.watch:
        print(f"👁  Watch mode — syncing every {args.interval}s. Press Ctrl+C to stop.\n")
        while True:
            sync()
            print(f"   Next sync in {args.interval}s...\n")
            time.sleep(args.interval)
    else:
        sync()


if __name__ == "__main__":
    main()
