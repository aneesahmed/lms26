# Regulatory Audit & Control — Component Spec
Consolidates: continuous compliance monitoring (Gap Analysis) and formal periodic audits (Audit & Control) — two halves of one concern. Depends on: Notification Management (alerting), Calendar Repository (review cycles, surveillance scheduling — see Learning Planning & Control, Part C), and every domain that produces a gap signal (Learning Planning & Control's syllabus alignment, Resource Pool's gaps, Resource Finance's budget tracking, Library's subscriptions).

---

# Part A — Gap Analysis (continuous monitoring)

## 1. Why this sits above the other specs, not beside them

Each domain already tracks its own gap concept — `SyllabusMapping` coverage, `ResourceGap`, budget-vs-spend, subscription lapses. Gap Analysis doesn't duplicate any of it. It's one registry pulling a met/not-met signal from each.

```
ComplianceRequirement
  source              INTERNAL | BOARD | REGULATOR | ACCREDITATION_BODY
  category             ACADEMIC | STAFFING | FACILITY | FINANCIAL | LIBRARY | SAFETY | OTHER
  scope_type, scope_id
  required_value / required_state
  review_cycle          ANNUAL | TERM | ONE_TIME
```

```
ComplianceCheck
  requirement_id, checked_at
  actual_value / actual_state
  status              MET | PARTIAL | NOT_MET | UNKNOWN
  source_ref            → SyllabusMapping, ResourceGap, ResourceFinanceView, Library holdings — whichever domain answers it
```

```
GapRecord                  -- only created when status != MET
  compliance_check_id
  severity              INFO | WARNING | CRITICAL
  status                  OPEN | ACKNOWLEDGED | IN_REMEDIATION | RESOLVED
  remediation_plan_ref    nullable — a hiring action, a procurement, a curriculum fix
```

---

## 2. Concrete examples, across domains

- **Academic** — syllabus coverage under 100% as exams approach, severity rising with proximity
- **Staffing** — an unresolved `ResourceGap` breaching a board-mandated student-teacher ratio
- **Financial** — maintenance spend running over budget, or depreciation showing replacement due with no budget allocated
- **Library** — a subscription's expiry approaching, or physical copy count falling below what a board expects

---

## 3. Direct reuse, no new plumbing

- A `GapRecord` at `CRITICAL` severity raises a `NotificationEvent` through the existing pipeline — same escalation chain
- The periodic `review_cycle` re-check uses the same recurrence engine as everything else
- The dashboard is a query over `GapRecord`, grouped by scope/category/severity, not a new table

---

# Part B — Audit & Control (formal, periodic, external-facing)

## 1. Relationship to Gap Analysis

Gap Analysis is continuous, automated monitoring. Audit & Control is the formal, periodic, external-facing event. Its findings become `GapRecord`s — a different source, not a sixth parallel tracking system.

---

## 2. Certification is an ongoing state, not a single event

```
CertificationStatus
  org_id, certification_type    ISO_21001 | HEC_ACCREDITATION | BOARD_AFFILIATION
  status                          CERTIFIED | SUSPENDED | EXPIRED | IN_RENEWAL | NOT_CERTIFIED
  certificate_number, issued_date, expiry_date, issuing_body
```

ISO 21001 is a three-year cycle with annual surveillance visits, not one audit. `CertificationStatus` is the parent; multiple engagements happen under it over its life.

---

## 3. Engagement lifecycle

```
AuditEngagement
  certification_status_id (nullable — government/HEC audits may not tie to an ongoing cert)
  audit_type              ISO_21001 | HEC | BOARD_INSPECTION | GOVERNMENT | INTERNAL
  scope_type, scope_id
  auditor_body
  status                   PLANNED | EVIDENCE_COLLECTION | FIELDWORK | FINDINGS_ISSUED | CLOSED
```

```
AuditCriterion
  audit_engagement_id
  requirement_id (nullable → ComplianceRequirement, where one already exists)
  clause_reference          e.g. ISO 21001 clause 8.2, a Cambridge inspection code
```

Many audit criteria are already tracked as `ComplianceRequirement`s day to day. An audit formally reviews the same ones at a point in time, plus whatever's audit-specific.

```
AuditFinding
  criterion_id
  finding_type      CONFORMS | OBSERVATION | MINOR_NONCONFORMITY | MAJOR_NONCONFORMITY
  evidence_ref

CorrectiveActionPlan
  audit_finding_id
  owner, due_date
  status              OPEN | IN_PROGRESS | COMPLETED | VERIFIED | OVERDUE
```

A `MINOR_NONCONFORMITY` or `MAJOR_NONCONFORMITY` creates a `GapRecord` — same dashboard, same notification/escalation pipeline as every other gap source.

---

# Consolidated Build Order

1. `ComplianceRequirement` (Part A)
2. `ComplianceCheck`, wired to each domain's `source_ref` (Part A)
3. `GapRecord`, wired to Notification Management (Part A)
4. Dashboard view (Part A)
5. `CertificationStatus` (Part B)
6. `AuditEngagement`, `AuditCriterion` — wired to `ComplianceRequirement` where applicable (Part B)
7. `AuditFinding`, `CorrectiveActionPlan` (Part B)
8. Wire nonconformities into `GapRecord` (Part B → Part A)

---

# Consolidated Open Decisions

- Whether board/regulator requirements are entered manually by a compliance officer, or synced against an external feed where one exists (assume manual for now)
- Whether government audits with no ongoing certification still route through `AuditEngagement` (nullable `certification_status_id`) or get a separate lighter table — leaning toward the same table, one place to look for every audit that's happened
