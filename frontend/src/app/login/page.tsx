"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, apiFetch, saveSession, AuthSession } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const session = await apiFetch<AuthSession>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      saveSession(session);
      if (session.role === "STUDENT") {
        router.push("/student");
      } else if (session.role === "ADMIN") {
        router.push("/dashboard?role=ADMIN");
      } else {
        router.push("/dashboard");
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="sp-root sp-login-wrap">
      <form className="sp-login-card" onSubmit={handleSubmit}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 24 }}>
          <div className="sp-brand-mark">B</div>
          <div>
            <div className="sp-display" style={{ fontSize: 17 }}>Brainiacs</div>
            <div style={{ fontSize: 11, color: "var(--sp-text-muted)" }}>Sign in to your account</div>
          </div>
        </div>

        {error && <div className="sp-login-error">{error}</div>}

        <div className="sp-login-field">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@brainiacs.edu"
            autoComplete="username"
          />
        </div>
        <div className="sp-login-field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            autoComplete="current-password"
          />
        </div>

        <button className="sp-login-btn" type="submit" disabled={loading}>
          {loading ? "Signing in…" : "Sign in"}
        </button>

        <div className="sp-login-hint">
          Demo student: danyal.ahmed@brainiacs.edu / Passw0rd!
        </div>
      </form>
    </div>
  );
}
