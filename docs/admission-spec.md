# Admission — Component Spec
Split out from Resource Pool, since this genuinely doesn't fit that spec's transfer semantics — a candidate isn't a `Resource` yet, so nothing about `Org` scoping or transfer logging applies until a decision is made. Depends on: Resource Pool (the funnel's endpoint), Financials Control (application/test fees), Notification Management (status updates to applicants).

---

## 1. The funnel is a separate, lighter concern from allocation

An enquiry, an application, an entrance test, an interview, an offer — none of it is a transfer yet, since the person isn't in the pool until accepted.

```
AdmissionApplication
  applicant_person_id (nullable until a Person record is created)
  target_org_id           the School/Branch applying to
  status                   ENQUIRY | APPLIED | TESTED | INTERVIEWED | OFFERED | ACCEPTED | REJECTED | WITHDRAWN
  applied_at, decided_at
```

A `Person` record may not exist yet at `ENQUIRY` — a lead isn't a resource, isn't a student, has no `RoleAssignment`. It gets created (or matched, for a sibling already in the system) once the application is serious enough to need one, at latest by `ACCEPTED`.

---

## 2. Only acceptance triggers the Resource Pool mechanism

```
ACCEPTED  →  ResourceTransferLog: from_org_id = NULL, to_org_id = target_org_id, reason = ADMITTED
          →  first ResourceLocalId issued (the student's first GR number)
          →  RoleAssignment opened (STUDENT, scope = Section)
```

Everything before `ACCEPTED` is pipeline. This is the same distinction the Learning Resource Planner draws between a `ResourceGap` being flagged and someone actually being hired to fill it — a candidate in the funnel isn't yet the thing the rest of the system reasons about.

---

## 3. Fees along the way

Application fees, test fees, admission fees — these are `Invoice`/`InvoiceLine` entries (Financials Control, Part A) against the `AdmissionApplication`, not against a `Person` who may not fully exist yet. Reconciled once the applicant becomes a real `Person` at acceptance.

---

## 4. Status changes notify

Every `AdmissionApplication.status` change is a `NotificationEvent` to the applicant/guardian — offer issued, interview scheduled, decision made. Same pipeline as everything else, not a bespoke admissions communication system.

---

## 5. Build order

1. `AdmissionApplication`
2. Fee integration with Financials Control
3. Notification wiring for status changes
4. Acceptance handler — creates/matches `Person`, fires the Resource Pool transfer, opens `RoleAssignment`

---

## 6. Open decisions

- Whether a rejected or withdrawn application's data is retained (for re-application history) or purged after a retention period
- Whether sibling auto-matching (an applicant whose sibling is already an enrolled student) is automatic or requires manual confirmation
