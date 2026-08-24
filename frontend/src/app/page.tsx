import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-white font-[family-name:var(--font-geist-sans)]">
      {/* Navigation */}
      <nav className="border-b border-gray-100 px-8 py-4 flex justify-between items-center bg-white sticky top-0 z-10">
        <div className="text-2xl font-black text-blue-900 tracking-tight">BRAINIACS.</div>
        <div className="flex gap-6 items-center font-medium text-sm">
          <Link href="#" className="text-gray-600 hover:text-blue-600">Academics</Link>
          <Link href="#" className="text-gray-600 hover:text-blue-600">Campus Life</Link>
          <Link href="#" className="text-gray-600 hover:text-blue-600">About Us</Link>
          <Link href="/login" className="px-5 py-2 bg-gray-100 text-gray-900 rounded-full hover:bg-gray-200 transition">
            Portal Login
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-5xl mx-auto px-8 py-20 text-center">
        <h1 className="text-6xl font-extrabold text-gray-900 mb-6 tracking-tight leading-tight">
          Empowering the next <br/><span className="text-blue-600">generation of thinkers.</span>
        </h1>
        <p className="text-xl text-gray-500 mb-12 max-w-2xl mx-auto leading-relaxed">
          At Brainiacs, we believe in a holistic approach to education. We combine rigorous academics, state-of-the-art facilities, and a supportive community to help every student reach their full potential.
        </p>
        
        {/* Public Calls to Action */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
          
          {/* Admission Tile */}
          <div className="bg-blue-50 p-8 rounded-3xl border border-blue-100 text-left hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mb-6 text-xl">🎓</div>
            <h2 className="text-2xl font-bold text-blue-900 mb-2">Student Admissions</h2>
            <p className="text-blue-700 mb-8 font-light">
              Join Brainiacs — Shape Your Future. Applications for Fall 2026 are now open.
            </p>
            <Link 
              href="/register"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Apply for Admission
            </Link>
          </div>

          {/* Join Our Team Tile */}
          <div className="bg-gray-50 p-8 rounded-3xl border border-gray-200 text-left hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-gray-900 text-white rounded-full flex items-center justify-center mb-6 text-xl">💼</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Join Our Team</h2>
            <p className="text-gray-600 mb-8 font-light">
              We are always looking for passionate educators and dedicated staff to join our growing campus.
            </p>
            <Link 
              href="/register?type=staff"
              className="inline-block px-6 py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors"
            >
              View Open Roles
            </Link>
          </div>

        </div>
      </main>
    </div>
  );
}
