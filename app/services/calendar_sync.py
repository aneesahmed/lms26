"""Regional holiday sync from Google's public holiday calendars.

Google publishes each country's public-holiday calendar as a plain,
unauthenticated ICS feed (no API key or OAuth needed - it's the same feed
"Holidays in <Country>" subscribes to in Google Calendar). We fetch it
directly and pull out the date + name of each all-day event.

If the fetch fails (no network access, feed unreachable, etc.) callers get
an empty list rather than an exception - holiday sync is a nice-to-have on
top of manually-entered CalendarDay rows, not a hard dependency.
"""
import re
import urllib.request
from datetime import date, datetime

GOOGLE_HOLIDAY_CALENDARS = {
    "pk": "en.pk#holiday@group.v.calendar.google.com",  # Pakistan
    "us": "en.usa#holiday@group.v.calendar.google.com",
    "uk": "en.uk#holiday@group.v.calendar.google.com",
}


def _ics_url(country_code: str) -> str:
    calendar_id = GOOGLE_HOLIDAY_CALENDARS[country_code]
    encoded = calendar_id.replace("#", "%23").replace("@", "%40")
    return f"https://calendar.google.com/calendar/ical/{encoded}/public/basic.ics"


def fetch_google_holidays(country_code: str, start: date, end: date, timeout: float = 8.0) -> list[tuple[date, str]]:
    """Returns [(date, holiday_name), ...] within [start, end], best-effort."""
    try:
        req = urllib.request.Request(_ics_url(country_code), headers={"User-Agent": "BrainiacsLMS/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return []

    holidays = []
    for block in body.split("BEGIN:VEVENT")[1:]:
        block = block.split("END:VEVENT")[0]
        date_match = re.search(r"DTSTART;VALUE=DATE:(\d{8})", block)
        summary_match = re.search(r"SUMMARY:(.+)", block)
        if not date_match or not summary_match:
            continue
        event_date = datetime.strptime(date_match.group(1), "%Y%m%d").date()
        if start <= event_date <= end:
            holidays.append((event_date, summary_match.group(1).strip()))
    return holidays
