"use client";

import { use, useEffect, useState } from "react";
import { getSubjectDetail, SubjectDetail } from "@/lib/student";

type TabKey = "content" | "attendance" | "assignments" | "assessments" | "dates";

const TABS: { key: TabKey; label: string }[] = [
  { key: "content", label: "Content" },
  { key: "attendance", label: "Attendance" },
  { key: "assignments", label: "Assignments" },
  { key: "assessments", label: "Assessments" },
  { key: "dates", label: "Important dates" },
];

function CheckIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 6L9 17l-5-5" />
    </svg>
  );
}

export default function SubjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [data, setData] = useState<SubjectDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<TabKey>("content");

  useEffect(() => {
    setData(null);
    setTab("content");
    getSubjectDetail(Number(id))
      .then(setData)
      .catch(() => setError("Couldn't load this subject."));
  }, [id]);

  if (error) return <div className="sp-empty-state">{error}</div>;
  if (!data) return <div className="sp-empty-state">Loading…</div>;

  return (
    <div>
      <div className="sp-subject-header">
        <div className="sp-subject-header-left">
          <div className="sp-subject-icon" style={{ background: "var(--sp-accent)" }}>
            {data.subject_name.charAt(0)}
          </div>
          <div>
            <h2 className="sp-subject-title sp-display">{data.subject_name}</h2>
            <div className="sp-subject-teacher">
              {data.teacher_name}
              {data.next_class ? ` · Next class ${data.next_class}` : ""}
            </div>
          </div>
        </div>
        <div className="sp-subject-stat">
          <div className="sp-val">{data.progress_pct ?? "—"}%</div>
          <div className="sp-lbl">Current progress</div>
        </div>
      </div>

      <div className="sp-tabs">
        {TABS.map((t) => (
          <button key={t.key} className={`sp-tab-btn ${tab === t.key ? "is-active" : ""}`} onClick={() => setTab(t.key)}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === "content" && (
        <div className="sp-card">
          <div className="sp-card-title">
            Syllabus coverage {data.coverage_pct !== null ? `· ${data.coverage_pct}% covered` : ""}
          </div>
          {data.content.length === 0 && <div className="sp-empty-state">No topics listed yet.</div>}
          {data.content.map((c, i) => (
            <div key={i} className="sp-topic-row">
              <span className={`sp-topic-check ${c.is_covered ? "done" : "pending"}`}>{c.is_covered && <CheckIcon />}</span>
              <span className="sp-topic-name">{c.name}</span>
              <span className="sp-topic-meta">{c.is_covered ? "Covered" : "Upcoming"}</span>
            </div>
          ))}

          {data.recent_activity.length > 0 && (
            <>
              <div className="sp-card-title" style={{ marginTop: 22 }}>
                Recent classwork &amp; homework
              </div>
              {data.recent_activity.slice(0, 5).map((a, i) => (
                <div key={i} className="sp-topic-row">
                  <span className="sp-topic-meta" style={{ width: 70, flexShrink: 0 }}>
                    {new Date(a.date + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                  </span>
                  <span className="sp-topic-name">
                    {a.classwork}
                    {a.homework && <span style={{ color: "var(--sp-accent-strong)" }}> · Homework: {a.homework}</span>}
                  </span>
                </div>
              ))}
            </>
          )}
        </div>
      )}

      {tab === "attendance" && (
        <div className="sp-card">
          <div className="sp-card-title">Attendance in {data.subject_name}</div>
          <div className="sp-attendance-hero">
            <div
              className="sp-attendance-ring-big"
              data-pct={`${data.attendance_pct ?? 0}%`}
              style={{ "--p": data.attendance_pct ?? 0 } as React.CSSProperties}
            />
            <div className="sp-attendance-meta">
              <div className="sp-big">{data.attendance_pct ?? "—"}% present this term</div>
              <div className="sp-muted">Based on {data.attendance.length} session(s) so far</div>
            </div>
          </div>
          <table className="sp-table" style={{ marginTop: 20 }}>
            <thead>
              <tr>
                <th>Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {[...data.attendance].reverse().map((a, i) => (
                <tr key={i}>
                  <td>{new Date(a.date + "T00:00:00").toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" })}</td>
                  <td>
                    <span className={`sp-week-mark ${a.status}`} style={{ display: "inline-flex", width: "auto", padding: "3px 10px" }}>
                      {a.status.toLowerCase()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "assignments" && (
        <div className="sp-card">
          <div className="sp-card-title">Assignments</div>
          {data.assignments.length === 0 && <div className="sp-empty-state">No assignments yet.</div>}
          {data.assignments.length > 0 && (
            <table className="sp-table">
              <thead>
                <tr>
                  <th>Assignment</th>
                  <th>Due</th>
                  <th>Status</th>
                  <th style={{ textAlign: "right" }}>Score</th>
                </tr>
              </thead>
              <tbody>
                {data.assignments.map((a) => (
                  <tr key={a.assessment_id}>
                    <td>{a.title}</td>
                    <td>{a.due_date ? new Date(a.due_date + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric" }) : "—"}</td>
                    <td>
                      <span className={`sp-status-pill ${a.status}`}>{a.status.toLowerCase()}</span>
                    </td>
                    <td className="sp-num">{a.score ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {tab === "assessments" && (
        <div className="sp-card">
          <div className="sp-card-title">Quizzes &amp; assessments</div>
          {data.assessments.length === 0 && <div className="sp-empty-state">No quizzes or exams yet.</div>}
          {data.assessments.length > 0 && (
            <table className="sp-table">
              <thead>
                <tr>
                  <th>Assessment</th>
                  <th>Type</th>
                  <th>Date</th>
                  <th style={{ textAlign: "right" }}>Score</th>
                </tr>
              </thead>
              <tbody>
                {data.assessments.map((a) => (
                  <tr key={a.assessment_id}>
                    <td>{a.title}</td>
                    <td>
                      <span className={`sp-badge ${a.type}`}>{a.type.toLowerCase()}</span>
                    </td>
                    <td>{a.due_date ? new Date(a.due_date + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric" }) : "—"}</td>
                    <td className="sp-num">{a.score ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {tab === "dates" && (
        <div className="sp-card">
          <div className="sp-card-title">Important dates</div>
          {data.important_dates.length === 0 && <div className="sp-empty-state">Nothing scheduled yet.</div>}
          {data.important_dates.map((a) => {
            const monthName = a.due_date ? new Date(a.due_date + "T00:00:00").toLocaleDateString("en-US", { month: "short" }) : "";
            const day = a.due_date ? a.due_date.split("-")[2] : "";
            return (
              <div key={a.assessment_id} className="sp-timeline-item">
                <div className="sp-timeline-date">
                  <div className="sp-d sp-mono">{day}</div>
                  <div className="sp-m">{monthName}</div>
                </div>
                <div className="sp-timeline-body">
                  <div className="sp-timeline-title">{a.title}</div>
                  <div className="sp-timeline-sub">{a.status.toLowerCase()}</div>
                </div>
                <span className={`sp-badge ${a.type}`}>{a.type.toLowerCase()}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
