# Resource Pool — Component Spec
A system beside School, not inside it. Extends the BrainiacsLMSV1 kernel.

**Mechanics only — who has a resource, when, and whether it's available.** Cost, income, depreciation, and maintenance spend live in `resource-finance-spec.md`, which reads this spec's IDs but owns none of its tables.

**Depends on, but does not own:** the `Org` tree (Organization/School/Branch — see hierarchy spec), `Employee` records (see identity spec), the Calendar repository's recurrence and clash-detection engine.

---

## 1. What it is

Everything allocatable across the Organization — teachers, TAs, students, admin staff, custodians, principals, buildings, vehicles, rooms, equipment — is registered once in `Resource`. This system sits next to `Org` in the architecture, not underneath it. A School references resources it's currently using; it never owns them.

```
Org (Organization / School / Branch)          Resource pool
        │                                           │
        └──────────── references ──────────────────┘
```

```
Resource
  id                  the master ID, permanent
  resource_type        TEACHER | TA | STUDENT | ADMIN_STAFF | CUSTODIAN | PRINCIPAL
                        | BUILDING | VEHICLE | EQUIPMENT | ROOM | AUDITORIUM | CANTEEN | LAB
  source_type, source_id     points to the owning record — Person or PhysicalAsset
  allocation_mode      TRANSFERABLE | SHARED | RESERVABLE      -- a sensible default per
                                                                    resource_type, overridable per instance
  ownership            OWNED | RENTED                            -- physical resources only
  status                ACTIVE | ALLOCATED | IN_MAINTENANCE | RETIRED | DISPOSED
```

Three allocation modes, and the distinction that matters most is between the two that involve more than one place at once — `SHARED` and `RESERVABLE` look similar but resolve differently:

## 2. Transferable — one master ID, a local ID per system, a transfer log

One home at a time, exclusively. Applies uniformly to every transferable resource — a student, a teacher, a staff member, a building, a projector, an LCD. Same table, same fields, no special casing per resource type.

```
ResourceLocalId
  resource_id (→ master), org_id, local_code, issued_at, revoked_at

ResourceTransferLog
  resource_id, transfer_date
  from_org_id, to_org_id           what actually moved — structural, always set
  from_local_id, to_local_id       the local code issued at each end
  from_role, to_role               nullable — set only if a role/grade also changed
  reason                           PROMOTED | BRANCH_CHANGE | SCHOOL_CHANGE
                                    | RELOCATION | WITHDRAWAL | REJOIN
                                    | ADMITTED | HIRED | RESIGNED | TERMINATED | GRADUATED | OTHER
  approved_by
```

**Two things are captured, and they answer different questions.** `from_org_id`/`to_org_id` is *what* moved — structural, derivable, never ambiguous. `reason` is *why* — and that's genuinely not derivable from the structural change alone. A school-level move (different `School` row) could be a routine promotion, a disciplinary transfer, or a parent-requested switch — all three look identical if only the org fields are stored. `reason` is what tells them apart in a report.

**`reason` can be suggested from the structural diff, but shouldn't be trusted blindly.** Same parent `School`, different `Branch` → the system can default to `BRANCH_CHANGE`. Different `School` under the same `Organization` with the grade level increasing → defaults to `PROMOTED`. But the person recording the transfer confirms or overrides it, since the default is a reasonable guess, not a fact.

A projector reassigned from one branch's inventory to another's and a student progressing from Middle to Higher are structurally the same kind of event — a `from_org_id`/`to_org_id` pair — but their `reason` values diverge immediately: `BRANCH_CHANGE` for the projector, `PROMOTED` for the student. Same mechanism, different intent, both captured.

**A role or grade change can ride along with a transfer, or happen on its own.** `from_role`/`to_role` are independent of whether the org changed. A student's Grade 6 → Grade 7 bump inside one School sets only `from_role`/`to_role`, `from_org_id = to_org_id`, `reason = PROMOTED`. A teacher promoted to Senior Teacher while moving from the Middle school to the Higher school sets all of it in one row — org, role, and `reason = PROMOTED` together, since it was one decision, not two.

A year-end bulk promotion run is this same table written many times in one job — one `ResourceTransferLog` row per student, `reason = PROMOTED` on every row, most with the org unchanged and only the grade field moving.

**Entry and exit are the same table, just with one side null.** Admission, hiring, resignation, and graduation aren't new mechanisms — they're transfers where `from_org_id` or `to_org_id` is absent instead of populated:

```
Admission / hiring    from_org_id = NULL,  to_org_id = the joining School/Branch,  reason = ADMITTED | HIRED
Resignation / exit    from_org_id = the leaving unit,  to_org_id = NULL,           reason = RESIGNED | TERMINATED | GRADUATED | WITHDRAWAL
```

A new student's first `ResourceLocalId` (their first GR number) and a new employee's first local code are issued at exactly this event — there's no prior local ID to reference, since nothing existed in the pool before it. `RoleAssignment` opens at the same moment `RoleAssignment` closes on a resignation, symmetric with how a transfer works everywhere else in this spec.

**The funnel leading up to admission or hiring lives in its own spec** — `admission-spec.md`. An enquiry, an application, a test, an interview aren't transfers yet, since nobody's in the pool until accepted; only the acceptance decision triggers the `ResourceTransferLog` entry above.

## 3. Shared — concurrent, on a roster, nobody wins the slot

A principal overseeing three schools, admin staff splitting a week across two branches, a security guard covering two adjacent campuses on alternating days, a student optionally riding a recurring transport route. Multiple parties have legitimate, simultaneous access — this isn't a contest one of them wins, it's a roster or a subscription.

```
ResourceShare
  resource_id
  participant_type      ORG | PERSON
  participant_id         → Org.id or Person.id, depending on participant_type
  schedule (nullable → a recurring pattern, same shape as Calendar's
  recurrence engine; null = unscheduled, available as needed)
  start_date, end_date (nullable = ongoing)
```

Two directions, same table. A principal shared across branches is `participant_type=ORG` — one resource, several orgs drawing on it. A transport route is the inverse — `participant_type=PERSON` — one resource, many students individually opting in. Neither direction needs its own mechanism.

A canteen or playground is the degenerate case of this — `ResourceShare` with no schedule at all, open to everyone, all the time. A daily transport route is the same table with an actual recurring schedule and one row per subscribed student. **Optional means exactly what it sounds like at the data level: a student who doesn't want the route simply has no `ResourceShare` row.** No opt-out flag needed. No clash-check runs here either way, because nothing is being contested.

Cost allocation for a share — who pays what, percentage or fixed — lives entirely in `resource-finance-spec.md`, keyed off `resource_share_id`.

## 4. Reservable — exclusive, time-boxed, contested

Auditoriums, labs, specific rooms, projectors, LCDs — usable by exactly one booking at a time, and a clash here is a real problem, not a schedule. A vehicle booked for a one-off school event — a picnic, a sports day, a swimming or taekwondo meet — is the same pattern: exclusive for that day, tied to the event's own `CalendarEvent` rather than to a recurring route.

```
ResourceBooking
  resource_id, calendar_event_id, start_at, end_at, status, requested_by
```

Plugs into the Calendar repository's clash-detection engine — a session that needs the auditorium creates a booking, and the same check that stops two sections colliding on a teacher stops two events colliding on a room. Whether the booking generates an invoice line lives in `resource-finance-spec.md`, referenced by `resource_booking_id` — this table itself carries no money fields.

A shared resource can still be pulled into a one-off reservation — the canteen closed for a school function is a `ResourceBooking` against a normally-`SHARED` resource, not a change to its default mode.

---

## 5. Resource status and maintenance windows

```
ResourceMaintenanceWindow
  resource_id, start_at, end_at
  maintenance_type       SCHEDULED | UNSCHEDULED | REPAIR
  status                  PLANNED | IN_PROGRESS | COMPLETED
```

While a window is active, `Resource.status = IN_MAINTENANCE` and the resource fails the same clash-check a double-booking would fail — no separate mechanism, it's just unavailable for that span like anything already booked. Scheduled maintenance is a recurring rule, same generation engine as everything else that repeats. What the maintenance actually cost is tracked in `resource-finance-spec.md`, referencing this window's ID.

`RETIRED`/`DISPOSED` are terminal — the resource stops appearing as bookable anywhere, and its depreciation schedule (finance spec) closes out.

---

## 6. Allocation dashboard — operational view

A resource-centric read, the inverse of "the team" view in the Learning Resource Planner (which filters by target). This filters by resource instead:

```
ResourceAllocationView    (a query, not a new table)
  resource_id
  current_status            from Resource.status
  current_allocation         → whichever of ResourcePlanAssignment / ResourceShare / ResourceBooking is active now
  utilization_rate            % of bookable time actually booked
  allocation_history           from ResourceTransferLog
```

Answers "where is this thing right now and how busy is it" — cost and income sit in the finance-side dashboard, which extends this same view with money fields.

---

## 7. Underlying physical records

Rooms, buildings, and equipment still need real tables to be physical facts about, independent of who's using them right now:

```
Facility          address, coordinates, buildings
Room, Equipment   facility_id, capacity, room_type, spec
Vehicle, Route     transport, same pattern
```

These stay outside the School hierarchy entirely — no dependency on `school_type` or `board`. `Resource` and `ResourceBooking` are what make them allocatable; `Facility` and `Room` are what make them real.

---

## 8. Build order

1. `Resource` registry table, with `ownership` and `status`
2. `Facility`/`Room`/`Equipment`/`Vehicle` — standalone physical records (Section 7)
3. `ResourceLocalId` + `ResourceTransferLog` — transferable (Section 2)
4. `ResourceShare` — shared (Section 3)
5. `ResourceBooking` — reservable (Section 4), wired to Calendar's clash-detection engine
6. `ResourceMaintenanceWindow` — status blocking (Section 5)

---

## 9. Open decisions

- Whether `Resource` and its supporting tables are populated on write, or computed as a view over `RoleAssignment` + physical asset tables
- Whether GR numbers (or other local codes) are branch-local or shared across all branches of one School — affects `ResourceLocalId` issuance logic on every transfer
- Whether `RETIRED`/`DISPOSED` requires an approval step before the status flips, given it terminates a depreciation schedule on the finance side
