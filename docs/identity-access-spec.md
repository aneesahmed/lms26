# Identity & Access — Component Spec
Foundational. Depends on: Org Hierarchy spec. Referenced by every other spec — `Person` and `RoleAssignment` are the identity layer everything else scopes against.

---

## 1. Roles

Everyone is a `Person`. What they can do at a given School is a `RoleAssignment`, scoped to whichever `Org` node matches their job. What they're employed to do is a separate concern — see below.

| Role | Typical scope |
|---|---|
| Student | Section, one board-School at a time — transferring boards is a full transfer, see Org Hierarchy spec, Section 3 |
| Guardian | Student — may span children at different Schools entirely |
| Teacher | Course offering — transferable |
| Assistant / TA | Course offering, narrower permissions than a teacher — transferable |
| Admin staff, Custodian | A Branch, or shared across nearby branches on a roster — see Resource Pool spec, Section 3 |
| Principal / Administrator | A School, or shared across several — see Resource Pool spec, Section 3 |
| Controller | The School, exam integrity only |

A teacher genuinely teaching at both the Cambridge and IB schools on one campus gets two separate `RoleAssignment` rows — one Person, two Schools.

## 2. Employment vs system access

These are two different things and two different tables. `RoleAssignment` answers "what can this person do, and where" — it's an access-control record. It says nothing about who pays them or under what contract.

```
Employee
  person_id, organization_id, contract_type, start_date, end_date, payroll_ref
```

`Employee` sits at the Organization level, once per person, regardless of how many Schools they touch. A principal who oversees three schools has one `Employee` row and either one `RoleAssignment` scoped at `ORGANIZATION` level, or three scoped at each `SCHOOL` — whichever matches how their actual authority works. A teacher moving from the Primary school to the Higher school keeps the same `Employee` row untouched; only their `RoleAssignment` set changes.

This is what "shared management" actually is: one `Employee`, several `RoleAssignment`s. Nothing about payroll, contract, or tenure needs to know how many schools someone touches this term.

## 3. A person moving between schools isn't a data migration

Teachers, TAs, and students are **transferable, not shareable** — one home at a time, moves fully, leaves a record behind. This is the same mechanism the Resource Pool spec uses for physical assets, applied to people: one permanent master ID, a local ID per system they're attached to, and a transfer log connecting the two.

```
Person.id                          the master ID, permanent, never changes
RoleAssignment.local_identifier    the GR number, employee number, whatever the
                                    receiving unit issues — local to that unit only
```

Three cases cover almost everything that actually happens. The mechanism is identical across all three — same `ResourceTransferLog`, same `RoleAssignment` lifecycle — what changes is which `Org` level moves and how much local context resets.

**1. Class-to-class promotion — the most common case, happens to nearly every student every year.** Grade 6 to Grade 7, same School, same Branch, same GR number. Nothing about the org changes at all — only `RoleAssignment.local_identifier` might stay identical and only `from_role`/`to_role` (the grade level) moves. This is the case a year-end `PromotionRun` writes in bulk, one row per student, most of the transfer log entry doing almost nothing except recording that the grade changed.

```
from_org_id = to_org_id          unchanged
from_local_id = to_local_id      unchanged, usually
from_role → to_role               Grade 6 → Grade 7
reason = PROMOTED
```

**2. Campus transfer — a family relocates, same School and board, different Branch.** A student moves from the Karachi campus to the Lahore campus of the same `Beaconhouse Higher School — Cambridge`. Same curriculum, same grading scale, same board — only the physical location changes. Whether the GR number carries over or the new branch issues its own is a real operational decision, not something the architecture assumes either way:

```
from_org_id (Karachi Branch) → to_org_id (Lahore Branch)
from_local_id → to_local_id        new local code if the branch numbers independently,
                                     unchanged if the School runs one shared numbering scheme
reason = BRANCH_CHANGE
```

Since curriculum belongs to the School, not the Branch (Org Hierarchy spec), nothing about content access needs to change on a campus transfer — the student picks up exactly where they left off, just physically elsewhere.

**3. School-to-school promotion — Middle to Higher, since they're separate `School` rows here.** Less frequent than a grade bump, but every student who stays with the group does it once. A new GR number, a new School-level `org_id`, same person.

```
from_org_id (Middle School) → to_org_id (Higher School)
from_local_id → to_local_id        new GR number issued by the Higher school
reason = PROMOTED
```

**Some staff roles are genuinely shared instead** — a principal, admin staff, or a security guard covering two nearby branches on a roster. See Resource Pool spec, Section 3 for how that differs from a transfer.

**What follows the person automatically, in all three cases:** identity, contact details, guardian links, the `Employee` record.

**What doesn't, by design:** the old unit's live gradebook and attendance records stay exactly where they were generated. The new unit reads a summary at enrolment, not an ongoing join into the old data — the same boundary a paper Transfer Certificate has always drawn. This matters least for a class-to-class promotion (the new grade's coordinator is often the same person who had the record already) and matters most for a school-to-school move, where a genuinely different team picks the student up.

---

## 4. Build order

1. `Person` — canonical identity record
2. `RoleAssignment` — role, scope_type, scope_id, local_identifier
3. `Employee` — org-level employment record, separate from access
4. Transfer mechanism — shared with Resource Pool spec (`ResourceTransferLog`), not duplicated here

---

## 5. Open decisions

- Whether GR numbers (or other local codes) are branch-local or shared across all branches of one School — affects issuance logic on every transfer
- Auth model: separate login per Person, or shared credentials for certain staff roles with an activity log distinguishing who acted
