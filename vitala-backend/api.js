// Thin wrapper around fetch that targets the FastAPI backend and attaches the
// JWT. The token is kept in localStorage so a page refresh stays logged in.

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

let token = localStorage.getItem("vitala_token") || null;

export function setToken(t) {
  token = t;
  if (t) localStorage.setItem("vitala_token", t);
  else localStorage.removeItem("vitala_token");
}

export function getToken() {
  return token;
}

export async function api(path, { method = "GET", body } = {}) {
  let res;
  try {
    res = await fetch(API + path, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    // Network-level failure — almost always "backend isn't running".
    const e = new Error(
      "Can't reach the server. Make sure the backend is running (docker compose up)."
    );
    e.status = 0;
    throw e;
  }

  let data = null;
  try {
    data = await res.json();
  } catch {
    /* empty / non-JSON body */
  }

  if (!res.ok) {
    let detail = data?.detail;
    if (Array.isArray(detail)) detail = detail.map((d) => d.msg || "Invalid input").join(", ");
    const e = new Error(typeof detail === "string" ? detail : "Something went wrong");
    e.status = res.status;
    throw e;
  }
  return data;
}
