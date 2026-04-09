"""
edith_calendar.py
=================
ICS calendar fetching, parsing, and HTML builders for the
E.D.I.T.H dashboard calendar sections.

  build_calendar(ics_text)          → full Calendar tab HTML (14-day view)
  build_overview_calendar(ics_text) → compact today-only Overview card HTML
  _fetch_ics(url)                   → fetch raw ICS text (call once, share)
  _parse_ics_events(text, days)     → list of parsed event dicts
"""

import urllib.request
from datetime import datetime, timedelta

from edith_builders import esc, _empty


# ── ICS FETCH & PARSE ─────────────────────────────────────────────────────────

def _fetch_ics(ics_url: str) -> str:
    """Fetch raw ICS text from URL. Returns empty string on failure."""
    # Outlook requires a browser-like User-Agent; custom agents get 403/redirect
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/calendar, text/plain, */*",
    }
    try:
        req = urllib.request.Request(ics_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode("utf-8", errors="ignore")
            if "BEGIN:VCALENDAR" not in raw:
                print(f"  ⚠  Calendar fetch returned unexpected content (not ICS). First 200 chars: {raw[:200]}")
                return ""
            print(f"  ✅  Calendar fetched OK ({len(raw)} bytes)")
            return raw
    except Exception as e:
        print(f"  ⚠  Calendar fetch failed: {e}")
        return ""


def _parse_ics_events(ics_text: str, days_ahead: int = 14) -> list:
    """Parse ICS text into a list of event dicts for the next N days.
    Deduplicates events with the same date + start time + title (APU Outlook
    often includes the same class in multiple subscribed calendars)."""
    today  = datetime.now().date()
    cutoff = today + timedelta(days=days_ahead)
    events  = []
    seen    = set()   # (date, time_str, summary_key) — dedup key
    current = {}
    for line in ics_text.splitlines():
        line = line.strip()
        if line == "BEGIN:VEVENT":
            current = {}
        elif line == "END:VEVENT":
            if current.get("start") and current.get("summary"):
                dedup_key = (
                    current.get("date"),
                    current.get("time_str", ""),
                    current.get("summary", "")[:60],
                )
                if dedup_key not in seen:
                    seen.add(dedup_key)
                    events.append(current.copy())
            current = {}
        elif line.startswith("SUMMARY:"):
            current["summary"] = line[8:].replace("\\n", " ").replace("\\,", ",")
        elif line.startswith("DTSTART"):
            val = line.split(":", 1)[-1].strip()
            try:
                if "T" in val:
                    dt = datetime.strptime(val[:15], "%Y%m%dT%H%M%S")
                    current["start"]    = dt
                    current["time_str"] = dt.strftime("%H:%M")
                    current["date"]     = dt.date()
                else:
                    dt = datetime.strptime(val[:8], "%Y%m%d")
                    current["start"]    = dt
                    current["time_str"] = "All day"
                    current["date"]     = dt.date()
            except Exception:
                pass
        elif line.startswith("DTEND"):
            val = line.split(":", 1)[-1].strip()
            try:
                if "T" in val:
                    current["end"] = datetime.strptime(val[:15], "%Y%m%dT%H%M%S")
            except Exception:
                pass
        elif line.startswith("LOCATION:"):
            current["location"] = line[9:].replace("\\,", ",")

    events = [e for e in events if e.get("date") and today <= e["date"] <= cutoff]
    events.sort(key=lambda e: e["start"])
    return events


# ── CALENDAR TAB (full 14-day view) ──────────────────────────────────────────

def build_calendar(ics_text: str) -> str:
    """Build full Calendar tab HTML from pre-fetched ICS text."""
    if not ics_text:
        return ""

    today  = datetime.now().date()
    events = _parse_ics_events(ics_text, days_ahead=14)

    if not events:
        return _empty("📅", "No upcoming events in the next 2 weeks.")

    COLORS = ["var(--amber)", "var(--blue)", "var(--purple)", "var(--green)", "var(--red)"]
    groups = {}
    for e in events:
        groups.setdefault(e["date"], []).append(e)

    html_parts = []
    for d, day_events in sorted(groups.items()):
        is_today    = d == today
        day_lbl     = "TODAY" if is_today else d.strftime("%A, %B %d").upper()
        today_badge = '<span class="cal-today-badge">TODAY</span>' if is_today else ""
        html_parts.append(
            f'<div class="cal-day-group" data-date="{d.isoformat()}">'
            f'<div class="cal-day-header">{day_lbl} {today_badge}</div>'
        )
        for i, e in enumerate(day_events):
            color    = COLORS[i % len(COLORS)]
            title    = esc(e.get("summary", "Event"))
            loc      = esc(e.get("location", ""))
            time_str = e.get("time_str", "")

            if time_str == "All day":
                time_display = "All day"
                dur_html     = ""
            elif e.get("end") and e.get("start") and hasattr(e["start"], "hour"):
                end_str      = e["end"].strftime("%H:%M")
                time_display = f"{time_str}–{end_str}"
                mins         = int((e["end"] - e["start"]).total_seconds() / 60)
                dur_html     = (
                    f'<div class="cal-event-dur">{mins//60}h {mins%60:02d}m</div>'
                    if mins >= 60 else
                    f'<div class="cal-event-dur">{mins}m</div>'
                ) if mins > 0 else ""
            else:
                time_display = time_str
                dur_html     = ""

            loc_html = f'<div class="cal-event-loc">{loc}</div>' if loc else ""
            html_parts.append(
                f'<div class="cal-event">'
                f'<div class="cal-event-time">{time_display}</div>'
                f'<div class="cal-event-dot" style="background:{color}"></div>'
                f'<div><div class="cal-event-title">{title}</div>{loc_html}</div>'
                f'{dur_html}</div>'
            )
        html_parts.append('</div>')

    return "\n".join(html_parts)


# ── OVERVIEW CALENDAR (compact today-only card) ───────────────────────────────

def build_overview_calendar(ics_text: str) -> str:
    """Build compact event-item list for the Overview calendar card (today only).
    Receives pre-fetched ICS text — no extra network call."""
    COLORS = ["var(--amber)", "var(--blue)", "var(--purple)", "var(--green)", "var(--red)"]
    today  = datetime.now().date()

    if not ics_text:
        return (
            '<div class="event-item"><div class="event-time">—</div>'
            '<div class="event-bar" style="background:var(--amber-dim)"></div>'
            '<div><div class="event-title">No calendar linked</div>'
            '<div class="event-sub">Add OUTLOOK_ICS_URL to .env</div></div></div>'
        )

    today_events = [e for e in _parse_ics_events(ics_text, days_ahead=14) if e.get("date") == today]

    if not today_events:
        return (
            '<div class="event-item"><div class="event-time">—</div>'
            '<div class="event-bar" style="background:var(--amber-dim)"></div>'
            '<div><div class="event-title">Nothing today</div>'
            '<div class="event-sub">Enjoy the free time</div></div></div>'
        )

    items = []
    for i, e in enumerate(today_events[:5]):
        color  = COLORS[i % len(COLORS)]
        title  = esc(e.get("summary", "Event"))
        loc    = esc(e.get("location", ""))
        time_s = e.get("time_str", "—")
        if time_s != "All day" and e.get("end") and e.get("start"):
            mins    = int((e["end"] - e["start"]).total_seconds() / 60)
            dur_str = f"{mins//60}h {mins%60:02d}m" if mins >= 60 else f"{mins}m"
            sub     = f"{loc} · {dur_str}" if loc else dur_str
        else:
            sub = loc if loc else ("All day" if time_s == "All day" else "")
        items.append(
            f'<div class="event-item">'
            f'<div class="event-time">{time_s}</div>'
            f'<div class="event-bar" style="background:{color}"></div>'
            f'<div><div class="event-title">{title}</div>'
            f'<div class="event-sub">{sub}</div></div></div>'
        )
    return "\n".join(items)
