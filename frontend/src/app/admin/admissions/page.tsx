"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

interface Application {
  id: number;
  applicant_person_id: number;
  status: string;
  is_locked: boolean;
  applied_at: string;
  documents?: Record<string, string>;
}

export default function AdminAdmissions() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);

  useEffect(() => {
    fetch("/api/admission/")
      .then((res) => res.json())
      .then((data) => {
        setApplications(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch applications", err);
        setLoading(false);
      });
  }, []);

  const updateStatus = async (id: number, newStatus: string) => {
    await fetch(`/api/admission/${id}/status`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });
    // Refresh
    const updated = applications.map(app => app.id === id ? { ...app, status: newStatus } : app);
    setApplications(updated);
    if (selectedApp && selectedApp.id === id) {
      setSelectedApp({ ...selectedApp, status: newStatus });
    }
  };

  const lockApplication = async (id: number) => {
    await fetch(`/api/admission/${id}/lock`, { method: "POST" });
    const updated = applications.map(app => app.id === id ? { ...app, is_locked: true } : app);
    setApplications(updated);
    if (selectedApp && selectedApp.id === id) {
      setSelectedApp({ ...selectedApp, is_locked: true });
    }
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
          <a href="#" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md bg-indigo-50 text-indigo-700">
            <svg className="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            Admissions
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
            Staff & HR
          </a>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-8">
          <h1 className="text-xl font-bold text-gray-900">Admission Management</h1>
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
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <p className="text-sm font-medium text-gray-500 mb-1">Total Applications</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-gray-900">{applications.length}</span>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <p className="text-sm font-medium text-gray-500 mb-1">New Enquiries</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-indigo-600">{applications.filter(a => a.status === 'ENQUIRY').length}</span>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <p className="text-sm font-medium text-gray-500 mb-1">Pending Interview</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-yellow-600">{applications.filter(a => a.status === 'TESTED').length}</span>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <p className="text-sm font-medium text-gray-500 mb-1">Accepted</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-green-600">{applications.filter(a => a.status === 'ACCEPTED').length}</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Applicant ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date Applied</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lock State</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {loading ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-sm text-gray-500">Loading applications...</td>
                    </tr>
                  ) : applications.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-sm text-gray-500">No applications found in the system.</td>
                    </tr>
                  ) : (
                    applications.map((app) => (
                      <tr key={app.id} className="hover:bg-gray-50 transition">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">APP-{app.id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{app.applicant_person_id || 'N/A'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{new Date(app.applied_at).toLocaleDateString()}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-block px-2.5 py-0.5 text-xs font-medium uppercase tracking-wider text-blue-800 bg-blue-100 rounded-full">
                            {app.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {app.is_locked ? (
                            <span className="inline-flex items-center gap-1 text-xs font-medium text-red-600 bg-red-50 px-2 py-0.5 rounded-full border border-red-100">
                              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd"/></svg>
                              Locked
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-xs font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full border border-green-100">
                              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a5 5 0 00-5 5v2a2 2 0 00-2 2v5a2 2 0 002 2h10a2 2 0 002-2v-5a2 2 0 00-2-2H7V7a3 3 0 015.905-.75 1 1 0 001.937-.5A5.002 5.002 0 0010 2z"/></svg>
                              Open
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button 
                            onClick={() => setSelectedApp(app)}
                            className="text-indigo-600 hover:text-indigo-900 bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded-md transition"
                          >
                            Review
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </main>

      {/* Slide-out Review Panel (Modal) */}
      {selectedApp && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/20 backdrop-blur-sm">
          <div className="w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
            
            <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Application Review</h2>
                <p className="text-sm text-gray-500">APP-{selectedApp.id} • Applicant ID: {selectedApp.applicant_person_id}</p>
              </div>
              <button 
                onClick={() => setSelectedApp(null)}
                className="w-8 h-8 flex items-center justify-center rounded-full bg-gray-200 text-gray-600 hover:bg-gray-300"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-8">
              
              {/* Status & Actions */}
              <div className="bg-blue-50 border border-blue-100 p-5 rounded-xl flex justify-between items-center">
                <div>
                  <p className="text-sm font-medium text-blue-800 mb-1">Current Status</p>
                  <select 
                    value={selectedApp.status} 
                    onChange={(e) => updateStatus(selectedApp.id, e.target.value)}
                    disabled={selectedApp.is_locked}
                    className={`text-sm font-bold uppercase tracking-wider rounded-md px-3 py-2 border ${selectedApp.is_locked ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : 'bg-white text-blue-900 border-blue-300'}`}
                  >
                    <option value="ENQUIRY">ENQUIRY</option>
                    <option value="APPLIED">APPLIED</option>
                    <option value="TESTED">TESTED</option>
                    <option value="INTERVIEWED">INTERVIEWED</option>
                    <option value="OFFERED">OFFERED</option>
                    <option value="ACCEPTED">ACCEPTED</option>
                    <option value="REJECTED">REJECTED</option>
                  </select>
                </div>
                <div>
                  {selectedApp.is_locked ? (
                    <span className="text-red-600 font-bold bg-red-50 px-4 py-2 rounded-lg border border-red-200">🔒 Locked by Admin</span>
                  ) : (
                    <button 
                      onClick={() => lockApplication(selectedApp.id)}
                      className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition"
                    >
                      Lock Application
                    </button>
                  )}
                </div>
              </div>

              {/* Profile Details (Mocked from form data) */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 border-b pb-2 mb-4">Student Profile</h3>
                <div className="grid grid-cols-2 gap-y-4 gap-x-8 text-sm">
                  <div>
                    <span className="block text-gray-500 mb-1">Full Name</span>
                    <span className="font-medium text-gray-900">Evan Student</span>
                  </div>
                  <div>
                    <span className="block text-gray-500 mb-1">Date of Birth</span>
                    <span className="font-medium text-gray-900">2012-05-14</span>
                  </div>
                  <div>
                    <span className="block text-gray-500 mb-1">Mother's Name</span>
                    <span className="font-medium text-gray-900">Sarah Student</span>
                  </div>
                  <div>
                    <span className="block text-gray-500 mb-1">Father's Name</span>
                    <span className="font-medium text-gray-900">Michael Student</span>
                  </div>
                  <div>
                    <span className="block text-gray-500 mb-1">Last School</span>
                    <span className="font-medium text-gray-900">Springfield Elementary</span>
                  </div>
                  <div>
                    <span className="block text-gray-500 mb-1">Applying for Class</span>
                    <span className="font-medium text-gray-900">Grade 8</span>
                  </div>
                </div>
              </div>

              {/* Document Review */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 border-b pb-2 mb-4">Uploaded Documents</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg bg-gray-50">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">📷</span>
                      <span className="font-medium text-gray-700 text-sm">Student Photo</span>
                    </div>
                    <button className="text-blue-600 text-sm font-medium hover:underline">View</button>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg bg-gray-50">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">📄</span>
                      <span className="font-medium text-gray-700 text-sm">Birth Certificate</span>
                    </div>
                    <button className="text-blue-600 text-sm font-medium hover:underline">View</button>
                  </div>

                  <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg bg-gray-50">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">🎓</span>
                      <span className="font-medium text-gray-700 text-sm">Transfer Certificate</span>
                    </div>
                    <button className="text-gray-400 text-sm font-medium cursor-not-allowed">Missing</button>
                  </div>

                  <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg bg-gray-50">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">🪪</span>
                      <span className="font-medium text-gray-700 text-sm">Parent NICs</span>
                    </div>
                    <button className="text-blue-600 text-sm font-medium hover:underline">View</button>
                  </div>
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
