"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

interface StaffMember {
  person_id: number;
  first_name: string;
  last_name: string;
  email: string;
  role: string;
  role_id: number;
}

interface JobApplication {
  id: number;
  applicant_person_id: number;
  position: string;
  status: string;
  is_locked: boolean;
}

export default function StaffManagement() {
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<"STAFF" | "APPLICATIONS">("STAFF");

  const fetchData = async () => {
    try {
      const [staffRes, appsRes] = await Promise.all([
        fetch("/api/staff/active"),
        fetch("/api/staff/applications")
      ]);
      const staffData = await staffRes.json();
      const appsData = await appsRes.json();
      setStaff(staffData);
      setApplications(appsData);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleHire = async (app: JobApplication, role: string) => {
    // 1. Update application status to HIRED
    await fetch(`/api/staff/applications/${app.id}/status?status=HIRED`, {
      method: "PUT"
    });
    
    // 2. Assign the role to the person
    await fetch(`/api/staff/roles`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ person_id: app.applicant_person_id, role })
    });
    
    fetchData(); // Refresh everything
  };

  return (
    <div className="min-h-screen bg-gray-50 flex font-[family-name:var(--font-geist-sans)]">
      {/* Sidebar - App Shell */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col hidden md:flex">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center gap-2 text-indigo-700 font-bold text-xl tracking-tight">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 3L1 9L5 11.18V17.18L12 21L19 17.18V11.18L21 10.09V17H23V9L12 3ZM18.82 9L12 12.72L5.18 9L12 5.28L18.82 9ZM12 18.72L7 15.99V12.27L12 15L17 12.27V15.99L12 18.72Z"/></svg>
            Brainiacs
          </div>
          <p className="text-xs text-gray-500 mt-1 uppercase font-medium tracking-wider">Main Campus</p>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          <Link href="/dashboard?role=ADMIN" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
            Overview Dashboard
          </Link>
          <a href="#" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            Admissions
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md bg-indigo-50 text-indigo-700">
            <svg className="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
            Staff & HR
          </a>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-8">
          <h1 className="text-xl font-bold text-gray-900">Staff & HR Management</h1>
          <div className="flex items-center gap-4">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Active Term: Fall 2026
            </span>
            <div className="w-8 h-8 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold text-sm">
              AA
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-6xl mx-auto">
            {/* Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <p className="text-sm font-medium text-gray-500 mb-1">Active Staff</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-gray-900">{staff.length}</span>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <p className="text-sm font-medium text-gray-500 mb-1">Pending Job Applications</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-indigo-600">{applications.filter(a => a.status !== 'HIRED').length}</span>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <p className="text-sm font-medium text-gray-500 mb-1">Recent Hires</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-green-600">{applications.filter(a => a.status === 'HIRED').length}</span>
                </div>
              </div>
            </div>

            {/* Tab Toggle */}
            <div className="flex gap-4 mb-6">
              <button 
                onClick={() => setView("STAFF")} 
                className={`px-6 py-2 rounded-lg font-medium transition ${view === "STAFF" ? "bg-indigo-600 text-white" : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"}`}
              >
                Active Personnel
              </button>
              <button 
                onClick={() => setView("APPLICATIONS")} 
                className={`px-6 py-2 rounded-lg font-medium transition ${view === "APPLICATIONS" ? "bg-indigo-600 text-white" : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"}`}
              >
                Recruitment Pipeline
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden min-h-[400px]">
              {loading ? (
                <div className="p-8 text-center text-gray-500 text-sm">Loading data...</div>
              ) : view === "STAFF" ? (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Person ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {staff.map((s) => (
                      <tr key={s.role_id} className="hover:bg-gray-50 transition">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{s.person_id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-bold text-gray-600">
                              {s.first_name.charAt(0)}{s.last_name.charAt(0)}
                            </div>
                            {s.first_name} {s.last_name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{s.email}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-block px-2.5 py-0.5 text-xs font-medium uppercase tracking-wider text-blue-800 bg-blue-100 rounded-full">
                            {s.role.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button className="text-indigo-600 hover:text-indigo-900 bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded-md transition">Edit Profile</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">App ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Applicant ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Position Applied</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hire / Assign Role</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {applications.map((app) => (
                      <tr key={app.id} className="hover:bg-gray-50 transition">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">JOB-{app.id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{app.applicant_person_id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{app.position}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-block px-2.5 py-0.5 text-xs font-medium uppercase tracking-wider rounded-full ${app.status === 'HIRED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                            {app.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {app.status !== "HIRED" ? (
                            <div className="flex gap-2">
                              <button onClick={() => handleHire(app, "TEACHER")} className="text-xs font-medium bg-green-50 text-green-700 px-3 py-1.5 rounded-md hover:bg-green-100 transition border border-green-200">Hire as Teacher</button>
                              <button onClick={() => handleHire(app, "ADMIN")} className="text-xs font-medium bg-gray-50 text-gray-700 px-3 py-1.5 rounded-md hover:bg-gray-200 transition border border-gray-300">Hire as Admin</button>
                            </div>
                          ) : (
                            <span className="text-sm font-medium text-gray-500 flex items-center gap-1">
                              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>
                              Successfully Hired
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
