"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

export default function ResourcePlanning() {
  const [plans, setPlans] = useState<any[]>([]);
  const [simResults, setSimResults] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);

  useEffect(() => {
    fetch("/api/academic/section_plans")
      .then((res) => res.json())
      .then((data) => {
        setPlans(data);
        setLoading(false);
      });
  }, []);

  const runSimulation = async (termId: number, gradeLevel: string) => {
    setSimulating(true);
    try {
      // 1. Run simulation
      const simRes = await fetch(`/api/academic/simulate_run/${termId}/${encodeURIComponent(gradeLevel)}`, { method: "POST" });
      const simData = await simRes.json();
      
      // 2. Fetch results
      const res = await fetch(`/api/academic/run/${simData.plan_run_id}/results`);
      const data = await res.json();
      setSimResults(data);
    } catch (e) {
      console.error(e);
      alert("Error running simulation. Check console.");
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
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
            <svg className="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
            Academic Planning
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
            Staff & HR
          </a>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-8">
          <h1 className="text-xl font-bold text-gray-900">Resource Planner</h1>
          <div className="flex items-center gap-4">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Active Term: Fall 2026
            </span>
            <div className="w-8 h-8 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold text-sm">
              AA
            </div>
          </div>
        </header>

        {/* Scrollable Content */}
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-5xl mx-auto space-y-8">

            {/* Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <p className="text-sm font-medium text-gray-500 mb-1">Total Enrolled</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-gray-900">90</span>
                  <span className="text-sm font-medium text-green-600">Students</span>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <p className="text-sm font-medium text-gray-500 mb-1">Generated Sections</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-gray-900">3</span>
                  <span className="text-sm font-medium text-gray-500">Across all grades</span>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <p className="text-sm font-medium text-gray-500 mb-1">Resource Readiness</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-yellow-600">Action Needed</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column: Input Panel */}
              <div className="lg:col-span-1 space-y-6">
                <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                  <div className="bg-gray-50 px-5 py-4 border-b border-gray-200 flex justify-between items-center">
                    <h2 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Demand (Section Plans)</h2>
                  </div>
                  <div className="p-5 space-y-4">
                    {loading ? (
                      <div className="animate-pulse flex space-x-4">
                        <div className="flex-1 space-y-4 py-1">
                          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                          <div className="h-4 bg-gray-200 rounded"></div>
                        </div>
                      </div>
                    ) : (
                      plans.map((plan) => (
                        <div key={plan.id} className="border border-gray-100 bg-gray-50 rounded-lg p-4">
                          <div className="flex justify-between items-start mb-2">
                            <h3 className="font-bold text-gray-900">{plan.grade_level}</h3>
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded">Est: {plan.estimated_enrollment}</span>
                          </div>
                          <p className="text-xs text-gray-500 mb-4">Max size: {plan.max_section_size} students/section</p>
                          <button 
                            onClick={() => runSimulation(plan.term_id, plan.grade_level)}
                            disabled={simulating}
                            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                          >
                            {simulating ? "Generating..." : "Generate & Match"}
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
              
              {/* Right Column: Output Panel */}
              <div className="lg:col-span-2 space-y-6">
                {!simResults ? (
                  <div className="h-full min-h-[300px] border-2 border-dashed border-gray-200 rounded-xl flex flex-col items-center justify-center text-gray-500 bg-gray-50">
                    <svg className="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                    <p className="text-sm font-medium">Select a Section Plan and run "Generate & Match"</p>
                    <p className="text-xs mt-1">The system will explode the requirement templates against the resource pool.</p>
                  </div>
                ) : (
                  <>
                    {/* Gaps Alert */}
                    {simResults.gaps.length > 0 && (
                      <div className="bg-red-50 border border-red-200 rounded-xl overflow-hidden shadow-sm">
                        <div className="px-5 py-3 border-b border-red-100 bg-red-100/50 flex items-center gap-2">
                          <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"/></svg>
                          <h3 className="font-bold text-red-900 text-sm">Critical Resource Gaps</h3>
                        </div>
                        <div className="p-5">
                          <ul className="space-y-3">
                            {simResults.gaps.map((gap: any, idx: number) => (
                              <li key={idx} className="flex justify-between items-center bg-white border border-red-100 px-4 py-3 rounded-lg">
                                <div>
                                  <p className="text-sm font-bold text-gray-900">{gap.course}</p>
                                  <p className="text-xs text-red-600 font-medium mt-0.5">Short {gap.count_short}x {gap.role_needed.replace('_', ' ')}</p>
                                </div>
                                <button className="text-xs font-bold text-red-700 bg-red-100 hover:bg-red-200 px-3 py-1.5 rounded transition">
                                  Request Hire
                                </button>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}

                    {/* Data Table */}
                    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                      <div className="bg-gray-50 px-5 py-4 border-b border-gray-200">
                        <h2 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Proposed Supply Assignments</h2>
                      </div>
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Section</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Teacher</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {simResults.assignments.map((a: any, idx: number) => (
                            <tr key={idx} className="hover:bg-gray-50 transition">
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{a.section}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{a.course}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                {a.teacher !== "None" ? (
                                  <span className="text-gray-900 font-medium flex items-center gap-2">
                                    <div className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-[10px] font-bold">
                                      {a.teacher.charAt(0)}
                                    </div>
                                    {a.teacher}
                                  </span>
                                ) : (
                                  <span className="text-gray-400 italic">—</span>
                                )}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  a.status === 'PROPOSED' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                }`}>
                                  {a.status}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                )}
              </div>
            </div>

          </div>
        </main>
      </div>
    </div>
  );
}
