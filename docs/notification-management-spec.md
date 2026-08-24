# Notification Management — Component Spec
Foundational infrastructure. Depends on: Identity & Access (role/scope resolution), Calendar Repository (due-date-driven alerts). Consumed by: Gap Analysis, Audit & Control, Learning Planning Management (remedial triggers), Learning Resource Planner (resource gaps) — any module with something worth alerting someone about.

---

## 1. One registry, not five bolted-on alerting systems

Multiple sources already need to notify someone: a `RemedialTrigger` going `SUGGESTED`, a `ResourceGap` going `OPEN`, a coverage gap falling behind schedule, a fee going overdue, an attendance absence. One shared registry, same principle as Calendar — everything else projects into it.

```
NotificationEvent
  source_type, source_id      polymorphic — any module's flagged item
  event_type                    REMEDIAL_SUGGESTED | RESOURCE_GAP_OPEN | FEE_OVERDUE
                                  | COVERAGE_BEHIND | COMPLIANCE_GAP | ...
  severity                       INFO | WARNING | CRITICAL
  created_at
```

---

## 2. Audience — reuses Calendar's targeting pattern

```
NotificationAudience
  notification_event_id
  audience_type          PERSON | ROLE_AT_SCOPE
  audience_id / (role, scope_type, scope_id)
```

"Notify the Coordinator of this Section" resolves through `RoleAssignment` the same way any role-scoped query does — no separate audience-resolution logic.

---

## 3. Delivery

```
NotificationDelivery
  notification_event_id, person_id
  channel        IN_APP | EMAIL | SMS | WHATSAPP | PUSH
  status          PENDING | SENT | DELIVERED | FAILED | READ

NotificationPreference
  person_id, event_type, channel, enabled
```

---

## 4. Escalation — what makes this an alerting system, not just a log

A `CRITICAL` alert unacknowledged within a set window escalates up — through the exact `RoleReportingDefault` chain from the Learning Resource Planner spec. TA → Subject Teacher → Coordinator → Branch Head. No second hierarchy to maintain.

```
NotificationEscalationRule
  event_type, severity
  escalate_after
```

**HOD note:** maps to the label pack's existing `discipline_head` role, sitting between Subject Teacher and Coordinator in the chain — not a new role, a slot in the existing one, provided that's what "HOD" means at a given school.

---

## 5. Build order

1. `NotificationEvent` / `NotificationAudience`
2. `NotificationDelivery` / `NotificationPreference`
3. Channel senders — in-app first, external providers (email/SMS/WhatsApp) after
4. `NotificationEscalationRule`, wired to `RoleReportingDefault`

---

## 6. Open decisions

- Whether escalation stops at the first acknowledgement, or continues up the chain regardless for genuinely critical alerts (a safety incident) where multiple people should know
- Provider selection for SMS/WhatsApp delivery — deferred until volume justifies the integration cost
