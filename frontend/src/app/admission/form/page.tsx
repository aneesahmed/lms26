"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function AdmissionForm() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      // In a complete implementation, this form data (including files) 
      // would be sent as a multipart/form-data request.
      // For this prototype, we'll create the base application first.
      
      const res = await fetch("/api/admission/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          target_org_id: 1,
          applicant_person_id: 4, 
          status: "APPLIED"
        }),
      });
      
      if (res.ok) {
        // Redirect back to dashboard to see the progress update
        router.push("/dashboard?role=APPLICANT");
      } else {
        alert("Failed to submit application");
        setSubmitting(false);
      }
    } catch (err) {
      console.error(err);
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-[family-name:var(--font-geist-sans)]">
      <div className="max-w-4xl mx-auto">
        
        <div className="flex items-center gap-4 mb-8">
          <Link href="/dashboard?role=APPLICANT" className="w-10 h-10 flex items-center justify-center bg-white border border-gray-200 rounded-full text-gray-500 hover:bg-gray-100 transition">
            ←
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Admission Application</h1>
            <p className="text-gray-500">Fall 2026 Enrollment</p>
          </div>
        </div>

        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-6 border-b pb-4">Applicant Profile & Documents</h2>
          
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Personal Details Section */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Personal Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                  <input type="text" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Date of Birth</label>
                  <input type="date" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Mother's Name</label>
                  <input type="text" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Father's Name</label>
                  <input type="text" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
              </div>
            </div>

            {/* Academic Details Section */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Academic Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Last School Attended</label>
                  <input type="text" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Class Applying For</label>
                  <input type="text" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="e.g. Grade 8" />
                </div>
              </div>
            </div>

            {/* Document Uploads Section */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Document Uploads</h3>
              <p className="text-sm text-gray-500 mb-4">You can upload pictures or PDFs of the required documents below.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Student Photo</label>
                  <input type="file" className="text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
                </div>
                
                <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Birth Certificate</label>
                  <input type="file" className="text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
                </div>

                <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Transfer Certificate</label>
                  <input type="file" className="text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
                </div>

                <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Mother & Father NICs</label>
                  <input type="file" className="text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" multiple />
                </div>
              </div>
            </div>
            
            <div className="flex justify-end pt-6 border-t border-gray-200">
              <button 
                type="submit" 
                disabled={submitting}
                className="px-8 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition"
              >
                {submitting ? "Submitting..." : "Submit Application"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
