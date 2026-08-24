"""Seeds the academic calendar (regional holidays) for the term. Depends on
seeders.people having run. Safe to rerun - re-syncing just refreshes the
label/source on existing rows and adds any new ones.

Run directly: python -m seeders.calendar
"""
import asyncio

from sqlalchemy.future import select

from app.database import AsyncSessionLocal
from app.models.academic import CalendarDay
from app.services.calendar_sync import fetch_google_holidays
from seeders.common import ensure_tables, get_org, get_term

# Manual fallback in case the Google holiday feed can't be reached (e.g. no
# outbound network in this environment) - keeps the "valid class days"
# calendar meaningful even offline.
FALLBACK_PK_HOLIDAYS_2026 = [
    ("2026-08-14", "Independence Day"),
    ("2026-11-09", "Iqbal Day"),
]


async def seed_calendar():
    await ensure_tables()

    async with AsyncSessionLocal() as db:
        org = await get_org(db)
        term = await get_term(db, org.id)

        print(f"Syncing holidays for {term.name} ({term.start_date} - {term.end_date})...")
        holidays = fetch_google_holidays("pk", term.start_date, term.end_date)
        source = "GOOGLE_SYNC"
        if not holidays:
            from datetime import date as _date
            holidays = [
                (_date.fromisoformat(d), label) for d, label in FALLBACK_PK_HOLIDAYS_2026
                if term.start_date <= _date.fromisoformat(d) <= term.end_date
            ]
            source = "MANUAL"

        created, updated = 0, 0
        for holiday_date, label in holidays:
            existing = (
                await db.execute(select(CalendarDay).where(CalendarDay.org_id == org.id, CalendarDay.date == holiday_date))
            ).scalars().first()
            if existing:
                existing.day_type = "HOLIDAY"
                existing.label = label
                existing.source = source
                updated += 1
            else:
                db.add(CalendarDay(org_id=org.id, date=holiday_date, day_type="HOLIDAY", label=label, source=source))
                created += 1
        await db.commit()
        print(f"  {created} new, {updated} updated (source={source})")
        print("Done.")


if __name__ == "__main__":
    asyncio.run(seed_calendar())
