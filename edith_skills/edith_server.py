#!/usr/bin/env python3
"""
E.D.I.T.H Local Server — bridges the static dashboard HTML to live Notion write-back.

Endpoints:
  GET  /                      Serves edith-command-center.html
  GET  /api/status            Returns server alive + last sync timestamp + next_sync
  POST /api/sync              Runs edith_sync.py once and returns result
  POST /api/task/complete     Marks a Notion task as Done
  POST /api/task/create       Creates a new Notion task
  POST /api/kpi/log           Logs a KPI value to the latest KPI Digest Notion page

Usage:
    python edith_server.py          # default port 5000
    python edith_server.py --port 8080

Open http://localhost:5000 in browser instead of opening the file directly.
Then all write-back calls work without CORS or token-exposure issues.
"""

import os
import json
import subprocess
import threading
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

NOTION_TOKEN   = os.getenv("NOTION_TOKEN", "")
TASK_DB        = os.getenv("NOTION_TASK_DB",     "903584e20e7645ef92487d9bb44fcc5a")
KPI_DB         = os.getenv("NOTION_KPI_DB",      "7339d0186ba44062b9de72e771131fad")
RESEARCH_DB    = os.getenv("NOTION_RESEARCH_DB", "0d96b2834ff8466ca67e04d4a1f6b984")
DASHBOARD      = Path(__file__).parent.parent / "edith-command-center.html"
SYNC_SCRIPT    = Path(__file__).parent / "edith_sync.py"
PORT           = 5000
WATCH_INTERVAL = 1800  # seconds — 30 min suggested re-sync interval

HEADERS = {
    "Authorization":  f"Bearer {NOTION_TOKEN}",
    "Content-Type":   "application/json",
    "Notion-Version": "2022-06-28",
}

_last_sync:    str                    = "never"
_last_sync_dt: datetime | None        = None
_sync_lock = threading.Lock()


# ── NOTION HELPERS ────────────────────────────────────────────────────────────

def notion_patch(page_id: str, properties: dict) -> dict:
    """PATCH a Notion page — update properties."""
    url  = f"https://api.notion.com/v1/pages/{page_id}"
    body = json.dumps({"properties": properties}).encode()
    req  = urllib.request.Request(url, data=body, headers=HEADERS, method="PATCH")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code} {e.reason}"}


def notion_create_task(title: str, priority: str = "Medium") -> dict:
    """Create a new task in the Notion Task Manager DB."""
    url  = "https://api.notion.com/v1/pages"
    props = {
        "Name":     {"title": [{"text": {"content": title}}]},
        "Priority": {"select": {"name": priority}},
        "Status":   {"select": {"name": "To Do"}},
    }
    body = json.dumps({"parent": {"database_id": TASK_DB}, "properties": props}).encode()
    req  = urllib.request.Request(url, data=body, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code} {e.reason}"}


def notion_query_db(db_id: str, payload: dict) -> dict:
    """POST /databases/{id}/query — returns the raw Notion response."""
    url  = f"https://api.notion.com/v1/databases/{db_id}/query"
    body = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=body, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code} {e.reason}"}


# KPI property name → Notion property type map
_KPI_PROP_MAP: dict[str, str] = {
    "Tasks Completed": "Tasks Completed",
    "Tasks Total":     "Tasks Total",
    "Study Hours":     "Study Hours",
    "Content Posted":  "Content Posted",
    "GPA Target":      "GPA Target",
}


def notion_create_page(db_id: str, properties: dict) -> dict:
    """Create a new page in any Notion DB."""
    url  = "https://api.notion.com/v1/pages"
    body = json.dumps({"parent": {"database_id": db_id}, "properties": properties}).encode()
    req  = urllib.request.Request(url, data=body, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code} {e.reason}"}


def notion_log_kpi(label: str, value: float) -> dict:
    """Find the latest KPI Digest page and PATCH the matching property."""
    if label not in _KPI_PROP_MAP:
        return {"error": f"Unknown KPI label: {label}"}
    # Fetch the most recently created KPI page
    resp = notion_query_db(KPI_DB, {
        "sorts": [{"timestamp": "created_time", "direction": "descending"}],
        "page_size": 1,
    })
    if "error" in resp:
        return resp
    results = resp.get("results", [])
    if not results:
        return {"error": "No KPI Digest pages found"}
    page_id   = results[0]["id"]
    prop_name = _KPI_PROP_MAP[label]
    return notion_patch(page_id, {prop_name: {"number": value}})


# ── SYNC RUNNER ───────────────────────────────────────────────────────────────

def run_sync() -> dict:
    """Run edith_sync.py in a subprocess and return {ok, output, timestamp}."""
    global _last_sync, _last_sync_dt
    with _sync_lock:
        try:
            result = subprocess.run(
                ["python", str(SYNC_SCRIPT)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            _last_sync_dt = datetime.now(timezone.utc)
            _last_sync    = _last_sync_dt.isoformat()
            next_sync     = (_last_sync_dt + timedelta(seconds=WATCH_INTERVAL)).isoformat()
            return {
                "ok":        result.returncode == 0,
                "output":    (result.stdout + result.stderr).strip(),
                "timestamp": _last_sync,
                "next_sync": next_sync,
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "output": "Sync timed out after 60s", "timestamp": ""}
        except Exception as exc:
            return {"ok": False, "output": str(exc), "timestamp": ""}


# ── HTTP HANDLER ──────────────────────────────────────────────────────────────

class EdithHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        # Quiet logging — only print errors
        if args and str(args[1]) not in ("200", "304"):
            super().log_message(fmt, *args)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "http://localhost:" + str(PORT))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _html(self, code: int, body: bytes, mime: str = "text/html"):
        self.send_response(code)
        self.send_header("Content-Type", mime + "; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length:
            try:
                return json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                return {}
        return {}

    # OPTIONS preflight
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]

        # Serve dashboard
        if path == "/" or path == "/index.html":
            if not DASHBOARD.exists():
                self._json(404, {"error": "Dashboard HTML not found"})
                return
            self._html(200, DASHBOARD.read_bytes())
            return

        # Serve static files (edith_static/)
        if path.startswith("/static/"):
            static_dir = Path(__file__).parent.parent / "edith_static"
            rel = path[8:]  # strip '/static/'
            if not rel or ".." in rel:
                self._json(400, {"error": "Bad path"})
                return
            filepath = static_dir / rel
            if not filepath.exists():
                self._json(404, {"error": f"Static file not found: {rel}"})
                return
            mime = "text/css" if rel.endswith(".css") else \
                   "application/javascript" if rel.endswith(".js") else \
                   "text/plain"
            self._html(200, filepath.read_bytes(), mime)
            return

        # Status check
        if path == "/api/status":
            payload: dict = {
                "ok":        True,
                "server":    "E.D.I.T.H local server",
                "last_sync": _last_sync,
                "port":      PORT,
            }
            if _last_sync_dt is not None:
                payload["next_sync"] = (
                    _last_sync_dt + timedelta(seconds=WATCH_INTERVAL)
                ).isoformat()
            self._json(200, payload)
            return

        self._json(404, {"error": "Not found"})

    def do_POST(self):
        path = self.path.split("?")[0]

        # Trigger sync
        if path == "/api/sync":
            result = run_sync()
            self._json(200 if result["ok"] else 500, result)
            return

        # Complete a task
        if path == "/api/task/complete":
            data    = self._read_body()
            page_id = data.get("page_id", "").strip()
            if not page_id:
                self._json(400, {"error": "page_id required"})
                return
            if not NOTION_TOKEN:
                self._json(500, {"error": "NOTION_TOKEN not set"})
                return
            result = notion_patch(page_id, {"Status": {"select": {"name": "Done"}}})
            self._json(200 if "error" not in result else 500, result)
            return

        # Create a task
        if path == "/api/task/create":
            data  = self._read_body()
            title = data.get("title", "").strip()
            if not title:
                self._json(400, {"error": "title required"})
                return
            if not NOTION_TOKEN:
                self._json(500, {"error": "NOTION_TOKEN not set"})
                return
            priority = data.get("priority", "Medium")
            result   = notion_create_task(title, priority)
            self._json(200 if "error" not in result else 500, result)
            return

        # Log a completed Pomodoro session to Research DB
        if path == "/api/pomodoro/log":
            data  = self._read_body()
            topic = data.get("topic", "General").strip() or "General"
            mins  = int(data.get("duration_mins", 25))
            if not NOTION_TOKEN:
                self._json(500, {"error": "NOTION_TOKEN not set"})
                return
            today = datetime.now().strftime("%Y-%m-%d")
            props = {
                "Topic": {"title": [{"text": {"content": topic}}]},
                "Notes": {"rich_text": [{"text": {"content": f"Pomodoro session: {mins}m"}}]},
                "Date":  {"date": {"start": today}},
                "Subject": {"multi_select": [{"name": "Pomodoro"}]},
            }
            result = notion_create_page(RESEARCH_DB, props)
            ok     = "error" not in result
            self._json(200 if ok else 500, {"ok": ok, **({"id": result.get("id")} if ok else result)})
            return

        # Log a KPI value to the latest KPI Digest page
        if path == "/api/kpi/log":
            data  = self._read_body()
            label = data.get("label", "").strip()
            value = data.get("value")
            if not label or value is None:
                self._json(400, {"error": "label and value required"})
                return
            if not NOTION_TOKEN:
                self._json(500, {"error": "NOTION_TOKEN not set"})
                return
            try:
                value = float(value)
            except (TypeError, ValueError):
                self._json(400, {"error": "value must be a number"})
                return
            result = notion_log_kpi(label, value)
            ok     = "error" not in result
            self._json(200 if ok else 500, {"ok": ok, **result})
            return

        self._json(404, {"error": "Not found"})


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="E.D.I.T.H local server")
    parser.add_argument("--port", type=int, default=PORT, help="Port to listen on (default: 5000)")
    args = parser.parse_args()

    global PORT
    PORT = args.port

    server = HTTPServer(("127.0.0.1", PORT), EdithHandler)
    print(f"E.D.I.T.H server running → http://localhost:{PORT}")
    print(f"  Dashboard:    http://localhost:{PORT}/")
    print(f"  Status:       http://localhost:{PORT}/api/status")
    print(f"  Sync trigger: POST http://localhost:{PORT}/api/sync")
    print(f"  KPI log:      POST http://localhost:{PORT}/api/kpi/log")
    print(f"  Pomodoro log: POST http://localhost:{PORT}/api/pomodoro/log")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
