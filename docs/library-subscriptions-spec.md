# Library & Subscriptions — Component Spec
Depends on: Resource Pool (physical copies and digital licenses are Resources), Resource Finance (subscription cost, late fees), Calendar Repository (due-date reminders).

---

## 1. Catalog — definition/instance, one new axis

```
Title       isbn, name, author, subject_tags, format
             PHYSICAL_BOOK | EBOOK | JOURNAL | DATABASE | STREAMING

Copy         a Resource, resource_type=BOOK_COPY, allocation_mode=RESERVABLE
              title_id, branch_id, accession_no (→ ResourceLocalId.local_code), condition
```

A physical copy is just another `Resource`. Nothing new to build for it.

---

## 2. Physical issue/return — reuses Resource Pool exactly

```
Issue    ResourceBooking(resource_id=copy, start_at=today, end_at=due_date,
                          calendar_event_id=a due-date reminder)
Return   status → RETURNED, actual_return_at recorded
Late     ResourceBookingBilling(billable=true, amount=days_late × rate)   -- Resource Finance
```

Inter-branch loan of a physical copy is an ordinary `ResourceTransferLog` entry — same mechanism that moves a projector between branches.

---

## 3. Digital access — two shapes, already distinct modes

- **Site-wide subscription** (JSTOR, an e-book platform) — `ResourceShare`, `participant_type=ORG`, no schedule, ongoing. No per-use booking.
- **Concurrent-seat license** (5 simultaneous readers) — `RESERVABLE`, but needs a capacity extension:

```
Resource.capacity    new field on the core Resource Pool spec, default 1 (physical exclusivity), N for multi-seat digital
```

Clash-check changes from "reject if any active booking exists" to "reject if active bookings ≥ capacity." General enough to belong in Resource Pool's core spec, not scoped narrowly to library.

---

## 4. Subscription cost

Structurally identical to `ResourceRentalExpense` (Resource Finance) — vendor, rate, billing cycle. A new `resource_type = DIGITAL_SUBSCRIPTION` feeding the existing shape, no new table.

---

## 5. Holds/waitlist — the one genuine gap

```
ResourceHoldRequest
  resource_id or title_id (any available copy)
  requested_by, requested_at
  status              QUEUED | FULFILLED | CANCELLED | EXPIRED
  fulfilled_booking_id (nullable)
```

General enough to benefit any contested `RESERVABLE` resource, not just books — worth considering as a Resource Pool core addition later.

---

## 6. Build order

1. `Title` / `Copy` catalog
2. Issue/return via existing `ResourceBooking`
3. `Resource.capacity` extension (coordinate with Resource Pool spec)
4. Digital access — `ResourceShare` for site-wide, capacity-bound `ResourceBooking` for seat-limited
5. `ResourceHoldRequest`

---

## 7. Open decisions

- Whether `capacity` ships in Resource Pool's core spec now, or is added when library is actually built and the need is concrete
- Whether `ResourceHoldRequest` stays library-scoped or generalizes into Resource Pool for other contested resources
