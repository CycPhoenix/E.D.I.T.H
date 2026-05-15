  // ── CLOCK ──
  // ── CLOCK DIGIT FLIP ──────────────────────────────────────────
  let _prevClockParts = ['','',''];
  function updateClock() {
    const now = new Date();
    const parts = [
      String(now.getHours()).padStart(2,'0'),
      String(now.getMinutes()).padStart(2,'0'),
      String(now.getSeconds()).padStart(2,'0'),
    ];
    const el = document.getElementById('clock');
    // Build flip units on first run
    if (!el.querySelector('.flip-unit')) {
      el.innerHTML = parts.map((p,i) =>
        `<span class="flip-unit" id="fu${i}"><span>${p}</span></span>${i<2?':':''}`
      ).join('');
      _prevClockParts = [...parts];
      return;
    }
    parts.forEach((p, i) => {
      if (p === _prevClockParts[i]) return;
      const fu = document.getElementById('fu' + i);
      fu.querySelector('span').textContent = p;
      fu.classList.remove('flipping');
      void fu.offsetWidth;
      fu.classList.add('flipping');
      setTimeout(() => fu.classList.remove('flipping'), 200);
    });
    _prevClockParts = [...parts];
  }
  updateClock();
  setInterval(updateClock, 1000);

  // ── SYNC TIME ──
  const syncEl = document.getElementById('sync-time');
  let syncSecs = 0;
  setInterval(() => {
    syncSecs++;
    syncEl.textContent = syncSecs < 60 ? syncSecs + 's ago' : Math.floor(syncSecs/60) + 'm ago';
  }, 1000);

  // ── COUNTDOWN ──
  let total = 6*3600+42*60+17;
  setInterval(() => {
    total = total > 0 ? total-1 : 8*3600;
    const h = String(Math.floor(total/3600)).padStart(2,'0');
    const m = String(Math.floor((total%3600)/60)).padStart(2,'0');
    const s = String(total%60).padStart(2,'0');
    const el = document.getElementById('countdown');
    if(el) el.textContent = h+':'+m+':'+s;
  }, 1000);

  // ── TAB SWITCHING ──
  function staggerTabCards(panel) {
    const selectors = [
      '.task-full-item', '.project-full-card', '.food-card', '.research-item',
      '.kpi-section', '.content-card', '.stat-card', '.agent-card',
      '.event-item', '.pipeline-row',
    ];
    panel.querySelectorAll(selectors.join(',')).forEach((item, i) => {
      item.classList.remove('stagger-enter');
      void item.offsetWidth; // force reflow to restart animation
      item.style.animationDelay = `${i * 60}ms`;
      item.classList.add('stagger-enter');
    });
  }

  const TAB_ORDER = ['overview','tasks','calendar','kpi','projects','agents','pipeline','content','research','food'];
  let _lastTabIndex = 0;

  function switchTab(name, el) {
    const newIndex = TAB_ORDER.indexOf(name);
    const direction = newIndex >= _lastTabIndex ? 'slide-left' : 'slide-right';
    _lastTabIndex = newIndex;

    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active','slide-left','slide-right'));
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    const panel = document.getElementById('tab-' + name);
    panel.classList.add('active', direction);
    el.classList.add('active');
    try { localStorage.setItem('edith-tab', name); } catch(e) {}

    // Stagger card entrances
    staggerTabCards(panel);

    // Animate progress bars
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

  // ── RESTORE LAST TAB ON LOAD ──
  (function restoreTab() {
    try {
      const saved = localStorage.getItem('edith-tab');
      if (!saved) return;
      const panel = document.getElementById('tab-' + saved);
      if (!panel) return;
      const btn = document.querySelector(`.nav-tab[onclick*="'${saved}'"]`);
      if (!btn) return;
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      panel.classList.add('active');
      btn.classList.add('active');
    } catch(e) {}
  })();

  // ── TASK TOGGLE + AUTO-SORT ──
  function bindTaskToggle(item) {
    item.addEventListener('click', () => {
      const check = item.querySelector('.task-check');
      const text  = item.querySelector('.task-text');
      const list  = item.parentElement;

      check.classList.toggle('done');
      text.classList.toggle('done');

      if (check.classList.contains('done')) {
        // Fade out briefly, then move to bottom
        item.style.opacity = '0.4';
        setTimeout(() => {
          item.style.opacity = '';
          list.appendChild(item);
        }, 180);
      } else {
        // Move back above the first done item
        item.style.opacity = '0.4';
        setTimeout(() => {
          item.style.opacity = '';
          const firstDone = [...list.querySelectorAll('.task-item')]
            .find(i => i !== item && i.querySelector('.task-check').classList.contains('done'));
          if (firstDone) list.insertBefore(item, firstDone);
          else list.prepend(item);
        }, 180);
      }
    });
  }
  document.querySelectorAll('.task-item').forEach(bindTaskToggle);

  // ── EMPTY STATES ──
  function checkEmptyStates() {
    const sections = [
      { container: '#tasks-card',    child: '.task-item',         icon: '📋', msg: "Ow, today's empty — <span>no tasks lined up</span>." },
      { container: '#calendar-card', child: '.event-item',        icon: '📅', msg: "Nothing scheduled — <span>enjoy the free time</span>." },
      { container: '#projects-card', child: '.project-row',       icon: '🚀', msg: "No active projects — <span>clean slate</span>." },
      { container: '#tab-content',   child: '.content-full-card', icon: '✍️', msg: "No content pieces yet — <span>ideas incoming</span>." },
      { container: '#tab-research',  child: '.research-item',     icon: '🔍', msg: "No research saved — <span>run a query above</span>." },
    ];
    sections.forEach(({ container, child, icon, msg }) => {
      const el = document.querySelector(container);
      if (!el) return;
      if (el.querySelectorAll(child).length === 0 && !el.querySelector('.empty-state')) {
        const div = document.createElement('div');
        div.className = 'empty-state';
        div.innerHTML = `<div class="empty-icon">${icon}</div><div class="empty-msg">${msg}</div>`;
        el.appendChild(div);
      }
    });
  }
  checkEmptyStates();

  // ── TASKS FULL PAGE FILTER ──
  function filterTasks(filter, btn) {
    document.querySelectorAll('#tab-tasks .filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('#tasks-full-list .task-full-item').forEach(item => {
      const pri  = (item.dataset.priority || '').toLowerCase();
      const done = item.dataset.done === 'true';
      let show = false;
      if (filter === 'all')    show = true;
      if (filter === 'high')   show = pri === 'high' && !done;
      if (filter === 'medium') show = pri === 'medium' && !done;
      if (filter === 'low')    show = pri === 'low' && !done;
      if (filter === 'done')   show = done;
      if (filter === 'pending') show = !done;
      item.style.display = show ? '' : 'none';
    });
  }

  // ── TASKS FULL PAGE STATS ──
  function updateTaskStats() {
    const items   = document.querySelectorAll('#tasks-full-list .task-full-item');
    const total   = items.length;
    const done    = [...items].filter(i => i.dataset.done === 'true').length;
    const pending = total - done;
    const high    = [...items].filter(i => i.dataset.priority === 'high' && i.dataset.done !== 'true').length;
    const ts = document.getElementById('tstat-total');
    const tp = document.getElementById('tstat-pending');
    const th = document.getElementById('tstat-high');
    const td = document.getElementById('tstat-done');
    if (ts) ts.textContent = total;
    if (tp) tp.textContent = pending;
    if (th) th.textContent = high;
    if (td) td.textContent = done;
  }
  updateTaskStats();

  // ── TASK FULL ITEM TOGGLE ──
  function bindTaskFullToggle(item) {
    item.addEventListener('click', () => {
      const check = item.querySelector('.task-full-check');
      const name  = item.querySelector('.task-full-name');
      check.classList.toggle('done');
      name.classList.toggle('done');
      item.dataset.done = check.classList.contains('done') ? 'true' : 'false';
      item.style.opacity = '0.4';
      setTimeout(() => { item.style.opacity = ''; updateTaskStats(); }, 180);
    });
  }
  document.querySelectorAll('#tasks-full-list .task-full-item').forEach(bindTaskFullToggle);

  // ── PROJECTS FULL PAGE FILTER ──
  function filterProjects(filter, btn) {
    const row = btn.closest('.filter-row');
    row.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('#projects-full-list .project-full-card').forEach(card => {
      const status = (card.dataset.status || '').toLowerCase();
      const show = filter === 'all' || status === filter.toLowerCase();
      card.style.display = show ? '' : 'none';
    });
  }

  // ── CALENDAR FILTER ──
  function _parseDateFromCalHeader(group) {
    // Prefer data-date attribute (set by new sync code)
    const dateStr = group.dataset.date;
    if (dateStr) return new Date(dateStr + 'T00:00:00');
    // Fallback: parse from header text (e.g. "WEDNESDAY, APRIL 01")
    // NOTE: "TODAY" headers without data-date are stale — return null so
    //       they only show in 'all' view and don't collide with date-labeled groups.
    const hdr = (group.querySelector('.cal-day-header') || {}).textContent || '';
    const txt = hdr.trim();
    const MONTHS = {JANUARY:0,FEBRUARY:1,MARCH:2,APRIL:3,MAY:4,JUNE:5,
                    JULY:6,AUGUST:7,SEPTEMBER:8,OCTOBER:9,NOVEMBER:10,DECEMBER:11};
    const m = txt.match(/[A-Z]+,\s+([A-Z]+)\s+(\d+)/);
    if (m && MONTHS[m[1]] !== undefined) {
      return new Date(new Date().getFullYear(), MONTHS[m[1]], parseInt(m[2]));
    }
    return null; // "TODAY" header with no data-date = stale, can't trust the date
  }

  function filterCalendar(view, btn) {
    document.querySelectorAll('#tab-calendar .filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const now = new Date();
    now.setHours(0, 0, 0, 0);

    // Start of week = Monday
    const dow = now.getDay(); // 0=Sun
    const diffToMon = (dow === 0) ? -6 : 1 - dow;
    const weekStart = new Date(now);
    weekStart.setDate(now.getDate() + diffToMon);
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6);

    document.querySelectorAll('#tab-calendar .cal-day-group').forEach(group => {
      const d = _parseDateFromCalHeader(group);
      // null = stale group with no parseable date (e.g. "TODAY" header without data-date)
      // Show only in 'all' view; hide in filtered views to avoid ghost duplicates
      if (!d) { group.style.display = view === 'all' ? '' : 'none'; return; }
      if (view === 'all') {
        group.style.display = '';
      } else if (view === 'today') {
        group.style.display = d.toDateString() === now.toDateString() ? '' : 'none';
      } else if (view === 'week') {
        group.style.display = (d >= weekStart && d <= weekEnd) ? '' : 'none';
      }
    });

    // Show empty message if nothing visible
    const calInject = document.querySelector('#tab-calendar');
    const visible = calInject ? [...calInject.querySelectorAll('.cal-day-group')].filter(g => g.style.display !== 'none') : [];
    const existing = calInject ? calInject.querySelector('.cal-empty-filter') : null;
    if (visible.length === 0 && calInject) {
      if (!existing) {
        const msg = document.createElement('div');
        msg.className = 'empty-state cal-empty-filter';
        msg.innerHTML = `<div class="empty-icon">📅</div><div class="empty-msg">No events for <span>${view === 'today' ? 'today' : 'this week'}</span>.</div>`;
        calInject.appendChild(msg);
      }
    } else if (existing) {
      existing.remove();
    }
  }

  // ── AUTO-POPULATE: Tasks tab from Overview task card ──
  function autoPopulateTasksFull() {
    const list = document.getElementById('tasks-full-list');
    if (!list) return;
    // Only run if the dedicated tab hasn't been filled by sync
    const hasRealData = list.querySelector('.task-full-item');
    if (hasRealData) return;

    const sourceItems = document.querySelectorAll('#tasks-card .task-item');
    if (!sourceItems.length) return;

    list.innerHTML = '';
    sourceItems.forEach(item => {
      const check  = item.querySelector('.task-check');
      const textEl = item.querySelector('.task-text');
      const badge  = item.querySelector('.task-badge');
      if (!textEl) return;

      const isDone  = check && check.classList.contains('done');
      const name    = textEl.textContent.trim();
      let priority  = 'low';
      let badgeCls  = 'badge-low';
      if (badge) {
        const bc = badge.className;
        if (bc.includes('badge-high')) { priority = 'high'; badgeCls = 'badge-high'; }
        else if (bc.includes('badge-med')) { priority = 'medium'; badgeCls = 'badge-med'; }
        else { priority = 'low'; badgeCls = 'badge-low'; }
      }

      const el = document.createElement('div');
      el.className = 'task-full-item';
      el.dataset.priority = priority;
      el.dataset.done = String(isDone);
      el.innerHTML =
        `<div class="task-full-check${isDone ? ' done' : ''}"></div>` +
        `<div class="task-full-body">` +
        `<div class="task-full-name${isDone ? ' done' : ''}">${name}</div>` +
        `<div class="task-full-meta"><span class="task-badge ${badgeCls}">${priority.toUpperCase()}</span></div>` +
        `</div>`;
      bindTaskFullToggle(el);
      list.appendChild(el);
    });
    updateTaskStats();
  }
  autoPopulateTasksFull();

  // ── AUTO-POPULATE: Projects tab from Pipeline project cards ──
  function autoPopulateProjectsFull() {
    const list = document.getElementById('projects-full-list');
    if (!list) return;
    if (list.querySelector('.project-full-card')) return; // already synced

    const sourceRows = document.querySelectorAll('#projects-card .project-row');
    if (!sourceRows.length) return;

    list.innerHTML = '';
    const COLORS = [
      ['var(--amber-dim)', 'var(--amber)'],
      ['#2a6b8a', 'var(--blue)'],
      ['#6b2a8a', 'var(--purple)'],
      ['#1a6b3a', 'var(--green)'],
    ];
    const BADGE_MAP = {
      'IN PROGRESS': ['badge-inprog', 'IN PROGRESS'],
      'PLANNING':    ['badge-plan',   'PLANNING'],
      'DONE':        ['badge-done',   'DONE'],
      'BLOCKED':     ['badge-block',  'BLOCKED'],
    };

    sourceRows.forEach((row, i) => {
      const nameEl    = row.querySelector('.project-name');
      const metaEl    = row.querySelector('.project-meta');
      const progValEl = row.querySelector('.prog-val');
      const progFill  = row.querySelector('.prog-fill');
      const badgeEl   = row.querySelector('.proj-badge');
      if (!nameEl) return;

      const name       = nameEl.textContent.trim();
      const meta       = metaEl ? metaEl.textContent.trim() : '';
      const progVal    = progValEl ? progValEl.textContent.trim() : '0%';
      const progNum    = parseInt(progVal) || 0;
      const badgeTxt   = badgeEl ? badgeEl.textContent.trim() : 'PLANNING';
      const [bCls, bLbl] = BADGE_MAP[badgeTxt] || ['badge-plan', badgeTxt];
      const [cStart, cEnd] = COLORS[i % COLORS.length];

      // Extract status for data-status filtering
      const statusMap = { 'IN PROGRESS': 'in progress', 'PLANNING': 'planning', 'DONE': 'done', 'BLOCKED': 'blocked' };
      const dataStatus = statusMap[badgeTxt] || badgeTxt.toLowerCase();

      const card = document.createElement('div');
      card.className = 'project-full-card';
      card.dataset.status = dataStatus;
      card.innerHTML =
        `<div class="project-full-header">` +
        `<div><div class="project-full-title">${name}</div>` +
        (meta ? `<div class="project-full-desc">${meta}</div>` : '') +
        `</div><div class="proj-badge ${bCls}">${bLbl}</div></div>` +
        `<div class="project-full-body"><div>` +
        `<div class="prog-header"><span class="prog-label">Progress</span><span class="prog-val">${progVal}</span></div>` +
        `<div class="prog-bar"><div class="prog-fill" style="width:${progNum}%;background:linear-gradient(90deg,${cStart},${cEnd})"></div></div>` +
        `</div></div>`;
      list.appendChild(card);
    });
  }
  autoPopulateProjectsFull();

  // ── AUTO-POPULATE: KPI tab from Overview KPI digest card ──
  function autoPopulateKpiFull() {
    const kpiTab = document.getElementById('tab-kpi');
    if (!kpiTab) return;
    // Only if there's no real kpi-week-card yet
    if (kpiTab.querySelector('.kpi-week-card')) return;

    const sourceRows = document.querySelectorAll('#kpi-digest-card .kpi-row');
    if (!sourceRows.length) return;

    // Remove placeholder
    const placeholder = kpiTab.querySelector('.empty-state');
    if (placeholder) placeholder.remove();

    const injectZone = kpiTab.querySelector('#tab-kpi > *:last-child') || kpiTab;

    // Build a single "current week" card from the overview data
    const card = document.createElement('div');
    card.className = 'kpi-week-card';

    let miniGrid = '<div class="kpi-week-grid">';
    let barsHtml = '';

    sourceRows.forEach(row => {
      const label = row.querySelector('.kpi-label');
      const val   = row.querySelector('.kpi-val');
      const fill  = row.querySelector('.kpi-fill');
      if (!label || !val) return;
      const lbl = label.textContent.trim();
      const v   = val.textContent.trim();
      const w   = fill ? (fill.style.width || '0%') : '0%';
      miniGrid += `<div class="kpi-mini-stat"><div class="kpi-mini-val">${v}</div><div class="kpi-mini-lbl">${lbl.toUpperCase()}</div></div>`;
      barsHtml += `<div class="kpi-row"><div class="kpi-header"><span class="kpi-label">${lbl}</span><span class="kpi-val">${v}</span></div><div class="kpi-bar"><div class="kpi-fill" style="width:${w}"></div></div></div>`;
    });
    miniGrid += '</div>';

    const now = new Date();
    const weekLabel = `WEEK OF ${now.toLocaleDateString('en-US', {month:'short', day:'numeric', year:'numeric'}).toUpperCase()}`;
    card.innerHTML =
      `<div class="kpi-week-header"><div class="kpi-week-title">${weekLabel}</div><div class="kpi-week-badge kpi-rating-average">THIS WEEK</div></div>` +
      miniGrid + barsHtml;

    // Insert inside the inject zone
    const injectEnd = kpiTab.innerHTML.indexOf('<!-- INJECT:KPI_FULL:END -->');
    if (injectEnd !== -1) {
      kpiTab.querySelector('[id]') ; // no-op — just use appendChild as fallback
    }
    kpiTab.appendChild(card);
  }
  autoPopulateKpiFull();

  // ── RESEARCH SEARCH (cosmetic) ──
  function runSearch() {
    const q = document.querySelector('.search-input').value.trim();
    if(q) alert('E.D.I.T.H Research Agent\n\nQuery: "' + q + '"\n\nConnect your ANTHROPIC_API_KEY to run live research.\nSee edith_skills.py → python edith_skills.py research');
  }
  function filterFood(status) {
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('onclick') === `filterFood('${status}')`);
    });
    document.querySelectorAll('#food-grid .food-card').forEach(card => {
      if (status === 'all') { card.style.display = ''; return; }
      const badge = card.querySelector('.food-badge');
      if (!badge) { card.style.display = 'none'; return; }
      card.style.display = badge.textContent.trim().toLowerCase() === status.toLowerCase() ? '' : 'none';
    });
  }

  document.querySelector('.search-btn').addEventListener('click', runSearch);
  document.querySelector('.search-input').addEventListener('keydown', (e) => {
    if(e.key === 'Enter') runSearch();
  });

  // ── STAT COUNTER COUNT-UP ────────────────────────────────────
  function countUp(el, duration) {
    const raw = el.textContent.trim();
    if (raw.includes('/')) {
      const [a, b] = raw.split('/').map(Number);
      if (isNaN(a) || isNaN(b)) return;
      let start = null;
      (function step(ts) {
        if (!start) start = ts;
        const p = Math.min((ts - start) / duration, 1);
        const ease = 1 - Math.pow(1 - p, 3);
        el.textContent = `${Math.round(a * ease)}/${Math.round(b * ease)}`;
        if (p < 1) requestAnimationFrame(step); else el.textContent = raw;
      })(performance.now());
      return;
    }
    const target = parseFloat(raw);
    if (isNaN(target)) return;
    const decimals = (raw.split('.')[1] || '').length;
    let start = null;
    (function step(ts) {
      if (!start) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      const ease = 1 - Math.pow(1 - p, 3);
      el.textContent = (target * ease).toFixed(decimals);
      if (p < 1) requestAnimationFrame(step); else el.textContent = raw;
    })(performance.now());
  }

  window.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
      document.querySelectorAll('#tab-overview .card-value').forEach(el => countUp(el, 1200));
    }, 400);
  });

  // ── TASK 10: MORNING BRIEF TYPEWRITER ───────────────────────
  // Types plain text char-by-char, then restores full HTML (with amber spans) when done.
  window.addEventListener('DOMContentLoaded', () => {
    const el = document.querySelector('.brief-message');
    if (!el) return;
    setTimeout(() => {
      const fullHTML = el.innerHTML;
      const fullText = el.textContent;
      el.textContent = '';
      const cursor = document.createElement('span');
      cursor.style.cssText = 'border-right:2px solid var(--amber);margin-left:1px;animation:blink 0.7s infinite;display:inline-block;height:1em;vertical-align:text-bottom;';
      el.appendChild(cursor);
      let i = 0;
      const interval = setInterval(() => {
        if (i < fullText.length) {
          cursor.insertAdjacentText('beforebegin', fullText[i++]);
        } else {
          clearInterval(interval);
          setTimeout(() => {
            cursor.remove();
            el.innerHTML = fullHTML; // restore amber spans
          }, 400);
        }
      }, 16);
    }, 900);
  });

  // ── TASK 14: NAV TAB RIPPLE ──────────────────────────────────
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

  // ── HUD BOOT SEQUENCE ────────────────────────────────────────
  (function bootSequence() {
    const overlay = document.getElementById('boot-overlay');
    if (!overlay) return;
    try {
      if (sessionStorage.getItem('edith-booted')) {
        overlay.style.display = 'none';
        return;
      }
      sessionStorage.setItem('edith-booted', '1');
    } catch(e) {}
    setTimeout(() => {
      overlay.classList.add('hidden');
      setTimeout(() => overlay.remove(), 700);
    }, 2500);
  })();

  // ── KEYBOARD SHORTCUTS ───────────────────────────────────────
  // 1-9,0 = switch tabs | / = focus search | r = trigger sync toast
  (function initKeyboardShortcuts() {
    const tabKeys = {
      '1': 'overview', '2': 'tasks',    '3': 'calendar', '4': 'kpi',
      '5': 'projects', '6': 'agents',   '7': 'pipeline', '8': 'content',
      '9': 'research', '0': 'food',
    };
    document.addEventListener('keydown', (e) => {
      // Skip if user is typing in an input/textarea
      if (['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) return;

      // 1–0: switch tabs
      if (tabKeys[e.key]) {
        const name = tabKeys[e.key];
        const btn = document.querySelector(`.nav-tab[onclick*="'${name}'"]`);
        if (btn) { e.preventDefault(); switchTab(name, btn); }
        return;
      }

      // /: focus search (research tab search input)
      if (e.key === '/') {
        e.preventDefault();
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
          const searchBtn = document.querySelector(`.nav-tab[onclick*="'research'"]`);
          if (searchBtn) switchTab('research', searchBtn);
          setTimeout(() => searchInput.focus(), 260);
        }
        return;
      }

      // r: trigger sync (via server if running, else reminder)
      if (e.key === 'r' || e.key === 'R') {
        triggerSync();
      }
    });
  })();

  // ── TOAST NOTIFICATION ───────────────────────────────────────
  function showToast(msg, duration) {
    duration = duration || 3000;
    let t = document.getElementById('edith-toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'edith-toast';
      t.style.cssText = 'position:fixed;bottom:24px;right:24px;background:rgba(18,18,26,0.95);border:1px solid rgba(255,179,71,0.4);color:var(--amber);font-family:"Share Tech Mono",monospace;font-size:12px;padding:10px 18px;border-radius:6px;z-index:9999;opacity:0;transition:opacity 0.3s;pointer-events:none;max-width:320px;line-height:1.5;';
      document.body.appendChild(t);
    }
    t.innerHTML = msg;
    t.style.opacity = '1';
    clearTimeout(t._timeout);
    t._timeout = setTimeout(() => { t.style.opacity = '0'; }, duration);
  }

  // ── SERVER WIRING ─────────────────────────────────────────────
  // Communicates with edith_server.py (python edith_skills/edith_server.py)
  // Falls back gracefully if server is not running.
  const EDITH_SERVER = 'http://localhost:5000';
  let _serverOnline = false;

  // Check server on load — show indicator in header if online
  let _syncCountdownTimer = null;

  function startSyncCountdown(nextSyncAt) {
    const el = document.getElementById('sync-countdown');
    if (!el || !nextSyncAt) return;
    if (_syncCountdownTimer) clearInterval(_syncCountdownTimer);
    function update() {
      const diff = Math.max(0, Math.floor((new Date(nextSyncAt) - Date.now()) / 1000));
      if (diff <= 0) { el.textContent = ' · SYNCING...'; return; }
      const m = Math.floor(diff / 60);
      const s = String(diff % 60).padStart(2, '0');
      el.textContent = ` · SYNC IN ${m}:${s}`;
      el.style.display = 'inline';
    }
    update();
    _syncCountdownTimer = setInterval(update, 1000);
  }

  (function checkServer() {
    fetch(EDITH_SERVER + '/api/status', { signal: AbortSignal.timeout(1500) })
      .then(r => r.json())
      .then(d => {
        if (d.ok) {
          _serverOnline = true;
          const logo = document.querySelector('.logo-text');
          if (logo && !document.getElementById('server-dot')) {
            const dot = document.createElement('span');
            dot.id = 'server-dot';
            dot.title = 'E.D.I.T.H server online — press R to sync';
            dot.style.cssText = 'display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--green);margin-left:8px;vertical-align:middle;box-shadow:0 0 6px var(--green);';
            logo.after(dot);
          }
          if (d.next_sync) startSyncCountdown(d.next_sync);
        }
      })
      .catch(() => { _serverOnline = false; });
  })();

  function triggerSync() {
    if (!_serverOnline) {
      showToast('🔄 Server offline — run: <code>python edith_skills/edith_server.py</code>', 4000);
      return;
    }
    showToast('🔄 Syncing…', 60000);
    fetch(EDITH_SERVER + '/api/sync', { method: 'POST' })
      .then(r => r.json())
      .then(d => {
        if (d.ok) {
          showToast('✅ Sync complete — reload to see updates', 4000);
          flashInjectedSections();
          if (d.next_sync) startSyncCountdown(d.next_sync);
        } else {
          showToast('⚠️ Sync failed: ' + (d.output || 'unknown error').slice(0, 120), 5000);
        }
      })
      .catch(() => showToast('⚠️ Sync request failed — is server running?', 4000));
  }

  function completeTask(pageId, cardEl) {
    if (!pageId) return;
    if (!_serverOnline) {
      showToast('⚠️ Server offline — task not saved to Notion', 3000);
      return;
    }
    // Optimistic UI — dim card immediately
    cardEl.style.opacity = '0.35';
    cardEl.style.pointerEvents = 'none';
    fetch(EDITH_SERVER + '/api/task/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page_id: pageId }),
    })
      .then(r => r.json())
      .then(d => {
        if (d.error) {
          cardEl.style.opacity = '';
          cardEl.style.pointerEvents = '';
          showToast('⚠️ Could not complete task: ' + d.error, 4000);
        } else {
          showToast('✅ Task marked Done in Notion', 2500);
        }
      })
      .catch(() => {
        cardEl.style.opacity = '';
        cardEl.style.pointerEvents = '';
        showToast('⚠️ Network error — task not saved', 3000);
      });
  }

  // Wire task complete buttons — data-page-id on .task-card triggers completeTask()
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.task-complete-btn');
    if (!btn) return;
    const card = btn.closest('.task-card, [data-page-id]');
    const pageId = btn.dataset.pageId || (card && card.dataset.pageId);
    if (pageId) completeTask(pageId, card || btn);
  });

  // ── QUICK-ADD TASK ────────────────────────────────────────────
  async function quickAddTask() {
    const input    = document.getElementById('quick-task-input');
    const priority = document.getElementById('quick-task-priority');
    const title    = input.value.trim();
    if (!title) return;
    input.disabled = true;
    showToast('Adding task...', 2000);
    try {
      const res  = await fetch(EDITH_SERVER + '/api/task/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority: priority.value }),
      });
      const data = await res.json();
      if (data.id || data.object === 'page') {
        showToast(`✅ "${title}" added — syncing...`, 3000);
        input.value = '';
        triggerSync();
      } else {
        showToast('⚠️ Failed to add task', 3000);
      }
    } catch {
      showToast('⚠️ Server offline — task not saved', 3000);
    } finally {
      input.disabled = false;
      input.focus();
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const inp = document.getElementById('quick-task-input');
    if (inp) inp.addEventListener('keydown', e => { if (e.key === 'Enter') quickAddTask(); });
  });

  // ── DATA FLASH ────────────────────────────────────────────────
  function flashInjectedSections() {
    const targets = [
      '#tasks-full-list',
      '#tab-calendar .cal-wrap, #tab-calendar .calendar-wrap',
      '#tab-food .food-grid',
      '#tab-content .content-list, #tab-pipeline .pipeline-wrap',
      '#tab-research .research-list',
    ];
    targets.forEach(sel => {
      sel.split(',').forEach(s => {
        const el = document.querySelector(s.trim());
        if (!el) return;
        el.classList.remove('flash-update');
        void el.offsetWidth;
        el.classList.add('flash-update');
        setTimeout(() => el.classList.remove('flash-update'), 800);
      });
    });
  }

  // ── INLINE KPI LOGGING ────────────────────────────────────────
  document.addEventListener('click', function(e) {
    const val = e.target.closest('.kpi-val[data-kpi-label]');
    if (!val || val.querySelector('input')) return;
    const label   = val.dataset.kpiLabel;
    const current = val.textContent.trim();
    const numOnly = current.replace(/[^0-9.]/g, '');
    const input   = document.createElement('input');
    input.type      = 'number';
    input.value     = numOnly;
    input.className = 'kpi-inline-input';
    input.style.cssText = 'width:60px;background:transparent;border:none;border-bottom:1px solid var(--amber);color:var(--amber);font-family:inherit;font-size:inherit;text-align:right;outline:none;';
    val.textContent = '';
    val.appendChild(input);
    input.focus();
    input.select();

    async function saveKpi() {
      const newVal = parseFloat(input.value);
      if (isNaN(newVal)) { val.textContent = current; return; }
      val.textContent = current.replace(numOnly, String(newVal));
      showToast(`Updating ${label}...`, 2000);
      try {
        const res  = await fetch(EDITH_SERVER + '/api/kpi/log', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ label, value: newVal }),
        });
        const data = await res.json();
        showToast(data.ok ? `✅ ${label} updated` : `⚠️ Update failed`, 3000);
      } catch {
        showToast('⚠️ Server offline', 3000);
      }
    }

    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') { input.blur(); }
      if (e.key === 'Escape') { val.textContent = current; }
    });
    input.addEventListener('blur', saveKpi);
  });

  // ── MOBILE NAV (TASK 7) ───────────────────────────────────────
  window.toggleMobileNav = function() {
    const nav = document.getElementById('mobile-nav');
    if (nav) nav.classList.toggle('open');
  };

  window.mobileSwitchTab = function(name, btn) {
    // Update active state on mobile buttons
    document.querySelectorAll('.mobile-nav-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    // Also sync desktop nav
    const desktopBtn = document.querySelector(`.nav-tab[onclick*="'${name}'"]`);
    switchTab(name, desktopBtn || btn);
    // Close the dropdown
    const nav = document.getElementById('mobile-nav');
    if (nav) nav.classList.remove('open');
  };

  // Close mobile nav when clicking outside
  document.addEventListener('click', function(e) {
    const nav = document.getElementById('mobile-nav');
    const hbBtn = document.getElementById('hamburger-btn');
    if (nav && nav.classList.contains('open') &&
        !nav.contains(e.target) && e.target !== hbBtn) {
      nav.classList.remove('open');
    }
  });

  // ── SWIPE TABS (TASK 7) ───────────────────────────────────────
  (function initSwipe() {
    const TAB_ORDER = ['overview','tasks','calendar','kpi','projects','agents','pipeline','content','research','food'];
    let _touchStartX = 0;
    let _touchStartY = 0;

    document.addEventListener('touchstart', function(e) {
      _touchStartX = e.touches[0].clientX;
      _touchStartY = e.touches[0].clientY;
    }, { passive: true });

    document.addEventListener('touchend', function(e) {
      const dx = e.changedTouches[0].clientX - _touchStartX;
      const dy = e.changedTouches[0].clientY - _touchStartY;
      // Only horizontal swipe with enough delta and not dominated by vertical
      if (Math.abs(dx) < 50 || Math.abs(dy) > Math.abs(dx) * 0.8) return;
      // Find current tab
      const active = document.querySelector('.tab-panel.active');
      if (!active) return;
      const currentName = active.id.replace('tab-', '');
      const idx         = TAB_ORDER.indexOf(currentName);
      if (idx === -1) return;
      if (dx < 0 && idx < TAB_ORDER.length - 1) {
        // Swipe left → next tab
        const nextName = TAB_ORDER[idx + 1];
        const btn = document.querySelector(`.nav-tab[onclick*="'${nextName}'"]`);
        switchTab(nextName, btn);
      } else if (dx > 0 && idx > 0) {
        // Swipe right → prev tab
        const prevName = TAB_ORDER[idx - 1];
        const btn = document.querySelector(`.nav-tab[onclick*="'${prevName}'"]`);
        switchTab(prevName, btn);
      }
    }, { passive: true });
  })();

  // ── POMODORO NOTION LOGGING (TASK 8) ──────────────────────────
  async function logPomodoro(topic, durationMins) {
    const statusEl = document.getElementById('pomo-log-status');
    try {
      const res = await fetch(EDITH_SERVER + '/api/pomodoro/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, duration_mins: durationMins }),
      });
      const data = await res.json();
      if (data.ok && statusEl) {
        statusEl.classList.add('visible');
        setTimeout(() => statusEl.classList.remove('visible'), 3000);
      }
    } catch {
      // Server offline — silent fail (no toast spam during focus)
    }
  }

  // ── POMODORO TIMER ────────────────────────────────────────────
  (function initPomodoro() {
    const MODES = [
      { label: 'Focus Session',  secs: 25 * 60, color: 'var(--amber)' },
      { label: 'Short Break',    secs:  5 * 60, color: 'var(--green)' },
      { label: 'Focus Session',  secs: 25 * 60, color: 'var(--amber)' },
      { label: 'Short Break',    secs:  5 * 60, color: 'var(--green)' },
      { label: 'Focus Session',  secs: 25 * 60, color: 'var(--amber)' },
      { label: 'Short Break',    secs:  5 * 60, color: 'var(--green)' },
      { label: 'Focus Session',  secs: 25 * 60, color: 'var(--amber)' },
      { label: 'Long Break',     secs: 15 * 60, color: 'var(--blue)'  },
    ];
    const CIRC = 276.46; // 2πr where r=44

    let modeIdx    = 0;
    let totalSecs  = MODES[0].secs;
    let remaining  = totalSecs;
    let running    = false;
    let sessions   = 0;
    let interval   = null;

    const ring     = document.getElementById('pomo-ring');
    const display  = document.getElementById('pomo-display');
    const modeLabel= document.getElementById('pomo-mode-label');
    const startBtn = document.getElementById('pomo-start');
    const sessSpan = document.getElementById('pomo-sessions');

    function fmt(s) {
      const m = Math.floor(s / 60);
      const sc = s % 60;
      return String(m).padStart(2,'0') + ':' + String(sc).padStart(2,'0');
    }

    function render() {
      display.textContent = fmt(remaining);
      const pct = remaining / totalSecs;
      ring.style.strokeDashoffset = CIRC * (1 - pct); // 0=full ring, CIRC=empty
      ring.style.stroke = MODES[modeIdx].color;
      modeLabel.textContent = MODES[modeIdx].label;
      sessSpan.textContent = sessions;
    }

    function tick() {
      if (!running) return;
      remaining--;
      render();
      if (remaining <= 0) {
        clearInterval(interval);
        running = false;
        startBtn.textContent = 'START';
        startBtn.classList.remove('pomo-active');
        // log focus sessions to Notion
        const wasFocus = MODES[modeIdx].label.startsWith('Focus');
        if (wasFocus) {
          sessions = Math.min(sessions + 1, 4);
          const topicEl = document.getElementById('pomo-topic');
          const topic   = topicEl ? topicEl.value : 'General';
          logPomodoro(topic, Math.round(MODES[modeIdx].secs / 60));
        }
        // advance mode
        modeIdx = (modeIdx + 1) % MODES.length;
        if (modeIdx === 0) sessions = 0; // cycle reset
        totalSecs = MODES[modeIdx].secs;
        remaining = totalSecs;
        render();
        showToast('⏱ ' + MODES[modeIdx].label + ' — timer ready', 3000);
      }
    }

    window.pomoAction = function(action) {
      if (action === 'start') {
        running = !running;
        if (running) {
          interval = setInterval(tick, 1000);
          startBtn.textContent = 'PAUSE';
          startBtn.classList.add('pomo-active');
        } else {
          clearInterval(interval);
          startBtn.textContent = 'START';
          startBtn.classList.remove('pomo-active');
        }
      } else if (action === 'reset') {
        clearInterval(interval);
        running = false;
        remaining = totalSecs;
        startBtn.textContent = 'START';
        startBtn.classList.remove('pomo-active');
        render();
      } else if (action === 'skip') {
        clearInterval(interval);
        running = false;
        if (MODES[modeIdx].label.startsWith('Focus')) sessions = Math.min(sessions + 1, 4);
        modeIdx = (modeIdx + 1) % MODES.length;
        if (modeIdx === 0) sessions = 0;
        totalSecs = MODES[modeIdx].secs;
        remaining = totalSecs;
        startBtn.textContent = 'START';
        startBtn.classList.remove('pomo-active');
        render();
      }
    };

    render();
  })();
