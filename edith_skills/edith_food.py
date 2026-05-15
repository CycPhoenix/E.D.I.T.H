"""
edith_food.py
=============
HTML builder for the E.D.I.T.H Food Places tab.
Takes Notion page data and returns HTML ready for INJECT:FOOD markers.
"""

from datetime import datetime
from edith_builders import prop, esc, strip_emoji, _empty


STATUS_MAP = {
    "Want to Try": ("badge-plan",   "WANT TO TRY"),
    "Visited":     ("badge-inprog", "VISITED"),
    "Regular":     ("badge-done",   "REGULAR"),
}

CUISINE_EMOJI = {
    "Japanese":  "🍱",
    "Korean":    "🍖",
    "Western":   "🍔",
    "Malaysian": "🍛",
    "Thai":      "🌶️",
    "Italian":   "🍝",
    "Chinese":   "🥢",
    "Café":      "☕",
    "Other":     "🍽️",
}


def build_food_tab(pages: list) -> str:
    """
    Build the full Food Places tab HTML from Notion pages.
    Returns an HTML string for injection into INJECT:FOOD markers.
    """
    if not pages:
        return _empty("🍜", "No food places saved yet — <span>send a Maps link to the bot</span>.")

    cards = []
    for p in pages:
        name        = esc(prop(p, "Name", "Title", fallback="Unnamed Place"))
        maps_url    = str(prop(p, "Google Maps URL", "Maps URL", "URL", fallback=""))
        cuisine_raw = strip_emoji(str(prop(p, "Cuisine", fallback="Other")))
        status_raw  = str(prop(p, "Status", fallback="Visited"))
        would_ret   = prop(p, "Would Return", fallback=False)
        notes_raw   = str(prop(p, "Notes", fallback=""))
        date_raw    = str(prop(p, "Date Visited", fallback=""))

        badge_cls, badge_lbl = STATUS_MAP.get(status_raw, ("badge-plan", status_raw.upper()))

        cuisine_emoji = CUISINE_EMOJI.get(cuisine_raw, "🍽️")
        cuisine_label = esc(cuisine_raw) if cuisine_raw else "Other"

        return_indicator = (
            '<span class="food-return yes">↩ Would Return</span>'
            if would_ret else
            '<span class="food-return no">✕ One Time</span>'
        )

        if date_raw:
            try:
                d = datetime.fromisoformat(date_raw[:10])
                date_str = d.strftime("%-d %b %Y")
            except ValueError:
                date_str = date_raw[:10]
        else:
            date_str = "Date unknown"

        notes_display = ""
        if notes_raw:
            truncated = esc(notes_raw[:120]) + ("..." if len(notes_raw) > 120 else "")
            notes_display = f'<div class="food-notes">{truncated}</div>'

        maps_btn = ""
        if maps_url:
            safe_url = esc(maps_url)
            maps_btn = (
                f'<a href="{safe_url}" target="_blank" class="food-maps-btn">'
                f'📍 Open in Maps</a>'
            )

        cards.append(
            f'<div class="food-card">'
            f'  <div class="food-card-top">'
            f'    <div class="food-name">{name}</div>'
            f'    <div class="food-badge {badge_cls}">{badge_lbl}</div>'
            f'  </div>'
            f'  <div class="food-meta">'
            f'    <span class="food-cuisine">{cuisine_emoji} {cuisine_label}</span>'
            f'    {return_indicator}'
            f'    <span class="food-date">🗓 {date_str}</span>'
            f'  </div>'
            f'  {notes_display}'
            f'  {maps_btn}'
            f'</div>'
        )

    return "\n        ".join(cards)


def build_food_stats(pages: list) -> dict:
    """Return food stats dict for Overview card use."""
    total       = len(pages)
    visited     = sum(1 for p in pages if str(prop(p, "Status", fallback="")) == "Visited")
    want_to_try = sum(1 for p in pages if str(prop(p, "Status", fallback="")) == "Want to Try")
    regulars    = sum(1 for p in pages if str(prop(p, "Status", fallback="")) == "Regular")
    would_ret   = sum(1 for p in pages if prop(p, "Would Return", fallback=False))
    return {
        "total":        total,
        "visited":      visited,
        "want_to_try":  want_to_try,
        "regulars":     regulars,
        "would_return": would_ret,
    }
