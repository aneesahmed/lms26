# Financials Control — Component Spec
Consolidates: institution-wide financials (tuition, activity fees, payroll, general expenses, ledger) and the narrower cost/income layer attached to pooled resources (depreciation, shared-resource billing, rental). One document because a family's invoice and a shared teacher's cost-recovery both post to the same ledger — they shouldn't live in specs that don't know about each other.

**Non-negotiable constraint:** everything here routes through the kernel's existing `commerce.py` — minor-unit integers, no floats, paired currency, already enforced by governance checks in the base repo. This spec adds sources feeding that ledger; it doesn't reinvent money handling.

---

# Part A — Institutional Financials (tuition, payroll, general expense, ledger)

## 1. Income — three origins, one invoice per payer

Tuition and activity fees aren't separate systems from each other. A sports club or music elective is just a `Course` (short-term, offline, `facility_type_needed` set accordingly — see Learning Planning & Control, Part A), so its fee flows through the exact same enrolment-based path as tuition. Transport is different — a `ResourceShare` subscription, billed through `ResourceCostAllocation` (Part B of this document). Resource rental *out* (renting an auditorium to an outside party) is a one-off `ResourceBooking` charge (also Part B).

Three different origins, but a family should see **one invoice per billing cycle**, not three:

```
Invoice          payer_id, billing_period, status
InvoiceLine       invoice_id, source_type (TUITION|ACTIVITY|TRANSPORT|RESOURCE_BOOKING), source_id, amount
```

## 2. Expense — four sources, no consolidation needed, they just post

**Salary** — `PayrollRun`/`PayslipLine`, tied to `Employee` (Identity & Access spec).

```
PayrollRun    organization_id, period, status
PayslipLine   employee_id, payroll_run_id, base_salary, allowances, deductions, net_pay
```

Worth being precise about a distinction: payroll is *paying* the person; `ResourceCostAllocation` (Part B) is how the *cost gets recovered* across branches sharing that person. Two different concerns that happen to both reference `Employee.base_cost`.

**Other expenses** — a plain categorized table, org-scoped, with approval.

```
Expense    org_id, category, amount, currency, date, approved_by, receipt_ref
```

**Resource rental *in*** and **depreciation** — covered in Part B, since both are specifically about pooled physical resources rather than general institutional spend.

## 3. General ledger

Everything above and everything in Part B posts here. Double-entry, minor-unit only, no exceptions.

```
LedgerEntry    account, debit/credit, amount, currency, source_type, source_id, posted_at
```

---

# Part B — Resource-Level Cost and Income (depreciation, shared-resource billing, rental)

## 1. Cost allocation for shared resources — percentage or fixed, pre-decided

```
ResourceCostAllocation
  resource_share_id (→ resource-pool-spec.md's ResourceShare)
  payer_type, payer_id        Org or Person, matching the share's participant
  method                      PERCENTAGE | FIXED
  value                       0-100 if PERCENTAGE, minor-unit amount if FIXED
  currency                    required for FIXED
  billing_cycle               MONTHLY | TERM | ANNUAL
  effective_from, effective_to (nullable = ongoing)
```

**Percentage** ties to the resource's actual cost — for a shared principal or guard, that's their `Employee.base_cost`; for a transport route, that's the route's total operating cost — and splits it: 40% to School A, 30% each to Schools B and C, or divided evenly across every student subscribed to a route this term. **100% is mandatory when percentage-based, not a soft target.** A share's active percentage allocations must sum to exactly 100% before it's allowed to go live — no partial split with an implicit remainder. If the parties involved can't agree on a full percentage split, the method becomes `FIXED` instead: each payer covers a hard, pre-decided amount — a flat 3,000 PKR/month transport fee per student, say — independent of what the resource actually costs to run. Write-time constraint, enforced the same way the kernel's `tools/checks/money_types.py`-style validators already enforce money discipline elsewhere.

**Fixed** is a pre-negotiated flat service fee, independent of actual cost. No sum constraint, since flat fees don't need to add up to anything in particular.

Each billing cycle, this generates a line item through the existing commerce module — the same recurring-generation pattern the Calendar repository uses to expand a rule into concrete sessions, now producing invoice lines on its tick instead.

**Privacy boundary, worth being careful with:** a percentage allocation computes off `Employee.base_cost`, which is payroll data. The invoice line a receiving branch's finance view sees should show the computed amount owed, not the underlying salary figure that produced it.

---

## 2. Reservation billing — one-off, event-driven

```
ResourceBookingBilling
  resource_booking_id (→ resource-pool-spec.md's ResourceBooking)
  billable BOOLEAN
  rate_ref, amount, currency
  order_id (nullable, set once invoiced)
```

Kept out of `ResourceBooking` itself so the pool's booking table never carries money fields — a booking is a booking whether or not it's billed; billing is a fact recorded alongside it.

---

## 3. Rental — the expense side of `ownership = RENTED`

```
ResourceRentalExpense
  resource_id (→ a RENTED resource in resource-pool-spec.md)
  vendor, rate, billing_cycle, currency
  effective_from, effective_to
```

A rented bus or a rented set of chairs for an event still plugs into the same booking mechanism as anything owned — `ownership` on the `Resource` row is what tells this spec it needs a cost record at all. `RENTED` resources never get a depreciation schedule (Section 4) — you don't depreciate what you don't own.

---

## 4. Depreciation — owned physical resources only

```
AssetDepreciation
  resource_id (→ an OWNED physical resource)
  acquisition_cost, acquisition_date
  depreciation_method    STRAIGHT_LINE | REDUCING_BALANCE
  useful_life_years, salvage_value
  disposal_value, disposal_date (nullable, set on RETIRED/DISPOSED)
```

Generates periodic expense entries automatically — the same recurrence engine again, now producing depreciation lines instead of class sessions or billing invoices. Closes out when the resource's status flips to `RETIRED`/`DISPOSED` in the pool spec.

---

## 5. Maintenance cost

```
AssetMaintenanceLog
  maintenance_window_id (→ resource-pool-spec.md's ResourceMaintenanceWindow)
  cost, currency, performed_by, invoice_ref
```

The pool spec owns *when* a resource was unavailable for maintenance and blocks bookings during that window. This table owns what it cost — kept separate so a maintenance record can exist as a scheduling fact even before its cost is known, and the cost gets attached once the work is billed.

---

## 6. Financial dashboard — extends the pool's allocation view

```
ResourceFinanceView    (extends resource-pool-spec.md's ResourceAllocationView)
  resource_id
  acquisition_cost, depreciation_to_date       from Section 4
  maintenance_cost_to_date                       sum of Section 5
  rental_cost_to_date                             if ownership = RENTED, from Section 3
  income_to_date                                   rental-out income (Section 2) + cost recovered (Section 1)
  net_position                                      income − cost
```

`net_position` is the number that actually matters here — not just "where is this resource," but "is this arrangement worth what it costs." A shared security guard covering two branches, an auditorium rented out for events, a fleet of buses — this is where the answer to "is it earning its keep" lives.

---

# Consolidated Build Order

1. `Invoice` / `InvoiceLine` — consolidated billing (Part A)
2. `PayrollRun` / `PayslipLine` (Part A)
3. `Expense` (Part A)
4. `LedgerEntry` — double-entry posting (Part A)
5. `ResourceCostAllocation` — shared resource billing (Part B)
6. `ResourceBookingBilling` — reservation billing (Part B)
7. `ResourceRentalExpense` — rental-in cost (Part B)
8. `AssetDepreciation` — owned asset depreciation (Part B)
9. `AssetMaintenanceLog` — maintenance cost (Part B)
10. `ResourceFinanceView` — the resource-level dashboard (Part B)

---

# Consolidated Open Decisions

- Full chart of accounts and double-entry posting from day one, or simpler categorized tracking that grows into double-entry once transaction volume justifies it
- Whether `ResourceCostAllocation` billing needs to be built for launch, or tracked without invoicing until inter-branch/inter-school charging is an actual business requirement
- Whether depreciation and maintenance cost post automatically to the ledger on generation, or require a finance approval step first
