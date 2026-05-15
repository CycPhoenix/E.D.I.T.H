"""
edith_builders.py
=================
All HTML section builders for the E.D.I.T.H dashboard.
Each function takes Notion page data and returns an HTML string
ready to be injected via the INJECT markers.

Also contains shared helper utilities (esc, prop, strip_emoji, etc.)
used across the sync and calendar modules.
"""

import re
from datetime import datetime, timezone


# ── SHARED HELPERS ────────────────────────────────────────────────────────────

def _empty(icon: str, msg: str) -> str:
    return (f'<div class="empty-state">'
            f'<div class="empty-icon">{icon}</div>'
            f'<div class="empty-msg">{msg}</div>'
            f'</div>')


def esc(s) -> str:
    """Basic HTML escaping."""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def strip_emoji(s: str) -> str:
    """Remove leading emoji + space from Notion values like '🔴 High' → 'High'."""
    s = s.strip()
    if s and ord(s[0]) > 127:
        parts = s.split(' ', 1)
        return parts[1] if len(parts) > 1 else ''
    return s


def norm_pct(value) -> int:
    """Notion percent fields are stored as 0–1. Normalize to 0–100."""
    v = float(value or 0)
    return int(v * 100 if 0 < v <= 1 else v)


def prop(page: dict, *names, fallback=""):
    """
    Extract a property value — tries multiple names so the script works even
    if your Notion column is called 'Task' instead of 'Name', etc.
    """
    props = page.get("properties", {})
    for name in names:
        if name not in props:
            continue
        p = props[name]
        t = p.get("type", "")
        if t == "title":
            parts = p.get("title", [])
            return parts[0]["plain_text"] if parts else fallback
        if t == "rich_text":
            parts = p.get("rich_text", [])
            return parts[0]["plain_text"] if parts else fallback
        if t == "select":
            s = p.get("select")
            return s["name"] if s else fallback
        if t == "multi_select":
            return [x["name"] for x in p.get("multi_select", [])]
        if t == "checkbox":
            return p.get("checkbox", False)
        if t == "number":
            v = p.get("number")
            return v if v is not None else fallback
        if t == "date":
            d = p.get("date")
            return d["start"] if d else fallback
        if t == "status":
            s = p.get("status")
            return s["name"] if s else fallback
    return fallback


def update_id(html: str, el_id: str, value: str) -> str:
    """Replace the text content of an element with a specific id."""
    pattern = rf'(<[^>]+\bid="{el_id}"[^>]*>)[^<]*(</)'
    def replacer(m):
        return f"{m.group(1)}{value}{m.group(2)}"
    return re.sub(pattern, replacer, html)


# ── SECTION BUILDERS ──────────────────────────────────────────────────────────

def build_tasks(pages: list) -> str:
    BADGE = {"HIGH": "badge-high", "MED": "badge-med", "MEDIUM": "badge-med", "LOW": "badge-low"}
    def norm_priority(raw: str) -> str:
        cleaned = raw.strip()
        for prefix in ("🔴 ", "🟡 ", "🔵 ", "🟢 "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
        return cleaned.upper()
    todo, done = [], []
    for p in pages:
        name     = esc(prop(p, "Task Name", "Name", "Task", "Title", fallback="Untitled"))
        status   = str(prop(p, "Status", fallback="")).lower()
        priority = norm_priority(str(prop(p, "Priority", fallback="Low")))
        is_done  = status in ("done", "complete", "completed") or prop(p, "Done", fallback=False) is True
        badge    = BADGE.get(priority, "badge-low")
        done_cls = "done" if is_done else ""
        html = (f'<div class="task-item">'
                f'<div class="task-check {done_cls}"></div>'
                f'<div class="task-text {done_cls}">{name}</div>'
                f'<div class="task-badge {badge}">{priority}</div>'
                f'</div>')
        (done if is_done else todo).append(html)
    if not todo and not done:
        return _empty("📋", "Ow, today's empty — <span>no tasks lined up</span>.")
    return "\n        ".join(todo + done)


def build_projects(pages: list) -> str:
    COLORS = [
        ("var(--amber-dim)", "var(--amber)"),
        ("#2a6b8a",          "var(--blue)"),
        ("#6b2a8a",          "var(--purple)"),
        ("#1a6b3a",          "var(--green)"),
    ]
    STATUS_MAP = {
        "In Progress": ("badge-inprog", "IN PROGRESS"),
        "Planning":    ("badge-plan",   "PLANNING"),
        "Done":        ("badge-done",   "DONE"),
        "Blocked":     ("badge-block",  "BLOCKED"),
        "Completed":   ("badge-done",   "DONE"),
    }
    rows = []
    for i, p in enumerate(pages[:6]):
        name     = esc(prop(p, "Project Name", "Name", "Project", "Title", fallback="Untitled"))
        status   = strip_emoji(str(prop(p, "Status", fallback="Planning")))
        progress = norm_pct(prop(p, "Progress", fallback=0))
        due      = str(prop(p, "Deadline", "Due Date", "Due", fallback=""))
        category = esc(strip_emoji(str(prop(p, "Type", "Category", fallback="Project"))))
        c_start, c_end = COLORS[i % len(COLORS)]
        badge_cls, badge_lbl = STATUS_MAP.get(status, ("badge-plan", "PLANNING"))
        due_str = f" · Due {due[:10]}" if due else ""
        rows.append(
            f'<div class="project-row">'
            f'<div class="project-icon" style="background:rgba(255,179,71,0.08)">📁</div>'
            f'<div style="min-width:0;flex:0 0 220px;">'
            f'<div class="project-name">{name}</div>'
            f'<div class="project-meta">{category}{due_str}</div>'
            f'</div>'
            f'<div class="project-progress">'
            f'<div class="prog-header"><span class="prog-label">Progress</span>'
            f'<span class="prog-val">{progress}%</span></div>'
            f'<div class="prog-bar"><div class="prog-fill" style="width:{progress}%;'
            f'background:linear-gradient(90deg,{c_start},{c_end})"></div></div>'
            f'</div>'
            f'<div class="proj-badge {badge_cls}">{badge_lbl}</div>'
            f'</div>'
        )
    if not rows:
        return _empty("🚀", "No active projects — <span>clean slate</span>.")
    return "\n      ".join(rows)


def build_kpi(pages: list) -> str:
    if not pages:
        return _empty("📊", "No KPI data yet — <span>add weekly entries to Notion</span>.")
    latest = pages[0]
    study_hrs  = float(prop(latest, "Study Hours",     fallback=0) or 0)
    tasks_done = float(prop(latest, "Tasks Completed", fallback=0) or 0)
    tasks_tot  = float(prop(latest, "Tasks Total",     fallback=1) or 1)
    gpa_target = norm_pct(prop(latest, "GPA Target",   fallback=0))
    content    = float(prop(latest, "Content Posted",  fallback=0) or 0)
    metrics = [
        ("Tasks Completed", f"{int(tasks_done)}/{int(tasks_tot)}", int(min(100, tasks_done / max(tasks_tot,1) * 100))),
        ("Study Hours",     f"{int(study_hrs)}h",                  int(min(100, study_hrs / 40 * 100))),
        ("Content Posted",  str(int(content)),                     int(min(100, content / 7 * 100))),
        ("GPA Target",      f"{gpa_target}%",                      min(100, gpa_target)),
    ]
    rows = []
    for label, val_str, pct in metrics:
        rows.append(
            f'<div class="kpi-row">'
            f'<div class="kpi-header">'
            f'<span class="kpi-label">{label}</span>'
            f'<span class="kpi-val">{val_str}</span>'
            f'</div>'
            f'<div class="kpi-bar"><div class="kpi-fill" style="width:{pct}%"></div></div>'
            f'</div>'
        )
    return "\n        ".join(rows)


def build_content(pages: list) -> str:
    STATUS_CSS = {
        "Idea":      ("s-idea",    "💡 IDEA"),
        "Scripting": ("s-script",  "✍️ SCRIPTING"),
        "Filming":   ("s-filming", "🎬 FILMING"),
        "Editing":   ("s-editing", "✂️ EDITING"),
        "Posted":    ("s-posted",  "✅ POSTED"),
    }
    PLATFORM_CSS = {"Instagram": "p-ig", "TikTok": "p-tt", "LinkedIn": "p-li", "YouTube": "p-yt"}
    cards = []
    for p in pages[:8]:
        title     = esc(prop(p, "Title", "Name", fallback="Untitled"))
        hook      = esc(prop(p, "Hook", "Description", fallback=""))
        status    = strip_emoji(str(prop(p, "Status", fallback="Idea")))
        publish   = str(prop(p, "Publish Date", "Date", fallback=""))
        platforms = prop(p, "Platform", "Platforms", fallback=[])
        if isinstance(platforms, str):
            platforms = [platforms]
        s_cls, s_lbl  = STATUS_CSS.get(status, ("s-idea", "💡 IDEA"))
        platform_html = " ".join(
            f'<div class="content-platform {PLATFORM_CSS.get(pl, "p-ig")}">{esc(pl)}</div>'
            for pl in platforms
        )
        date_html = f'<div class="content-date">Publish: {publish[:10]}</div>' if publish else ""
        hook_html = f'<div class="content-hook">{hook}</div>' if hook else ""
        cards.append(
            f'<div class="content-full-card">'
            f'<div class="content-full-header">'
            f'<div class="content-full-title">{title}</div>'
            f'<div class="content-status-badge {s_cls}">{s_lbl}</div>'
            f'</div>'
            f'{hook_html}'
            f'<div class="content-meta">{platform_html}{date_html}</div>'
            f'</div>'
        )
    if not cards:
        return _empty("✍️", "No content pieces yet — <span>ideas incoming</span>.")
    return "\n    ".join(cards)


def build_research(pages: list) -> str:
    TAG_COLORS = {
        "AI":             "rgba(192,132,252,0.1);color:var(--purple)",
        "ML":             "rgba(79,195,247,0.1);color:var(--blue)",
        "NLP":            "rgba(79,195,247,0.1);color:var(--blue)",
        "Complete":       "rgba(57,255,138,0.1);color:var(--green)",
        "Completed":      "rgba(57,255,138,0.1);color:var(--green)",
        "In Progress":    "rgba(255,179,71,0.15);color:var(--amber)",
        "To Review":      "rgba(255,68,68,0.1);color:var(--red)",
        "Assignment":     "rgba(255,179,71,0.1);color:var(--amber)",
        "Research Paper": "rgba(255,179,71,0.1);color:var(--amber)",
        "Lecture Notes":  "rgba(255,179,71,0.1);color:var(--amber)",
    }
    DEFAULT_TAG = "rgba(255,179,71,0.08);color:var(--text-dim)"
    items = []
    for p in pages[:8]:
        title   = esc(prop(p, "Topic", "Name", "Title", fallback="Untitled"))
        summary = esc(prop(p, "Notes", "Summary", "Description", fallback="No notes."))
        date    = str(prop(p, "Date", "Created", fallback=""))[:10]
        tags    = prop(p, "Subject", "Tags", "Category", fallback=[])
        if isinstance(tags, str):
            tags = [tags]
        tags_html = " ".join(
            f'<div class="research-tag" style="background:{TAG_COLORS.get(t, DEFAULT_TAG)}">{esc(t)}</div>'
            for t in tags
        )
        items.append(
            f'<div class="research-item">'
            f'<div class="research-header">'
            f'<div class="research-title">{title}</div>'
            f'<div class="research-date">{date}</div>'
            f'</div>'
            f'<div class="research-summary">{summary}</div>'
            f'<div class="research-tags">{tags_html}</div>'
            f'</div>'
        )
    if not items:
        return _empty("🔍", "No research saved — <span>run a query above</span>.")
    return "\n    ".join(items)


def build_tasks_full(pages: list) -> str:
    """Full task list for the Tasks tab with data attributes for JS filtering."""
    BADGE = {"HIGH": "badge-high", "MED": "badge-med", "MEDIUM": "badge-med", "LOW": "badge-low"}
    def norm_priority(raw):
        cleaned = raw.strip()
        for prefix in ("🔴 ", "🟡 ", "🔵 ", "🟢 "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
        return cleaned.upper()

    today = datetime.now().strftime("%Y-%m-%d")
    items = []
    for p in pages:
        name     = esc(prop(p, "Task Name", "Name", "Task", "Title", fallback="Untitled"))
        status   = str(prop(p, "Status", fallback="")).lower()
        priority = norm_priority(str(prop(p, "Priority", fallback="Low")))
        category = str(prop(p, "Category", fallback=""))
        due      = str(prop(p, "Due Date", "Deadline", fallback=""))[:10]
        is_done  = status in ("done", "complete", "completed") or prop(p, "Done", fallback=False) is True
        badge    = BADGE.get(priority, "badge-low")
        done_cls = "done" if is_done else ""

        if isinstance(category, list):
            cats = category
        elif category:
            cats = [category]
        else:
            cats = []
        cat_html = " ".join(f'<span class="task-cat">{esc(strip_emoji(c))}</span>' for c in cats)

        due_html = ""
        if due:
            due_cls = "overdue" if due < today and not is_done else ""
            due_html = f'<span class="task-due {due_cls}">Due {due}</span>'

        page_id  = p.get("id", "").replace("-", "")
        complete_btn = (
            f'<button class="task-complete-btn" data-page-id="{page_id}" '
            f'title="Mark Done in Notion">✓</button>'
        ) if not is_done and page_id else ""

        items.append(
            f'<div class="task-full-item" data-priority="{priority.lower()}" data-done="{str(is_done).lower()}" data-page-id="{page_id}">'
            f'<div class="task-full-check {done_cls}"></div>'
            f'<div class="task-full-body">'
            f'<div class="task-full-name {done_cls}">{name}</div>'
            f'<div class="task-full-meta">{cat_html}{due_html}'
            f'<span class="task-badge {badge}">{priority}</span>'
            f'</div></div>'
            f'{complete_btn}</div>'
        )
    if not items:
        return _empty("📋", "No tasks found — <span>add tasks in Notion</span>.")
    return "\n".join(items)


def build_kpi_full(pages: list) -> str:
    """Full KPI history for KPI tab — one card per weekly entry."""
    if not pages:
        return _empty("📊", "No KPI entries yet — <span>add weekly data to Notion</span>.")

    RATING_CSS = {
        "Excellent": "kpi-rating-excellent",
        "Good":      "kpi-rating-good",
        "Average":   "kpi-rating-average",
        "Poor":      "kpi-rating-poor",
    }
    cards = []
    for p in pages[:8]:
        week       = esc(prop(p, "Week", fallback="—"))
        study_hrs  = float(prop(p, "Study Hours",     fallback=0) or 0)
        tasks_done = float(prop(p, "Tasks Completed", fallback=0) or 0)
        tasks_tot  = float(prop(p, "Tasks Total",     fallback=0) or 0)
        gpa_target = norm_pct(prop(p, "GPA Target",   fallback=0))
        content    = float(prop(p, "Content Posted",  fallback=0) or 0)
        rating_raw = strip_emoji(str(prop(p, "Rating", fallback="")))
        wins       = esc(str(prop(p, "Wins",     fallback="")))
        blockers   = esc(str(prop(p, "Blockers", fallback="")))

        rating_css = RATING_CSS.get(rating_raw, "kpi-rating-average")
        rating_lbl = rating_raw if rating_raw else "—"

        tasks_pct   = int(min(100, tasks_done / max(tasks_tot, 1) * 100)) if tasks_tot else 0
        study_pct   = int(min(100, study_hrs / 40 * 100))
        content_pct = int(min(100, content / 7 * 100))

        notes_html = ""
        if wins or blockers:
            notes_html = '<div class="kpi-week-notes">'
            if wins:     notes_html += f'<strong>Wins:</strong> {wins}<br>'
            if blockers: notes_html += f'<strong>Blockers:</strong> {blockers}'
            notes_html += '</div>'

        cards.append(
            f'<div class="kpi-week-card">'
            f'<div class="kpi-week-header">'
            f'<div class="kpi-week-title">{week}</div>'
            f'<div class="kpi-week-badge {rating_css}">{rating_lbl}</div>'
            f'</div>'
            f'<div class="kpi-week-grid">'
            f'<div class="kpi-mini-stat"><div class="kpi-mini-val">{int(tasks_done)}/{int(tasks_tot)}</div><div class="kpi-mini-lbl">TASKS</div></div>'
            f'<div class="kpi-mini-stat"><div class="kpi-mini-val">{int(study_hrs)}h</div><div class="kpi-mini-lbl">STUDY HRS</div></div>'
            f'<div class="kpi-mini-stat"><div class="kpi-mini-val">{int(content)}</div><div class="kpi-mini-lbl">CONTENT</div></div>'
            f'<div class="kpi-mini-stat"><div class="kpi-mini-val">{gpa_target}%</div><div class="kpi-mini-lbl">GPA TARGET</div></div>'
            f'</div>'
            f'<div class="kpi-row"><div class="kpi-header"><span class="kpi-label">Tasks Completed</span>'
            f'<span class="kpi-val" data-kpi-label="Tasks Completed" title="Click to edit">{tasks_pct}%</span></div>'
            f'<div class="kpi-bar"><div class="kpi-fill" style="width:{tasks_pct}%"></div></div></div>'
            f'<div class="kpi-row"><div class="kpi-header"><span class="kpi-label">Study Hours</span>'
            f'<span class="kpi-val" data-kpi-label="Study Hours" title="Click to edit">{int(study_hrs)}h</span></div>'
            f'<div class="kpi-bar"><div class="kpi-fill" style="width:{study_pct}%"></div></div></div>'
            f'<div class="kpi-row"><div class="kpi-header"><span class="kpi-label">Content Posted</span>'
            f'<span class="kpi-val" data-kpi-label="Content Posted" title="Click to edit">{int(content)}</span></div>'
            f'<div class="kpi-bar"><div class="kpi-fill" style="width:{content_pct}%"></div></div></div>'
            f'{notes_html}'
            f'</div>'
        )
    return "\n".join(cards)


def build_projects_full(pages: list) -> str:
    """Full project cards for Projects tab."""
    COLORS = [
        ("var(--amber-dim)", "var(--amber)"),
        ("#2a6b8a",          "var(--blue)"),
        ("#6b2a8a",          "var(--purple)"),
        ("#1a6b3a",          "var(--green)"),
    ]
    STATUS_MAP = {
        "In Progress": ("badge-inprog", "IN PROGRESS"),
        "Planning":    ("badge-plan",   "PLANNING"),
        "Done":        ("badge-done",   "DONE"),
        "Blocked":     ("badge-block",  "BLOCKED"),
    }
    today = datetime.now().strftime("%Y-%m-%d")
    cards = []
    for i, p in enumerate(pages):
        name     = esc(prop(p, "Project Name", "Name", "Title", fallback="Untitled"))
        status   = strip_emoji(str(prop(p, "Status", fallback="Planning")))
        progress = norm_pct(prop(p, "Progress", fallback=0))
        deadline = str(prop(p, "Deadline", "Due Date", fallback=""))[:10]
        desc     = esc(str(prop(p, "Description", fallback="")))
        ptype    = esc(strip_emoji(str(prop(p, "Type", "Category", fallback=""))))
        c_start, c_end = COLORS[i % len(COLORS)]
        badge_cls, badge_lbl = STATUS_MAP.get(status, ("badge-plan", "PLANNING"))
        due_html = ""
        if deadline:
            due_cls = "overdue" if deadline < today and status.lower() not in ("done","completed") else ""
            due_html = f'<span class="proj-deadline {due_cls}">📅 {deadline}</span>'
        type_html = f'<span class="proj-type">{ptype}</span>' if ptype else ""
        desc_html = f'<div class="project-full-desc">{desc}</div>' if desc else ""
        cards.append(
            f'<div class="project-full-card" data-status="{status.lower()}">'
            f'<div class="project-full-header">'
            f'<div><div class="project-full-title">{name}</div>{desc_html}</div>'
            f'<div class="proj-badge {badge_cls}">{badge_lbl}</div>'
            f'</div>'
            f'<div class="project-full-body">'
            f'<div>'
            f'<div class="prog-header"><span class="prog-label">Progress</span><span class="prog-val">{progress}%</span></div>'
            f'<div class="prog-bar"><div class="prog-fill" style="width:{progress}%;background:linear-gradient(90deg,{c_start},{c_end})"></div></div>'
            f'<div class="project-full-meta">{type_html}{due_html}</div>'
            f'</div>'
            f'</div>'
            f'</div>'
        )
    if not cards:
        return _empty("🚀", "No projects yet — <span>add them in Notion</span>.")
    return "\n".join(cards)


def build_content_mini(pages: list) -> str:
    """Compact 3-item content preview for the Overview tab."""
    TYPE_TAG = {"Reel": "REEL", "Post": "POST", "Video": "VIDEO",
                "Thread": "THREAD", "Story": "STORY"}
    items = []
    for i, p in enumerate(pages[:3]):
        title  = esc(prop(p, "Title", "Name", fallback="Untitled"))
        ctype  = str(prop(p, "Format", "Type", "Content Type", fallback=""))
        tag    = TYPE_TAG.get(ctype, ctype.upper() or "IDEA")
        num    = str(i + 1).zfill(2)
        items.append(
            f'<div class="content-item">'
            f'<div class="content-num">{num}</div>'
            f'<div class="content-text">{title}</div>'
            f'<div class="content-tag">{tag}</div>'
            f'</div>'
        )
    if not items:
        return _empty("✍️", "No content ideas yet.")
    return "\n        ".join(items)


def build_deadlines(pages: list) -> str:
    """Upcoming project deadlines for the Pipeline tab."""
    URGENCY_COLORS = ["var(--red)", "var(--amber)", "var(--blue)", "var(--purple)", "var(--green)"]
    items = []
    dated = [(p, str(prop(p, "Deadline", "Due Date", "Due", fallback=""))) for p in pages]
    dated = [(p, d) for p, d in dated if d]
    dated.sort(key=lambda x: x[1])
    for i, (p, due) in enumerate(dated[:6]):
        name     = esc(prop(p, "Project Name", "Name", "Title", fallback="Untitled"))
        category = esc(strip_emoji(str(prop(p, "Type", "Category", fallback="Project"))))
        color    = URGENCY_COLORS[i % len(URGENCY_COLORS)]
        try:
            d = datetime.strptime(due[:10], "%Y-%m-%d")
            due_fmt = d.strftime("%b %d")
        except ValueError:
            due_fmt = due[:10]
        items.append(
            f'<div class="event-item">'
            f'<div class="event-time">{due_fmt}</div>'
            f'<div class="event-bar" style="background:{color}"></div>'
            f'<div><div class="event-title">{name}</div>'
            f'<div class="event-sub">{category}</div></div>'
            f'</div>'
        )
    if not items:
        return _empty("📅", "No upcoming deadlines — clear skies ahead.")
    return "\n        ".join(items)


def build_pipeline_health(pages: list) -> str:
    """Project progress bars for the Pipeline tab."""
    COLORS = [
        ("var(--amber-dim)", "var(--amber)"),
        ("#2a6b8a",          "var(--blue)"),
        ("#6b2a8a",          "var(--purple)"),
        ("#1a6b3a",          "var(--green)"),
    ]
    rows = []
    for i, p in enumerate(pages[:6]):
        name     = esc(prop(p, "Project Name", "Name", "Title", fallback="Untitled"))
        progress = norm_pct(prop(p, "Progress", fallback=0))
        c_start, c_end = COLORS[i % len(COLORS)]
        rows.append(
            f'<div class="kpi-row">'
            f'<div class="kpi-header">'
            f'<span class="kpi-label">{name}</span>'
            f'<span class="kpi-val">{progress}%</span>'
            f'</div>'
            f'<div class="kpi-bar"><div class="kpi-fill" style="width:{progress}%;'
            f'background:linear-gradient(90deg,{c_start},{c_end})"></div></div>'
            f'</div>'
        )
    return "\n        ".join(rows) if rows else ""


def compute_brief(tasks: list, projects: list):
    """Return (priorities, tasks_due, deadlines, active_projects) counts."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    DONE_STATUSES = ("done", "complete", "completed")
    priorities = sum(
        1 for p in tasks
        if strip_emoji(str(prop(p, "Priority", fallback=""))).upper() == "HIGH"
        and strip_emoji(str(prop(p, "Status", fallback=""))).lower() not in DONE_STATUSES
        and not prop(p, "Done", fallback=False)
    )
    tasks_due = sum(
        1 for p in tasks
        if strip_emoji(str(prop(p, "Status", fallback=""))).lower() not in DONE_STATUSES
        and not prop(p, "Done", fallback=False)
    )
    deadlines = sum(
        1 for p in projects
        if str(prop(p, "Deadline", "Due Date", "Due", fallback=""))[:10] <= today
        and strip_emoji(str(prop(p, "Status", fallback=""))).lower() not in DONE_STATUSES
    )
    active_projects = sum(
        1 for p in projects
        if strip_emoji(str(prop(p, "Status", fallback=""))).lower() not in DONE_STATUSES
    )
    return priorities, tasks_due, deadlines, active_projects
