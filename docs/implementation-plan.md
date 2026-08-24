# BrainiacsLMSV1 — Implementation Plan
For Claude Code. References `design-system-and-layouts.md` (UI) and the ten component specs (backend/data model): org-hierarchy-spec.md, identity-access-spec.md, resource-pool-spec.md, admission-spec.md, learning-planning-and-control-spec.md, financials-control-spec.md, regulatory-audit-control-spec.md, library-subscriptions-spec.md, notification-management-spec.md, system-summary.md.

---

## 1. Foundation — what already exists

Extends the `zynthrixAI/BrainiacsLMSV1` repo: multi-tenant Postgres kernel, SQLAlchemy 2.0 async, FastAPI, pack SDK, preset/label system. Don't rebuild these — check the existing repo structure before adding a new module, since tenancy, auth scaffolding, and the preset resolver likely already exist in some form.

**Non-negotiable conventions carried over from the base repo, apply everywhere below:**
- Money: minor-unit integers only, no floats, currency always paired with amount
- Every write scoped to a tenant/`Org` node — no unscoped queries
- Governance checks (money type validation, scope coverage, pack cross-import prevention) extend to new modules, not just the original kernel

---

## 2. Build order — dependency-driven, not alphabetical

Each phase only starts once its dependencies are real, not stubbed.

**Phase 0 — Org & Identity (blocks everything)**
1. `Org` table (`ORGANIZATION`/`SCHOOL`/`BRANCH`), `school_type` + `board` on School rows
2. Preset resolver reading `school_type` + `board`
3. `Person`, `RoleAssignment` (role, scope_type, scope_id, local_identifier)
4. `Employee` — org-level, separate from `RoleAssignment`

**Phase 1 — Calendar & Resource Pool (the two engines everything else calls)**
5. `CalendarEvent` / `CalendarEventAudience`, publish/status rules
6. Recurrence engine + clash-checking — build once, generically, since Phase 2–5 all reuse it
7. `Resource` registry with `ownership`, `status`, `capacity` (add `capacity` now — Library needs it later, cheaper to include from the start than retrofit)
8. Transferable: `ResourceLocalId`, `ResourceTransferLog` (with the extended `reason` enum including ADMITTED/HIRED/RESIGNED/etc.)
9. Shared: `ResourceShare`
10. Reservable: `ResourceBooking`, wired to the clash-checker from step 6
11. `ResourceMaintenanceWindow`
12. `Facility`/`Room`/`Equipment`/`Vehicle`

**Phase 2 — Admission**
13. `AdmissionApplication` funnel
14. Acceptance handler — creates/matches `Person`, fires the Resource Pool transfer (step 8), opens `RoleAssignment`

**Phase 3 — Learning Planning & Control**
15. `SubjectRequirementTemplate`, `SectionPlan`
16. `ResourcePlanRun` / `ResourcePlanAssignment`, `RoleReportingDefault`
17. `ResourceGap`
18. Curriculum: `Curriculum → Unit → Lesson → LearningObjective → Resource`
19. `SyllabusTopic` / `SyllabusMapping`
20. `SchemeOfWork` / `LessonPlan` (with `session_type`)
21. `AttendanceRecord`
22. Assessment/assignment scheduling, `PacingSchedule` for self-study
23. Coverage tracking queries

**Phase 4 — Notification Management (needed before Phase 5, since Financials/Audit both alert through it)**
24. `NotificationEvent` / `NotificationAudience`
25. `NotificationDelivery` / `NotificationPreference` — in-app channel first, external providers later
26. `NotificationEscalationRule`, wired to `RoleReportingDefault` from step 16

**Phase 5 — Financials Control**
27. `Invoice` / `InvoiceLine` — consolidated billing
28. `PayrollRun` / `PayslipLine`
29. `Expense`
30. `LedgerEntry`
31. `ResourceCostAllocation`, `ResourceBookingBilling`, `ResourceRentalExpense`
32. `AssetDepreciation`, `AssetMaintenanceLog`

**Phase 6 — Regulatory Audit & Control**
33. `ComplianceRequirement`, `ComplianceCheck`, `GapRecord` — wired to Notification (step 24) and every domain's `source_ref`
34. `CertificationStatus`, `AuditEngagement`, `AuditCriterion`
35. `AuditFinding`, `CorrectiveActionPlan` — nonconformities create `GapRecord`s

**Phase 7 — Library & Subscriptions**
36. `Title` / `Copy` catalog
37. Issue/return via existing `ResourceBooking` (Phase 1, step 10)
38. Digital access — `ResourceShare` for site-wide, capacity-bound `ResourceBooking` for seat-limited (uses `Resource.capacity` from step 7)
39. `ResourceHoldRequest`

**Phase 8 — Frontend**
40. App shell (sidebar + context switcher) — see `design-system-and-layouts.md`, Section 2
41. Screens in the order their backing data exists: Resource Pool → Learning Planning (team + timetable) → Admission → Financials → Audit & Control → Library
42. Dashboard last — it aggregates everything else

---

## 3. Frontend stack

Given the existing Digi Academy frontends (Next.js, per the earlier repo review) and BrainiacsLMSV1's own conventions:

- **Framework:** Next.js App Router, TypeScript
- **Styling:** the CSS custom property token system from `design-system-and-layouts.md`, Section 1 — set up as global CSS variables with light/dark overrides before building any screen
- **Components:** extract the primitives in `design-system-and-layouts.md`, Section 7 (app shell, metric card, status badge, filter rail, data table) as shared components in `components/ui/` before building screen-specific layouts — every screen from Phase 8 reuses them
- **Data fetching:** server components where the data is read-heavy and doesn't need live interaction (dashboards, tables); client components for anything with the clash-checker or plan-run publish flow, since those need immediate feedback

---

## 4. Suggested repo structure

```
app/
  models/
    org.py                    Phase 0
    identity.py                Phase 0
    calendar.py                 Phase 1
    resource_pool.py             Phase 1
    admission.py                  Phase 2
    learning_planning/            Phase 3
      resource_planner.py
      curriculum.py
      scheduling.py
      attendance.py
      assessment.py
    notification.py                Phase 4
    financials/                     Phase 5
      institutional.py
      resource_finance.py
    audit_control/                   Phase 6
      gap_analysis.py
      audit.py
    library.py                        Phase 7
  services/
    recurrence_engine.py       shared by Phase 1, 5, 6 — build once
    clash_checker.py           shared by Phase 1, 3, 7
    preset_resolver.py         Phase 0
  api/
    (one router module per Phase, mirroring models/)

frontend/
  components/
    ui/                        shell, metric-card, status-badge, filter-rail, data-table
    screens/                   one folder per Phase 8 screen
```

---

## 5. What NOT to build yet

- University support (explicitly deferred per Org Hierarchy spec)
- OAuth push calendar sync (ICS feed first, per Calendar spec)
- SMS/WhatsApp notification providers (in-app channel first)
- Full double-entry chart of accounts (Financials Control's open decision — start with categorized tracking)
- `ResourceHoldRequest` generalized beyond Library (currently library-scoped only)

---

## 6. Open decisions to resolve before or during build

Pulled from each spec's own open-decisions section — resolve these as they're hit, don't block earlier phases waiting on later ones:

- GR-numbering: branch-local or School-wide (affects Phase 0, step 3 and Phase 1, step 8)
- Attendance grace period / half-day policy default per `school_type` (Phase 3, step 21)
- `ResourcePlanRun` publish: hard-blocked by open `ResourceGap`, or warning-only (Phase 3, step 17)
- Assessment scheduled ahead of `SchemeOfWork` completion: hard block or warning (Phase 3, step 22)
- Depreciation/maintenance auto-post to ledger, or requires finance approval (Phase 5, step 32)
- Government audits: same `AuditEngagement` table or separate lighter one (Phase 6, step 34 — spec leans toward same table)
