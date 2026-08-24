"use client";

import { useEffect, useRef, useState } from "react";
import { getNotifications, markNotificationRead, StudentNotification } from "@/lib/student";

const DOT_COLOR: Record<string, string> = {
  GRADE_POSTED: "var(--sp-accent)",
  ABSENCE: "var(--sp-critical)",
  DEADLINE: "var(--sp-warning)",
  ANNOUNCEMENT: "var(--sp-teal)",
};

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const diffMs = Date.now() - new Date(iso).getTime();
  const hours = Math.floor(diffMs / 3600000);
  if (hours < 1) return "Just now";
  if (hours < 24) return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  const days = Math.floor(hours / 24);
  return days === 1 ? "Yesterday" : `${days} days ago`;
}

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<StudentNotification[]>([]);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getNotifications()
      .then(setNotifications)
      .catch(() => setNotifications([]));
  }, []);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  async function handleOpen(n: StudentNotification) {
    if (!n.is_read) {
      setNotifications((prev) => prev.map((x) => (x.id === n.id ? { ...x, is_read: true } : x)));
      try {
        await markNotificationRead(n.id);
      } catch {
        // best-effort
      }
    }
  }

  return (
    <div className="sp-bell-wrap" ref={wrapRef}>
      <button className="sp-bell-btn" onClick={() => setOpen((v) => !v)} aria-label="Notifications">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 8a6 6 0 10-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 01-3.46 0" />
        </svg>
        {unreadCount > 0 && <span className="sp-bell-dot" />}
      </button>
      {open && (
        <div className="sp-bell-panel">
          <div className="sp-bell-panel-title">Notifications</div>
          {notifications.length === 0 && <div className="sp-notif-empty">You&apos;re all caught up</div>}
          {notifications.map((n) => (
            <div key={n.id} className="sp-notif-row" onClick={() => handleOpen(n)}>
              <div className="sp-notif-dot" style={{ background: DOT_COLOR[n.type] || "var(--sp-text-faint)" }} />
              <div>
                <div className="sp-notif-text">
                  <strong>{n.title}</strong>
                  {n.body ? ` — ${n.body}` : ""}
                </div>
                <div className="sp-notif-time">{timeAgo(n.created_at)}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
