# BrainiacsLMSV1 — System Summary
Index of all component specs, at concept level only. Table names, fields, and schema live in the linked spec files, not here — a separate technical design and implementation document will cover that.

---

## Core principle

One flexible organisational structure (Organization → School → Branch), configurable behaviour per school type and board, and a small set of shared systems (identity, calendar, notifications) that every other part of the platform plugs into instead of rebuilding.

---

## 1. Org Hierarchy — `org-hierarchy-spec.md`
How a business, its schools, and its physical campuses relate. A school with two curricula (say Cambridge and IB) is treated as two separate schools, even if they share a building.

## 2. Identity & Access — `identity-access-spec.md`
Who everyone is, and what they're allowed to do, where. Separates a person's employment record from their day-to-day system access, since those are different concerns.

## 3. Resource Pool — `resource-pool-spec.md`
Anything shareable or assignable — teachers, staff, rooms, equipment, vehicles — tracked in one consistent way. Covers three situations: something moved permanently, something shared on a roster, and something booked for a slot.

## 4. Admission — `admission-spec.md`
The funnel from enquiry to enrolled student, kept separate from the Resource Pool until a decision is actually made.

## 5. Learning Planning & Control — `learning-planning-and-control-spec.md`
The core teaching workflow: deciding who teaches what, building curriculum and lesson plans, scheduling classes, tracking attendance, and planning assessments — all built on one shared scheduling engine.

## 6. Financials Control — `financials-control-spec.md`
Institution-wide money — tuition, salaries, general expenses — and the narrower cost picture for shared or owned resources, like depreciation and cross-branch cost-sharing.

## 7. Regulatory Audit & Control — `regulatory-audit-control-spec.md`
Ongoing monitoring of whether the institution is meeting internal and external requirements, plus formal audit management for things like ISO 21001, HEC, or board inspections.

## 8. Library & Subscriptions — `library-subscriptions-spec.md`
Physical books and digital subscriptions, reusing the same booking and billing concepts already built for other resources.

## 9. Notification Management — `notification-management-spec.md`
One alerting system for the whole platform, with escalation up the reporting chain when something urgent goes unacknowledged.

---

## Patterns that repeat across sections

- **Definitions vs instances** — things like curriculum or question banks are authored once and reused; actual sessions, attempts, and submissions are separate records that never rewrite history
- **One scheduling engine, many uses** — the same underlying mechanism generates class timetables, recurring bills, and periodic compliance checks
- **One way of tracking movement** — people and physical assets both use the same approach for transfers, hires, and exits
- **Monitoring sits above the system, not beside it** — compliance and notifications read signals from everything else rather than holding their own separate data

---

## Known open questions

- A shared limit/capacity concept needed by Library isn't yet part of the core Resource Pool design
- How deep the financial ledger needs to go — full formal accounting vs simpler tracking to start
- Default attendance policy (grace periods, half days) per school type isn't decided
- Whether ID numbering is shared across a school's branches or local to each one, needs one answer instead of two open questions

---

## Not yet designed

Internal communication tools (separate from system alerts), general reporting and analytics, and the overall app navigation and screen layout.
