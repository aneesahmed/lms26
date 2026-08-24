"use client";
import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";

function DashboardContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [role, setRole] = useState<"APPLICANT" | "ADMIN">("APPLICANT");

  useEffect(() => {
    const roleParam = searchParams.get("role");
    if (roleParam === "ADMIN" || roleParam === "APPLICANT") {
      setRole(roleParam);
    }
  }, [searchParams]);

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-[family-name:var(--font-geist-sans)]">

      {/* MOCK LOGIN SELECTOR (For Testing Only - Admin/Applicant panels aren't wired to real auth yet) */}
      <div className="max-w-6xl mx-auto mb-6 bg-yellow-50 border border-yellow-200 p-4 rounded-xl flex gap-4 items-center">
        <span className="text-sm font-bold text-yellow-800 uppercase tracking-wider">Test Mode: View As</span>
        <button onClick={() => setRole("ADMIN")} className={`px-4 py-1 text-sm rounded-full font-medium ${role === 'ADMIN' ? 'bg-yellow-800 text-white' : 'bg-white text-yellow-800 border border-yellow-300'}`}>Admin Staff</button>
        <button onClick={() => router.push("/login")} className="px-4 py-1 text-sm rounded-full font-medium bg-white text-yellow-800 border border-yellow-300">
          Student (real login &rarr;)
        </button>
        <button onClick={() => setRole("APPLICANT")} className={`px-4 py-1 text-sm rounded-full font-medium ${role === 'APPLICANT' ? 'bg-yellow-800 text-white' : 'bg-white text-yellow-800 border border-yellow-300'}`}>Applicant (Admissions)</button>
      </div>

      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Header */}
        <header className="flex justify-between items-center bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {role === 'ADMIN' ? 'Alice (Admin)' : 'Jane (Applicant)'}!
            </h1>
            <p className="text-gray-500 text-sm mt-1">
              {role === 'ADMIN' ? 'Brainiacs Main Campus' : 'Applicant ID: BRN-2024-9428'}
            </p>
          </div>
          <div className="flex gap-4">
            <button className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200">Help</button>
            <div className="w-10 h-10 bg-blue-100 text-blue-700 flex items-center justify-center rounded-full font-bold">
              {role === 'ADMIN' ? 'AA' : 'JD'}
            </div>
          </div>
        </header>

        {/* --- ADMIN VIEW --- */}
        {role === "ADMIN" && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Link href="/admin/admissions" className="bg-white p-6 rounded-2xl shadow-sm border border-blue-100 hover:shadow-md cursor-pointer transition">
              <div className="text-3xl mb-4">🎓</div>
              <h2 className="text-lg font-bold text-gray-900">Admissions</h2>
              <p className="text-sm text-gray-500 mt-2">Manage applications</p>
            </Link>
            <Link href="/admin/staff" className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 hover:shadow-md cursor-pointer transition">
              <div className="text-3xl mb-4">👥</div>
              <h2 className="text-lg font-bold text-gray-900">Staff Management</h2>
              <p className="text-sm text-gray-500 mt-2">Manage roles & schedules</p>
            </Link>
            <Link href="/admin/assets" className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 hover:shadow-md cursor-pointer transition">
              <div className="text-3xl mb-4">🏫</div>
              <h2 className="text-lg font-bold text-gray-900">Asset Management</h2>
              <p className="text-sm text-gray-500 mt-2">Rooms, vehicles & equipment</p>
            </Link>
            <Link href="/admin/academic" className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 hover:shadow-md cursor-pointer transition">
              <div className="text-3xl mb-4">📅</div>
              <h2 className="text-lg font-bold text-gray-900">Learning & Planning</h2>
              <p className="text-sm text-gray-500 mt-2">Courses, schedules & grading</p>
            </Link>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 hover:shadow-md cursor-pointer transition">
              <div className="text-3xl mb-4">💰</div>
              <h2 className="text-lg font-bold text-gray-900">Financials</h2>
              <p className="text-sm text-gray-500 mt-2">Payroll & billing</p>
            </div>
          </div>
        )}

        {/* --- APPLICANT VIEW (From Earlier) --- */}
        {role === "APPLICANT" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="col-span-2 space-y-6">
              <div className="bg-blue-50 border border-blue-100 p-8 rounded-xl flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-blue-900">Start Your Admission Application</h2>
                  <p className="text-blue-700 mt-2">You haven't started your Fall 2026 application yet.</p>
                </div>
                <Link href="/admission/form" className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 shadow-sm inline-block">
                  Begin Form
                </Link>
              </div>
              <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <h3 className="text-lg font-bold text-gray-900 mb-6">Application Status</h3>
                <div className="flex justify-between relative">
                  <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-200 -z-10 -translate-y-1/2"></div>
                  <div className="flex flex-col items-center gap-2 bg-white px-2">
                    <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold">✓</div>
                    <span className="text-sm font-medium text-blue-600">Registered</span>
                  </div>
                  <div className="flex flex-col items-center gap-2 bg-white px-2">
                    <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-500 flex items-center justify-center font-bold">2</div>
                    <span className="text-sm font-medium text-gray-500">Form Submitted</span>
                  </div>
                  <div className="flex flex-col items-center gap-2 bg-white px-2">
                    <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-500 flex items-center justify-center font-bold">3</div>
                    <span className="text-sm font-medium text-gray-500">Entrance Test</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default function Dashboard() {
  return (
    <Suspense fallback={<div className="p-8">Loading dashboard...</div>}>
      <DashboardContent />
    </Suspense>
  );
}
