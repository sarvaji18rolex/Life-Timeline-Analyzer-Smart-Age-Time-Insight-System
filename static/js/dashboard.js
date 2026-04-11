/**
 * dashboard.js
 * Handles live counters, clock, birthday countdown, and Chart.js visualizations.
 */

// ── Parse server-side data ────────────────────────────────────────────────────
const STATS      = JSON.parse(document.getElementById('statsData').textContent);
const DOB_STR    = JSON.parse(document.getElementById('dobData').textContent);
const DOB_DATE   = new Date(DOB_STR + 'T00:00:00');

// Track cumulative seconds from the server's snapshot
let serverSeconds = STATS.totals.seconds;
let lastTick      = Date.now();


// ── Live Clock ────────────────────────────────────────────────────────────────
function updateClock() {
  const now   = new Date();
  const h     = String(now.getHours()).padStart(2, '0');
  const m     = String(now.getMinutes()).padStart(2, '0');
  const s     = String(now.getSeconds()).padStart(2, '0');
  const clock = document.getElementById('liveClock');
  const date  = document.getElementById('liveDate');
  if (clock) clock.textContent = `${h}:${m}:${s}`;
  if (date)  date.textContent  = now.toLocaleDateString(undefined, { weekday:'long', year:'numeric', month:'long', day:'numeric' });
}


// ── Live Age in Seconds (ticks every second) ──────────────────────────────────
function tickSeconds() {
  const now    = Date.now();
  const delta  = Math.floor((now - lastTick) / 1000);
  if (delta >= 1) {
    serverSeconds += delta;
    lastTick = now - ((now - lastTick) % 1000);  // keep sub-second precision

    const el = document.getElementById('ageSeconds');
    if (el) el.textContent = serverSeconds.toLocaleString();

    // Also update total minutes & hours occasionally
    updateDerivedTotals();
  }
}

function updateDerivedTotals() {
  const mins  = Math.floor(serverSeconds / 60);
  const hours = Math.floor(serverSeconds / 3600);

  const mEl = document.getElementById('totalMins');
  const hEl = document.getElementById('totalHours');
  if (mEl) mEl.textContent  = mins.toLocaleString();
  if (hEl) hEl.textContent  = hours.toLocaleString();
}


// ── Birthday Countdown ────────────────────────────────────────────────────────
function updateBirthdayCountdown() {
  const el = document.getElementById('bdayLive');
  if (!el) return;

  const now      = new Date();
  const thisYear = now.getFullYear();
  let bday       = new Date(thisYear, DOB_DATE.getMonth(), DOB_DATE.getDate(), 0, 0, 0);
  if (bday <= now) bday = new Date(thisYear + 1, DOB_DATE.getMonth(), DOB_DATE.getDate(), 0, 0, 0);

  const diff  = bday - now;
  const d     = Math.floor(diff / 86400000);
  const h     = Math.floor((diff % 86400000) / 3600000);
  const m     = Math.floor((diff % 3600000)  / 60000);
  const s     = Math.floor((diff % 60000)    / 1000);

  el.textContent = `${String(d).padStart(3,'0')}d : ${String(h).padStart(2,'0')}h : ${String(m).padStart(2,'0')}m : ${String(s).padStart(2,'0')}s`;

  // Update bdayDays element
  const dEl = document.getElementById('bdayDays');
  if (dEl) dEl.textContent = d;
}


// ── Master Tick (every 100 ms for smooth second counter) ─────────────────────
function masterTick() {
  updateClock();
  tickSeconds();
  updateBirthdayCountdown();
}


// ── Animate Number Counter ────────────────────────────────────────────────────
function animateCounter(el, targetVal, duration = 1200) {
  const start     = performance.now();
  const startVal  = 0;

  function step(now) {
    const elapsed  = now - start;
    const progress = Math.min(elapsed / duration, 1);
    // Ease-out cubic
    const eased    = 1 - Math.pow(1 - progress, 3);
    const current  = Math.round(startVal + (targetVal - startVal) * eased);
    el.textContent = current.toLocaleString();
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}


// ── Initialize Counters ───────────────────────────────────────────────────────
function initCounters() {
  const counters = {
    totalDays:  STATS.totals.days,
    totalWeeks: STATS.totals.weeks,
    totalHours: STATS.totals.hours,
    totalMins:  STATS.totals.minutes,
  };
  for (const [id, val] of Object.entries(counters)) {
    const el = document.getElementById(id);
    if (el) animateCounter(el, val, 1400);
  }

  // Age components
  const ageEl = document.getElementById('ageSeconds');
  if (ageEl) animateCounter(ageEl, serverSeconds, 1800);
}


// ── Chart.js Configuration ────────────────────────────────────────────────────
const CHART_COLORS = {
  cyan:   '#00d4ff',
  purple: '#b388ff',
  gold:   '#f0c040',
  green:  '#3fb950',
  red:    '#ff6b6b',
  yellow: '#ffdd57',
  gridLine: 'rgba(255,255,255,0.05)',
  text:   '#8b949e',
};

const FONT = { family: "'DM Sans', sans-serif" };

Chart.defaults.color  = CHART_COLORS.text;
Chart.defaults.font   = FONT;

function initCharts() {

  // ── 1. Day vs Night Pie ──────────────────────────────────────────────────
  const pieCtx = document.getElementById('pieChart');
  if (pieCtx) {
    new Chart(pieCtx, {
      type: 'doughnut',
      data: {
        labels: ['Daylight (6AM–6PM)', 'Night (6PM–6AM)'],
        datasets: [{
          data: [
            STATS.day_night.day_hours,
            STATS.day_night.night_hours,
          ],
          backgroundColor: [
            'rgba(255,221,87,0.75)',
            'rgba(179,136,255,0.75)',
          ],
          borderColor: [
            '#ffdd57',
            '#b388ff',
          ],
          borderWidth: 2,
          hoverOffset: 8,
        }],
      },
      options: {
        responsive: true,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { padding: 20, font: { size: 12 } },
          },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.label}: ${ctx.parsed.toLocaleString()} hours`,
            },
          },
        },
        animation: { animateRotate: true, duration: 1400, easing: 'easeOutQuart' },
      },
    });
  }

  // ── 2. Age Breakdown Bar ─────────────────────────────────────────────────
  const barCtx = document.getElementById('barChart');
  if (barCtx) {
    new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: ['Years', 'Months', 'Weeks', 'Days (÷100)'],
        datasets: [{
          label: 'Age Components',
          data: [
            STATS.age.years,
            STATS.age.years * 12 + STATS.age.months,
            STATS.totals.weeks,
            Math.floor(STATS.totals.days / 100),
          ],
          backgroundColor: [
            'rgba(0,212,255,0.6)',
            'rgba(179,136,255,0.6)',
            'rgba(240,192,64,0.6)',
            'rgba(63,185,80,0.6)',
          ],
          borderColor: [
            CHART_COLORS.cyan,
            CHART_COLORS.purple,
            CHART_COLORS.gold,
            CHART_COLORS.green,
          ],
          borderWidth: 1.5,
          borderRadius: 8,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.raw.toLocaleString()}`,
            },
          },
        },
        scales: {
          x: { grid: { color: CHART_COLORS.gridLine } },
          y: {
            grid: { color: CHART_COLORS.gridLine },
            ticks: { callback: v => v.toLocaleString() },
            beginAtZero: true,
          },
        },
        animation: { duration: 1400, easing: 'easeOutQuart' },
      },
    });
  }

  // ── 3. Life Progress Chart ───────────────────────────────────────────────
  const progressCtx = document.getElementById('progressChart');
  if (progressCtx) {
    const pct      = STATS.life_progress.pct_complete;
    const livedYrs = STATS.age.years + STATS.age.months / 12;
    const leftYrs  = STATS.life_progress.remaining_years;
    const avgLife  = STATS.life_progress.avg_lifespan;

    new Chart(progressCtx, {
      type: 'bar',
      data: {
        labels: ['Your Life (80 yr avg)'],
        datasets: [
          {
            label: `Lived (${pct}%)`,
            data: [livedYrs],
            backgroundColor: 'rgba(0,212,255,0.7)',
            borderColor: CHART_COLORS.cyan,
            borderWidth: 2,
            borderRadius: { topLeft: 8, bottomLeft: 8 },
            borderSkipped: false,
          },
          {
            label: `Remaining (~${leftYrs} yrs)`,
            data: [leftYrs],
            backgroundColor: 'rgba(255,255,255,0.07)',
            borderColor: 'rgba(255,255,255,0.12)',
            borderWidth: 1,
            borderRadius: { topRight: 8, bottomRight: 8 },
            borderSkipped: false,
          },
        ],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { padding: 20, font: { size: 12 } },
          },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.dataset.label}: ${ctx.raw.toLocaleString()} years`,
            },
          },
        },
        scales: {
          x: {
            stacked: true,
            max: avgLife,
            grid: { color: CHART_COLORS.gridLine },
            ticks: { callback: v => `${v}y` },
          },
          y: {
            stacked: true,
            grid: { color: CHART_COLORS.gridLine },
          },
        },
        animation: { duration: 1600, easing: 'easeOutQuart' },
      },
    });
  }
}


// ── Sidebar Active Link Highlighting on Scroll ────────────────────────────────
function initScrollSpy() {
  const sections = document.querySelectorAll('[id]');
  const navItems = document.querySelectorAll('.nav-item[href^="#"]');

  const obs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navItems.forEach(n => n.classList.remove('active'));
        const active = document.querySelector(`.nav-item[href="#${entry.target.id}"]`);
        if (active) active.classList.add('active');
      }
    });
  }, { threshold: 0.4 });

  sections.forEach(s => obs.observe(s));
}


// ── Animate Progress Bar on Load ──────────────────────────────────────────────
function animateProgressBar() {
  const bar = document.getElementById('lifeProgressBar');
  if (!bar) return;
  const target = bar.style.width;
  bar.style.width = '0%';
  setTimeout(() => { bar.style.width = target; }, 300);
}


// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  masterTick();                          // immediate first tick
  setInterval(masterTick, 100);          // update every 100 ms

  initCounters();                        // animated number counters
  initCharts();                          // Chart.js graphs
  initScrollSpy();                       // sidebar active link
  animateProgressBar();                  // progress bar animation

  // Staggered insight card entrance
  document.querySelectorAll('.insight-card').forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = `opacity 0.5s ${i * 0.07}s ease, transform 0.5s ${i * 0.07}s ease`;
    setTimeout(() => {
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 100 + i * 70);
  });
});
