# E.D.I.T.H Dashboard — Animation & Transition Upgrade Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `edith-command-center.html` with HUD-authentic animations — scanlines, glitch, staggered card entrances, animated progress bars, stat count-up, and a boot sequence.

**Architecture:** All changes are CSS + JS inside the single `edith-command-center.html` file. CSS goes inside the existing `<style>` block (before `</style>`). JS goes inside the existing `<script>` block (before `</script>`). No new files. No Python changes.

**Tech Stack:** Vanilla CSS (`@keyframes`, `transition`, `animation`), Vanilla JS (`requestAnimationFrame`, `sessionStorage`)

---

## What Already Exists (don't duplicate)

| Already there | Location |
|---|---|
| `@keyframes pulse` — green dot blink | line ~75 |
| `@keyframes fadeIn` — tab panel fade+slide | line ~105 |
| `transition: all 0.2s` on nav-tabs, buttons | scattered |
| `transition: border-color 0.2s` on cards | scattered |
| `transition: opacity 0.18s` on task items | line ~160 |

---

## File Change Summary

| File | Change |
|---|---|
| `edith-command-center.html` | Add CSS inside `<style>` block + JS inside `<script>` block |

---

## Task 1 — Scanline + Ambient Glow Overlay

**What it does:** Adds a classic CRT scanline texture over the whole page via `body::after`. Adds a subtle amber ambient glow to the page body border. Pure CSS, zero JS.

**Files:**
- Modify: `edith-command-center.html` — add inside `<style>` block, before `</style>`

---

- [ ] **Step 1: Add CSS — scanline overlay + body glow**

Find `</style>` and add immediately before it:

```css
/* ── SCANLINE OVERLAY ───────────────────────────────────────── */
body::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.08) 2px,
    rgba(0, 0, 0, 0.08) 4px
  );
  animation: scanline-drift 12s linear infinite;
}

@keyframes scanline-drift {
  0%   { background-position: 0 0; }
  100% { background-position: 0 100px; }
}

/* ── AMBIENT PAGE GLOW ──────────────────────────────────────── */
body {
  box-shadow: inset 0 0 120px rgba(255, 179, 71, 0.04);
}
```

- [ ] **Step 2: Verify in browser**

Open `edith-command-center.html`. You should see very faint horizontal scan lines scrolling slowly downward across the whole page. Should be subtle — if it looks too heavy, reduce `rgba(0,0,0,0.08)` to `rgba(0,0,0,0.05)`.

- [ ] **Step 3: Commit**

```bash
git add edith-command-center.html
git commit -m "feat: add CRT scanline overlay and ambient body glow"
```

---

## Task 2 — Logo Glitch Effect

**What it does:** The `E.D.I.T.H` logo in the header occasionally glitches — a brief chromatic-aberration-style clip-path flicker, 3 times in a 14-second loop. Runs forever, infrequently enough to not be annoying.

**Files:**
- Modify: `edith-command-center.html` — add CSS inside `<style>`, before `</style>`

---

- [ ] **Step 1: Add CSS — glitch keyframes + apply to logo**

```css
/* ── LOGO GLITCH ────────────────────────────────────────────── */
@keyframes edith-glitch {
  0%, 88%, 100% {
    text-shadow: none;
    transform: none;
    clip-path: none;
  }
  89% {
    text-shadow: -2px 0 #ff0044, 2px 0 #00ffe7;
    transform: skewX(-4deg);
  }
  90% {
    text-shadow: 2px 0 #ff0044, -2px 0 #00ffe7;
    transform: skewX(3deg);
    clip-path: polygon(0 30%, 100% 30%, 100% 55%, 0 55%);
  }
  91% {
    text-shadow: none;
    transform: none;
    clip-path: none;
  }
  92% {
    text-shadow: -1px 0 #ff0044;
    transform: translateX(1px);
  }
  93%, 100% {
    text-shadow: none;
    transform: none;
    clip-path: none;
  }
}

.logo-text {
  animation: edith-glitch 14s 4s infinite;
}
```

- [ ] **Step 2: Verify in browser**

Open the dashboard. Wait ~18 seconds (4s delay + first loop). The `E.D.I.T.H` logo should briefly flicker with a red/cyan split for ~0.4s, then snap back to normal. Should feel like a HUD glitch, not a strobe.

- [ ] **Step 3: Commit**

```bash
git add edith-command-center.html
git commit -m "feat: add logo glitch animation"
```

---

## Task 3 — Animated Progress Bar Fill

**What it does:** Progress bars (`.prog-fill`, `.kpi-fill`) animate from 0% to their target width every time a tab is opened. Without this they just appear at full width with no motion.

**Files:**
- Modify: `edith-command-center.html` — add CSS inside `<style>`, add JS inside `<script>`

---

- [ ] **Step 1: Add CSS — smooth transition on fill elements**

```css
/* ── PROGRESS BAR ANIMATION ─────────────────────────────────── */
.prog-fill,
.kpi-fill {
  transition: width 1s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
```

- [ ] **Step 2: Add JS — animate bars on tab switch**

Find the `switchTab` function:

```javascript
function switchTab(name, el) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  el.classList.add('active');
  try { localStorage.setItem('edith-tab', name); } catch(e) {}
}
```

Replace it with:

```javascript
function switchTab(name, el) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  const panel = document.getElementById('tab-' + name);
  panel.classList.add('active');
  el.classList.add('active');
  try { localStorage.setItem('edith-tab', name); } catch(e) {}

  // Animate progress bars in the newly active tab
  panel.querySelectorAll('.prog-fill, .kpi-fill').forEach(bar => {
    const target = bar.style.width;
    bar.style.transition = 'none';
    bar.style.width = '0%';
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        bar.style.transition = '';
        bar.style.width = target;
      });
    });
  });
}
```

- [ ] **Step 3: Verify in browser**

Click the **KPI** tab and then **Projects** tab. Progress bars should animate from left to right (0% → target) each time you switch in. Takes ~1 second to complete.

- [ ] **Step 4: Commit**

```bash
git add edith-command-center.html
git commit -m "feat: animate progress bars on tab switch"
```

---

## Task 4 — Card Entrance Stagger

**What it does:** When a tab opens, its cards/items slide up and fade in one by one with a staggered delay (each card 60ms after the previous). Gives the UI a "loading data" feel.

**Files:**
- Modify: `edith-command-center.html` — add CSS inside `<style>`, add JS inside `<script>`

---

- [ ] **Step 1: Add CSS — stagger keyframe + base class**

```css
/* ── STAGGER ENTRANCE ───────────────────────────────────────── */
@keyframes staggerUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stagger-enter {
  animation: staggerUp 0.3s ease both;
}
```

- [ ] **Step 2: Add JS — inject stagger class on tab open**

Add this function inside the `<script>` block (anywhere before `</script>`):

```javascript
function staggerTabCards(panel) {
  // Target the direct card/item children inside the active tab
  const selectors = [
    '.task-full-item',
    '.project-full-card',
    '.food-card',
    '.research-item',
    '.kpi-section',
    '.content-card',
    '.stat-card',
    '.agent-card',
    '.event-item',
    '.pipeline-row',
  ];
  const items = panel.querySelectorAll(selectors.join(','));
  items.forEach((item, i) => {
    item.classList.remove('stagger-enter');
    // Force reflow so removing+re-adding the class restarts the animation
    void item.offsetWidth;
    item.style.animationDelay = `${i * 60}ms`;
    item.classList.add('stagger-enter');
  });
}
```

Then update `switchTab` to call `staggerTabCards` after setting the panel active (add one line after `panel.classList.add('active')`):

```javascript
function switchTab(name, el) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  const panel = document.getElementById('tab-' + name);
  panel.classList.add('active');
  el.classList.add('active');
  try { localStorage.setItem('edith-tab', name); } catch(e) {}

  // Stagger card entrances
  staggerTabCards(panel);

  // Animate progress bars in the newly active tab
  panel.querySelectorAll('.prog-fill, .kpi-fill').forEach(bar => {
    const target = bar.style.width;
    bar.style.transition = 'none';
    bar.style.width = '0%';
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        bar.style.transition = '';
        bar.style.width = target;
      });
    });
  });
}
```

- [ ] **Step 3: Verify in browser**

Click **Tasks** tab, then **Projects**, then **Food**. Each time you switch, the cards should cascade in from bottom — first card instant, each subsequent card 60ms later. Should feel snappy, not sluggish.

- [ ] **Step 4: Commit**

```bash
git add edith-command-center.html
git commit -m "feat: stagger card entrance animation on tab switch"
```

---

## Task 5 — Stat Counter Count-Up

**What it does:** The Overview stat cards (Tasks `1/12`, GPA `3.82`, etc.) animate their numbers counting up from 0 on page load. One-time animation — runs once per page open.

**Files:**
- Modify: `edith-command-center.html` — add JS inside `<script>`

---

- [ ] **Step 1: Add JS — count-up function**

Add inside the `<script>` block:

```javascript
function countUp(el, duration) {
  const raw = el.textContent.trim();

  // Handle "X/Y" format (e.g. "1/12")
  if (raw.includes('/')) {
    const [a, b] = raw.split('/').map(Number);
    if (isNaN(a) || isNaN(b)) return;
    let start = null;
    function step(ts) {
      if (!start) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      const ease = 1 - Math.pow(1 - p, 3); // ease-out cubic
      el.textContent = `${Math.round(a * ease)}/${Math.round(b * ease)}`;
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = raw;
    }
    requestAnimationFrame(step);
    return;
  }

  // Handle plain number or decimal (e.g. "3.82", "4")
  const target = parseFloat(raw);
  if (isNaN(target)) return;
  const decimals = (raw.split('.')[1] || '').length;
  let start = null;
  function step(ts) {
    if (!start) start = ts;
    const p = Math.min((ts - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    el.textContent = (target * ease).toFixed(decimals);
    if (p < 1) requestAnimationFrame(step);
    else el.textContent = raw;
  }
  requestAnimationFrame(step);
}

// Run count-up on all Overview stat card values after load
window.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('#tab-overview .card-value').forEach(el => {
      countUp(el, 1200);
    });
  }, 400); // 400ms delay so the page settles first
});
```

- [ ] **Step 2: Verify in browser**

Hard-refresh the page (`Ctrl+Shift+R`). The Overview stat card numbers (GPA, Tasks, etc.) should count up from 0 over ~1.2 seconds. The final value should exactly match what the sync wrote.

- [ ] **Step 3: Commit**

```bash
git add edith-command-center.html
git commit -m "feat: stat counter count-up animation on page load"
```

---

## Task 6 — HUD Boot Sequence

**What it does:** On the very first page open (per browser session), a full-screen overlay shows `INITIALIZING E.D.I.T.H...` with a scan-wipe reveal, then fades away after ~2.5 seconds. Subsequent tabs/refreshes skip it (stored in `sessionStorage`).

**Files:**
- Modify: `edith-command-center.html` — add CSS inside `<style>`, add HTML after `<body>`, add JS inside `<script>`

---

- [ ] **Step 1: Add CSS — boot overlay styles**

```css
/* ── HUD BOOT SEQUENCE ──────────────────────────────────────── */
#boot-overlay {
  position: fixed;
  inset: 0;
  background: #090909;
  z-index: 99999;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
  pointer-events: none;
}

#boot-overlay.hidden {
  opacity: 0;
  transition: opacity 0.6s ease;
  pointer-events: none;
}

.boot-logo {
  font-family: 'Orbitron', monospace;
  font-size: 32px;
  font-weight: 800;
  color: var(--amber);
  letter-spacing: 8px;
  text-shadow: 0 0 20px rgba(255, 179, 71, 0.6);
  opacity: 0;
  animation: bootFadeIn 0.4s 0.3s ease forwards;
}

.boot-line {
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  color: var(--text-dim);
  letter-spacing: 3px;
  text-transform: uppercase;
  opacity: 0;
  animation: bootFadeIn 0.4s 0.8s ease forwards;
}

.boot-bar-wrap {
  width: 240px;
  height: 2px;
  background: rgba(255, 179, 71, 0.1);
  border-radius: 2px;
  overflow: hidden;
  opacity: 0;
  animation: bootFadeIn 0.4s 1s ease forwards;
}

.boot-bar {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--amber-dim), var(--amber));
  border-radius: 2px;
  animation: bootBarFill 1.2s 1.1s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

@keyframes bootFadeIn {
  to { opacity: 1; }
}

@keyframes bootBarFill {
  to { width: 100%; }
}
```

- [ ] **Step 2: Add HTML — boot overlay element**

Find `<body>` and add immediately after it (before `<header>`):

```html
<!-- HUD BOOT SEQUENCE -->
<div id="boot-overlay">
  <div class="boot-logo">E.D.I.T.H</div>
  <div class="boot-line">Initializing command center...</div>
  <div class="boot-bar-wrap"><div class="boot-bar"></div></div>
</div>
```

- [ ] **Step 3: Add JS — dismiss overlay after 2.5s (first session only)**

```javascript
(function bootSequence() {
  const overlay = document.getElementById('boot-overlay');
  if (!overlay) return;

  // Skip boot on subsequent loads in the same browser session
  try {
    if (sessionStorage.getItem('edith-booted')) {
      overlay.style.display = 'none';
      return;
    }
    sessionStorage.setItem('edith-booted', '1');
  } catch(e) {}

  // Dismiss after 2.5s
  setTimeout(() => {
    overlay.classList.add('hidden');
    // Remove from DOM after fade completes
    setTimeout(() => overlay.remove(), 700);
  }, 2500);
})();
```

- [ ] **Step 4: Verify in browser**

1. Open `edith-command-center.html` in a **private/incognito window** (forces fresh session).
2. Should see black screen → `E.D.I.T.H` logo fades in → `Initializing...` appears → amber progress bar fills → overlay fades away revealing dashboard. Total: ~3 seconds.
3. Close and reopen the same tab (non-incognito) — boot should be skipped.

- [ ] **Step 5: Commit**

```bash
git add edith-command-center.html
git commit -m "feat: HUD boot sequence on first session load"
```

---

## Self-Review

**Spec coverage:**
- Scanline overlay ✅ Task 1
- Logo glitch ✅ Task 2
- Progress bar animation ✅ Task 3
- Card stagger entrance ✅ Task 4
- Stat count-up ✅ Task 5
- Boot sequence ✅ Task 6

**Placeholder scan:** None found. All tasks contain complete CSS/JS code.

**Conflict check:**
- Task 3 and Task 4 both modify `switchTab`. Task 4 shows the final merged version of `switchTab` — implement Task 3 first, then Task 4 replaces `switchTab` with the merged version.
- `.stagger-enter` uses `animation: staggerUp 0.3s ease both` — `both` fill-mode means `opacity:0` before the animation plays. This could conflict with existing `fadeIn` on `.tab-panel.active`. Tab panel fade and card stagger are on different elements so no conflict.
- `body::after` (Task 1) has `pointer-events: none` so it won't block clicks.
- Boot overlay (Task 6) has `z-index: 99999` — above scanline overlay (`9999`). Correct layering.

**Build order note:** Implement in task order (1 → 6). Tasks 3 and 4 both touch `switchTab` — do Task 3 first so Task 4's merged version includes the progress bar logic.

---

*Plan written by Claude · Cowork mode · April 23, 2026*

---

## Phase 2 — Planned (Not Yet Built)

All target `edith-command-center.html` only. CSS + JS, no Python.

### Task 7 — Tab Slide Direction

Tabs slide left or right based on tab index order instead of plain fade. Switching to a higher-index tab → slides left. Lower-index → slides right. Feels like real navigation.

**CSS needed:**
```css
@keyframes slideInRight { from { opacity:0; transform:translateX(30px); } to { opacity:1; transform:translateX(0); } }
@keyframes slideInLeft  { from { opacity:0; transform:translateX(-30px); } to { opacity:1; transform:translateX(0); } }
.tab-panel.slide-left  { animation: slideInLeft  0.25s ease both; }
.tab-panel.slide-right { animation: slideInRight 0.25s ease both; }
```

**JS needed:** Track `lastTabIndex`. In `switchTab`, compare new index vs old — add `.slide-left` or `.slide-right` to panel instead of relying on `fadeIn`.

---

### Task 8 — Card Hover Lift

Cards lift `3px` and glow stronger on hover. Applies to `.food-card`, `.project-full-card`, `.stat-card`, `.agent-card-detail`.

**CSS needed:**
```css
.food-card:hover,
.project-full-card:hover,
.stat-card:hover,
.agent-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(255,179,71,0.12);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s;
}
```

Note: add `transition: transform 0.2s ease, box-shadow 0.2s ease` alongside existing `border-color` transition on these elements.

---

### Task 9 — Clock Digit Flip

Clock digits flip (card-flip style) on each second tick. Applies to the `#clock` element in the header.

**Approach:** Wrap each digit pair (HH, MM, SS) in a `.flip-unit` div. On tick, add `.flip` class which triggers a Y-axis rotate animation, swaps the number at 90°, then completes the flip.

**CSS needed:**
```css
.flip-unit { display: inline-block; perspective: 200px; }
.flip-unit span { display: inline-block; transition: transform 0.2s ease; transform-style: preserve-3d; }
.flip-unit.flipping span { animation: digitFlip 0.2s ease; }
@keyframes digitFlip {
  0%   { transform: rotateX(0deg); }
  50%  { transform: rotateX(-90deg); }
  100% { transform: rotateX(0deg); }
}
```

**JS needed:** Refactor `updateClock()` to render `HH:MM:SS` as individual `.flip-unit` spans. Add `.flipping` class on digits that changed each second, remove after 200ms.

---

### Task 10 — Morning Brief Typewriter

`.brief-message` text types out character by character on page load. Cursor blinks at the end. Runs once per load.

**JS needed:**
```javascript
function typewriter(el, speed) {
  const full = el.innerHTML;
  el.innerHTML = '';
  let i = 0;
  // Parse as plain text to avoid splitting HTML tags mid-type
  const text = el.textContent; // fallback: type plain text version
  const cursor = document.createElement('span');
  cursor.style.cssText = 'border-right:2px solid var(--amber);animation:blink 0.7s infinite;';
  el.appendChild(cursor);
  const interval = setInterval(() => {
    cursor.insertAdjacentText('beforebegin', full[i++] || '');
    if (i >= full.length) { clearInterval(interval); setTimeout(() => cursor.remove(), 1200); }
  }, speed);
}
// Call on load — target the brief message paragraph
window.addEventListener('DOMContentLoaded', () => {
  const el = document.querySelector('.brief-message');
  if (el) setTimeout(() => typewriter(el, 22), 600);
});
```

**CSS needed:**
```css
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0;} }
```

---

### Task 11 — Header Sweep

Single bright amber line sweeps horizontally across the header every ~20s. Subtle — like a radar sweep.

**CSS needed:**
```css
header { overflow: hidden; }
header::after {
  content: '';
  position: absolute;
  top: 0; left: -100%; bottom: 0;
  width: 60px;
  background: linear-gradient(90deg, transparent, rgba(255,179,71,0.15), transparent);
  animation: header-sweep 20s 5s linear infinite;
  pointer-events: none;
}
@keyframes header-sweep {
  0%   { left: -60px; }
  100% { left: 100%; }
}
```

---

### Task 12 — Agent Pulse Rings

Expanding ring animation around online agent status dots (`.agent-dot`). Two rings expand outward and fade — like a sonar ping.

**CSS needed:**
```css
.agent-dot { position: relative; }
.agent-dot::before,
.agent-dot::after {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 1px solid var(--green);
  animation: agentRing 2.4s ease-out infinite;
  opacity: 0;
}
.agent-dot::after { animation-delay: 1.2s; }
@keyframes agentRing {
  0%   { transform: scale(1);   opacity: 0.6; }
  100% { transform: scale(2.8); opacity: 0; }
}
```

---

### Task 13 — Progress Bar Shimmer

After bars finish filling, a shimmer highlight sweeps left→right across `.prog-fill`. Loops every 3s.

**CSS needed:**
```css
.prog-fill { position: relative; overflow: hidden; }
.prog-fill::after {
  content: '';
  position: absolute;
  top: 0; left: -100%; bottom: 0;
  width: 50%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
  animation: bar-shimmer 3s 1.2s ease-in-out infinite;
}
@keyframes bar-shimmer {
  0%   { left: -50%; }
  100% { left: 150%; }
}
```

---

### Task 14 — Nav Tab Ripple

Click ripple effect on nav tab buttons — circle expands from click point and fades.

**CSS needed:**
```css
.nav-tab { position: relative; overflow: hidden; }
.nav-tab .ripple {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,179,71,0.3);
  transform: scale(0);
  animation: ripple-expand 0.5s linear;
  pointer-events: none;
}
@keyframes ripple-expand {
  to { transform: scale(4); opacity: 0; }
}
```

**JS needed:**
```javascript
document.querySelectorAll('.nav-tab').forEach(btn => {
  btn.addEventListener('click', function(e) {
    const r = document.createElement('span');
    r.className = 'ripple';
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    r.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX-rect.left-size/2}px;top:${e.clientY-rect.top-size/2}px`;
    btn.appendChild(r);
    setTimeout(() => r.remove(), 500);
  });
});
```
