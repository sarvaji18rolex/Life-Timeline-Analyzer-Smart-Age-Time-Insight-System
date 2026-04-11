"""
utils/calculations.py
Core calculation engine for Life Timeline Analyzer.
All time-based life statistics are computed here.
"""

from datetime import datetime, date, timedelta
import pytz
import math


class LifeCalculator:
    """Encapsulates all life-timeline calculations for a given DOB."""

    AVG_LIFESPAN_YEARS   = 80
    HEARTBEATS_PER_MIN   = 72
    BREATHS_PER_MIN      = 16
    STEPS_PER_DAY        = 7500
    SLEEP_FRACTION       = 1 / 3          # ~8 hrs/day
    DAY_START_HOUR       = 6              # 06:00 AM
    DAY_END_HOUR         = 18             # 06:00 PM (18:00)
    DAY_HOURS            = DAY_END_HOUR - DAY_START_HOUR          # 12 hrs
    NIGHT_HOURS          = 24 - DAY_HOURS                          # 12 hrs

    def __init__(self, dob_str: str, timezone_str: str = 'UTC'):
        self.tz  = self._resolve_tz(timezone_str)
        self.dob = datetime.strptime(dob_str, '%Y-%m-%d').replace(tzinfo=self.tz)
        self.now = datetime.now(self.tz)

    # ── Timezone ──────────────────────────────────────────────────────────────
    @staticmethod
    def _resolve_tz(tz_str: str):
        try:
            return pytz.timezone(tz_str)
        except pytz.UnknownTimeZoneError:
            return pytz.UTC

    # ── Core Age ──────────────────────────────────────────────────────────────
    def age_components(self):
        """Return dict with years, months, days components of age."""
        years  = self.now.year  - self.dob.year
        months = self.now.month - self.dob.month
        days   = self.now.day   - self.dob.day

        if days < 0:
            months -= 1
            prev_month_end = (self.now.replace(day=1) - timedelta(days=1))
            days += prev_month_end.day

        if months < 0:
            years  -= 1
            months += 12

        return {'years': years, 'months': months, 'days': days}

    def total_seconds_lived(self):
        delta = self.now - self.dob
        return int(delta.total_seconds())

    def total_minutes_lived(self):
        return int(self.total_seconds_lived() / 60)

    def total_hours_lived(self):
        return int(self.total_seconds_lived() / 3600)

    def total_days_lived(self):
        return (self.now.date() - self.dob.date()).days

    def total_weeks_lived(self):
        return int(self.total_days_lived() / 7)

    # ── Day / Night split ─────────────────────────────────────────────────────
    def day_night_split(self):
        """
        For each day of life, 12 hours are 'day' (06:00-18:00) and 12 are 'night'.
        Returns approximate totals in hours.
        """
        total_days   = self.total_days_lived()
        day_hours    = total_days * self.DAY_HOURS
        night_hours  = total_days * self.NIGHT_HOURS
        return {
            'day_hours':     day_hours,
            'night_hours':   night_hours,
            'day_days':      round(day_hours / 24, 1),
            'night_days':    round(night_hours / 24, 1),
            'day_percent':   50,
            'night_percent': 50,
        }

    # ── Life Progress ─────────────────────────────────────────────────────────
    def life_progress(self):
        age_comps      = self.age_components()
        years_lived    = age_comps['years'] + age_comps['months'] / 12
        pct_complete   = min(round((years_lived / self.AVG_LIFESPAN_YEARS) * 100, 2), 100)
        remaining_yrs  = max(self.AVG_LIFESPAN_YEARS - years_lived, 0)
        remaining_days = int(remaining_yrs * 365.25)

        return {
            'pct_complete':   pct_complete,
            'remaining_years': round(remaining_yrs, 1),
            'remaining_days':  remaining_days,
            'avg_lifespan':    self.AVG_LIFESPAN_YEARS,
        }

    # ── Birthday Countdown ────────────────────────────────────────────────────
    def birthday_countdown(self):
        today     = self.now.date()
        next_bday = date(today.year, self.dob.month, self.dob.day)
        if next_bday <= today:
            next_bday = date(today.year + 1, self.dob.month, self.dob.day)
        days_left = (next_bday - today).days
        return {
            'days_left':  days_left,
            'next_bday':  next_bday.strftime('%B %d, %Y'),
            'is_today':   days_left == 0,
        }

    # ── Fun Bio Statistics ────────────────────────────────────────────────────
    def fun_stats(self):
        total_mins    = self.total_minutes_lived()
        total_days    = self.total_days_lived()
        heartbeats    = total_mins * self.HEARTBEATS_PER_MIN
        breaths       = total_mins * self.BREATHS_PER_MIN
        sleep_days    = round(total_days * self.SLEEP_FRACTION, 1)
        sleep_years   = round(sleep_days / 365.25, 2)
        steps         = total_days * self.STEPS_PER_DAY
        steps_km      = round(steps * 0.762 / 1000, 0)   # avg stride ~76.2 cm

        return {
            'heartbeats':    heartbeats,
            'breaths':       breaths,
            'sleep_days':    sleep_days,
            'sleep_years':   sleep_years,
            'steps':         steps,
            'steps_km':      int(steps_km),
        }

    # ── Time Insights Messages ────────────────────────────────────────────────
    def time_insights(self):
        secs   = self.total_seconds_lived()
        days   = self.total_days_lived()
        years  = self.age_components()['years']
        fstats = self.fun_stats()
        prog   = self.life_progress()

        insights = []

        if secs >= 1_000_000_000:
            insights.append(f"🌟 You have lived over {secs // 1_000_000_000} billion seconds!")
        elif secs >= 1_000_000:
            insights.append(f"✨ You have lived over {secs // 1_000_000:,} million seconds!")

        sleep_pct = round((fstats['sleep_days'] / days) * 100, 1) if days else 0
        insights.append(f"😴 You've spent approximately {sleep_pct}% of your life sleeping.")

        insights.append(f"❤️  Your heart has beaten roughly {fstats['heartbeats']:,} times.")

        if days >= 10_000:
            insights.append(f"🎯 You have crossed the 10,000 days milestone!")

        insights.append(f"🚶 You've walked an estimated {fstats['steps_km']:,} km in your lifetime.")

        insights.append(
            f"⏳ You've completed {prog['pct_complete']}% of the average human lifespan."
        )

        if years >= 18:
            insights.append("🔑 You've been a legal adult for at least some years — own it!")

        insights.append(
            f"🌬️  You've taken approximately {fstats['breaths']:,} breaths so far."
        )

        return insights

    # ── Master Stats Bundle ───────────────────────────────────────────────────
    def get_all_stats(self):
        """Return a single dict with every statistic needed by the dashboard."""
        return {
            'age':            self.age_components(),
            'totals': {
                'seconds': self.total_seconds_lived(),
                'minutes': self.total_minutes_lived(),
                'hours':   self.total_hours_lived(),
                'days':    self.total_days_lived(),
                'weeks':   self.total_weeks_lived(),
            },
            'day_night':      self.day_night_split(),
            'life_progress':  self.life_progress(),
            'birthday':       self.birthday_countdown(),
            'fun_stats':      self.fun_stats(),
            'insights':       self.time_insights(),
            'timestamp':      self.now.isoformat(),
        }
