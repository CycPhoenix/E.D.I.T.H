"""
edith_agents.py
===============
E.D.I.T.H AI Agent system.

Agents:
  Orchestrator  — routes messages to the right specialist (invisible layer)
  Scout         — web research, article summarisation, current info
  Atlas         — CS/AI/ML study companion, quiz mode, paper breakdown
  Muse          — content ideas, Instagram/TikTok captions, reel scripts

API config — swap to LM Studio when ready (one line change):
  # import openai
  # _client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
  # MODEL   = "qwen2.5-32b-instruct"

Usage:
    from edith_agents import build_agents
    orch = build_agents()
    reply = orch.run("Explain transformer attention mechanisms")
    orch.set_mode("focus")    # silences Muse
    orch.set_mode("standby")  # all dormant
    print(orch.status())
"""

import os
import json
from pathlib import Path

try:
    import anthropic as _anthropic_lib
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass


# ── API CONFIG ────────────────────────────────────────────────────────────────
# Current: Anthropic Claude (API key from .env)
# Future swap — uncomment these two lines and remove the Anthropic block:
#   import openai
#   _client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
#   MODEL   = "qwen2.5-32b-instruct"

if _HAS_ANTHROPIC:
    _client = _anthropic_lib.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
else:
    _client = None  # type: ignore

MODEL = os.getenv("EDITH_MODEL", "claude-haiku-4-5-20251001")


# ── MODES ─────────────────────────────────────────────────────────────────────
MODES: dict[str, list[str]] = {
    "active":    ["scout", "atlas", "muse"],   # all agents on
    "focus":     ["scout", "atlas"],           # Muse silenced (study/work)
    "overnight": [],                           # dormant — queue only
    "standby":   [],                           # fully dormant
}


# ── SYSTEM PROMPTS ────────────────────────────────────────────────────────────

_ORCHESTRATOR_PROMPT = """\
You are E.D.I.T.H (Even Dead I'm The Hero), an AI orchestration layer.
Your job: read the user message and output ONLY a JSON object:
  {{"agent": "<name>", "reason": "<one sentence>"}}

Available agents: {agents}

Routing rules:
- scout  → web research, finding info, summarising articles, current events, links
- atlas  → CS/AI/ML concepts, university subjects, explaining papers, quiz/study mode, code help
- muse   → content ideas, Instagram/TikTok captions, reel scripts, hooks, creative copy

Default to "atlas" if unclear.
Output JSON only — no other text, no markdown fences.\
"""

_SCOUT_PROMPT = """\
You are Scout, E.D.I.T.H's research agent.
Role: fast, accurate information retrieval and article summarisation.
Tone: direct and dense — no filler. Bullet points for multi-part answers.
Always flag if info might be outdated relative to your training cutoff.
Format: lead with the direct answer, then supporting detail.\
"""

_ATLAS_PROMPT = """\
You are Atlas, E.D.I.T.H's study companion.
Role: teach CS, AI, and ML concepts. Break down research papers. Run quiz sessions.
Tone: like a senior engineer who teaches well — precise but approachable.

For concept explanations: intuition first, then formalism.
For paper breakdowns use this structure:
  Summary | Key contributions | Method | Limitations | Verdict

For quiz mode: ask one question at a time, wait for answer, give concise feedback,
then ask the next question. Track score mentally.\
"""

_MUSE_PROMPT = """\
You are Muse, E.D.I.T.H's content strategist.
Role: generate content ideas, hooks, captions, and reel scripts.
Platforms: Instagram, TikTok, LinkedIn.
Tone: authentic Gen-Z tech creator — confident, curious, never cringe.
Output: lead with the hook. Provide 3 variations when possible.
Keep captions punchy — under 150 chars unless LinkedIn.\
"""


# ── BASE AGENT ────────────────────────────────────────────────────────────────

class Agent:
    """Single LLM agent with a fixed system prompt."""

    def __init__(self, name: str, role: str, system_prompt: str) -> None:
        self.name          = name
        self.role          = role
        self.system_prompt = system_prompt

    def run(self, message: str, history: list[dict] | None = None) -> str:
        """
        Call the LLM.
        history = list of {"role": "user"|"assistant", "content": "..."} dicts.
        Returns the assistant reply as a plain string.
        """
        if _client is None:
            return "[Error] anthropic package not installed. Run: pip install anthropic"

        messages: list[dict] = list(history or [])
        messages.append({"role": "user", "content": message})

        resp = _client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=self.system_prompt,
            messages=messages,
        )
        return resp.content[0].text

    def __repr__(self) -> str:
        return f"<Agent:{self.name} '{self.role}'>"


# ── ORCHESTRATOR ──────────────────────────────────────────────────────────────

class Orchestrator:
    """
    Routes messages to the correct specialist agent.
    Transparent to callers — just call orch.run(message).
    """

    def __init__(self, agents: dict[str, Agent]) -> None:
        self._agents  = agents
        self._mode    = "active"
        self._router:  Agent | None = None   # built lazily

    # ── mode control ──────────────────────────────────────────────────────────

    @property
    def mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str) -> None:
        if mode not in MODES:
            raise ValueError(f"Unknown mode '{mode}'. Valid: {list(MODES)}")
        self._mode    = mode
        self._router  = None  # rebuild router prompt on next use

    # ── routing ───────────────────────────────────────────────────────────────

    def _get_router(self) -> Agent:
        if self._router is None:
            active  = MODES[self._mode] or list(self._agents)
            prompt  = _ORCHESTRATOR_PROMPT.format(agents=", ".join(active))
            self._router = Agent("orchestrator", "route", prompt)
        return self._router

    def _route(self, message: str) -> str:
        """Returns the agent name that should handle this message."""
        raw = self._get_router().run(message)
        try:
            name = json.loads(raw).get("agent", "atlas")
        except (json.JSONDecodeError, AttributeError):
            name = "atlas"
        return str(name)

    # ── main entrypoint ───────────────────────────────────────────────────────

    def run(self, message: str, history: list[dict] | None = None) -> str:
        active_names = MODES[self._mode]
        if not active_names:
            return f"[EDITH — {self._mode.upper()}] All agents dormant."

        active = {k: v for k, v in self._agents.items() if k in active_names}
        if not active:
            return "[EDITH] No agents available in current mode."

        target = self._route(message)
        if target not in active:
            target = next(iter(active))   # silenced agent — fall back to first active

        return active[target].run(message, history)

    # ── introspection ─────────────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "mode":          self._mode,
            "active_agents": MODES[self._mode],
            "all_agents":    list(self._agents),
            "model":         MODEL,
        }

    def __repr__(self) -> str:
        return f"<Orchestrator mode={self._mode} agents={list(self._agents)}>"


# ── FACTORY ───────────────────────────────────────────────────────────────────

def build_agents() -> Orchestrator:
    """Build and return a ready-to-use Orchestrator with all specialist agents."""
    agents = {
        "scout": Agent("scout", "web research and summarisation", _SCOUT_PROMPT),
        "atlas": Agent("atlas", "CS/AI study companion",          _ATLAS_PROMPT),
        "muse":  Agent("muse",  "content strategy and ideas",     _MUSE_PROMPT),
    }
    return Orchestrator(agents)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if not _HAS_ANTHROPIC:
        print("Error: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set in .env")
        sys.exit(1)

    orch    = build_agents()
    history: list[dict] = []

    print(f"E.D.I.T.H Agents ready | mode: {orch.mode} | model: {MODEL}")
    print("Commands: 'mode <name>' | 'status' | 'clear' | 'quit'\n")

    while True:
        try:
            msg = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nShutting down.")
            break

        if not msg:
            continue

        match msg.lower().split():
            case ["quit"] | ["exit"]:
                break
            case ["clear"]:
                history.clear()
                print("[History cleared]")
            case ["status"]:
                print(json.dumps(orch.status(), indent=2))
            case ["mode", new_mode]:
                try:
                    orch.set_mode(new_mode)
                    print(f"[Mode → {new_mode}]")
                except ValueError as e:
                    print(f"[Error] {e}")
            case _:
                reply = orch.run(msg, history)
                history.append({"role": "user",      "content": msg})
                history.append({"role": "assistant", "content": reply})
                print(f"\nEDITH: {reply}\n")
