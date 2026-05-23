const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface UserProfile {
  id: number;
  name: string;
  email: string;
  institution: string | null;
  research_area: string | null;
  created_at: string;
}

export async function register(data: {
  name: string;
  email: string;
  password: string;
  institution?: string;
  research_area?: string;
}): Promise<UserProfile> {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? "Registration failed");
  }
  return res.json();
}

export async function login(email: string, password: string): Promise<{ access_token: string; refresh_token: string }> {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? "Login failed");
  }
  return res.json();
}

export async function getMe(token: string): Promise<UserProfile> {
  const res = await fetch(`${API_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Unauthorized");
  return res.json();
}
