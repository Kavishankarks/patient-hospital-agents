"use client";

import { useMemo, useState } from "react";

const DEFAULT_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

type Patient = {
  id: number;
  name: string;
  age?: number | null;
  sex?: string | null;
  contact_masked?: string | null;
};

type Triage = {
  level: string;
  red_flags?: string[];
  specialty_needed?: string | null;
  safety?: string[];
};

type Summary = {
  situation: string;
  background: string;
  assessment: string;
  recommendation: string;
  safety?: string[];
};

type SummaryLatest = {
  sbar: Summary;
  created_at?: string | null;
};

type ProfileLatest = {
  profile: Record<string, unknown>;
  created_at?: string | null;
};

type PreIntel = {
  risks?: string[];
  interactions?: string[];
  suggested_tests?: string[];
  differential_hints?: string[];
  safety?: string[];
};

type Hospital = {
  hospital_id: string;
  name: string;
  score: number;
  why?: string[];
};

type Document = {
  document_id: number;
  extracted_text?: string | null;
};

type Questionnaire = {
  questions?: string[];
};

type Coach = {
  script_text: string;
  audio_path: string;
};

type AuthRole = "patient" | "doctor" | "hospital";

type Session = {
  role: AuthRole;
  accountId: number;
  patientId?: number | null;
  mobile: string;
};

async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const detail = data?.detail?.[0]?.msg || data?.detail || res.statusText;
    throw new Error(typeof detail === "string" ? detail : "Request failed");
  }
  return data as T;
}

export default function HomePage() {
  const [apiBase, setApiBase] = useState(DEFAULT_BASE);
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [session, setSession] = useState<Session | null>(null);
  const [authRole, setAuthRole] = useState<AuthRole>("patient");
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [authMobile, setAuthMobile] = useState("");
  const [authPassword, setAuthPassword] = useState("");

  const [patientIdInput, setPatientIdInput] = useState("");
  const [patient, setPatient] = useState<Patient | null>(null);
  const [profile, setProfile] = useState<Record<string, unknown> | null>(null);
  const [profileMeta, setProfileMeta] = useState<ProfileLatest | null>(null);
  const [triage, setTriage] = useState<Triage | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [summaryMeta, setSummaryMeta] = useState<SummaryLatest | null>(null);
  const [preIntel, setPreIntel] = useState<PreIntel | null>(null);
  const [hospitalRecs, setHospitalRecs] = useState<Hospital[] | null>(null);
  const [questionnaire, setQuestionnaire] = useState<Questionnaire | null>(null);
  const [patientsList, setPatientsList] = useState<Patient[] | null>(null);
  const [documents, setDocuments] = useState<Document[] | null>(null);
  const [coach, setCoach] = useState<Coach | null>(null);

  const [newPatient, setNewPatient] = useState({
    name: "",
    age: "",
    sex: "",
    contact: "",
    mobile: "",
    password: ""
  });

  const [docFile, setDocFile] = useState<File | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [radiusKm, setRadiusKm] = useState("20");
  const [questionnaireAnswer, setQuestionnaireAnswer] = useState("{}");

  const activePatientId = useMemo(() => {
    if (!patientIdInput) return null;
    const id = Number(patientIdInput);
    return Number.isFinite(id) ? id : null;
  }, [patientIdInput]);

  const resetInsights = () => {
    setProfile(null);
    setProfileMeta(null);
    setTriage(null);
    setSummary(null);
    setSummaryMeta(null);
    setPreIntel(null);
    setHospitalRecs(null);
    setQuestionnaire(null);
    setDocuments(null);
    setCoach(null);
  };

  const resetPatientContext = () => {
    setPatient(null);
    setPatientIdInput("");
    setPatientsList(null);
    resetInsights();
  };

  const withBusy = async (fn: () => Promise<void>) => {
    setBusy(true);
    setStatus(null);
    try {
      await fn();
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  };

  const createPatient = () =>
    withBusy(async () => {
      const payload = {
        name: newPatient.name,
        age: newPatient.age ? Number(newPatient.age) : null,
        sex: newPatient.sex || null,
        contact: newPatient.contact || null,
        mobile: newPatient.mobile || null,
        password: newPatient.password || null
      };
      const data = await requestJson<Patient>(`${apiBase}/api/v1/patients`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      setPatient(data);
      setPatientIdInput(String(data.id));
      resetInsights();
      setStatus(`Patient created: ${data.name} (#${data.id})`);
    });

  const fetchPatient = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Enter a valid patient ID");
      const data = await requestJson<Patient>(
        `${apiBase}/api/v1/patients/${activePatientId}`
      );
      setPatient(data);
      resetInsights();
      if (session?.role === "doctor") {
        try {
          await fetchLatestProfileById(activePatientId);
        } catch {
          // ignore missing latest profile
        }
        try {
          await fetchLatestSummaryById(activePatientId);
        } catch {
          // ignore missing latest summary
        }
      }
      setStatus(`Loaded patient #${data.id}`);
    });

  const listPatients = () =>
    withBusy(async () => {
      const data = await requestJson<Patient[]>(`${apiBase}/api/v1/patients`);
      setPatientsList(data);
      setStatus(`Loaded ${data.length} patients.`);
    });

  const uploadDocument = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Set patient ID first");
      if (!docFile) throw new Error("Choose a document file");
      const form = new FormData();
      form.append("file", docFile);
      await requestJson(`${apiBase}/api/v1/patients/${activePatientId}/uploads`, {
        method: "POST",
        body: form
      });
      setStatus("Document uploaded. Refresh documents to review.");
    });

  const uploadAudio = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Set patient ID first");
      if (!audioFile) throw new Error("Choose an audio file");
      const form = new FormData();
      form.append("file", audioFile);
      await requestJson(`${apiBase}/api/v1/patients/${activePatientId}/audio`, {
        method: "POST",
        body: form
      });
      setStatus("Audio uploaded and transcribed. Build profile when ready.");
    });

  const buildProfile = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Set patient ID first");
      const data = await requestJson<{ profile: Record<string, unknown> }>(
        `${apiBase}/api/v1/patients/${activePatientId}/profile/build`,
        { method: "POST" }
      );
      setProfile(data.profile);
      setStatus("Profile built from latest uploads.");
    });

  const runTriage = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Set patient ID first");
      const data = await requestJson<Triage>(
        `${apiBase}/api/v1/patients/${activePatientId}/triage`,
        { method: "POST" }
      );
      setTriage(data);
      setStatus(`Triage level: ${data.level}`);
    });

  const getSummary = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Set patient ID first");
      const data = await requestJson<Summary>(
        `${apiBase}/api/v1/patients/${activePatientId}/summary`
      );
      setSummary(data);
      setStatus("SBAR summary generated.");
    });

  const getPreIntel = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Set patient ID first");
      const data = await requestJson<PreIntel>(
        `${apiBase}/api/v1/patients/${activePatientId}/preintelligence`
      );
      setPreIntel(data);
      setStatus("Pre-intelligence ready.");
    });

  const getHospitals = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Set patient ID first");
      const radius = radiusKm ? Number(radiusKm) : 20;
      const data = await requestJson<Hospital[]>(
        `${apiBase}/api/v1/patients/${activePatientId}/hospitals/recommendations?radius_km=${radius}`
      );
      setHospitalRecs(data);
      setStatus(`Found ${data.length} hospital matches.`);
    });

  const getNextQuestions = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Set patient ID first");
      const data = await requestJson<Questionnaire>(
        `${apiBase}/api/v1/patients/${activePatientId}/questionnaire/next`,
        { method: "POST" }
      );
      setQuestionnaire(data);
      setStatus("Fetched adaptive questions.");
    });

  const submitAnswers = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Set patient ID first");
      let parsed: Record<string, unknown> = {};
      try {
        parsed = JSON.parse(questionnaireAnswer || "{}");
      } catch {
        throw new Error("Answers must be valid JSON");
      }
      await requestJson(
        `${apiBase}/api/v1/patients/${activePatientId}/questionnaire/answer`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ answers: parsed })
        }
      );
      setStatus("Answers submitted. Refresh profile when ready.");
    });

  const badgeClass = (level?: string) => {
    switch ((level || "").toLowerCase()) {
      case "red":
        return "badge red";
      case "amber":
        return "badge amber";
      case "green":
        return "badge green";
      default:
        return "badge";
    }
  };

  const fetchDocumentsById = async (patientId: number) => {
    const data = await requestJson<Document[]>(
      `${apiBase}/api/v1/patients/${patientId}/uploads`
    );
    setDocuments(data);
    setStatus(`Loaded ${data.length} documents.`);
  };

  const fetchLatestProfileById = async (patientId: number) => {
    const data = await requestJson<ProfileLatest>(
      `${apiBase}/api/v1/patients/${patientId}/profile/latest`
    );
    setProfile(data.profile);
    setProfileMeta(data);
  };

  const fetchLatestSummaryById = async (patientId: number) => {
    const data = await requestJson<SummaryLatest>(
      `${apiBase}/api/v1/patients/${patientId}/summary/latest`
    );
    setSummary(data.sbar);
    setSummaryMeta(data);
  };

  const fetchCoachById = async (patientId: number) => {
    const data = await requestJson<Coach>(
      `${apiBase}/api/v1/patients/${patientId}/recovery-coach/latest`
    );
    setCoach(data);
  };

  const getDocuments = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Set patient ID first");
      await fetchDocumentsById(activePatientId);
    });

  const getCoach = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Set patient ID first");
      await fetchCoachById(activePatientId);
    });

  const generateCoach = () =>
    withBusy(async () => {
      if (!activePatientId) throw new Error("Set patient ID first");
      const data = await requestJson<Coach>(
        `${apiBase}/api/v1/patients/${activePatientId}/recovery-coach/generate`,
        { method: "POST" }
      );
      setCoach(data);
      setStatus("Generated a new recovery coach message.");
    });

  const buildAudioSrc = (path: string) => {
    const base = apiBase.endsWith("/") ? apiBase.slice(0, -1) : apiBase;
    const normalized = path.startsWith("./") ? path.slice(2) : path;
    return `${base}/${normalized.replace(/^\/+/, "")}`;
  };

  const formatDateTime = (value?: string | null) => {
    if (!value) return null;
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short"
    }).format(date);
  };

  const login = () =>
    withBusy(async () => {
      if (!authMobile || !authPassword) {
        throw new Error("Enter mobile and password");
      }
      const data = await requestJson<{
        role: AuthRole;
        account_id: number;
        patient_id?: number | null;
      }>(`${apiBase}/api/v1/auth/${authRole}s/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mobile: authMobile, password: authPassword })
      });
      await applyLoginResponse(data, authMobile);
    });

  const signup = () =>
    withBusy(async () => {
      if (authRole === "patient") {
        if (!newPatient.name || !newPatient.mobile || !newPatient.password) {
          throw new Error("Patient signup needs name, mobile, and password");
        }
        const payload = {
          name: newPatient.name,
          age: newPatient.age ? Number(newPatient.age) : null,
          sex: newPatient.sex || null,
          contact: newPatient.contact || null,
          mobile: newPatient.mobile,
          password: newPatient.password
        };
        const data = await requestJson<{
          role: AuthRole;
          account_id: number;
          patient_id?: number | null;
        }>(`${apiBase}/api/v1/auth/patients/signup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        await applyLoginResponse(data, newPatient.mobile);
        setStatus("Patient account created.");
        return;
      }
      if (!authMobile || !authPassword) {
        throw new Error("Enter mobile and password");
      }
      const data = await requestJson<{
        role: AuthRole;
        account_id: number;
        patient_id?: number | null;
      }>(`${apiBase}/api/v1/auth/${authRole}s/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mobile: authMobile, password: authPassword })
      });
      await applyLoginResponse(data, authMobile);
      setStatus(`Created ${data.role} account.`);
    });

  const logout = () => {
    setSession(null);
    setAuthMobile("");
    setAuthPassword("");
    resetPatientContext();
  };

  const canSeePatientOps = session?.role === "patient" || session?.role === "doctor";
  const canSeeHospitalOps = session?.role === "hospital" || session?.role === "doctor";
  const showPatientIntake = session?.role === "doctor";
  const showPatientContext = session !== null;
  const showCoach = session?.role === "patient";

  const applyLoginResponse = async (
    data: { role: AuthRole; account_id: number; patient_id?: number | null },
    mobile: string
  ) => {
    setSession({
      role: data.role,
      accountId: data.account_id,
      patientId: data.patient_id ?? null,
      mobile
    });
    resetPatientContext();
    if (data.patient_id) {
      setPatientIdInput(String(data.patient_id));
      const loaded = await requestJson<Patient>(
        `${apiBase}/api/v1/patients/${data.patient_id}`
      );
      setPatient(loaded);
      await fetchDocumentsById(data.patient_id);
      await fetchCoachById(data.patient_id);
    }
    setAuthMode("login");
  };

  return (
    <main>
      <header>
        <div className="hero">
          <div>
            <p className="label">Patient + Hospital Copilot</p>
            <h1>Clinical decision support, in one calm workspace.</h1>
            <p>
              Create patients, upload intake evidence, and retrieve triage and
              hospital recommendations. Always verify with a licensed clinician.
            </p>
          </div>
          <div className="hero-card">
            <div className="label">API base</div>
            <input
              value={apiBase}
              onChange={(event) => setApiBase(event.target.value)}
              placeholder="http://localhost:8000"
            />
            <p className="mono">Set to your running backend server.</p>
          </div>
        </div>
        <div className="banner">
          This interface supports clinical teams. It does not prescribe or
          replace clinician judgment.
        </div>
      </header>

      <section className="section">
        <h2>Access</h2>
        <div className="card">
          <div className="grid-3">
            {(["patient", "doctor", "hospital"] as AuthRole[]).map((role) => (
              <button
                key={role}
                className={role === authRole ? "secondary" : "ghost"}
                onClick={() => setAuthRole(role)}
                disabled={busy}
              >
                {role}
              </button>
            ))}
          </div>
          <div className="grid-2">
            <button
              className={authMode === "login" ? "secondary" : "ghost"}
              onClick={() => setAuthMode("login")}
              disabled={busy}
            >
              Log in
            </button>
            <button
              className={authMode === "signup" ? "secondary" : "ghost"}
              onClick={() => setAuthMode("signup")}
              disabled={busy}
            >
              Sign up
            </button>
          </div>
          <div className="grid-2">
            <input
              placeholder="Mobile"
              value={authRole === "patient" && authMode === "signup" ? newPatient.mobile : authMobile}
              onChange={(event) =>
                authRole === "patient" && authMode === "signup"
                  ? setNewPatient((prev) => ({ ...prev, mobile: event.target.value }))
                  : setAuthMobile(event.target.value)
              }
            />
            <input
              placeholder="Password"
              type="password"
              value={authRole === "patient" && authMode === "signup" ? newPatient.password : authPassword}
              onChange={(event) =>
                authRole === "patient" && authMode === "signup"
                  ? setNewPatient((prev) => ({ ...prev, password: event.target.value }))
                  : setAuthPassword(event.target.value)
              }
            />
          </div>
          {authMode === "signup" && authRole === "patient" ? (
            <div className="grid-2">
              <input
                placeholder="Full name"
                value={newPatient.name}
                onChange={(event) =>
                  setNewPatient((prev) => ({ ...prev, name: event.target.value }))
                }
              />
              <input
                placeholder="Age"
                type="number"
                value={newPatient.age}
                onChange={(event) =>
                  setNewPatient((prev) => ({ ...prev, age: event.target.value }))
                }
              />
              <select
                value={newPatient.sex}
                onChange={(event) =>
                  setNewPatient((prev) => ({ ...prev, sex: event.target.value }))
                }
              >
                <option value="">Sex</option>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="intersex">Intersex</option>
                <option value="other">Other</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
              <input
                placeholder="Contact"
                value={newPatient.contact}
                onChange={(event) =>
                  setNewPatient((prev) => ({ ...prev, contact: event.target.value }))
                }
              />
            </div>
          ) : null}
          {authMode === "login" ? (
            <button onClick={login} disabled={busy}>
              Log in as {authRole}
            </button>
          ) : (
            <button onClick={signup} disabled={busy}>
              Sign up as {authRole}
            </button>
          )}
          {session ? (
            <div>
              <p className="mono">
                Signed in as {session.role} · Account #{session.accountId}
              </p>
              <button className="ghost" onClick={logout}>
                Log out
              </button>
            </div>
          ) : (
            <p className="mono">Sign in to unlock relevant workflows.</p>
          )}
        </div>
      </section>

      {showPatientContext && (
        <section className="section">
          <h2>Active patient</h2>
          <div className="grid-2">
            <div className="card">
              <div className="label">Load patient</div>
              {session?.role === "doctor" ? (
                <div className="grid-2">
                  <button className="secondary" onClick={listPatients} disabled={busy}>
                    Refresh list
                  </button>
                  <select
                    value={patientIdInput}
                    onChange={(event) => setPatientIdInput(event.target.value)}
                  >
                    <option value="">Select patient</option>
                    {(patientsList ?? []).map((item) => (
                      <option key={item.id} value={item.id}>
                        #{item.id} · {item.name}
                      </option>
                    ))}
                  </select>
                  <button
                    className="secondary"
                    onClick={fetchPatient}
                    disabled={busy || !patientIdInput}
                  >
                    Load selected
                  </button>
                </div>
              ) : (
                <div className="grid-2">
                  <input
                    placeholder="Patient ID"
                    value={patientIdInput}
                    onChange={(event) => setPatientIdInput(event.target.value)}
                    disabled={session?.role === "patient"}
                  />
                  <button
                    className="secondary"
                    onClick={fetchPatient}
                    disabled={busy || !patientIdInput}
                  >
                    Load patient
                  </button>
                </div>
              )}
              <div className="divider" />
              {patient ? (
                <div>
                  <div className="label">Active patient</div>
                  <p>
                    <strong>{patient.name}</strong> (#{patient.id})
                  </p>
                  <p className="mono">
                    {patient.age ?? "—"} years · {patient.sex ?? "—"}
                  </p>
                  <p className="mono">Contact: {patient.contact_masked ?? "—"}</p>
                </div>
              ) : (
                <p className="mono">No patient selected yet.</p>
              )}
            </div>
            {showPatientIntake && (
              <div className="card">
                <div>
                  <div className="label">Create new patient</div>
                  <div className="grid-2">
                    <input
                      placeholder="Name"
                      value={newPatient.name}
                      onChange={(event) =>
                        setNewPatient((prev) => ({
                          ...prev,
                          name: event.target.value
                        }))
                      }
                    />
                    <input
                      placeholder="Age"
                      type="number"
                      value={newPatient.age}
                      onChange={(event) =>
                        setNewPatient((prev) => ({
                          ...prev,
                          age: event.target.value
                        }))
                      }
                    />
                    <select
                      value={newPatient.sex}
                      onChange={(event) =>
                        setNewPatient((prev) => ({
                          ...prev,
                          sex: event.target.value
                        }))
                      }
                    >
                      <option value="">Sex</option>
                      <option value="female">Female</option>
                      <option value="male">Male</option>
                      <option value="intersex">Intersex</option>
                      <option value="other">Other</option>
                      <option value="prefer_not_to_say">Prefer not to say</option>
                    </select>
                    <input
                      placeholder="Contact"
                      value={newPatient.contact}
                      onChange={(event) =>
                        setNewPatient((prev) => ({
                          ...prev,
                          contact: event.target.value
                        }))
                      }
                    />
                  </div>
                </div>
                <button onClick={createPatient} disabled={busy || !newPatient.name}>
                  Create patient
                </button>
              </div>
            )}
          </div>
        </section>
      )}

      {showCoach && (
        <section className="section">
          <h2>Recovery coach</h2>
          <div className="card">
            <div className="grid-2">
              <button className="secondary" onClick={getCoach} disabled={busy}>
                Refresh message
              </button>
              <button onClick={generateCoach} disabled={busy}>
                Build coach
              </button>
            </div>
            {coach ? (
              <div>
                <div className="label">Today's guidance</div>
                <p>{coach.script_text}</p>
                {coach.audio_path ? (
                  <audio controls src={buildAudioSrc(coach.audio_path)} />
                ) : (
                  <p className="mono">No audio available.</p>
                )}
              </div>
            ) : (
              <p className="mono">No coach message loaded yet.</p>
            )}
          </div>
        </section>
      )}

      {canSeePatientOps && (
        <section className="section">
        <h2>Evidence uploads</h2>
        <div className="grid-2">
          <div className="card">
            <div className="label">Document intake</div>
            <input
              type="file"
              onChange={(event) => setDocFile(event.target.files?.[0] || null)}
            />
            <button className="secondary" onClick={uploadDocument} disabled={busy}>
              Upload document
            </button>
          </div>
          <div className="card">
            <div className="label">Audio intake</div>
            <input
              type="file"
              accept="audio/*"
              onChange={(event) => setAudioFile(event.target.files?.[0] || null)}
            />
            <button className="secondary" onClick={uploadAudio} disabled={busy}>
              Upload audio
            </button>
          </div>
        </div>
        <div className="card">
          <div className="label">Uploaded documents</div>
          <div className="grid-2">
            <button className="secondary" onClick={getDocuments} disabled={busy}>
              Refresh documents
            </button>
          </div>
          {documents?.length ? (
            <ul className="list">
              {documents.map((doc) => (
                <li key={doc.document_id}>
                  <strong>Document #{doc.document_id}</strong>
                  {doc.extracted_text ? (
                    <p className="mono">{doc.extracted_text}</p>
                  ) : (
                    <p className="mono">No extracted text.</p>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mono">No documents loaded yet.</p>
          )}
        </div>
        </section>
      )}

      {canSeePatientOps && (
        <section className="section">
        <h2>Patient intelligence</h2>
        <div className="card">
          <div className="grid-3">
            <button className="secondary" onClick={buildProfile} disabled={busy}>
              Build profile
            </button>
            <button className="secondary" onClick={runTriage} disabled={busy}>
              Run triage
            </button>
            <button className="secondary" onClick={getSummary} disabled={busy}>
              Get SBAR summary
            </button>
            <button className="secondary" onClick={getPreIntel} disabled={busy}>
              Pre-intelligence
            </button>
            <button className="secondary" onClick={getNextQuestions} disabled={busy}>
              Next questions
            </button>
          </div>
        </div>

        {triage && (
          <div className="card">
            <div className="label">Triage</div>
            <div className={badgeClass(triage.level)}>{triage.level}</div>
            {triage.specialty_needed && (
              <p className="mono">Specialty: {triage.specialty_needed}</p>
            )}
            {triage.red_flags?.length ? (
              <ul className="list">
                {triage.red_flags.map((flag, index) => (
                  <li key={`${flag}-${index}`}>{flag}</li>
                ))}
              </ul>
            ) : (
              <p className="mono">No red flags reported.</p>
            )}
          </div>
        )}

        {profile && (
          <div className="card">
            <div className="label">Structured profile</div>
            {profileMeta?.created_at ? (
              <p className="mono">Created at: {formatDateTime(profileMeta.created_at)}</p>
            ) : null}
            <ProfileView profile={profile} />
          </div>
        )}

        {summary && (
          <div className="card">
            <div className="label">SBAR summary</div>
            {summaryMeta?.created_at ? (
              <p className="mono">
                Created at: {formatDateTime(summaryMeta.created_at)}
              </p>
            ) : null}
            <div className="grid-2">
              <div>
                <strong>Situation</strong>
                <p>{summary.situation}</p>
              </div>
              <div>
                <strong>Background</strong>
                <p>{summary.background}</p>
              </div>
              <div>
                <strong>Assessment</strong>
                <p>{summary.assessment}</p>
              </div>
              <div>
                <strong>Recommendation</strong>
                <p>{summary.recommendation}</p>
              </div>
            </div>
            {summary.safety?.length ? (
              <ul className="list">
                {summary.safety.map((item, index) => (
                  <li key={`${item}-${index}`}>{item}</li>
                ))}
              </ul>
            ) : null}
          </div>
        )}

        {preIntel && (
          <div className="card">
            <div className="label">Pre-intelligence</div>
            <div className="grid-2">
              <IntelBlock title="Risks" items={preIntel.risks} />
              <IntelBlock title="Interactions" items={preIntel.interactions} />
              <IntelBlock
                title="Suggested tests"
                items={preIntel.suggested_tests}
              />
              <IntelBlock
                title="Differential hints"
                items={preIntel.differential_hints}
              />
            </div>
          </div>
        )}

        {questionnaire && (
          <div className="card">
            <div className="label">Adaptive questionnaire</div>
            {questionnaire.questions?.length ? (
              <ul className="list">
                {questionnaire.questions.map((question, index) => (
                  <li key={`${question}-${index}`}>{question}</li>
                ))}
              </ul>
            ) : (
              <p className="mono">No open questions right now.</p>
            )}
            <div>
              <div className="label">Submit answers (JSON)</div>
              <textarea
                value={questionnaireAnswer}
                onChange={(event) => setQuestionnaireAnswer(event.target.value)}
              />
            </div>
            <button onClick={submitAnswers} disabled={busy}>
              Submit answers
            </button>
          </div>
        )}
        </section>
      )}

      {canSeeHospitalOps && (
        <section className="section">
        <h2>Hospital recommendations</h2>
        <div className="card">
          <div className="grid-2">
            <input
              type="number"
              value={radiusKm}
              onChange={(event) => setRadiusKm(event.target.value)}
              placeholder="Radius km"
            />
            <button className="secondary" onClick={getHospitals} disabled={busy}>
              Fetch recommendations
            </button>
          </div>
          {hospitalRecs?.length ? (
            <ul className="list">
              {hospitalRecs.map((hospital) => (
                <li key={hospital.hospital_id}>
                  <strong>{hospital.name}</strong> · Score {hospital.score}
                  {hospital.why?.length ? (
                    <p className="mono">{hospital.why.join(" • ")}</p>
                  ) : null}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mono">No recommendations loaded yet.</p>
          )}
        </div>
        </section>
      )}

      {status && (
        <section className="section">
          <div className="card">
            <div className="label">Status</div>
            <p>{status}</p>
          </div>
        </section>
      )}
    </main>
  );
}

function IntelBlock({ title, items }: { title: string; items?: string[] }) {
  return (
    <div>
      <strong>{title}</strong>
      {items?.length ? (
        <ul className="list">
          {items.map((item, index) => (
            <li key={`${item}-${index}`}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="mono">No items reported.</p>
      )}
    </div>
  );
}

function ProfileView({ profile }: { profile: Record<string, unknown> }) {
  const conditions = (profile.conditions as string[] | undefined) ?? [];
  const allergies = (profile.allergies as string[] | undefined) ?? [];
  const medications = (profile.medications as Record<string, unknown>[] | undefined) ?? [];
  const vitals = (profile.vitals as Record<string, string> | undefined) ?? {};
  const timeline = (profile.timeline as string[] | undefined) ?? [];
  const missing = (profile.missing_fields as string[] | undefined) ?? [];

  return (
    <div className="grid-2">
      <div>
        <strong>Conditions</strong>
        {conditions.length ? (
          <ul className="list">
            {conditions.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="mono">No conditions listed.</p>
        )}
      </div>
      <div>
        <strong>Allergies</strong>
        {allergies.length ? (
          <ul className="list">
            {allergies.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="mono">No known allergies.</p>
        )}
      </div>
      <div>
        <strong>Medications</strong>
        {medications.length ? (
          <ul className="list">
            {medications.map((med, index) => (
              <li key={`med-${index}`}>
                <div>
                  <strong>{String(med.name ?? "Medication")}</strong>
                  <p className="mono">
                    {[med.dosage, med.frequency].filter(Boolean).join(" · ")}
                  </p>
                  {med.purpose ? <p>{String(med.purpose)}</p> : null}
                  {med.duration || med.instructions ? (
                    <p className="mono">
                      {[med.duration, med.instructions].filter(Boolean).join(" · ")}
                    </p>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mono">No medications recorded.</p>
        )}
      </div>
      <div>
        <strong>Vitals</strong>
        {Object.keys(vitals).length ? (
          <ul className="list">
            {Object.entries(vitals).map(([label, value]) => (
              <li key={label}>
                <strong>{label}</strong>
                <p className="mono">{value}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mono">No vitals recorded.</p>
        )}
      </div>
      <div>
        <strong>Timeline</strong>
        {timeline.length ? (
          <ul className="list">
            {timeline.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="mono">No timeline entries.</p>
        )}
      </div>
      <div>
        <strong>Missing fields</strong>
        {missing.length ? (
          <ul className="list">
            {missing.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="mono">No missing fields.</p>
        )}
      </div>
    </div>
  );
}
