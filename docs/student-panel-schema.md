# Student Panel — database schema

Covers the tables added for auth and the student dashboard, plus how they connect to what already existed (`Org`, `Person`, `RoleAssignment`, `Asset`, `Course`, `Term`). Read this alongside [`docs/implementation-plan.md`](implementation-plan.md) and the plan this build followed.

## Entity-relationship diagram

```mermaid
erDiagram
    ORG ||--o{ SCHOOL_CLASS : "scopes"
    ORG ||--o{ ROLE_ASSIGNMENT : "scopes"
    TERM ||--o{ SCHOOL_CLASS : "runs during"
    TERM ||--o{ COURSE_SECTION : "runs during"

    PERSON ||--o{ ROLE_ASSIGNMENT : "has"
    PERSON ||--o{ CLASS_ENROLLMENT : "student in"
    PERSON ||--o{ NOTIFICATION : "receives"
    PERSON ||--o{ SCORE : "earns"
    PERSON ||--o{ ATTENDANCE_RECORD : "marked for"
    PERSON ||--o{ COURSE_SECTION : "teaches (teacher_id)"
    PERSON ||--o{ SCHOOL_CLASS : "homeroom teacher"

    SCHOOL_CLASS ||--o{ CLASS_ENROLLMENT : "roster"
    SCHOOL_CLASS ||--o{ COURSE_SECTION : "offers"

    COURSE ||--o{ COURSE_SECTION : "taught as"
    ASSET ||--o{ COURSE_SECTION : "hosts (classroom_id)"

    COURSE_SECTION ||--o{ TOPIC : "syllabus"
    COURSE_SECTION ||--o{ CLASS_SESSION : "scheduled meetings"
    COURSE_SECTION ||--o{ ASSESSMENT : "quizzes/assignments"
    COURSE_SECTION ||--o{ NOTIFICATION : "related to"

    ORG ||--o{ CALENDAR_DAY : "school-day calendar"

    CLASS_SESSION ||--o{ ATTENDANCE_RECORD : "one per student"
    CLASS_SESSION ||--o| CLASS_SESSION_LOG : "daily activity log"
    CLASS_SESSION ||--o{ TOPIC : "covered in (covered_in_session_id)"
    CLASS_SESSION ||--o{ ASSESSMENT : "assigned/given in (assigned_class_session_id)"

    ASSESSMENT ||--o{ SCORE : "one per student"

    ORG {
        int id PK
        int parent_id FK
        string type "ORGANIZATION|SCHOOL|BRANCH"
        string name
    }
    PERSON {
        int id PK
        string first_name
        string last_name
        string email UK
        string password_hash "nullable - set once a login exists"
    }
    ROLE_ASSIGNMENT {
        int id PK
        int person_id FK
        int org_id FK
        string role "STUDENT|TEACHER|ADMIN|GUARDIAN"
        string local_identifier "GR/employee number, nullable"
    }
    TERM {
        int id PK
        string name
        date start_date
        date end_date
        int org_id FK
    }
    COURSE {
        int id PK
        string name
        string code UK
        string grade_level
    }
    ASSET {
        int id PK
        string type "BUILDING|CLASSROOM|..."
        string name
        int parent_id FK
        int org_id FK
    }
    SCHOOL_CLASS {
        int id PK
        string grade_name "e.g. Grade 9"
        string section_label "e.g. A"
        int term_id FK
        int org_id FK
        int homeroom_teacher_id FK
        string enrollment_mode "RESTRICTED (only mode built) | ELECTIVE (reserved)"
    }
    CLASS_ENROLLMENT {
        int id PK
        int student_id FK
        int school_class_id FK
        datetime enrolled_at
    }
    COURSE_SECTION {
        int id PK
        string name "e.g. Section A"
        int course_id FK
        int school_class_id FK
        int term_id FK
        int teacher_id FK
        int classroom_id FK
        int capacity
    }
    TOPIC {
        int id PK
        int course_section_id FK
        string name
        bool is_covered "cached convenience flag"
        int covered_in_session_id FK "which class day actually covered it"
        int sort_order
    }
    CALENDAR_DAY {
        int id PK
        int org_id FK
        date date
        string day_type "SCHOOL_DAY|HOLIDAY|WEEKEND"
        string label "e.g. Independence Day"
        string source "MANUAL|GOOGLE_SYNC"
    }
    CLASS_SESSION {
        int id PK
        int course_section_id FK
        date date
        time start_time
        time end_time
    }
    CLASS_SESSION_LOG {
        int id PK
        int class_session_id FK UK "1:1 with ClassSession"
        string classwork "what was done in class"
        string homework "house work assigned"
        string notes
        int recorded_by FK
        datetime created_at
    }
    ATTENDANCE_RECORD {
        int id PK
        int class_session_id FK
        int student_id FK
        string status "PRESENT|ABSENT|LATE|EXCUSED|HALF_DAY|REMOTE"
        int recorded_by FK
        datetime recorded_at
    }
    ASSESSMENT {
        int id PK
        int course_section_id FK
        int assigned_class_session_id FK "nullable - which day it was given"
        string title
        string type "ASSIGNMENT|QUIZ|PROJECT|PARTICIPATION|EXAM"
        int max_score
        float weight
        date due_date
    }
    SCORE {
        int id PK
        int assessment_id FK
        int student_id FK
        int marks_obtained "nullable until graded"
        string status "PENDING|SUBMITTED|GRADED|OVERDUE"
        datetime recorded_at
    }
    NOTIFICATION {
        int id PK
        int person_id FK
        string type "GRADE_POSTED|ABSENCE|DEADLINE|ANNOUNCEMENT"
        string title
        string body
        int related_course_section_id FK
        bool is_read
        datetime created_at
    }
```

## Why it's shaped this way

- **`SchoolClass` is the homeroom cohort** ("Grade 9 - A"). `enrollment_mode` defaults to `RESTRICTED`: a student's single `ClassEnrollment` row grants them every `CourseSection` tied to their class — there's no separate per-subject enrollment table, because the whole point of restricted mode is "join the class, get all its courses." `ELECTIVE` is reserved on the column for a future per-course pick-and-choose flow (college-style) but nothing reads it yet.
- **`CourseSection` carries the teacher and schedule**, not `Course`. The same `Course` (e.g. "Physics") taught to two different `SchoolClass` sections can have different teachers and different `ClassSession` times — or the same ones. Nothing forces either way.
- **`AttendanceRecord` is one row per `ClassSession` per student** — matches the learning-planning spec's design (`docs/learning-planning-and-control-spec.md`, section 4.1) exactly.
- **`Assessment`/`Score` are a pragmatic extension**, not something the specs define — the specs explicitly leave grading/marks storage out of scope. `weight` lets the dashboard compute a weighted "current progress %" per subject instead of a flat average.
- **`Notification` is simplified** — one flat table for the student-facing bell, not the full spec's `NotificationEvent`/`NotificationAudience`/`NotificationDelivery` split.
- **`Person.password_hash`** is nullable because most `Person` rows (applicants, unlinked contacts) never get a login — only accounts that go through `/auth/login` setup need it set.
- **`CalendarDay` is the source of truth for "is this a real class day"** — `ClassSession` generation walks the term date range and skips weekends and any date with a `HOLIDAY` row here, instead of assuming every weekday is a class day. It's populated by syncing Google's public regional-holiday calendar (a plain `.ics` feed, no API key needed — see `app/services/calendar_sync.py`) rather than queried live on every request; `source` distinguishes a synced row from one an admin enters by hand.
- **`ClassSessionLog` is the daily activity record** — one row per `ClassSession`, holding what was actually taught (`classwork`), what house work was assigned (`homework`), and free-form `notes`. This is what "what happened in class today" reads from, separate from the cumulative `Topic.is_covered` flag.
- **`Topic.covered_in_session_id` and `Assessment.assigned_class_session_id`** both point back at `ClassSession`, turning it into the anchor that individual student performance (attendance + scores, both already per-session) and overall course-pacing (which day covered which topic, which day a quiz was given) are both read from — without inventing a separate Curriculum/Unit/Lesson hierarchy, which the specs explicitly leave for later.

## Tables intentionally not touched here

`SubjectRequirementTemplate`, `SectionPlan`, `ResourcePlanRun`, `ResourcePlanAssignment`, `ResourceGap` — the existing resource-planning tables — are a separate concern (capacity planning for the Admin panel) and aren't read or written by the student panel.

## Seeding

Demo data lives in the `seeders/` package — one module per concern (`people`, `calendar`, `courses`, `sessions`, `assessments`, `notifications`), each independently runnable (`python -m seeders.assessments`) and idempotent, so changing one area doesn't require re-running or touching the others. `seed_student_panel.py` at the repo root just runs all of them in dependency order — the convenience entrypoint for a fresh database, not where the actual seed logic lives.
