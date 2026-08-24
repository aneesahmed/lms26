# Learning Planning & Control — Component Spec
Consolidates: resource planning for teaching (who teaches what), curriculum and scheduling (what's taught when), and the calendar engine underneath both. Depends on: Org Hierarchy, Identity & Access, Resource Pool (teachers/rooms/TAs as Resources), Notification Management.

**Note on scope:** the recurrence and clash-detection engine defined in Part C is also used by Resource Pool (bookings), Resource Finance (recurring billing), Library (due dates), and Regulatory Audit & Control (review cycles). It lives here because this is where it was built for and is used most heavily, but it's shared infrastructure — those specs reference this document for scheduling mechanics.

---

# Part A — Resource Planning (who teaches what)

## 1. In school terminology, plan directly against the Class

"Class" here means the same thing as `Section` — Grade 9-Blue's classes are its subjects and sessions, with no separate multi-year structure sitting above it. `Program` still exists for genuinely multi-year structured plans (a two-year A-Level track, a university degree), but ordinary grade-level planning doesn't need that extra layer. The planner targets whichever one actually applies — a Class directly for a normal school section, a Program where a real multi-term structure exists above it.

---

## 2. The team — five roles, two different scopes

| Role | Attaches to | What they do |
|---|---|---|
| Coordinator | Class, or Program where one exists | Oversees the whole class or program — exclusive to it, or shared across several (Resource Pool, Section 3) |
| Class teacher | Class (Section) | Attendance, pastoral care, owns the class as a unit — one per class, not per subject |
| Subject teacher | Course offering | Teaches one subject to one class |
| Teaching assistant | Course offering (usually), occasionally the whole Class | One or more, supports a subject teacher or the class teacher directly |
| Support staff | Class or Program | Whatever the stage needs — a Pre-Primary helper, a lab assistant |

The class teacher is not a subject teacher with extra duties — a distinct role, scoped to the class as a whole. A class has exactly one class teacher and as many subject teachers as it has course offerings running.

---

## 3. Subject requirement template — the reusable definition

Defined once per Course, versioned like content already is, updated on whatever cadence makes sense — yearly, quarterly, or on demand. This is the "what does this subject need" statement, made once, reused every term until it changes.

```
SubjectRequirementTemplate
  course_id, version, effective_from, effective_to (nullable = current)
  role_needed             SUBJECT_TEACHER | LAB_INCHARGE | TA | SUPPORT_STAFF
  count_per_section         usually 1; a lab in-charge is often fractional, shared
  allocation_mode_hint      DEDICATED | SHARED
  room_type_needed          defaults from Course.facility_type_needed, overridable
  equipment_needed           [PROJECTOR, WHITEBOARD, ...]
  periods_per_week
```

`Course.facility_type_needed` (REGULAR/LAB/GROUND/HALL/THEATRE/AUDITORIUM, default REGULAR) drives the default room requirement — sports needs a ground or hall, music or art needs a theatre, chemistry needs a lab, most subjects need a regular classroom. The template can override this per subject when the default doesn't fit.

---

## 4. Section count — computed from a fixed estimate, not live enrolment

```
SectionPlan
  class_level_id, term_id
  estimated_enrollment      given as an input at planning time, not read live
  max_section_size
  computed_section_count    = ceil(estimated_enrollment / max_section_size)
  status                     DRAFT | LOCKED
```

`LOCKED` means fixed for that planning cycle. If actual enrolment ends up different from the estimate, that's a new planning cycle's concern, not a reason to reopen this one. 90 estimated students at a 30-student cap produces 3 sections — 9-A, 9-B, 9-C — created from this, not typed in by hand.

---

## 5. The planning run — template × section count, matched to supply

```
ResourcePlanRun
  id, container_type (CLASS | PROGRAM), container_id, term_id
  status                 DRAFT | SIMULATED | PUBLISHED

ResourcePlanAssignment
  plan_run_id
  target_type            CLASS | COURSE_OFFERING | PROGRAM
  target_id                → Section.id (a Class), CourseOffering.id, or Program.id
  role                    CLASS_TEACHER | SUBJECT_TEACHER | TA | COORDINATOR | SUPPORT_STAFF | PRO
  resource_id              → the specific Resource filling this role, from the Resource Pool
  room_resource_id, equipment_resource_ids     nullable
  reports_to_assignment_id  nullable — overrides the default reporting line (Section 6)
  status                  PROPOSED | CONFIRMED | GAP
```

The flow: `SubjectRequirementTemplate` (Section 3) exploded by `computed_section_count` (Section 4) produces this term's actual requirement list, which gets matched against the Resource Pool as supply — same shape as the Class Planner's `TimetableVersion` (draft, simulate, publish), one layer up. This decides *who and what*; the Class Planner then decides *when*, using these confirmed assignments as its input. A plan run doesn't generate class sessions itself.

**Rooms behave differently depending on type.** A class's home classroom is a term-length dedicated booking — two sections means two classrooms, full stop. A lab, ground, or theatre is contested, shared across many sections' periods, booked per-session through the same clash-check. Both are `RESERVABLE` resources in the Resource Pool; only the booking's duration and how often it's contested differs.

**"The team" is a view, not a new table.** Everything a coordinator needs to see for one class or program — coordinator, class teacher, every subject teacher, every TA, support staff, rooms — is `ResourcePlanAssignment` filtered by `target_id`. The UI's planning layout (built later) queries this directly.

---

## 6. Reporting lines — a default lookup, not a per-assignment decision

Most reporting lines are the same shape every time, so they're a preset-level default, not something re-decided per person.

```
RoleReportingDefault      -- preset-level, like the label pack
  role                      the role reporting up
  reports_to_role            the role above it
```

TA → Subject Teacher, Subject Teacher → Coordinator, Class Teacher → Coordinator, Support Staff → Class Teacher, Coordinator → Branch Head. `ResourcePlanAssignment.reports_to_assignment_id` handles the rare override — a TA who genuinely reports straight to the coordinator instead of the usual subject teacher.

---

## 7. Gaps trigger acquisition, not silent failure

```
ResourceGap
  plan_run_id, role_needed, subject_id, count_short
  room_type_needed          nullable
  status                     OPEN | HIRING_INITIATED | PROCUREMENT_INITIATED | RESOLVED
```

If a plan run needs three Chemistry teachers and the Resource Pool only has two competent and available, that's a `ResourceGap`, not a plan that silently ships incomplete. A staffing gap routes toward hiring (a new `Employee`, entering the Resource Pool as any resource does). An equipment gap routes toward procurement against `Facility`. Either way, the gap is visible and owned, not discovered later when a coordinator can't find a teacher for a class that was supposedly planned.

---

# Part B — Curriculum, Scheduling, Attendance, Assessment (what's taught, when)

## 1. Scope

Seven-stage pipeline. Resource allocation is handled in Part A above — this component starts once teachers, rooms, and sections are already confirmed.

1. Curriculum & study material definition
2. Syllabus alignment
3. Scheduling (term-level + session-level)
4. Attendance
5. Assessment & assignment planning
6. Self-study material
7. Coverage tracking

---

## 2. Curriculum & study material definition

- One authoring layer, reused for both live teaching and self-study
- `Curriculum → Unit → Lesson → LearningObjective → Resource`
- Versioned per Course — editing next year's copy never touches last year's
- `PublishState`: draft → review → published → archived
- Self-study uses the *same* resources — no separate content system, just a different delivery sequence

---

## 3. Syllabus alignment

- Maps internal planning to the board's official topic list — Cambridge, Federal, IB, or `INTERNAL` where a school sets its own curriculum with no external certifying body
- `SyllabusTopic` — board_id, course_id, topic_code, topic_name
- `SyllabusMapping` — unit_id/lesson_id → syllabus_topic_id
- A topic with no mapping = a gap worse than a scheduling gap — something the board requires isn't planned anywhere. For `INTERNAL`, the school's own curriculum team owns the topic list and the same rule applies
- Feeds the coverage dashboard (Section 7)

---

## 4. Scheduling

**Term-level — `SchemeOfWork`**
- Maps curriculum units onto term weeks, per class
- Status: PLANNED | IN_PROGRESS | COMPLETED | DELAYED

**Session-level — `LessonPlan`**
- One per `ClassSession`
- `session_type`: TEACHING | PRACTICE | ASSESSMENT | REMEDIAL | SELF_STUDY | REVIEW
- Remedial (relabeled "Support" for Pre-Primary/Primary) targets a subset of students, not the whole class — uses Calendar's existing student-level audience targeting

---

## 4.1 Attendance — one record per session, per student

Tied to the session, not to the day in isolation — attendance is a per-`ClassSession` fact.

```
AttendanceRecord
  class_session_id, student_id
  status            PRESENT | ABSENT | LATE | EXCUSED | HALF_DAY | REMOTE
  recorded_by, recorded_at
```

- SELF_STUDY sessions never generate attendance — no live session exists to be present for (Section 6)
- REMEDIAL sessions track attendance the same as any other type, just for the subset of students actually invited
- Grace period, half-day cutoff, and leave-request integration are policy, not schema — configurable per preset the same way behaviour flags are elsewhere in this system, not hardcoded
- An absence raises a `NotificationEvent` (Notification Management spec) to the guardian, same pipeline as everything else that alerts someone
- Attendance rate feeds `GapRecord` in Gap Analysis where it crosses a compliance threshold (a board-mandated minimum attendance requirement), same as a coverage gap does

---

## 5. Assessment & assignment planning

- One definition/instance pattern for both — not two parallel systems
- `Quiz`/`Assignment` (definition) → `QuizAttempt`/`Submission` (instance)
- Differentiated by weight and format, not by separate content models
- Sequencing rule: an assessment on a unit shouldn't schedule before `SchemeOfWork` marks that unit taught
- External board deadlines (Cambridge/Federal coursework and marks submission) as a `CalendarEvent` type at the Board-level School — assessment planning respects them instead of discovering them

---

## 6. Self-study material

- Same content as Section 2, sequenced differently
- `PacingSchedule` — suggested milestones, no live `ClassSession`, no attendance
- Progress tracked by completion, not presence

---

## 7. Coverage tracking

- One dashboard, four questions: planned vs delivered vs board-required vs assessed
- Delivered — `LessonPlan.delivered`, marked after the fact, not assumed from being scheduled
- Board-required — `SyllabusMapping` coverage %
- A gap here is the same signal type as a `RemedialTrigger` — this is where the two loops connect

---

## 8. New data elements (incremental — everything else already exists)

```
SyllabusTopic       board_id, course_id, topic_code, topic_name
SyllabusMapping      unit_id/lesson_id, syllabus_topic_id
session_type         enum added to LessonPlan/ClassSession
```

---

# Part C — Calendar Engine (the scheduling backbone for A and B, and shared with other specs)

## 1. One shared table, not a date column per module

Domain modules stay authoritative for their own data. The calendar table is a projection, not a second source of truth.

```
Domain module writes its row  →  emits an event  →  Calendar repository upserts a projection
```

A `ClassSession` still lives in the planner's tables with teacher, room, offering. An `Exam` still lives in assessment's tables with syllabus scope and invigilators. Neither disappears. Each one, on create/update/cancel, writes one row into `CalendarEvent`. Nothing outside this repository ever needs to know how many domain tables have a date field.

---

## 2. The table

```
CalendarEvent
  id, org_id                  scoped to whichever Org node it belongs to — School or Branch
  event_type          CLASS_SESSION | EXAM | ASSIGNMENT_DUE | PTM_SLOT | HOLIDAY
                       | LEAVE | ANNOUNCEMENT_DATED | PACING_MILESTONE | REMEDIAL_SESSION
  source_type, source_id      the owning domain table and row
  start_at, end_at, all_day
  recurrence_rule       RFC5545-style rule, for recurring entries
  status                 DRAFT | PUBLISHED | CANCELLED | RESCHEDULED
  visibility              INTERNAL_ONLY | SYNCABLE
  term_week_id, cycle_day

CalendarEventAudience
  event_id
  audience_type          STUDENT | GUARDIAN | TEACHER | SECTION | COURSE_OFFERING | UNIT
  audience_id
```

Every screen that answers "what's happening, and when, for whom" reads `CalendarEvent` joined to `CalendarEventAudience` — never a UNION across five domain tables.

**Why one table:**
- One place enforces "an event only appears once it's published" — not five modules each remembering the rule
- One place drives the sync boundary (Section 3) instead of five sync jobs
- Coverage, workload, and clash queries stop needing custom joins
- A new event-bearing module — a library due-date reminder, a Gap Analysis remediation deadline — is one new `event_type`, not a new query path threaded through every screen

**Discipline that keeps it honest:** `CalendarEvent` never stores teacher assignments or room bookings itself. Those stay on `ClassSession`/`ResourceBooking`. The calendar row points back via `source_type`/`source_id` for detail.

---

## 3. Sync boundary

Scans `CalendarEvent` where `status = PUBLISHED` and `visibility = SYNCABLE`, pushes or feeds those out. Never queries domain tables directly.

- **Syncable by default:** CLASS_SESSION, EXAM, ASSIGNMENT_DUE, PTM_SLOT, PACING_MILESTONE (if opted in)
- **Internal-only always:** anything still DRAFT, plus operational rows nobody needs on their phone — seating plans, invigilator rosters, scheme-of-work entries
- **Audience-scoped:** reads `CalendarEventAudience` to know whose feed an event belongs to

`EventSyncMap` keys off `CalendarEvent.id`, not the underlying domain row — the sync layer stays ignorant of which module produced any given entry.

---

## 4. Recurrence and clash-checking — the engine other specs reuse

One generation engine, reused across the system, not rebuilt per module:

- Expands a `TimetableSlot` rule into concrete `ClassSession` rows (Learning Resource Planner)
- Generates recurring `ResourceCostAllocation` invoice lines (Resource Finance)
- Generates periodic `AssetDepreciation` and scheduled `ResourceMaintenanceWindow` entries (Resource Finance, Resource Pool)
- Re-runs `ComplianceCheck`s on their `review_cycle` (Gap Analysis)

Clash-checking works the same way across every consumer: a session that needs a room creates a `ResourceBooking`, and the same check that stops two sections colliding on a teacher stops two events colliding on a room or an auditorium.

---

---

# Consolidated Build Order

1. `CalendarEvent` / `CalendarEventAudience` — the table and publish/status rules (Part C)
2. Recurrence engine and clash-checking (Part C)
3. `SubjectRequirementTemplate`, `SectionPlan` (Part A)
4. `ResourcePlanRun` / `ResourcePlanAssignment`, `RoleReportingDefault` (Part A)
5. `ResourceGap` (Part A)
6. Curriculum authoring: `Curriculum → Unit → Lesson → LearningObjective → Resource` (Part B)
7. `SyllabusTopic` / `SyllabusMapping` (Part B)
8. `SchemeOfWork` / `LessonPlan` with `session_type` (Part B)
9. `AttendanceRecord` (Part B)
10. Assessment/assignment scheduling, `PacingSchedule` for self-study (Part B)
11. Coverage tracking dashboard (Part B)
12. Sync boundary — ICS feed, OAuth push later (Part C)

---

# Consolidated Open Decisions

- Whether `LAB_INCHARGE` (and similarly fractional/shared roles) defaults to `SHARED` allocation mode automatically, or is chosen explicitly per template
- Whether a `ResourcePlanRun` publish is blocked by an open `ResourceGap` (hard block) or allowed through with a visible warning
- Whether `SubjectRequirementTemplate` versioning needs approval workflow or is a plain edit-and-save
- Who owns `SyllabusMapping` — central content team, or each subject teacher per class
- Whether an assessment scheduled ahead of its unit's `SchemeOfWork` completion is a hard block or a warning
- What attendance grace period and half-day rules default to per school type — a preset behaviour flag, not yet enumerated per `school_type`
- Whether `CalendarEvent` is populated on write by each domain module, or maintained by a background listener
- OAuth push timing — build alongside ICS from day one, or defer
