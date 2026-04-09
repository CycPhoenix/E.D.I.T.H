# 🎤 E.D.I.T.H Voice Agent — Setup Guide

## What you're building
An AI phone agent that:
- **Answers inbound calls** when you're busy
- **Makes outbound calls** on your behalf
- **Drops voicemails** automatically
- **Sounds like you** (optional voice cloning)

---

## Step 1 — Install dependencies
```bash
pip install python-dotenv requests
```

---

## Step 2 — Create accounts

| Service | URL | Cost | What it's for |
|---|---|---|---|
| **Vapi** | vapi.ai | Free trial, then ~$0.05/min | Phone infrastructure |
| **ElevenLabs** | elevenlabs.io | Free: 10k chars/mo | Voice cloning |
| **Anthropic** | console.anthropic.com | Pay per use | Agent's brain |

---

## Step 3 — Run setup wizard
```bash
python edith_voice_agent.py setup
```
This walks you through saving all your API keys.

---

## Step 4 — Clone your voice (optional but 🔥)
```bash
python edith_voice_agent.py clone
```
Records of you speaking → ElevenLabs trains a clone.
Your agent will literally sound like you on every call.

**Tips for best clone quality:**
- Record 1–3 minutes of clear speech
- No background noise / music
- Use your natural speaking voice
- Vary your sentences (don't just repeat the same thing)

---

## Step 5 — Deploy your agent
```bash
python edith_voice_agent.py deploy
```
Creates your E.D.I.T.H assistant on Vapi and links it to your phone number.

---

## Step 6 — Test it!
Call your Vapi number from your phone. E.D.I.T.H should answer.

---

## Daily Usage

```bash
# Check agent is running
python edith_voice_agent.py status

# Make an outbound call
python edith_voice_agent.py call

# Drop a voicemail to a number
python edith_voice_agent.py voicemail

# See recent call history
python edith_voice_agent.py logs
```

---

## How inbound calls work
1. Someone calls your Vapi number
2. E.D.I.T.H answers automatically
3. Handles the conversation using Claude as the brain
4. Logs the call + transcript in Vapi dashboard
5. You review it anytime at dashboard.vapi.ai

---

## How outbound calls work
1. You run `python edith_voice_agent.py call`
2. Enter the number + purpose
3. E.D.I.T.H calls them immediately
4. Handles the conversation
5. You get a full transcript

---

## .env file reference
```
VAPI_API_KEY=your_vapi_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_cloned_voice_id    # Set after cloning
VAPI_ASSISTANT_ID=your_assistant_id          # Set after deploy
VAPI_PHONE_NUMBER=+1XXXXXXXXXX               # Your Vapi number
ANTHROPIC_API_KEY=your_anthropic_key
```

---

## Pricing estimate
| Item | Cost |
|---|---|
| Vapi phone number | ~$2/month |
| Vapi call minutes | ~$0.05/min |
| ElevenLabs voice | Free tier (10k chars) |
| Claude API | ~$0.003/1k tokens |
| **Total for light use** | **~$5–10/month** |

Way cheaper than hiring a receptionist. 😄
