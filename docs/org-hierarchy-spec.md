# Org Hierarchy — Component Spec
Foundational. Every other spec in this system references `Org` — this is the one place it's actually defined.

---

## 1. One self-referencing table, not fixed tiers

```
Org
  id
  parent_id      → Org.id, nullable at the root
  type           ORGANIZATION | SCHOOL | BRANCH
  name
```

Same mechanism Canvas's account/sub-account tree and the OneRoster K-12 standard both use — arbitrary depth in principle, three levels in practice here.

- **Organization** — the business entity. Billing, top-level reporting. No academic logic of its own.
- **School** — one full curriculum identity: one stage, one board, one teaching system, one brand name. Separate ID, separate everything downstream. `board = INTERNAL` when a school sets its own curriculum with no external certifying body — never null.
- **Branch** — one physical location running that school.

---

## 2. A school with two boards is two schools

`Brainiac High School — Cambridge` and `Brainiac High School — IB` are two separate `School` rows. Different curriculum, different grading scale, different exam calendar, different teaching philosophy.

```
Organization: "Brainiac Education Group"
  ├── School: "Brainiac High School — Cambridge"   school_type = HIGHER, board = CAMBRIDGE
  │     └── Branch: PECHS Campus
  └── School: "Brainiac High School — IB"           school_type = HIGHER, board = IB
        └── Branch: PECHS Campus
```

Each School carries `school_type` (education stage) and `board` (curriculum authority). The combination makes it distinct — a HIGHER/CAMBRIDGE school and a HIGHER/IB school are never the same row.

**Everything scopes to School, nothing shared by default:** `GradingScale`, `Curriculum`, exam calendar, students, teachers, sections, courses.

**Co-location is a fact about addresses, not a structural relationship.**

```
PhysicalLocation
  id, address, city, latitude, longitude

Branch
  id, org_id (→ School), physical_location_id (→ PhysicalLocation, nullable)
```

Two Schools sharing a campus reference the same `PhysicalLocation` — descriptive, not administrative. Nothing about students, staff, or curriculum crosses that reference.

---

## 3. Boards are exclusive

A student is active in exactly one board-School at a time — no dual `Enrolment` across boards. A board switch is an ordinary `SCHOOL_CHANGE` transfer (Resource Pool spec, Section 2), with the receiving board's coordinator placing the student rather than the system inferring standing across two syllabi. Rare in practice — most transfers are the class-to-class or campus cases covered in Identity & Access, Section 3.

---

## 4. Presets and the label pack

Each `school_type` + `board` combination resolves a preset — labels and behaviour flags, not hardcoded per school. Labels are free to change (Settings, no migration); behaviour flags (attendance grain, progression rule) are gated separately and require confirmation, since they affect how data gets recorded, not just how it reads.

| school_type | Labels default to | Attendance | Calendar cycle |
|---|---|---|---|
| PRE_PRIMARY | Wing, Child, Key Person | Daily | Weekly |
| PRIMARY / MIDDLE | Wing, Student, Class Teacher | Daily | Weekly |
| HIGHER | Curriculum Board, Student, Subject Head | Per session | 6-day cycle |
| COLLEGE | Faculty, Student, Group | Per session | Weekly |
| UNIVERSITY (deferred) | Faculty, Student, Department | Per session | Weekly |

Full ~60-key term dictionary lives in `label-pack-spec.md`.

---

## 5. Build order

1. `Org` table with `type`
2. `School`-type row attributes: `school_type`, `board`
3. `PhysicalLocation` — only once a real co-located case exists, not speculatively
4. Preset resolver reading `school_type` + `board`

---

## 6. Open decisions

- Whether `PhysicalLocation` is worth building before any two Schools actually share a building
- Whether cross-board transfer needs a dedicated placement/admissions flow, or the standard admission process is enough with a transfer summary attached
