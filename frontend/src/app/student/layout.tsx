"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getSession } from "@/lib/api";
import { getOverview, StudentOverview } from "@/lib/student";
import { StudentOverviewContext } from "@/lib/StudentContext";
import AppShell from "@/components/ui/AppShell";

export default function StudentLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [overview, setOverview] = useState<StudentOverview | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const session = getSession();
    if (!session || session.role !== "STUDENT") {
      router.replace("/login");
      return;
    }
    setChecked(true);
    getOverview()
      .then(setOverview)
      .catch(() => router.replace("/login"));
  }, [router]);

  if (!checked || !overview) {
    return (
      <div className="sp-root" style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh" }}>
        <div style={{ color: "var(--sp-text-muted)", fontSize: 13 }}>Loading your dashboard…</div>
      </div>
    );
  }

  return (
    <StudentOverviewContext.Provider value={overview}>
      <AppShell studentName={overview.student.full_name} classLabel={overview.student.class_label} subjects={overview.subjects}>
        {children}
      </AppShell>
    </StudentOverviewContext.Provider>
  );
}
