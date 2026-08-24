"use client";

import Link from "next/link";
import { UpcomingItem } from "@/lib/student";
import { useStudentOverview } from "@/lib/StudentContext";

function CoachIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3c-4 0-7 2.5-7 6.5 0 2 .8 3.6 2 4.8L6 19l3.4-1.6c.8.2 1.7.3 2.6.3 4 0 7-2.5 7-6.5S16 3 12 3z" />
      <circle cx="9.5" cy="9.5" r=".6" fill="currentColor" stroke="none" />
      <circle cx="14.5" cy="9.5" r=".6" fill="currentColor" stroke="none" />
    </svg>
  );
}

function buildCoachHeadline(pendingToday: UpcomingItem[], overdue: UpcomingItem[], overallAttendance: number | null): string {
  if (overdue.length > 0) {
    const item = overdue[0];
    const extra = overdue.length > 1 ? ` and ${overdue.length - 1} other item${overdue.length > 2 ? "s" : ""}` : "";
    return `${item.subject_name}'s "${item.title}" is still open from earlier${extra} — worth catching up on before anything new piles on.`;
  }
  if (pendingToday.length > 0) {
    const item = pendingToday[0];
    return `${item.subject_name} has "${item.title}" due today. Everything else is on track.`;
  }
  if (overallAttendance !== null && overallAttendance < 90) {
    return `Nothing due right today — a good moment to catch up, since attendance has dipped to ${overallAttendance}% this term.`;
  }
  return "Nothing urgent today — every subject is on track. Great pace to keep up.";
}

export default function StudentOverviewPage() {
  const data = useStudentOverview();

  const today = new Date().toISOString().slice(0, 10);
  const pendingToday = data.upcoming.filter((u) => u.due_date === today && u.status !== "GRADED" && u.status !== "SUBMITTED");
  const overdue = data.upcoming.filter((u) => u.status === "OVERDUE");
  const headline = buildCoachHeadline(pendingToday, overdue, data.overall_attendance_pct);

  const attendancePct = data.overall_attendance_pct ?? 0;
  const timelineItems = data.upcoming.slice(0, 6);

  return (
    <div className="sp-grid-3">
      <div className="sp-coach-card">
        <div className="sp-coach-avatar">
          <CoachIcon />
        </div>
        <div className="sp-coach-body">
          <div className="sp-coach-label">Your coach, today</div>
          <div className="sp-coach-headline">{headline}</div>
          <div className="sp-coach-tags">
            {overdue.length > 0 && (
              <span className="sp-coach-tag">
                <span className="sp-dot" style={{ background: "var(--sp-critical)" }} />
                {overdue.length} still open
              </span>
            )}
            {pendingToday.length > 0 && (
              <span className="sp-coach-tag">
                <span className="sp-dot" style={{ background: "var(--sp-warning)" }} />
                {pendingToday.length} due today
              </span>
            )}
            <span className="sp-coach-tag">
              <span className="sp-dot" style={{ background: attendancePct >= 90 ? "var(--sp-success)" : "var(--sp-warning)" }} />
              Attendance {attendancePct}%
            </span>
          </div>
        </div>
      </div>

      <div className="sp-card">
        <div className="sp-card-title">Attendance · overall</div>
        <div className="sp-attendance-hero">
          <div
            className="sp-attendance-ring-big"
            data-pct={`${attendancePct}%`}
            style={{ "--p": attendancePct } as React.CSSProperties}
          />
          <div className="sp-attendance-meta">
            <div className="sp-big">{attendancePct}% present this term</div>
            <div className="sp-muted">Across {data.subjects.length} subjects</div>
          </div>
        </div>
      </div>

      <div className="sp-card">
        <div className="sp-card-title">Performance by subject</div>
        {data.subjects.map((s) => (
          <div key={s.course_section_id} className="sp-perf-row">
            <span className="sp-perf-swatch" style={{ background: "var(--sp-accent)" }} />
            <Link href={`/student/subjects/${s.course_section_id}`} className="sp-perf-name" style={{ color: "inherit", textDecoration: "none" }}>
              {s.subject_name}
            </Link>
            <span className="sp-perf-bar-track">
              <span className="sp-perf-bar-fill" style={{ width: `${s.progress_pct ?? 0}%`, background: "var(--sp-accent)" }} />
            </span>
            <span className="sp-perf-pct sp-mono">{s.progress_pct ?? "—"}%</span>
          </div>
        ))}
      </div>

      <div className="sp-card" style={{ gridColumn: "1 / span 2" }}>
        <div className="sp-card-title">Upcoming &amp; open items</div>
        {timelineItems.length === 0 && <div className="sp-empty-state">Nothing due in the next two weeks.</div>}
        {timelineItems.map((item) => {
          const [, m, d] = item.due_date.split("-");
          const monthName = new Date(item.due_date + "T00:00:00").toLocaleDateString("en-US", { month: "short" });
          return (
            <div key={item.assessment_id} className="sp-timeline-item">
              <div className="sp-timeline-date">
                <div className="sp-d sp-mono">{d}</div>
                <div className="sp-m">{monthName}</div>
              </div>
              <div className="sp-timeline-body">
                <div className="sp-timeline-title">{item.title}</div>
                <div className="sp-timeline-sub">
                  {item.subject_name} · {item.day_label}
                  {item.status === "OVERDUE" ? " · overdue" : ""}
                </div>
              </div>
              <span className={`sp-badge ${item.type}`}>{item.type.toLowerCase()}</span>
            </div>
          );
        })}
      </div>

      <div className="sp-card">
        <div className="sp-card-title">Overall progress</div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 10 }}>
          <span className="sp-mono" style={{ fontFamily: "var(--font-data)", fontSize: 34 }}>
            {data.overall_progress_pct ?? "—"}%
          </span>
          <span style={{ fontSize: 12, color: "var(--sp-text-muted)" }}>across {data.subjects.length} subjects</span>
        </div>
        <div style={{ fontSize: 12.5, color: "var(--sp-text-muted)", lineHeight: 1.5 }}>
          {data.subjects.length > 0 &&
            (() => {
              const best = [...data.subjects].sort((a, b) => (b.progress_pct ?? 0) - (a.progress_pct ?? 0))[0];
              const worst = [...data.subjects].sort((a, b) => (a.progress_pct ?? 0) - (b.progress_pct ?? 0))[0];
              return `Strongest in ${best.subject_name} right now, with ${worst.subject_name} needing the most attention this term.`;
            })()}
        </div>
      </div>
    </div>
  );
}
