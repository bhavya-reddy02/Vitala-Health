import React, { useState, useEffect, useMemo, useCallback, useRef } from "react";
import { api, setToken, getToken } from "./api.js";

/* =====================================================================================
   VITALA — frontend wired to the FastAPI backend (PostgreSQL + Redis).
   Every action (signup, profile, quest completion) is an API call; the server is
   the source of truth for XP, streaks, badges and the leaderboard.
   ===================================================================================== */

const FOCUS_AREAS = [
  { id: "hydration",   label: "Hydration",   emoji: "💧" },
  { id: "movement",    label: "Movement",    emoji: "🏃" },
  { id: "mindfulness", label: "Mindfulness", emoji: "🧘" },
  { id: "nutrition",   label: "Nutrition",   emoji: "🥗" },
  { id: "sleep",       label: "Sleep",       emoji: "😴" },
  { id: "social",      label: "Connection",  emoji: "🤝" },
];
const GOALS = [
  { id: "active",   label: "Stay active",    emoji: "⚡" },
  { id: "weight",   label: "Manage weight",  emoji: "⚖️" },
  { id: "strength", label: "Build strength", emoji: "💪" },
  { id: "sleep",    label: "Sleep better",   emoji: "🌙" },
  { id: "stress",   label: "Lower stress",   emoji: "🌿" },
];
const ACTIVITY = [
  { id: "low",  label: "Lightly active" },
  { id: "mid",  label: "Moderately active" },
  { id: "high", label: "Very active" },
];
const TIER = {
  bronze: ["#C98A5E", "#8A5A38"], silver: ["#CFD6E6", "#8A93AB"],
  gold: ["#FFD66B", "#E89A1C"],   plat: ["#7BE8C9", "#34A0FF"],
};

/* ------------------------------------------------------------------ SVG pieces */
function Heartbeat({ c = "#062b1f" }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <path d="M12 21s-7-4.6-9.2-9.2C1.2 8.4 3 5 6.3 5c2 0 3.3 1.2 5.7 4.2C14.4 6.2 15.7 5 17.7 5 21 5 22.8 8.4 21.2 11.8 19 16.4 12 21 12 21Z" fill={c} />
    </svg>
  );
}
const ICONS = {
  home:  <path d="M3 11.5 12 4l9 7.5M5 10v9h5v-5h4v5h5v-9" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" fill="none" />,
  quest: <path d="M5 4h11l3 3v13H5zM9 9h6M9 13h6M9 17h3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" fill="none" />,
  badge: <path d="M12 3l2.2 4.5 5 .7-3.6 3.5.9 5-4.5-2.4L7.5 19.7l.9-5L4.8 8.2l5-.7z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" fill="none" />,
  board: <g stroke="currentColor" strokeWidth="1.8" fill="none" strokeLinecap="round"><path d="M6 20V10M12 20V4M18 20v-7" /></g>,
  chat:  <path d="M4 5h16v11H9l-4 3v-3H4z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" fill="none" />,
  learn: <path d="M4 5.5A2 2 0 0 1 6 4h5v15H6a2 2 0 0 0-2 1.5zM20 5.5A2 2 0 0 0 18 4h-5v15h5a2 2 0 0 1 2 1.5z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" fill="none" />,
  user:  <g stroke="currentColor" strokeWidth="1.8" fill="none"><circle cx="12" cy="8" r="4" /><path d="M5 20a7 7 0 0 1 14 0" strokeLinecap="round" /></g>,
};

function VitalityRing({ level, into, need }) {
  const R = 58, C = 2 * Math.PI * R;
  const pct = need ? Math.min(into / need, 1) : 0;
  const off = C * (1 - pct);
  return (
    <div style={{ position: "relative", width: 148, height: 148, flex: "0 0 148px" }}>
      <svg width="148" height="148" viewBox="0 0 148 148" style={{ animation: "spinpulse 4s ease-in-out infinite" }}>
        <defs><linearGradient id="vring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#34E0A1" /><stop offset="1" stopColor="#5BA8FF" /></linearGradient></defs>
        <circle cx="74" cy="74" r={R} stroke="var(--ink-4)" strokeWidth="11" fill="none" />
        <circle cx="74" cy="74" r={R} stroke="url(#vring)" strokeWidth="11" fill="none" strokeLinecap="round"
          strokeDasharray={C} strokeDashoffset={off} transform="rotate(-90 74 74)"
          style={{ transition: "stroke-dashoffset .8s cubic-bezier(.4,0,.2,1)" }} />
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", textAlign: "center" }}>
        <div>
          <div style={{ fontSize: 11, letterSpacing: ".14em", color: "var(--faint)", fontWeight: 600 }}>LEVEL</div>
          <div className="num" style={{ fontSize: 44, fontWeight: 700, lineHeight: 1 }}>{level}</div>
        </div>
      </div>
    </div>
  );
}
function FlameMark({ size = 40 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" style={{ animation: "flick 1.6s ease-in-out infinite", transformOrigin: "50% 100%" }}>
      <defs><linearGradient id="fl" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stopColor="#FF3D6E" /><stop offset=".5" stopColor="#FF6B4A" /><stop offset="1" stopColor="#FFC24B" /></linearGradient></defs>
      <path d="M12 2c1 3-1 4-2 6-1.2 2.4 0 4 0 4s-2-.4-2.4-2.4C5.4 12 4 14 4 16.2 4 20 7.6 22 12 22s8-2 8-5.8c0-3.6-2.6-5.4-3.6-7.6C15.2 6 14 5 14 3c-.8.8-1.6 1.2-2 2-.6-1.2-.4-2.2 0-3z" fill="url(#fl)" />
    </svg>
  );
}
function BadgeSVG({ tier, emoji, size = 58, locked }) {
  const [a, b] = TIER[tier] || TIER.bronze;
  const id = "bg" + tier + (locked ? "l" : "") + Math.round(size);
  return (
    <svg width={size} height={size} viewBox="0 0 64 64">
      <defs><linearGradient id={id} x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor={a} /><stop offset="1" stopColor={b} /></linearGradient></defs>
      <path d="M32 3l25 14v18c0 16-12 23-25 26C19 58 7 51 7 35V17z" fill={`url(#${id})`} opacity={locked ? 0.5 : 1} />
      <path d="M32 3l25 14v18c0 16-12 23-25 26C19 58 7 51 7 35V17z" fill="none" stroke="rgba(255,255,255,.35)" strokeWidth="1.2" />
      <text x="32" y="40" textAnchor="middle" fontSize="26" style={{ filter: locked ? "grayscale(1)" : "none" }}>{locked ? "🔒" : emoji}</text>
    </svg>
  );
}
function Stat({ icon, value, label, bg, fg }) {
  return (
    <div className="stat">
      <div className="ic" style={{ background: bg, color: fg }}>{icon}</div>
      <div className="num v">{value}</div>
      <div className="l">{label}</div>
    </div>
  );
}
function QuestCard({ q, busy, onToggle }) {
  return (
    <div className={"quest" + (q.done ? " done" : "")}>
      <div className="qic" style={{ background: "var(--ink-3)", border: "1px solid var(--line)" }}>{q.emoji}</div>
      <div className="qbody">
        <div className="qt">{q.t}</div>
        <div className="qd">{q.d}</div>
      </div>
      <span className="qxp">+{q.xp} XP</span>
      <button className={"qcheck" + (q.done ? " on" : "")} disabled={q.done || busy} onClick={onToggle} aria-label="Complete quest">
        {q.done
          ? <svg width="16" height="16" viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 6.5" stroke="currentColor" strokeWidth="3" fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
          : busy ? <span className="spin" style={{ width: 15, height: 15 }} /> : null}
      </button>
    </div>
  );
}
function Confetti() {
  const cols = ["#0BA572", "#D69412", "#F2542D", "#3B8EF0", "#F0457E", "#8B6BF5"];
  return (
    <div className="confetti">
      {Array.from({ length: 26 }).map((_, i) => (
        <span key={i} style={{
          left: Math.random() * 100 + "%", background: cols[i % cols.length],
          animationDuration: 1.4 + Math.random() * 1.2 + "s", animationDelay: Math.random() * 0.4 + "s",
          transform: `rotate(${Math.random() * 360}deg)`,
        }} />
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ auth */
function Auth({ onDone }) {
  const [mode, setMode] = useState("login");
  const [f, setF] = useState({ username: "", email: "", password: "" });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF((s) => ({ ...s, [k]: e.target.value }));

  async function submit() {
    setErr("");
    if (!f.username.trim()) return setErr("Pick a username to continue.");
    if (f.password.length < 4) return setErr("Use a password of at least 4 characters.");
    if (mode === "signup" && !/.+@.+\..+/.test(f.email)) return setErr("Enter a valid email address.");
    setBusy(true);
    try {
      const path = mode === "signup" ? "/auth/signup" : "/auth/login";
      const body = mode === "signup"
        ? { username: f.username.trim(), email: f.email.trim(), password: f.password }
        : { username: f.username.trim(), password: f.password };
      const res = await api(path, { method: "POST", body });
      setToken(res.access_token);
      await onDone();
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="authwrap">
      <div className="authcard">
        <div className="brandbig"><div className="mark"><Heartbeat /></div><div className="wm">Vitala</div></div>
        <p style={{ textAlign: "center", color: "var(--muted)", margin: "0 0 26px", fontSize: 14 }}>Level up your health.</p>
        <div className="card pad">
          <div style={{ display: "flex", gap: 8, background: "var(--ink-3)", padding: 5, borderRadius: 13, marginBottom: 22 }}>
            {["login", "signup"].map((m) => (
              <button key={m} onClick={() => { setMode(m); setErr(""); }}
                style={{ flex: 1, padding: "10px", borderRadius: 9, fontWeight: 600, fontSize: 13.5,
                  background: mode === m ? "var(--ink-2)" : "transparent", color: mode === m ? "var(--txt)" : "var(--muted)",
                  boxShadow: mode === m ? "0 2px 8px -3px rgba(28,24,50,.22)" : "none", transition: ".15s" }}>
                {m === "login" ? "Log in" : "Sign up"}
              </button>
            ))}
          </div>
          <div className="field"><label>Username</label>
            <input value={f.username} onChange={set("username")} placeholder="e.g. tharun" autoCapitalize="off" />
          </div>
          {mode === "signup" && (
            <div className="field"><label>Email</label>
              <input value={f.email} onChange={set("email")} placeholder="you@email.com" type="email" />
            </div>
          )}
          <div className="field"><label>Password</label>
            <input value={f.password} onChange={set("password")} placeholder="••••••••" type="password" onKeyDown={(e) => e.key === "Enter" && submit()} />
          </div>
          {err && <div className="err">{err}</div>}
          <button className="btn btn-primary" style={{ width: "100%" }} onClick={submit} disabled={busy}>
            {busy ? <span className="spin" /> : mode === "login" ? "Log in" : "Create account"}
          </button>
        </div>
        <p style={{ textAlign: "center", fontSize: 11.5, color: "var(--faint)", marginTop: 18, lineHeight: 1.6 }}>
          Connected to your live API · data is stored in PostgreSQL & Redis.
        </p>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ onboarding */
function Onboarding({ onDone }) {
  const [step, setStep] = useState(0);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [p, setP] = useState({ name: "", age: "", sex: "", height_cm: "", weight_kg: "", goal: "active", activity: "mid", focus: ["hydration", "movement"] });
  const set = (k, v) => setP((s) => ({ ...s, [k]: v }));
  const toggleFocus = (id) => setP((s) => ({ ...s, focus: s.focus.includes(id) ? s.focus.filter((x) => x !== id) : [...s.focus, id] }));

  const bmi = useMemo(() => {
    const h = parseFloat(p.height_cm) / 100, w = parseFloat(p.weight_kg);
    if (!h || !w) return null; return +(w / (h * h)).toFixed(1);
  }, [p.height_cm, p.weight_kg]);
  const band = bmi == null ? null : bmi < 18.5 ? ["Underweight", "var(--azure)"] : bmi < 25 ? ["Healthy range", "var(--vital)"] : bmi < 30 ? ["Overweight", "var(--gold)"] : ["Higher range", "var(--flame)"];

  const canNext = step === 0 ? (p.name.trim() && p.age && p.height_cm && p.weight_kg) : step === 1 ? p.goal : p.focus.length > 0;

  async function finish() {
    setBusy(true); setErr("");
    try {
      await api("/profile", { method: "PUT", body: {
        name: p.name.trim(), age: p.age ? parseInt(p.age) : null, sex: p.sex,
        height_cm: p.height_cm ? parseFloat(p.height_cm) : null,
        weight_kg: p.weight_kg ? parseFloat(p.weight_kg) : null,
        goal: p.goal, activity: p.activity, focus: p.focus,
      } });
      await onDone();
    } catch (e) {
      setErr(e.message); setBusy(false);
    }
  }

  return (
    <div className="authwrap">
      <div className="authcard" style={{ maxWidth: 520 }}>
        <div style={{ display: "flex", gap: 7, marginBottom: 22, justifyContent: "center" }}>
          {[0, 1, 2].map((i) => <div key={i} style={{ width: i === step ? 28 : 8, height: 8, borderRadius: 99, background: i <= step ? "var(--vital)" : "var(--ink-4)", transition: ".3s" }} />)}
        </div>
        <div className="card pad">
          {step === 0 && (<>
            <p className="eyebrow">Your health profile · 1 of 3</p>
            <h2 className="display" style={{ fontSize: 22, margin: "0 0 4px" }}>The basics</h2>
            <p style={{ color: "var(--muted)", fontSize: 13.5, margin: "0 0 22px" }}>These personalise your quests and are saved to your account.</p>
            <div className="field"><label>Preferred name</label><input value={p.name} onChange={(e) => set("name", e.target.value)} placeholder="What should we call you?" /></div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
              <div className="field"><label>Age</label><input type="number" value={p.age} onChange={(e) => set("age", e.target.value)} placeholder="years" /></div>
              <div className="field"><label>Sex</label>
                <select value={p.sex} onChange={(e) => set("sex", e.target.value)}>
                  <option value="">Prefer not to say</option><option>Female</option><option>Male</option><option>Other</option>
                </select>
              </div>
              <div className="field"><label>Height (cm)</label><input type="number" value={p.height_cm} onChange={(e) => set("height_cm", e.target.value)} placeholder="cm" /></div>
              <div className="field"><label>Weight (kg)</label><input type="number" value={p.weight_kg} onChange={(e) => set("weight_kg", e.target.value)} placeholder="kg" /></div>
            </div>
            {bmi && (
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", background: "var(--ink)", border: "1px solid var(--line)", borderRadius: 12, padding: "12px 15px", marginTop: 4 }}>
                <span style={{ fontSize: 13, color: "var(--muted)" }}>Your BMI</span>
                <span style={{ display: "flex", alignItems: "center", gap: 10 }}><b className="num" style={{ fontSize: 18 }}>{bmi}</b><span style={{ fontSize: 12, fontWeight: 600, color: band[1] }}>{band[0]}</span></span>
              </div>
            )}
          </>)}
          {step === 1 && (<>
            <p className="eyebrow">Your health profile · 2 of 3</p>
            <h2 className="display" style={{ fontSize: 22, margin: "0 0 4px" }}>What's your main goal?</h2>
            <p style={{ color: "var(--muted)", fontSize: 13.5, margin: "0 0 22px" }}>Pick the one that matters most right now.</p>
            <div style={{ display: "grid", gap: 10 }}>
              {GOALS.map((g) => (
                <button key={g.id} onClick={() => set("goal", g.id)} className="chip"
                  style={{ justifyContent: "flex-start", padding: "14px 16px", ...(p.goal === g.id ? { background: "rgba(11,165,114,.12)", borderColor: "var(--vital)", color: "var(--vital)" } : {}) }}>
                  <span style={{ fontSize: 20 }}>{g.emoji}</span><span style={{ fontWeight: 600 }}>{g.label}</span>
                </button>
              ))}
            </div>
            <div className="field" style={{ marginTop: 18 }}>
              <label>How active are you usually?</label>
              <select value={p.activity} onChange={(e) => set("activity", e.target.value)}>
                {ACTIVITY.map((a) => <option key={a.id} value={a.id}>{a.label}</option>)}
              </select>
            </div>
          </>)}
          {step === 2 && (<>
            <p className="eyebrow">Your health profile · 3 of 3</p>
            <h2 className="display" style={{ fontSize: 22, margin: "0 0 4px" }}>Choose your focus areas</h2>
            <p style={{ color: "var(--muted)", fontSize: 13.5, margin: "0 0 22px" }}>Your daily quests lean toward what you pick. Choose two or three.</p>
            <div className="chips">
              {FOCUS_AREAS.map((fa) => (
                <button key={fa.id} className={"chip" + (p.focus.includes(fa.id) ? " on" : "")} onClick={() => toggleFocus(fa.id)}>
                  <span style={{ fontSize: 17 }}>{fa.emoji}</span>{fa.label}
                </button>
              ))}
            </div>
          </>)}
          {err && <div className="err" style={{ marginTop: 16 }}>{err}</div>}
          <div style={{ display: "flex", gap: 12, marginTop: 26 }}>
            {step > 0 && <button className="btn btn-ghost" onClick={() => setStep((s) => s - 1)}>Back</button>}
            <button className="btn btn-primary" style={{ flex: 1 }} disabled={!canNext || busy}
              onClick={() => { if (step < 2) setStep((s) => s + 1); else finish(); }}>
              {busy ? <span className="spin" /> : step < 2 ? "Continue" : "Start my journey"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ app screens */
function Dashboard({ s, busyId, onComplete, go }) {
  const doneCount = s.quests.filter((q) => q.done).length;
  const allDone = doneCount === s.quests.length && s.quests.length > 0;
  const recent = s.badges.filter((b) => b.unlocked).slice(-4).reverse();
  const greet = (() => { const h = new Date().getHours(); return h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening"; })();

  return (<>
    <div className="topbar">
      <div className="hello">
        <h1>{greet}, {s.profile?.name || s.username} 👋</h1>
        <p>{new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" })}</p>
      </div>
      <div style={{ display: "flex", gap: 10 }}>
        <span className="pill"><FlameMark size={18} /><b className="num">{s.streak}</b> day streak</span>
        <span className="pill" style={{ color: "var(--gold)" }}>⚡ <b className="num">{s.xp}</b> XP</span>
      </div>
    </div>
    <div className="grid" style={{ gridTemplateColumns: "minmax(280px,1.1fr) 1fr" }}>
      <div className="card pad" style={{ display: "flex", gap: 22, alignItems: "center" }}>
        <VitalityRing level={s.level} into={s.xpInto} need={s.xpNeed} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <p className="eyebrow" style={{ margin: "0 0 6px" }}>Vitality</p>
          <div style={{ fontSize: 14, color: "var(--muted)", marginBottom: 12 }}>
            <b className="num" style={{ color: "var(--gold)", fontSize: 16 }}>{s.xpNeed - s.xpInto}</b> XP to level {s.level + 1}
          </div>
          <div className="xpbar"><i style={{ width: (s.xpInto / s.xpNeed * 100) + "%" }} /></div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 7, fontSize: 11.5, color: "var(--faint)" }}>
            <span className="num">{s.xpInto} / {s.xpNeed}</span><span>this level</span>
          </div>
        </div>
      </div>
      <div className="card pad" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
        <p className="eyebrow" style={{ margin: 0 }}>Streak</p>
        <div style={{ display: "flex", alignItems: "center", gap: 16, margin: "8px 0" }}>
          <FlameMark size={52} />
          <div><div className="num" style={{ fontSize: 40, fontWeight: 700, lineHeight: 1 }}>{s.streak}</div>
            <div style={{ fontSize: 12.5, color: "var(--muted)" }}>day{s.streak === 1 ? "" : "s"} in a row</div></div>
        </div>
        <div style={{ fontSize: 12.5, color: "var(--faint)" }}>
          {s.streak === 0 ? "Finish a quest today to light the flame." : allDone ? "🔥 Today's locked in. Beautiful work." : "Complete one quest today to keep it alive."} · Best: <b className="num" style={{ color: "var(--muted)" }}>{s.longestStreak}</b>
        </div>
      </div>
    </div>
    <div className="grid" style={{ gridTemplateColumns: "repeat(4,1fr)", marginTop: 18 }}>
      <Stat icon="⚡" value={s.xp} label="Total XP" bg="rgba(214,148,18,.14)" fg="var(--gold)" />
      <Stat icon="✅" value={s.totalQuests} label="Quests done" bg="rgba(11,165,114,.14)" fg="var(--vital)" />
      <Stat icon="🏅" value={s.badgesEarned.length} label="Badges" bg="rgba(139,107,245,.16)" fg="var(--violet)" />
      <Stat icon="💎" value={s.perfectDays} label="Perfect days" bg="rgba(59,142,240,.14)" fg="var(--azure)" />
    </div>
    <div className="card pad" style={{ marginTop: 18 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <p className="eyebrow" style={{ margin: 0 }}>Today's quests</p>
        <span style={{ fontSize: 12.5, color: "var(--muted)" }}><b className="num" style={{ color: allDone ? "var(--vital)" : "var(--txt)" }}>{doneCount}</b> / {s.quests.length} complete</span>
      </div>
      <div style={{ display: "grid", gap: 10 }}>
        {s.quests.map((q) => <QuestCard key={q.id} q={q} busy={busyId === q.id} onToggle={(e) => onComplete(q, e)} />)}
      </div>
      {allDone && (
        <div style={{ marginTop: 16, padding: "14px 16px", borderRadius: 12, textAlign: "center", background: "rgba(11,165,114,.10)", border: "1px solid rgba(11,165,114,.3)", fontSize: 13.5, color: "var(--vital)", fontWeight: 600 }}>
          💎 Flawless day — every quest cleared. New quests arrive tomorrow.
        </div>
      )}
    </div>
    <div className="card pad" style={{ marginTop: 18 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <p className="eyebrow" style={{ margin: 0 }}>Recent badges</p>
        <button onClick={() => go("badges")} style={{ fontSize: 12.5, color: "var(--vital)", fontWeight: 600 }}>View all →</button>
      </div>
      {recent.length === 0
        ? <p style={{ color: "var(--muted)", fontSize: 13.5, margin: 0 }}>No badges yet — complete a quest to earn your first. ✨</p>
        : <div style={{ display: "flex", gap: 18, flexWrap: "wrap" }}>
            {recent.map((b) => (
              <div key={b.id} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, width: 96, textAlign: "center" }}>
                <BadgeSVG tier={b.tier} emoji={b.emoji} size={52} /><span style={{ fontSize: 12, fontWeight: 600 }}>{b.name}</span>
              </div>
            ))}
          </div>}
    </div>

    {s.learning && (
      <div className="card pad" style={{ marginTop: 18, display: "flex", alignItems: "center", gap: 18, flexWrap: "wrap" }}>
        <div style={{ width: 46, height: 46, borderRadius: 13, display: "grid", placeItems: "center", fontSize: 24, background: "rgba(59,142,240,.12)" }}>🧠</div>
        <div style={{ flex: 1, minWidth: 180 }}>
          <div style={{ fontWeight: 600, fontSize: 14.5, marginBottom: 8 }}>Health literacy · {s.learning.completed}/{s.learning.total} modules</div>
          <div className="lprog"><i style={{ width: (s.learning.total ? s.learning.completed / s.learning.total * 100 : 0) + "%" }} /></div>
        </div>
        <button className="btn btn-primary" onClick={() => go("learn")}>{s.learning.completed === 0 ? "Start learning" : "Keep learning"}</button>
      </div>
    )}
  </>);
}

function QuestsPage({ s, busyId, onComplete }) {
  const doneCount = s.quests.filter((q) => q.done).length;
  const totalXp = s.quests.reduce((a, q) => a + q.xp, 0);
  const earned = s.quests.filter((q) => q.done).reduce((a, q) => a + q.xp, 0);
  return (<>
    <div className="topbar">
      <div className="hello"><h1>Daily quests</h1><p>Fresh quests every day, picked around your focus areas.</p></div>
      <span className="pill" style={{ color: "var(--gold)" }}>⚡ <b className="num">{earned}</b> / {totalXp} XP today</span>
    </div>
    <div className="card pad" style={{ marginBottom: 18 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
        <span style={{ fontSize: 13.5, fontWeight: 600 }}>Today's progress</span>
        <span style={{ fontSize: 12.5, color: "var(--muted)" }}><b className="num">{doneCount}</b>/{s.quests.length}</span>
      </div>
      <div className="xpbar"><i style={{ width: (s.quests.length ? doneCount / s.quests.length * 100 : 0) + "%", background: "linear-gradient(90deg,var(--vital),var(--azure))" }} /></div>
    </div>
    <div style={{ display: "grid", gap: 11 }}>
      {s.quests.map((q) => <div key={q.id} className="card" style={{ padding: 0, overflow: "hidden" }}><QuestCard q={q} busy={busyId === q.id} onToggle={(e) => onComplete(q, e)} /></div>)}
    </div>
    <p style={{ textAlign: "center", color: "var(--faint)", fontSize: 12.5, marginTop: 24 }}>🌙 New quests unlock at midnight. Keep your streak alive by clearing at least one each day.</p>
  </>);
}

function BadgesPage({ s }) {
  const earned = s.badges.filter((b) => b.unlocked).length;
  return (<>
    <div className="topbar">
      <div className="hello"><h1>Achievements</h1><p>Milestones you unlock as healthy habits stack up.</p></div>
      <span className="pill"><b className="num" style={{ color: "var(--vital)" }}>{earned}</b> / {s.badges.length} unlocked</span>
    </div>
    <div className="badgegrid">
      {s.badges.map((b) => (
        <div key={b.id} className={"badgecell" + (b.unlocked ? "" : " locked")}>
          <BadgeSVG tier={b.tier} emoji={b.emoji} size={62} locked={!b.unlocked} />
          <div className="bn">{b.name}</div>
          <div className="bd">{b.desc}</div>
          {b.unlocked
            ? <span style={{ fontSize: 11, color: "var(--vital)", fontWeight: 600 }}>✓ Unlocked</span>
            : <>
                <div className="bprog"><i style={{ width: Math.min(b.current / b.target * 100, 100) + "%", background: `linear-gradient(90deg,${TIER[b.tier][0]},${TIER[b.tier][1]})` }} /></div>
                <span className="num" style={{ fontSize: 11, color: "var(--faint)" }}>{b.current} / {b.target}</span>
              </>}
        </div>
      ))}
    </div>
  </>);
}

function LeaderboardPage({ meName }) {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");
  useEffect(() => {
    let ok = true;
    api("/leaderboard?limit=20").then((d) => ok && setData(d)).catch((e) => ok && setErr(e.message));
    return () => { ok = false; };
  }, []);
  return (<>
    <div className="topbar"><div className="hello"><h1>Leaderboard</h1><p>Ranked by total XP — powered by Redis.</p></div></div>
    {err && <div className="card pad"><p style={{ color: "var(--flame-2)", margin: 0 }}>{err}</p></div>}
    {!data && !err && <div className="card pad" style={{ textAlign: "center" }}><span className="spin" /></div>}
    {data && (
      <div style={{ display: "grid", gap: 9 }}>
        {data.top.length === 0 && <div className="card pad"><p style={{ color: "var(--muted)", margin: 0 }}>No players ranked yet. Complete a quest to get on the board!</p></div>}
        {data.top.map((r) => (
          <div key={r.username} className={"lbrow" + (r.username === meName ? " me" : "")}>
            <div className={"lbrank" + (r.rank <= 3 ? " top" + r.rank : "")}>{r.rank}</div>
            <div className="lbname">{r.username}{r.username === meName ? "  (you)" : ""}</div>
            <div className="lbxp">⚡ {r.xp}</div>
          </div>
        ))}
        {data.me && data.me.rank && !data.top.some((r) => r.username === meName) && (
          <>
            <div style={{ textAlign: "center", color: "var(--faint)", fontSize: 12 }}>· · ·</div>
            <div className="lbrow me">
              <div className="lbrank">{data.me.rank}</div>
              <div className="lbname">{data.me.username}  (you)</div>
              <div className="lbxp">⚡ {data.me.xp}</div>
            </div>
          </>
        )}
      </div>
    )}
  </>);
}

function ProfilePage({ s, onLogout }) {
  const p = s.profile || {};
  const goal = GOALS.find((g) => g.id === p.goal);
  const rows = [
    ["Name", p.name || "—"], ["Age", p.age ? p.age + " yrs" : "—"],
    ["Height", p.heightCm ? p.heightCm + " cm" : "—"], ["Weight", p.weightKg ? p.weightKg + " kg" : "—"],
    ["BMI", p.bmi ?? "—"], ["Main goal", goal ? `${goal.emoji} ${goal.label}` : "—"],
  ];
  return (<>
    <div className="topbar"><div className="hello"><h1>Your profile</h1><p>Everything Vitala uses to tailor your journey.</p></div></div>
    <div className="grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
      <div className="card pad">
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
          <div style={{ width: 64, height: 64, borderRadius: 18, display: "grid", placeItems: "center", fontSize: 28, background: "linear-gradient(150deg,var(--vital),var(--azure))", color: "#062b1f", fontWeight: 700 }}>
            {(p.name || s.username).charAt(0).toUpperCase()}
          </div>
          <div><div className="display" style={{ fontSize: 20, fontWeight: 600 }}>{p.name || s.username}</div>
            <div style={{ fontSize: 13, color: "var(--muted)" }}>Level {s.level} · {s.xp} XP</div></div>
        </div>
        {rows.map(([k, v]) => (
          <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "11px 0", borderBottom: "1px solid var(--line)", fontSize: 13.5 }}>
            <span style={{ color: "var(--muted)" }}>{k}</span><span style={{ fontWeight: 600 }} className={typeof v === "number" ? "num" : ""}>{v}</span>
          </div>
        ))}
      </div>
      <div style={{ display: "grid", gap: 18, alignContent: "start" }}>
        <div className="card pad">
          <p className="eyebrow">Focus areas</p>
          <div className="chips">
            {(p.focus || []).map((id) => { const fa = FOCUS_AREAS.find((x) => x.id === id); return fa ? <span key={id} className="chip on"><span style={{ fontSize: 16 }}>{fa.emoji}</span>{fa.label}</span> : null; })}
          </div>
        </div>
        <div className="card pad">
          <p className="eyebrow">Lifetime stats</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
            <Stat icon="✅" value={s.totalQuests} label="Quests" bg="rgba(11,165,114,.14)" fg="var(--vital)" />
            <Stat icon="🔥" value={s.longestStreak} label="Best streak" bg="rgba(242,84,45,.14)" fg="var(--flame)" />
          </div>
        </div>
        <div className="card pad">
          <p className="eyebrow">Account</p>
          <button className="btn btn-ghost" style={{ width: "100%" }} onClick={onLogout}>Log out</button>
        </div>
      </div>
    </div>
  </>);
}

/* ------------------------------------------------------------------ assistant */
const SUGGESTIONS = [
  "How much water should I drink?",
  "Tips to sleep better tonight",
  "How do streaks work in Vitala?",
  "Simple ways to lower stress",
];

function AssistantPage({ userName }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [literacy, setLiteracy] = useState("standard");
  const [sending, setSending] = useState(false);
  const [configured, setConfigured] = useState(true);
  const [disclaimer, setDisclaimer] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    api("/chat/history").then((d) => {
      setMessages(d.messages || []);
      setDisclaimer(d.disclaimer || "");
      setConfigured(d.configured);
    }).catch(() => {});
  }, []);
  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, sending]);

  async function send(text) {
    const q = (text ?? input).trim();
    if (!q || sending) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: q, citations: [] }]);
    setSending(true);
    try {
      const res = await api("/chat", { method: "POST", body: { message: q, literacy } });
      setMessages((m) => [...m, { role: "assistant", content: res.answer, citations: res.citations || [] }]);
      setDisclaimer(res.disclaimer || disclaimer);
    } catch (e) {
      if (e.status === 503) setConfigured(false);
      setMessages((m) => [...m, {
        role: "assistant", citations: [],
        content: e.status === 503
          ? "I'm not switched on yet — an Anthropic API key needs to be added to the backend (see the setup notes)."
          : "Sorry, I couldn't respond just now. " + e.message,
      }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      <div className="topbar">
        <div className="hello"><h1>Health coach</h1><p>Grounded in Vitala's vetted wellbeing knowledge base.</p></div>
        <div className="litseg" title="How should answers be explained?">
          {[["simple", "Simple"], ["standard", "Standard"], ["detailed", "In-depth"]].map(([id, label]) => (
            <button key={id} className={literacy === id ? "on" : ""} onClick={() => setLiteracy(id)}>{label}</button>
          ))}
        </div>
      </div>

      {!configured && (
        <div className="configbanner">
          ⚙️ The assistant isn't switched on yet. Check the backend's LLM setup (Ollama running, or an API key set), then reload this page.
        </div>
      )}

      <div className="card pad chatwrap">
        <div className="chatscroll" ref={scrollRef}>
          {messages.length === 0 && (
            <div className="msg bot">
              Hi {userName || "there"} 👋 I'm your Vitala coach. I can help with hydration, movement, sleep, nutrition, stress, and how the app works — always grounded in verified wellbeing info. What's on your mind?
              <div className="suggest">
                {SUGGESTIONS.map((sug) => <button key={sug} onClick={() => send(sug)}>{sug}</button>)}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={"msg " + (m.role === "user" ? "user" : "bot")}>
              {m.content}
              {m.role === "assistant" && m.citations && m.citations.length > 0 && (
                <div className="cites">
                  {m.citations.map((c, j) => <span key={j} className="cite">📄 {c.title}</span>)}
                </div>
              )}
            </div>
          ))}
          {sending && <div className="msg bot"><span className="typing"><i /><i /><i /></span></div>}
        </div>

        <div className="chatbar">
          <textarea
            className="chatinput" rows={1} value={input}
            placeholder="Ask about your health or the app…"
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
          />
          <button className="sendbtn" onClick={() => send()} disabled={sending || !input.trim()} aria-label="Send">
            <svg width="20" height="20" viewBox="0 0 24 24"><path d="M4 12l16-8-6 8 6 8z" fill="currentColor" /></svg>
          </button>
        </div>
        {disclaimer && <p className="disclaimer">{disclaimer}</p>}
      </div>
    </>
  );
}

/* ------------------------------------------------------------------ learning (Phase 3) */
function ModuleView({ mod, onReward, onBack, onStatus }) {
  const [section, setSection] = useState(mod.status.cards_completed ? "quiz" : "read");
  const [card, setCard] = useState(0);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(mod.status);

  const lastCard = card === mod.cards.length - 1;
  const allAnswered = mod.quiz.every((q) => answers[q.id] != null);

  async function markRead(e) {
    setBusy(true);
    try {
      const res = await api(`/learn/${mod.id}/read`, { method: "POST" });
      onReward(res, e);
      setStatus((s) => ({ ...s, cards_completed: true }));
      onStatus(mod.id, { cards_completed: true });
      setSection("quiz");
    } catch (err) { alert(err.message); } finally { setBusy(false); }
  }
  async function submitQuiz(e) {
    setBusy(true);
    try {
      const res = await api(`/learn/${mod.id}/quiz`, { method: "POST", body: { answers } });
      setResult(res);
      onReward(res, e);
      setStatus((s) => ({ ...s, quiz_completed: true, best_score: res.bestScore }));
      onStatus(mod.id, { quiz_completed: true, best_score: res.bestScore });
    } catch (err) { alert(err.message); } finally { setBusy(false); }
  }
  function retake() { setAnswers({}); setResult(null); }

  return (
    <>
      <div className="topbar">
        <div className="hello" style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <button className="btn btn-ghost" style={{ padding: "9px 13px" }} onClick={onBack}>← Back</button>
          <div><h1 style={{ display: "flex", alignItems: "center", gap: 10 }}><span style={{ fontSize: 26 }}>{mod.icon}</span>{mod.title}</h1></div>
        </div>
        <div className="litseg">
          <button className={section === "read" ? "on" : ""} onClick={() => setSection("read")}>Read {status.cards_completed ? "✓" : ""}</button>
          <button className={section === "quiz" ? "on" : ""} onClick={() => setSection("quiz")}>Quiz {status.quiz_completed ? "✓" : ""}</button>
        </div>
      </div>

      {section === "read" && (
        <>
          <div className="lcard">
            <h3>{mod.cards[card].heading}</h3>
            <p>{mod.cards[card].body}</p>
          </div>
          <div className="dots">{mod.cards.map((_, i) => <i key={i} className={i === card ? "on" : ""} />)}</div>
          <div style={{ display: "flex", gap: 12 }}>
            <button className="btn btn-ghost" disabled={card === 0} onClick={() => setCard((c) => c - 1)}>Previous</button>
            {!lastCard
              ? <button className="btn btn-primary" style={{ flex: 1 }} onClick={() => setCard((c) => c + 1)}>Next</button>
              : status.cards_completed
                ? <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => setSection("quiz")}>✓ Read — go to quiz</button>
                : <button className="btn btn-primary" style={{ flex: 1 }} disabled={busy} onClick={markRead}>{busy ? <span className="spin" /> : `Mark as read  ·  +${mod.xp_read} XP`}</button>}
          </div>
        </>
      )}

      {section === "quiz" && !result && (
        <>
          {mod.quiz.map((q, qi) => (
            <div key={q.id} className="quizq">
              <div className="qh"><span className="qn">{qi + 1}</span><span>{q.question}</span></div>
              {q.options.map((opt, oi) => (
                <button key={oi} className={"opt" + (answers[q.id] === oi ? " sel" : "")} onClick={() => setAnswers((a) => ({ ...a, [q.id]: oi }))}>
                  <span className="mark">✓</span>{opt}
                </button>
              ))}
            </div>
          ))}
          <button className="btn btn-primary" style={{ width: "100%" }} disabled={!allAnswered || busy} onClick={submitQuiz}>
            {busy ? <span className="spin" /> : allAnswered ? "Submit answers" : "Answer all questions to submit"}
          </button>
        </>
      )}

      {section === "quiz" && result && (
        <>
          <div className="card pad" style={{ textAlign: "center", marginBottom: 18 }}>
            <p className="eyebrow" style={{ margin: "0 0 8px" }}>Your score</p>
            <div className="scorebig" style={{ color: result.score >= 60 ? "var(--vital)" : "var(--flame)" }}>{result.score}%</div>
            <p style={{ color: "var(--muted)", fontSize: 13.5, margin: "8px 0 0" }}>
              {result.correct} of {result.total} correct{result.awardedXp > 0 ? ` · +${result.awardedXp} XP earned` : " · best so far: " + result.bestScore + "%"}
            </p>
          </div>
          {mod.quiz.map((q, qi) => {
            const res = result.results.find((r) => r.id === q.id);
            return (
              <div key={q.id} className="quizq">
                <div className="qh"><span className="qn">{qi + 1}</span><span>{q.question}</span></div>
                {q.options.map((opt, oi) => {
                  let cls = "opt";
                  if (oi === res.answer) cls += " correct";
                  else if (oi === res.your) cls += " wrong";
                  return <div key={oi} className={cls}><span className="mark">{oi === res.answer ? "✓" : oi === res.your ? "✗" : ""}</span>{opt}</div>;
                })}
                <div className="expl">💡 {res.explanation}</div>
              </div>
            );
          })}
          <div style={{ display: "flex", gap: 12 }}>
            <button className="btn btn-ghost" style={{ flex: 1 }} onClick={retake}>Retake quiz</button>
            <button className="btn btn-primary" style={{ flex: 1 }} onClick={onBack}>Back to modules</button>
          </div>
        </>
      )}
    </>
  );
}

function LearnPage({ onReward }) {
  const [data, setData] = useState(null);
  const [active, setActive] = useState(null);   // full module detail
  const [loading, setLoading] = useState(false);

  const loadList = useCallback(() => { api("/learn").then(setData).catch(() => {}); }, []);
  useEffect(() => { loadList(); }, [loadList]);

  async function open(id) {
    setLoading(true);
    try { setActive(await api("/learn/" + id)); } catch (e) { alert(e.message); } finally { setLoading(false); }
  }
  function updateStatus(id, patch) {
    setData((d) => d && ({ ...d, modules: d.modules.map((m) => m.id === id ? { ...m, status: { ...m.status, ...patch } } : m) }));
  }

  if (active) {
    return <ModuleView mod={active} onReward={onReward} onBack={() => { setActive(null); loadList(); }} onStatus={updateStatus} />;
  }

  return (
    <>
      <div className="topbar">
        <div className="hello"><h1>Learn</h1><p>Bite-sized health lessons. Read, take the quiz, earn XP.</p></div>
        {data && <span className="pill"><b className="num" style={{ color: "var(--vital)" }}>{data.completed}</b> / {data.total} modules</span>}
      </div>
      {data && (
        <div className="card pad" style={{ marginBottom: 18 }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10, fontSize: 13.5 }}>
            <span style={{ fontWeight: 600 }}>Health-literacy progress</span>
            <span style={{ color: "var(--muted)" }}><b className="num">{data.completed}</b>/{data.total}</span>
          </div>
          <div className="lprog"><i style={{ width: (data.total ? data.completed / data.total * 100 : 0) + "%" }} /></div>
        </div>
      )}
      {loading && <div className="card pad" style={{ textAlign: "center" }}><span className="spin" /></div>}
      {!data && !loading && <div className="card pad" style={{ textAlign: "center" }}><span className="spin" /></div>}
      {data && (
        <div className="modgrid">
          {data.modules.map((m) => {
            const done = m.status.cards_completed && m.status.quiz_completed;
            return (
              <button key={m.id} className="modcard" onClick={() => open(m.id)}>
                <div className="modtop">
                  <div className="modico">{m.icon}</div>
                  <div><div className="modttl">{m.title}</div></div>
                </div>
                <div className="moddesc">{m.description}</div>
                <div className="modmeta">
                  {done
                    ? <span className="tag done">✓ Completed{m.status.best_score ? ` · ${m.status.best_score}%` : ""}</span>
                    : <>
                        <span className={"tag " + (m.status.cards_completed ? "done" : "todo")}>{m.status.cards_completed ? "✓ Read" : "📖 Read"}</span>
                        <span className={"tag " + (m.status.quiz_completed ? "done" : "todo")}>{m.status.quiz_completed ? "✓ Quiz" : "❓ Quiz"}</span>
                      </>}
                  <span className="tag xp">⚡ up to {m.xp_read + m.xp_quiz}</span>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </>
  );
}

/* ------------------------------------------------------------------ root */
export default function App() {
  const [phase, setPhase] = useState("loading"); // loading | auth | onboarding | app
  const [s, setS] = useState(null);
  const [tab, setTab] = useState("home");
  const [busyId, setBusyId] = useState(null);
  const [toast, setToast] = useState("");
  const [celebration, setCelebration] = useState(null);
  const [xpFloat, setXpFloat] = useState(null);
  const queueRef = useRef([]);

  const loadState = useCallback(async () => {
    const state = await api("/quests/today");
    setS(state);
    setPhase(state.profile ? "app" : "onboarding");
    return state;
  }, []);

  // boot: resume session if a token exists
  useEffect(() => {
    if (!getToken()) { setPhase("auth"); return; }
    loadState().catch(() => { setToken(null); setPhase("auth"); });
  }, [loadState]);

  const pump = useCallback(() => {
    if (!celebration && queueRef.current.length) setCelebration(queueRef.current.shift());
  }, [celebration]);
  useEffect(() => { if (!celebration) pump(); }, [celebration, pump]);

  const flashToast = (msg) => { setToast(msg); setTimeout(() => setToast(""), 2600); };

  // Shared reward handler for quests AND learning: update state, queue
  // level-up/badge celebrations, and float the earned XP.
  const applyReward = useCallback((res, evt) => {
    if (res.state) setS(res.state);
    if (res.levelUp) queueRef.current.push({ type: "level", level: res.newLevel });
    (res.newBadges || []).forEach((b) => queueRef.current.push({ type: "badge", badge: b }));
    if (res.awardedXp > 0) {
      const x = evt?.clientX ?? window.innerWidth / 2, y = evt?.clientY ?? 120;
      setXpFloat({ id: Date.now(), x, y, amt: res.awardedXp });
      setTimeout(() => setXpFloat((f) => (f && f.x === x ? null : f)), 1100);
    }
    pump();
  }, [pump]);

  const completeQuest = useCallback(async (q, evt) => {
    if (q.done || busyId) return;
    setBusyId(q.id);
    try {
      const res = await api("/quests/complete", { method: "POST", body: { quest_id: q.id } });
      applyReward(res, evt);
    } catch (e) {
      if (e.status === 409) { flashToast("You've already completed that today."); await loadState().catch(() => {}); }
      else flashToast(e.message);
    } finally {
      setBusyId(null);
    }
  }, [busyId, applyReward, loadState]);

  async function logout() {
    try { await api("/auth/logout", { method: "POST" }); } catch { /* ignore */ }
    setToken(null); setS(null); setTab("home"); setPhase("auth");
  }

  if (phase === "loading") return (
    <div className="vitala-root"><div style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <div style={{ textAlign: "center" }}>
        <div className="mark" style={{ width: 54, height: 54, borderRadius: 16, display: "grid", placeItems: "center", margin: "0 auto 14px", background: "linear-gradient(150deg,var(--vital),var(--azure))", animation: "spinpulse 2s infinite" }}><Heartbeat /></div>
        <div style={{ color: "var(--muted)", fontSize: 14 }}>Connecting to your account…</div>
      </div>
    </div></div>
  );
  if (phase === "auth") return <div className="vitala-root"><Auth onDone={loadState} /></div>;
  if (phase === "onboarding") return <div className="vitala-root"><Onboarding onDone={loadState} /></div>;

  const NAV = [["home", "Home", ICONS.home], ["quests", "Quests", ICONS.quest], ["learn", "Learn", ICONS.learn], ["assistant", "Coach", ICONS.chat], ["badges", "Badges", ICONS.badge], ["leaderboard", "Ranks", ICONS.board], ["profile", "Profile", ICONS.user]];

  return (
    <div className="vitala-root">
      <div className="shell">
        <nav className="rail">
          <div className="logo"><Heartbeat /></div>
          {NAV.map(([id, label, icon]) => (
            <button key={id} className={"navbtn" + (tab === id ? " on" : "")} onClick={() => setTab(id)}><svg viewBox="0 0 24 24">{icon}</svg>{label}</button>
          ))}
        </nav>
        <div className="main">
          <div className="page">
            {tab === "home" && <Dashboard s={s} busyId={busyId} onComplete={completeQuest} go={setTab} />}
            {tab === "quests" && <QuestsPage s={s} busyId={busyId} onComplete={completeQuest} />}
            {tab === "assistant" && <AssistantPage userName={s.profile?.name || s.username} />}
            {tab === "learn" && <LearnPage onReward={applyReward} />}
            {tab === "badges" && <BadgesPage s={s} />}
            {tab === "leaderboard" && <LeaderboardPage meName={s.username} />}
            {tab === "profile" && <ProfilePage s={s} onLogout={logout} />}
          </div>
        </div>
        <nav className="tabbar">
          {NAV.map(([id, label, icon]) => (
            <button key={id} className={"navbtn" + (tab === id ? " on" : "")} onClick={() => setTab(id)}><svg viewBox="0 0 24 24">{icon}</svg>{label}</button>
          ))}
        </nav>
      </div>

      {xpFloat && <div className="xpfloat" style={{ left: xpFloat.x - 14, top: xpFloat.y - 14 }}>+{xpFloat.amt} XP</div>}
      {toast && <div className="toast">{toast}</div>}

      {celebration && (
        <div className="cele" onClick={() => setCelebration(null)}>
          <div className="celecard" onClick={(e) => e.stopPropagation()}>
            <Confetti />
            {celebration.type === "level" ? (<>
              <VitalityRing level={celebration.level} into={1} need={1} />
              <h3 style={{ color: "var(--gold)" }}>Level {celebration.level}!</h3>
              <p>You're getting stronger. New milestones are within reach.</p>
            </>) : (<>
              <div style={{ display: "grid", placeItems: "center" }}><BadgeSVG tier={celebration.badge.tier} emoji={celebration.badge.emoji} size={96} /></div>
              <h3>Badge unlocked</h3>
              <p><b style={{ color: "var(--txt)" }}>{celebration.badge.name}</b> — {celebration.badge.desc}</p>
            </>)}
            <button className="btn btn-primary" style={{ width: "100%" }} onClick={() => setCelebration(null)}>Keep going</button>
          </div>
        </div>
      )}
    </div>
  );
}
