# 🕶️ E.D.I.T.H Skills — Setup Guide

## 1. Install Dependencies
```bash
pip install anthropic python-dotenv google-api-python-client google-auth-oauthlib requests
```

## 2. Configure API Keys
```bash
cp .env.template .env
# Open .env and fill in your keys
```

### Keys you need:
| Key | Where to get it | Required for |
|---|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com | All AI skills |
| `NOTION_TOKEN` | notion.so/my-integrations | Task Manager, KPI Digest |
| `SERPER_API_KEY` | serper.dev (free tier) | Web Research |
| `GCAL_CREDS_FILE` | Google Cloud Console | Calendar Manager |

## 3. Connect Notion Integration
1. Go to notion.so/my-integrations
2. Create a new integration → copy the token
3. In Notion, open each database → Share → Invite your integration
4. The DB IDs are already pre-filled in `.env.template`

## 4. Connect Google Calendar (optional)
1. Go to console.cloud.google.com
2. Create project → Enable Google Calendar API
3. Create OAuth 2.0 credentials → Download as `credentials.json`
4. Place `credentials.json` in the same folder as `edith_skills.py`
5. First run will open a browser to authenticate

## 5. Run a Skill
```bash
python edith_skills.py brief      # Morning brief
python edith_skills.py email      # Draft an email
python edith_skills.py notes      # Summarize meeting notes
python edith_skills.py research   # Research a topic
python edith_skills.py tasks      # Manage Notion tasks
python edith_skills.py calendar   # View/add calendar events
python edith_skills.py kpi        # Weekly KPI digest
```

## 6. Sync Notion → Dashboard

The dashboard shows live data from your Notion databases. Run the sync script whenever you want it updated:

```bash
# Sync once
python edith_sync.py

# Sync automatically every 5 minutes (leave running in background)
python edith_sync.py --watch

# Sync on a custom interval (e.g. every 10 minutes)
python edith_sync.py --watch --interval 600
```

The script pulls from: Task Manager · Projects · KPI Digest · Content Pipeline · Study Hub
It then rewrites those sections of `edith-command-center.html` with your real Notion data.

> **Tip:** Run `python edith_sync.py --watch` in a terminal before opening the dashboard so it stays fresh while you work.

## 7. Notion Database IDs (pre-configured)
- 📋 Task Manager: `903584e20e7645ef92487d9bb44fcc5a`
- 📊 KPI Digest: `7339d0186ba44062b9de72e771131fad`
- 🚀 Projects: `0c2fa008b3aa4d5195e17ec11d9ffa36`
- 🎬 Content Pipeline: `448f9f35c8c7441a9683f72fb13a2650`
- 📚 Study Hub: `0d96b2834ff8466ca67e04d4a1f6b984`
- 🤝 Client Onboarding: `05bc936c8aef4dccbbce9ebd60e34909`
