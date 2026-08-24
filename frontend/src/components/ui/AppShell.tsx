"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode } from "react";
import { SubjectSummary } from "@/lib/student";
import { clearSession, getSession } from "@/lib/api";
import NotificationBell from "./NotificationBell";

function initials(name: string) {
  return name
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

export default function AppShell({
  studentName,
  classLabel,
  subjects,
  children,
}: {
  studentName: string;
  classLabel: string;
  subjects: SubjectSummary[];
  children: ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const session = getSession();

  function handleLogout() {
    clearSession();
    router.push("/login");
  }

  return (
    <div className="sp-root">
      <div className="sp-shell">
        <nav className="sp-sidebar">
          <div className="sp-brand">
            <div className="sp-brand-mark">B</div>
            <div>
              <div className="sp-brand-name">Brainiacs</div>
              <div className="sp-brand-sub">Student Hub</div>
            </div>
          </div>

          <div className="sp-nav-list">
            <Link href="/student" className={`sp-nav-item ${pathname === "/student" ? "is-active" : ""}`}>
              <span className="sp-nav-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="7" height="9" rx="1.5" />
                  <rect x="14" y="3" width="7" height="5" rx="1.5" />
                  <rect x="14" y="12" width="7" height="9" rx="1.5" />
                  <rect x="3" y="16" width="7" height="5" rx="1.5" />
                </svg>
              </span>
              <span>Overview</span>
            </Link>
          </div>

          <div>
            <div className="sp-nav-section-label">My subjects</div>
            <div className="sp-nav-list">
              {subjects.map((s) => {
                const active = pathname === `/student/subjects/${s.course_section_id}`;
                const pct = s.progress_pct ?? 0;
                return (
                  <Link
                    key={s.course_section_id}
                    href={`/student/subjects/${s.course_section_id}`}
                    className={`sp-nav-item sp-subject-row ${active ? "is-active" : ""}`}
                  >
                    <span className="sp-subject-row-left">
                      <span
                        className="sp-ring"
                        style={{ "--p": pct, "--ring-color": "var(--sp-accent)" } as React.CSSProperties}
                      />
                      <span className="sp-subject-name">{s.subject_name}</span>
                    </span>
                    <span className="sp-ring-pct">{s.progress_pct ?? "—"}%</span>
                  </Link>
                );
              })}
            </div>
          </div>

          <button className="sp-sidebar-footer" onClick={handleLogout} style={{ border: "none", cursor: "pointer" }}>
            <div className="sp-avatar">{initials(studentName)}</div>
            <div style={{ textAlign: "left" }}>
              <div className="sp-sidebar-footer-name">{studentName}</div>
              <div className="sp-sidebar-footer-role">{classLabel} · Sign out</div>
            </div>
          </button>
        </nav>

        <div className="sp-main">
          <header className="sp-topbar">
            <div className="sp-greeting">
              <h1 className="sp-display">Hi, {studentName.split(" ")[0]}</h1>
              <div className="sp-sub">{classLabel} · Brainiacs Main Campus</div>
            </div>
            <div className="sp-topbar-right">
              <NotificationBell />
            </div>
          </header>
          <main className="sp-content">{children}</main>
        </div>
      </div>
    </div>
  );
}
