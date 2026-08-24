# BrainiacsLMSV1 — Design System & Screen Layouts
Reference document for implementation. Pairs with the component specs in the project (org-hierarchy-spec.md, resource-pool-spec.md, learning-planning-and-control-spec.md, etc.) — this document covers UI only, no backend schema.

**Status:** 4 of ~10 core screens designed. Remaining: Admission, Financials Control, Regulatory Audit & Control, Library & Subscriptions, Identity & Access, Notification Management.

---

## 1. Design tokens

Uses a CSS custom property token system — never hardcode colors, always reference tokens so light/dark mode both work automatically.

```
Surfaces:   --surface-0 (page bg), --surface-1 (card), --surface-2 (elevated panel)
Text:       --text-primary, --text-secondary, --text-muted
Role text:  --text-accent, --text-danger, --text-success, --text-warning
Role bg:    --bg-accent, --bg-danger, --bg-success, --bg-warning
Borders:    --border (default 0.5px hairline), --border-strong
Fills:      --fill-accent, --fill-success, --fill-warning, --fill-danger (solid, for badges/legend dots)
Layout:     --radius (8px default), --pad-{sm,md,lg}, --gap-{xs,sm,md,lg}
```

**Rules:**
- Sentence case everywhere — no Title Case, no ALL CAPS
- Two font weights only: 400 regular, 500 medium
- Status/state always communicated via role tokens (`--bg-success` + `--text-success` together), never raw colors
- Icons: Tabler outline icon set (`<i class="ti ti-{name}">`)
- No shadows, no gradients — flat surfaces, 0.5px borders only

---

## 2. App shell — used on every screen

Fixed pattern: left sidebar (190px) with module navigation, top bar with org/branch context switcher, main content area.

**Sidebar nav items, in order, matching the ten component specs:**
Dashboard · Org hierarchy · Identity & access · Resource pool · Admission · Learning planning · Financials · Audit & control · Library · Notifications

**Context switcher (top right):** Organization selector, Branch selector — scopes every metric and table below it. Changing this re-queries, doesn't navigate away.

---

## 3. Screen: Main Dashboard

**Purpose:** cross-module landing view, role-aware (an admin/owner sees everything; a coordinator would see only their scope — role-based filtering is a v2 concern, not in this first pass).

**Layout:** sidebar + top bar with org/branch switcher → 4-column metric card grid → 2-column split (activity feed, left, wider; alerts panel, right, narrower).

**Data bindings:**
- Metric cards: enrolled students (Identity & Access), attendance today (Learning Planning & Control, Part B), revenue this month (Financials Control, Part A `Invoice`), open compliance gaps (Regulatory Audit & Control, `GapRecord` count where status=OPEN)
- Activity feed: recent `ResourceGap`, `CorrectiveActionPlan`, overdue `Invoice` rows, cross-module
- Alerts panel: `NotificationEvent` where severity=WARNING/CRITICAL and unread, most recent first

```html
<div style="display:flex;gap:0;border:0.5px solid var(--border);border-radius:12px;overflow:hidden;min-height:520px">
<div style="width:190px;flex-shrink:0;background:var(--surface-1);padding:1rem 0.75rem;display:flex;flex-direction:column;gap:2px">
  <div style="font-size:13px;font-weight:500;color:var(--text-primary);padding:6px 8px 14px">BrainiacsLMSV1</div>
  <div style="display:flex;align-items:center;gap:8px;padding:8px;border-radius:var(--radius);background:var(--fill-ghost-selected);font-size:13px"><i class="ti ti-home"></i>Dashboard</div>
  <div style="display:flex;align-items:center;gap:8px;padding:8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)"><i class="ti ti-sitemap"></i>Org hierarchy</div>
  <div style="display:flex;align-items:center;gap:8px;padding:8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)"><i class="ti ti-users"></i>Identity &amp; access</div>
  <div style="display:flex;align-items:center;gap:8px;padding:8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)"><i class="ti ti-building-warehouse"></i>Resource pool</div>
  <div style="display:flex;align-items:center;gap:8px;padding:8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)"><i class="ti ti-clipboard-list"></i>Admission</div>
  <div style="display:flex;align-items:center;gap:8px;padding:8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)"><i class="ti ti-calendar"></i>Learning planning</div>
  <div style="display:flex;align-items:center;gap:8px;padding:8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)"><i class="ti ti-report-money"></i>Financials</div>
  <div style="display:flex;align-items:center;gap:8px;padding:8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)"><i class="ti ti-shield-check"></i>Audit &amp; control</div>
  <div style="display:flex;align-items:center;gap:8px;padding:8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)"><i class="ti ti-books"></i>Library</div>
  <div style="display:flex;align-items:center;gap:8px;padding:8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)"><i class="ti ti-bell"></i>Notifications</div>
</div>
<div style="flex:1;padding:1rem 1.25rem;background:var(--surface-2)">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
    <div style="font-size:16px;font-weight:500">Good morning</div>
    <div style="display:flex;gap:8px">
      <select style="font-size:13px"><option>Brainiac Education Group</option></select>
      <select style="font-size:13px"><option>All branches</option></select>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:1.25rem">
    <div style="background:var(--surface-1);border-radius:var(--radius);padding:1rem"><div style="font-size:13px;color:var(--text-secondary)">Enrolled students</div><div style="font-size:24px;font-weight:500">2,340</div></div>
    <div style="background:var(--surface-1);border-radius:var(--radius);padding:1rem"><div style="font-size:13px;color:var(--text-secondary)">Attendance today</div><div style="font-size:24px;font-weight:500">94%</div></div>
    <div style="background:var(--surface-1);border-radius:var(--radius);padding:1rem"><div style="font-size:13px;color:var(--text-secondary)">Revenue this month</div><div style="font-size:24px;font-weight:500">18.2M</div></div>
    <div style="background:var(--surface-1);border-radius:var(--radius);padding:1rem"><div style="font-size:13px;color:var(--text-secondary)">Open compliance gaps</div><div style="font-size:24px;font-weight:500;color:var(--text-danger)">7</div></div>
  </div>
  <div style="display:grid;grid-template-columns:1.4fr 1fr;gap:12px">
    <div style="background:var(--surface-1);border-radius:var(--radius);padding:1rem">
      <div style="font-size:13px;color:var(--text-secondary);margin-bottom:8px">Today across the group</div>
      <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:0.5px solid var(--border)"><span style="font-size:13px">3 resource gaps open in Higher School — Cambridge</span><span style="font-size:12px;color:var(--text-secondary)">Resource pool</span></div>
      <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:0.5px solid var(--border)"><span style="font-size:13px">2 audit CAPAs due this week</span><span style="font-size:12px;color:var(--text-secondary)">Audit &amp; control</span></div>
      <div style="display:flex;justify-content:space-between;padding:8px 0"><span style="font-size:13px">14 fee invoices overdue</span><span style="font-size:12px;color:var(--text-secondary)">Financials</span></div>
    </div>
    <div style="background:var(--surface-1);border-radius:var(--radius);padding:1rem">
      <div style="font-size:13px;color:var(--text-secondary);margin-bottom:8px">Alerts</div>
      <div style="display:flex;align-items:center;gap:8px;padding:6px 0"><i class="ti ti-alert-triangle" style="color:var(--text-danger);font-size:16px"></i><span style="font-size:13px">Syllabus coverage behind, Grade 9 Chemistry</span></div>
      <div style="display:flex;align-items:center;gap:8px;padding:6px 0"><i class="ti ti-alert-triangle" style="color:var(--text-warning);font-size:16px"></i><span style="font-size:13px">Digital subscription expiring in 5 days</span></div>
    </div>
  </div>
</div>
</div>
```

---

## 4. Screen: Resource Pool

**Purpose:** browse and filter every `Resource` across the organization — the single place to see allocation mode, current status, and utilization regardless of resource type.

**Layout:** sidebar + top bar (shared shell) → left filter rail (170px, resource type + allocation mode filters) → main table (search bar, add-resource button, sortable columns).

**Data bindings:** table reads `ResourceAllocationView` (Resource Pool spec, Section 6) — one row per `Resource`, joined to whichever of `ResourcePlanAssignment`/`ResourceShare`/`ResourceBooking` is currently active. Status badge reflects `Resource.status` (ACTIVE/IN_MAINTENANCE/RETIRED/DISPOSED).

```html
<div style="display:flex;gap:0;border:0.5px solid var(--border);border-radius:12px;overflow:hidden;min-height:480px">
<div style="width:170px;flex-shrink:0;background:var(--surface-1);padding:1rem 0.75rem">
  <div style="font-size:12px;color:var(--text-secondary);margin-bottom:8px">Resource type</div>
  <div style="display:flex;flex-direction:column;gap:2px">
    <div style="padding:6px 8px;border-radius:var(--radius);background:var(--fill-ghost-selected);font-size:13px">All</div>
    <div style="padding:6px 8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)">Teachers</div>
    <div style="padding:6px 8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)">TAs &amp; staff</div>
    <div style="padding:6px 8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)">Rooms &amp; labs</div>
    <div style="padding:6px 8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)">Equipment</div>
    <div style="padding:6px 8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)">Vehicles</div>
  </div>
  <div style="font-size:12px;color:var(--text-secondary);margin:16px 0 8px">Allocation mode</div>
  <div style="display:flex;flex-direction:column;gap:2px">
    <div style="padding:6px 8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)">Transferable</div>
    <div style="padding:6px 8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)">Shared</div>
    <div style="padding:6px 8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)">Reservable</div>
  </div>
</div>
<div style="flex:1;padding:1rem 1.25rem;background:var(--surface-2)">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
    <input type="text" placeholder="Search resources" style="width:220px" />
    <button style="font-size:13px"><i class="ti ti-plus" style="font-size:14px;vertical-align:-2px"></i> Add resource</button>
  </div>
  <table style="width:100%;font-size:13px;border-collapse:collapse">
    <tr style="color:var(--text-secondary);text-align:left">
      <th style="font-weight:400;padding:6px 8px;border-bottom:0.5px solid var(--border)">Resource</th>
      <th style="font-weight:400;padding:6px 8px;border-bottom:0.5px solid var(--border)">Type</th>
      <th style="font-weight:400;padding:6px 8px;border-bottom:0.5px solid var(--border)">Mode</th>
      <th style="font-weight:400;padding:6px 8px;border-bottom:0.5px solid var(--border)">Status</th>
      <th style="font-weight:400;padding:6px 8px;border-bottom:0.5px solid var(--border)">Utilization</th>
    </tr>
    <tr>
      <td style="padding:8px">Nadia Farooq</td>
      <td style="padding:8px;color:var(--text-secondary)">Teacher</td>
      <td style="padding:8px;color:var(--text-secondary)">Transferable</td>
      <td style="padding:8px"><span style="background:var(--bg-success);color:var(--text-success);font-size:12px;padding:2px 8px;border-radius:var(--radius)">Active</span></td>
      <td style="padding:8px;color:var(--text-secondary)">92%</td>
    </tr>
    <tr>
      <td style="padding:8px">Security — Zafar</td>
      <td style="padding:8px;color:var(--text-secondary)">Custodian</td>
      <td style="padding:8px;color:var(--text-secondary)">Shared</td>
      <td style="padding:8px"><span style="background:var(--bg-success);color:var(--text-success);font-size:12px;padding:2px 8px;border-radius:var(--radius)">Active</span></td>
      <td style="padding:8px;color:var(--text-secondary)">2 branches</td>
    </tr>
    <tr>
      <td style="padding:8px">Chemistry lab, Room 14</td>
      <td style="padding:8px;color:var(--text-secondary)">Lab</td>
      <td style="padding:8px;color:var(--text-secondary)">Reservable</td>
      <td style="padding:8px"><span style="background:var(--bg-success);color:var(--text-success);font-size:12px;padding:2px 8px;border-radius:var(--radius)">Active</span></td>
      <td style="padding:8px;color:var(--text-secondary)">67%</td>
    </tr>
    <tr>
      <td style="padding:8px">Projector — PJ-04</td>
      <td style="padding:8px;color:var(--text-secondary)">Equipment</td>
      <td style="padding:8px;color:var(--text-secondary)">Reservable</td>
      <td style="padding:8px"><span style="background:var(--bg-warning);color:var(--text-warning);font-size:12px;padding:2px 8px;border-radius:var(--radius)">Maintenance</span></td>
      <td style="padding:8px;color:var(--text-secondary)">—</td>
    </tr>
    <tr>
      <td style="padding:8px">School van — SV-2</td>
      <td style="padding:8px;color:var(--text-secondary)">Vehicle</td>
      <td style="padding:8px;color:var(--text-secondary)">Reservable</td>
      <td style="padding:8px"><span style="background:var(--bg-success);color:var(--text-success);font-size:12px;padding:2px 8px;border-radius:var(--radius)">Active</span></td>
      <td style="padding:8px;color:var(--text-secondary)">38%</td>
    </tr>
  </table>
</div>
</div>
```

---

## 5. Screen: Learning Planning — Team Assignment View

**Purpose:** the "team" view for one class — coordinator, class teacher, subject teachers, TAs, resource gaps — matches Learning Planning & Control spec, Part A, Section 5 ("the team is a view, not a new table").

**Layout:** sidebar + top bar → left rail (class picker + plan status badge) → main panel split into "Class-level" roles and "Subject-level" roles, each row showing role + assigned resource. Gap rows render with danger styling inline, not a separate error panel.

**Data bindings:** `ResourcePlanAssignment` filtered by `target_id` = selected Class, grouped by `target_type` (CLASS rows first, then COURSE_OFFERING rows). Rows with `status=GAP` render as the red gap row.

```html
<div style="display:flex;gap:0;border:0.5px solid var(--border);border-radius:12px;overflow:hidden;min-height:480px">
<div style="width:180px;flex-shrink:0;background:var(--surface-1);padding:1rem 0.75rem">
  <div style="font-size:12px;color:var(--text-secondary);margin-bottom:8px">Classes — Grade 9</div>
  <div style="display:flex;flex-direction:column;gap:2px">
    <div style="padding:8px;border-radius:var(--radius);background:var(--fill-ghost-selected);font-size:13px">9-Cambridge-A</div>
    <div style="padding:8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)">9-Cambridge-B</div>
    <div style="padding:8px;border-radius:var(--radius);font-size:13px;color:var(--text-secondary)">9-Cambridge-C</div>
  </div>
  <div style="font-size:12px;color:var(--text-secondary);margin:16px 0 8px">Plan status</div>
  <span style="background:var(--bg-warning);color:var(--text-warning);font-size:12px;padding:3px 10px;border-radius:var(--radius)">Draft — 1 gap</span>
</div>
<div style="flex:1;padding:1rem 1.25rem;background:var(--surface-2)">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
    <div style="font-size:15px;font-weight:500">9-Cambridge-A — Term 1 team</div>
    <button style="font-size:13px">Publish plan</button>
  </div>
  <div style="font-size:12px;color:var(--text-secondary);margin-bottom:6px">Class-level</div>
  <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 10px;background:var(--surface-1);border-radius:var(--radius);margin-bottom:6px">
    <span style="font-size:13px">Class teacher</span>
    <span style="font-size:13px;color:var(--text-secondary)">Ayesha Malik</span>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 10px;background:var(--surface-1);border-radius:var(--radius);margin-bottom:14px">
    <span style="font-size:13px">Coordinator</span>
    <span style="font-size:13px;color:var(--text-secondary)">Bilal Ahmed (shared, 2 schools)</span>
  </div>
  <div style="font-size:12px;color:var(--text-secondary);margin-bottom:6px">Subject-level</div>
  <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 10px;background:var(--surface-1);border-radius:var(--radius);margin-bottom:6px">
    <span style="font-size:13px">Chemistry</span>
    <span style="font-size:13px;color:var(--text-secondary)">Nadia Farooq + 1 TA</span>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 10px;background:var(--surface-1);border-radius:var(--radius);margin-bottom:6px">
    <span style="font-size:13px">Mathematics</span>
    <span style="font-size:13px;color:var(--text-secondary)">Omar Sheikh</span>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 10px;background:var(--bg-danger);border-radius:var(--radius)">
    <span style="font-size:13px;color:var(--text-danger)">Physics</span>
    <span style="font-size:13px;color:var(--text-danger)">Gap — no teacher assigned</span>
  </div>
</div>
</div>
```

---

## 6. Screen: Learning Planning — Weekly Timetable

**Purpose:** the actual generated schedule for one class, color-coded by `session_type` — matches Learning Planning & Control spec, Part B, Section 4.

**Layout:** single panel, legend at top right, 5-day × N-period grid, each cell colored by session type.

**Data bindings:** `ClassSession` rows for the selected class/week, joined to `LessonPlan.session_type` for coloring. Legend maps directly to the enum: Teaching (accent), Practice (success), Support/Remedial (warning), Assessment (danger).

```html
<div style="border:0.5px solid var(--border);border-radius:12px;padding:1rem 1.25rem;background:var(--surface-2)">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
  <div style="font-size:15px;font-weight:500">9-Cambridge-A — timetable, Week 7</div>
  <div style="display:flex;gap:12px;font-size:12px;color:var(--text-secondary)">
    <span><span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:var(--fill-accent);margin-right:4px"></span>Teaching</span>
    <span><span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:var(--fill-success);margin-right:4px"></span>Practice</span>
    <span><span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:var(--fill-warning);margin-right:4px"></span>Support</span>
    <span><span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:var(--fill-danger);margin-right:4px"></span>Assessment</span>
  </div>
</div>
<table style="width:100%;border-collapse:collapse;table-layout:fixed">
<tr>
  <th style="width:60px"></th>
  <th style="font-size:12px;color:var(--text-secondary);font-weight:400;padding:6px">Mon</th>
  <th style="font-size:12px;color:var(--text-secondary);font-weight:400;padding:6px">Tue</th>
  <th style="font-size:12px;color:var(--text-secondary);font-weight:400;padding:6px">Wed</th>
  <th style="font-size:12px;color:var(--text-secondary);font-weight:400;padding:6px">Thu</th>
  <th style="font-size:12px;color:var(--text-secondary);font-weight:400;padding:6px">Fri</th>
</tr>
<tr>
  <td style="font-size:12px;color:var(--text-secondary);padding:4px">P1</td>
  <td style="padding:3px"><div style="background:var(--bg-accent);color:var(--text-accent);font-size:11px;padding:6px;border-radius:6px;text-align:center">Chemistry</div></td>
  <td style="padding:3px"><div style="background:var(--bg-accent);color:var(--text-accent);font-size:11px;padding:6px;border-radius:6px;text-align:center">Maths</div></td>
  <td style="padding:3px"><div style="background:var(--bg-success);color:var(--text-success);font-size:11px;padding:6px;border-radius:6px;text-align:center">Chem lab</div></td>
  <td style="padding:3px"><div style="background:var(--bg-accent);color:var(--text-accent);font-size:11px;padding:6px;border-radius:6px;text-align:center">English</div></td>
  <td style="padding:3px"><div style="background:var(--bg-danger);color:var(--text-danger);font-size:11px;padding:6px;border-radius:6px;text-align:center">Maths quiz</div></td>
</tr>
<tr>
  <td style="font-size:12px;color:var(--text-secondary);padding:4px">P2</td>
  <td style="padding:3px"><div style="background:var(--bg-accent);color:var(--text-accent);font-size:11px;padding:6px;border-radius:6px;text-align:center">Maths</div></td>
  <td style="padding:3px"><div style="background:var(--bg-accent);color:var(--text-accent);font-size:11px;padding:6px;border-radius:6px;text-align:center">Urdu</div></td>
  <td style="padding:3px"><div style="background:var(--bg-accent);color:var(--text-accent);font-size:11px;padding:6px;border-radius:6px;text-align:center">Physics</div></td>
  <td style="padding:3px"><div style="background:var(--bg-warning);color:var(--text-warning);font-size:11px;padding:6px;border-radius:6px;text-align:center">Support — 3</div></td>
  <td style="padding:3px"><div style="background:var(--bg-accent);color:var(--text-accent);font-size:11px;padding:6px;border-radius:6px;text-align:center">English</div></td>
</tr>
<tr>
  <td style="font-size:12px;color:var(--text-secondary);padding:4px">P3</td>
  <td style="padding:3px"><div style="background:var(--bg-accent);color:var(--text-accent);font-size:11px;padding:6px;border-radius:6px;text-align:center">Physics</div></td>
  <td style="padding:3px"><div style="background:var(--bg-success);color:var(--text-success);font-size:11px;padding:6px;border-radius:6px;text-align:center">Maths practice</div></td>
  <td style="padding:3px"><div style="background:var(--bg-accent);color:var(--text-accent);font-size:11px;padding:6px;border-radius:6px;text-align:center">Urdu</div></td>
  <td style="padding:3px"><div style="background:var(--bg-accent);color:var(--text-accent);font-size:11px;padding:6px;border-radius:6px;text-align:center">Chemistry</div></td>
  <td style="padding:3px"><div style="background:var(--bg-accent);color:var(--text-accent);font-size:11px;padding:6px;border-radius:6px;text-align:center">Physics</div></td>
</tr>
</table>
</div>
```

---

## 7. Reusable primitives observed across screens

Worth extracting into shared components rather than rebuilt per screen:

- **App shell** — sidebar + top context switcher, identical across all screens
- **Metric card** — label (13px muted) over value (24px medium)
- **Status badge** — colored pill, `bg-{role}` + `text-{role}` pair, never raw colors
- **Filter rail** — left sidebar list pattern, reused for Resource Pool's type/mode filters and Learning Planning's class picker
- **Data table** — hairline row borders, muted header row, used for Resource Pool's listing

---

## 8. Remaining screens to design

Admission (funnel/pipeline view), Financials Control (invoice + ledger dashboard), Regulatory Audit & Control (compliance dashboard + audit engagement tracker), Library & Subscriptions (catalog + circulation), Identity & Access (user/role management), Notification Management (notification center + escalation rules).
