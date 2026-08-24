"""Runs every Student Panel seeder in dependency order, against a fresh (or
existing) database. Each step is independently rerunnable on its own if
only that area changes - see seeders/*.py. This script is just the
"do everything in order" convenience entrypoint, e.g. after a full reset.

Run: python seed_student_panel.py
"""
import asyncio

from seeders.people import seed_people
from seeders.calendar import seed_calendar
from seeders.courses import seed_courses
from seeders.sessions import seed_sessions
from seeders.assessments import seed_assessments
from seeders.notifications import seed_notifications


async def main():
    await seed_people()
    await seed_calendar()
    await seed_courses()
    await seed_sessions()
    await seed_assessments()
    await seed_notifications()
    print("\nAll Student Panel seed data is in place.")


if __name__ == "__main__":
    asyncio.run(main())
