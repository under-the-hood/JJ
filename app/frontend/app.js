/* ====================== API layer ====================== */
const API_BASE = "/api";

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

function formatDetail(detail) {
  if (!detail) return null;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map(d => d.msg || JSON.stringify(d)).join("; ");
  }
  return JSON.stringify(detail);
}

async function api(method, path, body) {
  const opts = {
    method,
    credentials: "include",
    headers: {},
  };
  if (body !== undefined) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(API_BASE + path, opts);
  let data = null;
  try { data = await res.json(); } catch (e) { /* no body */ }

  if (!res.ok) {
    const message = formatDetail(data && data.detail) || (data && data.message) || `Error ${res.status}`;
    throw new ApiError(message, res.status, data);
  }
  return data;
}

const get = (path) => api("GET", path);
const post = (path, body) => api("POST", path, body);
const patch = (path, body) => api("PATCH", path, body);
const del = (path) => api("DELETE", path);

function qs(params) {
  const usable = Object.entries(params).filter(([, v]) => v !== "" && v !== null && v !== undefined);
  if (!usable.length) return "";
  return "?" + usable.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join("&");
}

/* ====================== state ====================== */
const state = {
  user: null,        // {id, email, name, role}
  view: "home",
  loading: false,
};

function normalizeRole(role) {
  if (!role) return null;
  const r = role.toLowerCase();
  if (r.includes("tenant")) return "tenant";
  if (r.includes("applicant")) return "applicant";
  if (r.includes("admin")) return "admin";
  return role;
}

/* ====================== toast ====================== */
function toast(message, type = "success") {
  const host = document.getElementById("toastHost");
  const el = document.createElement("div");
  el.className = `toast glass ${type}`;
  el.textContent = message;
  host.appendChild(el);
  setTimeout(() => {
    el.style.transition = "opacity 0.3s ease";
    el.style.opacity = "0";
    setTimeout(() => el.remove(), 300);
  }, 3200);
}

function reportError(err) {
  console.error(err);
  toast(err.message || "Something went wrong", "error");
}

/* ====================== modal ====================== */
function closeModal() {
  document.getElementById("modalHost").innerHTML = "";
}

function openModal(innerHtml, { onMount } = {}) {
  const host = document.getElementById("modalHost");
  host.innerHTML = `
    <div class="modal-backdrop" id="modalBackdrop">
      <div class="modal-box glass">${innerHtml}</div>
    </div>`;
  document.getElementById("modalBackdrop").addEventListener("click", (e) => {
    if (e.target.id === "modalBackdrop") closeModal();
  });
  if (onMount) onMount();
}

/* ====================== nav / shell ====================== */
function defaultViewForRole(role) {
  const r = normalizeRole(role);
  if (r === "tenant") return "search-resumes";
  if (r === "admin") return "admin";
  return "search-vacancies";
}

const NAV_BY_ROLE = {
  applicant: [
    { key: "search-vacancies", label: "Search vacancies" },
    { key: "my-resumes", label: "My resumes" },
    { key: "my-responses", label: "My applications" },
    { key: "mailbox", label: "Mail" },
    { key: "profile", label: "Profile" },
  ],
  tenant: [
    { key: "search-resumes", label: "Search resumes" },
    { key: "my-vacancies", label: "My vacancies" },
    { key: "mailbox", label: "Mail" },
    { key: "profile", label: "Profile" },
  ],
  admin: [
    { key: "admin", label: "Admin panel" },
    { key: "mailbox", label: "Mail" },
    { key: "profile", label: "Profile" },
  ],
};

function renderShell() {
  const navHost = document.getElementById("nav");
  const authHost = document.getElementById("authArea");

  if (!state.user) {
    navHost.innerHTML = "";
    // The landing page keeps the header intentionally minimal: only the logo.
    // Authentication actions are available in the hero instead.
    authHost.innerHTML = "";
  } else {
    const role = normalizeRole(state.user.role);
    const items = NAV_BY_ROLE[role] || [];
    navHost.innerHTML = items.map(i =>
      `<button data-key="${i.key}" class="${state.view === i.key ? "active" : ""}">${i.label}</button>`
    ).join("");
    navHost.querySelectorAll("button").forEach(btn => {
      btn.onclick = () => setView(btn.dataset.key);
    });
    authHost.innerHTML = `
      <span class="pill-badge">${role}</span>
      <span class="muted" style="font-size:14px;">${state.user.name}</span>
      <button class="btn btn-glass btn-sm" id="navLogout">Log out</button>`;
    authHost.querySelector("#navLogout").onclick = logout;
  }

}

async function setView(view) {
  state.view = view;
  renderShell();
  const app = document.getElementById("app");
  app.innerHTML = `<div class="center" style="padding:80px;"><div class="spinner"></div></div>`;
  try {
    switch (view) {
      case "home": renderHome(); break;
      case "login": renderLogin(); break;
      case "register": renderRegister(); break;
      case "search-vacancies": await renderSearchVacancies(); break;
      case "search-resumes": await renderSearchResumes(); break;
      case "my-vacancies": await renderMyVacancies(); break;
      case "my-resumes": await renderMyResumes(); break;
      case "my-responses": await renderMyResponses(); break;
      case "mailbox": await renderMailbox(); break;
      case "admin": await renderAdmin(); break;
      case "profile": await renderProfile(); break;
      default: renderHome();
    }
  } catch (err) {
    reportError(err);
    app.innerHTML = `<div class="empty-state">Failed to load the page</div>`;
  }
}

/* ====================== auth ====================== */
async function fetchMe() {
  try {
    const res = await get("/users/me");
    state.user = res.info;
  } catch (e) {
    state.user = null;
  }
}

async function logout() {
  state.user = null;
  toast("You have been logged out");
  setView("home");
}

function renderHome() {
  document.getElementById("app").innerHTML = `
    <div class="view">
      <div class="hero">
        <h1>Find a job.<br>Find an employee.</h1>
        <p>JJ is a platform for job seekers and employers: search for vacancies, resumes, and applications in one place.</p>
        <div class="landing-buttons">
          <button class="btn btn-primary" id="heroRegister">Get started</button>
          <button class="btn btn-secondary" id="heroLogin">I already have an account</button>
        </div>
      </div>
    </div>`;
  document.getElementById("heroRegister").onclick = () => setView("register");
  document.getElementById("heroLogin").onclick = () => setView("login");
}

function renderLogin() {
  document.getElementById("app").innerHTML = `
    <div class="view center" style="padding-top:20px;">
      <div class="panel glass" style="max-width:400px; width:100%;">
        <h2 class="section-title">Sign In</h2>
        <div class="field"><label>Email</label><input type="email" id="email"></div>
        <div class="field"><label>Password</label><input type="password" id="password"></div>
        <button class="btn btn-primary" id="submitLogin" style="width:100%;">Sign in</button>
        <p class="muted" style="text-align:center; margin-top:16px; font-size:14px;">
          Don't have an account? <a href="#" id="goRegister">Sign up</a>
        </p>
      </div>
    </div>`;
  document.getElementById("goRegister").onclick = (e) => { e.preventDefault(); setView("register"); };
  document.getElementById("submitLogin").onclick = async () => {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    try {
      await post("/users/sign_in", { email, password });
      await fetchMe();
      toast("Welcome");
      setView(defaultViewForRole(state.user.role));
    } catch (err) { reportError(err); }
  };
}

function renderRegister() {
  document.getElementById("app").innerHTML = `
    <div class="view center" style="padding-top:20px;">
      <div class="panel glass" style="max-width:440px; width:100%;">
        <h2 class="section-title">Sign Up</h2>
        <div class="field"><label>I want to</label>
          <select id="role">
            <option value="applicant">Find a job</option>
            <option value="tenant">Hire employees</option>
          </select>
        </div>
        <div class="field"><label>Name</label><input id="name" placeholder="3–15 characters, letters"></div>
        <div class="field"><label>Email</label><input type="email" id="email"></div>
        <div class="field"><label>Password</label><input type="password" id="password" placeholder="8–25 characters"></div>
        <div class="field"><label>Repeat password</label><input type="password" id="repeat_password"></div>
        <button class="btn btn-primary" id="submitRegister" style="width:100%;">Create account</button>
        <p class="muted" style="text-align:center; margin-top:16px; font-size:14px;">
          Already have an account? <a href="#" id="goLogin">Sign in</a>
        </p>
      </div>
    </div>`;
  document.getElementById("goLogin").onclick = (e) => { e.preventDefault(); setView("login"); };
  document.getElementById("submitRegister").onclick = async () => {
    const body = {
      role: document.getElementById("role").value,
      name: document.getElementById("name").value.trim(),
      email: document.getElementById("email").value.trim(),
      password: document.getElementById("password").value,
      repeat_password: document.getElementById("repeat_password").value,
    };
    try {
      await post("/users/sign_up", body);
      toast("Account created, please sign in now");
      setView("login");
    } catch (err) { reportError(err); }
  };
}

/* ====================== search: vacancies (applicant) ====================== */
async function renderSearchVacancies() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="view">
      <h2 class="section-title">Search Vacancies</h2>
      <div class="panel glass">
        <div class="form-row">
          <div class="field"><label>Job Title</label><input id="fTitle" placeholder="Python Developer"></div>
          <div class="field"><label>City</label><input id="fCity" placeholder="Almaty"></div>
          <div class="field"><label>Salary from</label><input id="fComp" type="number" min="0"></div>
        </div>
        <button class="btn btn-primary" id="doSearch">Search</button>
      </div>
      <div id="results" class="grid"></div>
    </div>`;

  const runSearch = async () => {
    const results = document.getElementById("results");
    results.innerHTML = `<div class="center" style="padding:40px; grid-column:1/-1;"><div class="spinner"></div></div>`;
    try {
      const params = {
        title: document.getElementById("fTitle").value.trim(),
        city: document.getElementById("fCity").value.trim(),
        compensation: document.getElementById("fComp").value,
      };
      const res = await get("/search/vacancies" + qs(params));
      const vacancies = res.vacancies || [];
      if (!vacancies.length) {
        results.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Nothing found</div>`;
        return;
      }
      results.innerHTML = vacancies.map(v => `
        <div class="card glass">
          <div class="card-top">
            <h3>${escapeHtml(v.title)}</h3>
          </div>
          <div class="meta">
            <span class="chip">📍 ${escapeHtml(v.city)}</span>
            <span class="chip money">${formatMoney(v.compensation)}</span>
          </div>
          <button class="btn btn-primary btn-sm" style="margin-top:16px;" data-id="${v.id}" data-title="${escapeAttr(v.title)}">Apply</button>
        </div>`).join("");
      results.querySelectorAll("button[data-id]").forEach(btn => {
        btn.onclick = () => openApplyModal(btn.dataset.id, btn.dataset.title);
      });
    } catch (err) {
      reportError(err);
      results.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Failed to load</div>`;
    }
  };

  document.getElementById("doSearch").onclick = runSearch;
  [document.getElementById("fTitle"), document.getElementById("fCity"), document.getElementById("fComp")]
    .forEach(el => el.addEventListener("keydown", e => { if (e.key === "Enter") runSearch(); }));

  await runSearch();
}

async function openApplyModal(vacancyId, vacancyTitle) {
  let myResumes = [];
  try {
    const res = await get("/resumes/my");
    myResumes = res.resumes || [];
  } catch (err) { reportError(err); return; }

  if (!myResumes.length) {
    openModal(`
      <h2>Resume Required</h2>
      <p class="muted">To apply, first create a resume in the "My resumes" section.</p>
      <div class="modal-actions"><button class="btn btn-glass" id="closeM">Close</button></div>`);
    document.getElementById("closeM").onclick = closeModal;
    return;
  }

  openModal(`
    <h2>Application for '${escapeHtml(vacancyTitle)}'</h2>
    <div class="field"><label>Resume</label>
      <select id="resumeSelect">
        ${myResumes.map(r => `<option value="${r.id}">${escapeHtml(r.title)}</option>`).join("")}
      </select>
    </div>
    <div class="field"><label>Cover Letter</label>
      <textarea id="coverLetter" maxlength="100" placeholder="A few words about yourself (up to 100 characters)"></textarea>
    </div>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelApply">Cancel</button>
      <button class="btn btn-primary" id="submitApply">Submit</button>
    </div>`);

  document.getElementById("cancelApply").onclick = closeModal;
  document.getElementById("submitApply").onclick = async () => {
    try {
      await post(`/responses/vacancies/${vacancyId}`, {
        resume_id: parseInt(document.getElementById("resumeSelect").value, 10),
        cover_letter: document.getElementById("coverLetter").value.trim(),
      });
      toast("Application sent!");
      closeModal();
    } catch (err) { reportError(err); }
  };
}

/* ====================== search: resumes (tenant) ====================== */
async function renderSearchResumes() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="view">
      <h2 class="section-title">Search Resumes</h2>
      <div class="panel glass">
        <div class="form-row">
          <div class="field"><label>Job Title</label><input id="fTitle" placeholder="FastAPI Developer"></div>
          <div class="field"><label>City</label><input id="fCity" placeholder="Almaty"></div>
          <div class="field"><label>Stack</label><input id="fStack" placeholder="Python, FastAPI"></div>
        </div>
        <button class="btn btn-primary" id="doSearch">Search</button>
      </div>
      <div id="results" class="grid"></div>
    </div>`;

  const runSearch = async () => {
    const results = document.getElementById("results");
    results.innerHTML = `<div class="center" style="padding:40px; grid-column:1/-1;"><div class="spinner"></div></div>`;
    try {
      const params = {
        title: document.getElementById("fTitle").value.trim(),
        city: document.getElementById("fCity").value.trim(),
        stack: document.getElementById("fStack").value.trim(),
      };
      const res = await get("/search/resumes" + qs(params));
      const resumes = res.resumes || [];
      if (!resumes.length) {
        results.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Nothing found</div>`;
        return;
      }
      results.innerHTML = resumes.map(r => `
        <div class="card glass">
          <h3>${escapeHtml(r.title)}</h3>
          <div class="meta">
            <span class="chip">📍 ${escapeHtml(r.city)}</span>
          </div>
          ${r.stack ? `<div class="meta" style="margin-top:8px;"><span class="chip">🛠 ${escapeHtml(r.stack)}</span></div>` : ""}
          ${r.about ? `<div class="about">${escapeHtml(r.about)}</div>` : ""}
          <button class="btn btn-primary btn-sm" style="margin-top:16px;" data-id="${r.id}" data-title="${escapeAttr(r.title)}">Invite</button>
        </div>`).join("");
      results.querySelectorAll("button[data-id]").forEach(btn => {
        btn.onclick = () => openInviteModal(btn.dataset.id, btn.dataset.title);
      });
    } catch (err) {
      reportError(err);
      results.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Failed to load</div>`;
    }
  };

  document.getElementById("doSearch").onclick = runSearch;
  [document.getElementById("fTitle"), document.getElementById("fCity"), document.getElementById("fStack")]
    .forEach(el => el.addEventListener("keydown", e => { if (e.key === "Enter") runSearch(); }));

  await runSearch();
}

async function openInviteModal(resumeId, resumeTitle) {
  let myVacancies = [];
  try {
    const res = await get("/vacancies/my");
    myVacancies = res.vacancies || [];
  } catch (err) { reportError(err); return; }

  if (!myVacancies.length) {
    openModal(`
      <h2>Vacancy Required</h2>
      <p class="muted">To invite, first create a vacancy in the "My vacancies" section.</p>
      <div class="modal-actions"><button class="btn btn-glass" id="closeM">Close</button></div>`);
    document.getElementById("closeM").onclick = closeModal;
    return;
  }

  openModal(`
    <h2>Invite '${escapeHtml(resumeTitle)}' to interview</h2>
    <div class="field"><label>Vacancy</label>
      <select id="vacancySelect">
        ${myVacancies.map(v => `<option value="${v.id}">${escapeHtml(v.title)}</option>`).join("")}
      </select>
    </div>
    <div class="field"><label>Cover Letter</label>
      <textarea id="coverLetter" maxlength="100" placeholder="A few words about the invitation (up to 100 characters)"></textarea>
    </div>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelInvite">Cancel</button>
      <button class="btn btn-primary" id="submitInvite">Submit</button>
    </div>`);

  document.getElementById("cancelInvite").onclick = closeModal;
  document.getElementById("submitInvite").onclick = async () => {
    try {
      await post(`/invitation/interview/${resumeId}`, {
        vacancy_id: parseInt(document.getElementById("vacancySelect").value, 10),
        cover_letter: document.getElementById("coverLetter").value.trim(),
      });
      toast("Invitation sent!");
      closeModal();
    } catch (err) { reportError(err); }
  };
}

/* ====================== my vacancies (tenant) ====================== */
async function renderMyVacancies() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="view">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
        <h2 class="section-title" style="margin:0;">My Vacancies</h2>
        <button class="btn btn-primary" id="createBtn">+ New Vacancy</button>
      </div>
      <div id="list" class="grid"></div>
    </div>`;

  document.getElementById("createBtn").onclick = () => openVacancyForm();

  await loadMyVacancies();
}

async function loadMyVacancies() {
  const list = document.getElementById("list");
  list.innerHTML = `<div class="center" style="padding:40px; grid-column:1/-1;"><div class="spinner"></div></div>`;
  try {
    const res = await get("/vacancies/my");
    const vacancies = res.vacancies || [];
    if (!vacancies.length) {
      list.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">You have no vacancies yet</div>`;
      return;
    }
    list.innerHTML = vacancies.map(v => `
      <div class="card glass">
        <h3>${escapeHtml(v.title)}</h3>
        <div class="meta">
          <span class="chip">📍 ${escapeHtml(v.city)}</span>
          <span class="chip money">${formatMoney(v.compensation)}</span>
        </div>
        <div style="display:flex; gap:8px; margin-top:16px; flex-wrap:wrap;">
          <button class="btn btn-glass btn-sm" data-act="responses" data-id="${v.id}" data-title="${escapeAttr(v.title)}">Applications</button>
          <button class="btn btn-glass btn-sm" data-act="edit" data-id="${v.id}">Edit</button>
          <button class="btn btn-danger btn-sm" data-act="delete" data-id="${v.id}">Delete</button>
        </div>
      </div>`).join("");

    list.querySelectorAll("button[data-act]").forEach(btn => {
      const id = btn.dataset.id;
      if (btn.dataset.act === "responses") btn.onclick = () => openResponsesModal(id, btn.dataset.title);
      if (btn.dataset.act === "edit") btn.onclick = () => openVacancyForm(vacancies.find(v => String(v.id) === id));
      if (btn.dataset.act === "delete") btn.onclick = () => deleteVacancy(id);
    });
  } catch (err) {
    reportError(err);
    list.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Failed to load</div>`;
  }
}

function openVacancyForm(existing) {
  const isEdit = !!existing;
  openModal(`
    <h2>${isEdit ? "Edit Vacancy" : "New Vacancy"}</h2>
    <div class="field"><label>Job Title</label><input id="vTitle" value="${isEdit ? escapeAttr(existing.title) : ""}" placeholder="4–30 characters"></div>
    <div class="field"><label>City</label><input id="vCity" value="${isEdit ? escapeAttr(existing.city) : ""}"></div>
    <div class="field"><label>Salary</label><input id="vComp" type="number" min="0" value="${isEdit ? existing.compensation : ""}"></div>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelV">Cancel</button>
      <button class="btn btn-primary" id="saveV">${isEdit ? "Save" : "Create"}</button>
    </div>`);

  document.getElementById("cancelV").onclick = closeModal;
  document.getElementById("saveV").onclick = async () => {
    const title = document.getElementById("vTitle").value.trim();
    const city = document.getElementById("vCity").value.trim();
    const compensation = parseInt(document.getElementById("vComp").value, 10);
    try {
      if (isEdit) {
        await patch(`/vacancies/${existing.id}`, { new_title: title, new_city: city, new_compensation: compensation });
        toast("Vacancy updated");
      } else {
        await post("/vacancies", { title, city, compensation });
        toast("Vacancy created");
      }
      closeModal();
      await loadMyVacancies();
    } catch (err) { reportError(err); }
  };
}

async function deleteVacancy(id) {
  openModal(`
    <h2>Delete Vacancy?</h2>
    <p class="muted">This action cannot be undone.</p>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelD">Cancel</button>
      <button class="btn btn-danger" id="confirmD">Delete</button>
    </div>`);
  document.getElementById("cancelD").onclick = closeModal;
  document.getElementById("confirmD").onclick = async () => {
    try {
      await del(`/vacancies/${id}`);
      toast("Vacancy deleted");
      closeModal();
      await loadMyVacancies();
    } catch (err) { reportError(err); }
  };
}

const STATUS_LABELS = {
  send: "Sent", viewed: "Viewed", shortlisted: "Shortlisted",
  interview: "Interview", hired: "Hired", rejected: "Rejected",
};

function tenantResponsesSearchMarkup(respState) {
  const statusOptions = ["", ...Object.keys(STATUS_LABELS).filter(s => s !== "send")]
    .map(s => `<option value="${s}" ${respState.status === s ? "selected" : ""}>${s === "" ? "All statuses" : STATUS_LABELS[s]}</option>`)
    .join("");
  return `
    <form id="respSearchForm" style="display:flex; gap:8px; align-items:end; margin-bottom:16px; flex-wrap:wrap;">
      <div class="field" style="flex:1; min-width:160px; margin:0;">
        <label>Search</label>
        <input name="q" placeholder="Title" value="${escapeAttr(respState.query)}">
      </div>
      <div class="field" style="min-width:150px; margin:0;">
        <label>Status</label>
        <select name="status">${statusOptions}</select>
      </div>
      <button class="btn btn-primary" type="submit">Search</button>
    </form>`;
}

async function openResponsesModal(vacancyId, title) {
  const respState = { query: "", status: "", offset: 0, limit: 10 };

  async function renderList() {
    const host = document.getElementById("respList");
    host.className = "center";
    host.style.padding = "30px";
    host.innerHTML = `<div class="spinner"></div>`;

    try {
      const res = await get("/responses" + qs({
        vacancy_id: vacancyId,
        title: respState.query,
        status: respState.status,
        limit: respState.limit,
        offset: respState.offset,
      }));
      const responses = res.responses || [];
      const total = res.total ?? responses.length;

      host.className = "";
      host.removeAttribute("style");

      if (!responses.length) {
        host.innerHTML = `<div class="empty-state">No applications</div>`;
        return;
      }

      host.innerHTML = `
        ${responses.map(r => `
          <div class="card glass" style="margin-bottom:12px;">
            <div class="card-top">
              <div>
                <h3 style="margin-bottom:2px;">Application #${r.id}</h3>
                <div class="muted" style="font-size:13px;">Applicant ID: ${r.applicant_id}</div>
              </div>
              <span class="status-badge status-${r.status}">${STATUS_LABELS[r.status] || r.status}</span>
            </div>
            ${r.resume ? `<div class="meta" style="margin-top:10px;">
              <span class="chip">${escapeHtml(r.resume.title)}</span>
              ${r.resume.stack ? `<span class="chip">🛠 ${escapeHtml(r.resume.stack)}</span>` : ""}
            </div>` : ""}
            <div class="field" style="margin-top:14px; margin-bottom:0;">
              <select data-resp="${r.id}">
                ${Object.keys(STATUS_LABELS).filter(s => s !== "send").map(s =>
                  `<option value="${s}" ${s === r.status ? "selected" : ""}>${STATUS_LABELS[s]}</option>`).join("")}
              </select>
            </div>
          </div>`).join("")}
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
          <span class="muted" style="font-size:13px;">Total: ${total}</span>
          <div style="display:flex; gap:8px;">
            <button class="btn btn-glass btn-sm" id="respPrev" ${respState.offset <= 0 ? "disabled" : ""}>Previous</button>
            <button class="btn btn-glass btn-sm" id="respNext" ${respState.offset + respState.limit >= total ? "disabled" : ""}>Next</button>
          </div>
        </div>`;

      host.querySelectorAll("select[data-resp]").forEach(sel => {
        sel.onchange = async () => {
          try {
            await patch(`/responses/${sel.dataset.resp}/status`, { status: sel.value });
            toast("Status updated");
          } catch (err) { reportError(err); }
        };
      });

      const prevBtn = document.getElementById("respPrev");
      const nextBtn = document.getElementById("respNext");
      if (prevBtn) prevBtn.onclick = () => { respState.offset = Math.max(0, respState.offset - respState.limit); renderList(); };
      if (nextBtn) nextBtn.onclick = () => { respState.offset += respState.limit; renderList(); };
    } catch (err) {
      reportError(err);
      host.innerHTML = `<div class="empty-state">Failed to load</div>`;
    }
  }

  openModal(`
    <h2>Applications: ${escapeHtml(title)}</h2>
    ${tenantResponsesSearchMarkup(respState)}
    <div id="respList" class="center" style="padding:30px;"><div class="spinner"></div></div>
    <div class="modal-actions"><button class="btn btn-glass" id="closeR">Close</button></div>`);

  document.getElementById("closeR").onclick = closeModal;
  document.getElementById("respSearchForm").onsubmit = (event) => {
    event.preventDefault();
    const form = event.target;
    respState.query = form.querySelector("input[name='q']").value.trim();
    respState.status = form.querySelector("select[name='status']").value;
    respState.offset = 0;
    renderList();
  };

  await renderList();
}

/* ====================== my resumes (applicant) ====================== */
async function renderMyResumes() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="view">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
        <h2 class="section-title" style="margin:0;">My Resumes</h2>
        <button class="btn btn-primary" id="createBtn">+ New Resume</button>
      </div>
      <div id="list" class="grid"></div>
    </div>`;
  document.getElementById("createBtn").onclick = () => openResumeForm();
  await loadMyResumes();
}

async function loadMyResumes() {
  const list = document.getElementById("list");
  list.innerHTML = `<div class="center" style="padding:40px; grid-column:1/-1;"><div class="spinner"></div></div>`;
  try {
    const res = await get("/resumes/my");
    const resumes = res.resumes || [];
    if (!resumes.length) {
      list.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">You have no resumes yet</div>`;
      return;
    }
    list.innerHTML = resumes.map(r => `
      <div class="card glass">
        <h3>${escapeHtml(r.title)}</h3>
        <div class="meta"><span class="chip">📍 ${escapeHtml(r.city)}</span></div>
        ${r.stack ? `<div class="meta" style="margin-top:8px;"><span class="chip">🛠 ${escapeHtml(r.stack)}</span></div>` : ""}
        ${r.about ? `<div class="about">${escapeHtml(r.about)}</div>` : ""}
        <div style="display:flex; gap:8px; margin-top:16px;">
          <button class="btn btn-glass btn-sm" data-act="edit" data-id="${r.id}">Edit</button>
          <button class="btn btn-danger btn-sm" data-act="delete" data-id="${r.id}">Delete</button>
        </div>
      </div>`).join("");

    list.querySelectorAll("button[data-act]").forEach(btn => {
      const id = btn.dataset.id;
      if (btn.dataset.act === "edit") btn.onclick = () => openResumeForm(resumes.find(r => String(r.id) === id));
      if (btn.dataset.act === "delete") btn.onclick = () => deleteResume(id);
    });
  } catch (err) {
    reportError(err);
    list.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Failed to load</div>`;
  }
}

function openResumeForm(existing) {
  const isEdit = !!existing;
  openModal(`
    <h2>${isEdit ? "Edit Resume" : "New Resume"}</h2>
    <div class="field"><label>Job Title</label><input id="rTitle" value="${isEdit ? escapeAttr(existing.title) : ""}"></div>
    <div class="field"><label>City</label><input id="rCity" value="${isEdit ? escapeAttr(existing.city) : ""}"></div>
    <div class="field"><label>Stack</label><input id="rStack" value="${isEdit ? escapeAttr(existing.stack) : ""}" placeholder="Python, FastAPI, PostgreSQL"></div>
    <div class="field"><label>About me</label><textarea id="rAbout">${isEdit ? escapeHtml(existing.about || "") : ""}</textarea></div>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelR">Cancel</button>
      <button class="btn btn-primary" id="saveR">${isEdit ? "Save" : "Create"}</button>
    </div>`);

  document.getElementById("cancelR").onclick = closeModal;
  document.getElementById("saveR").onclick = async () => {
    const title = document.getElementById("rTitle").value.trim();
    const city = document.getElementById("rCity").value.trim();
    const stack = document.getElementById("rStack").value.trim();
    const about = document.getElementById("rAbout").value.trim();
    try {
      if (isEdit) {
        await patch(`/resumes/${existing.id}`, { new_title: title, new_city: city, new_stack: stack, new_about: about });
        toast("Resume updated");
      } else {
        await post("/resumes", { title, city, stack, about });
        toast("Resume created");
      }
      closeModal();
      await loadMyResumes();
    } catch (err) { reportError(err); }
  };
}

async function deleteResume(id) {
  openModal(`
    <h2>Delete Resume?</h2>
    <p class="muted">This action cannot be undone.</p>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelD">Cancel</button>
      <button class="btn btn-danger" id="confirmD">Delete</button>
    </div>`);
  document.getElementById("cancelD").onclick = closeModal;
  document.getElementById("confirmD").onclick = async () => {
    try {
      await del(`/resumes/${id}`);
      toast("Resume deleted");
      closeModal();
      await loadMyResumes();
    } catch (err) { reportError(err); }
  };
}

/* ====================== my responses (applicant) ====================== */
async function renderMyResponses() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="view">
      <h2 class="section-title" style="margin-bottom:16px;">My Applications</h2>
      <div id="list" class="grid"></div>
    </div>`;
  await loadMyResponses();
}

async function loadMyResponses() {
  const list = document.getElementById("list");
  list.innerHTML = `<div class="center" style="padding:40px; grid-column:1/-1;"><div class="spinner"></div></div>`;
  try {
    const responses = await get("/responses/my");
    if (!responses.length) {
      list.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">You haven't applied to any vacancies yet</div>`;
      return;
    }
    list.innerHTML = responses.map(r => `
      <div class="card glass">
        <div class="card-top">
          <h3 style="margin:0;">${escapeHtml(r.vacancy.title)}</h3>
          <span class="status-badge status-${r.status}">${STATUS_LABELS[r.status] || r.status}</span>
        </div>
        <div class="meta" style="margin-top:6px;"><span class="chip">${escapeHtml(r.resume.title)}</span></div>
        ${r.cover_letter ? `<div class="about">${escapeHtml(r.cover_letter)}</div>` : ""}
        <div style="display:flex; gap:8px; margin-top:16px;">
          <button class="btn btn-danger btn-sm" data-act="delete" data-id="${r.id}">Delete</button>
        </div>
      </div>`).join("");

    list.querySelectorAll("button[data-act='delete']").forEach(btn => {
      btn.onclick = () => deleteMyResponse(btn.dataset.id);
    });
  } catch (err) {
    reportError(err);
    list.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Failed to load</div>`;
  }
}

async function deleteMyResponse(id) {
  openModal(`
    <h2>Delete Application?</h2>
    <p class="muted">This action cannot be undone.</p>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelD">Cancel</button>
      <button class="btn btn-danger" id="confirmD">Delete</button>
    </div>`);
  document.getElementById("cancelD").onclick = closeModal;
  document.getElementById("confirmD").onclick = async () => {
    try {
      await del("/responses" + qs({ response_id: id }));
      toast("Application deleted");
      closeModal();
      await loadMyResponses();
    } catch (err) { reportError(err); }
  };
}

/* ====================== mailbox (MailDev) ====================== */
async function renderMailbox() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="view">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
        <div>
          <h2 class="section-title" style="margin:0;">Mail</h2>
        </div>
        <div style="display:flex; gap:8px;">
          <button class="btn btn-glass btn-sm" id="refreshMail">Refresh</button>
          <button class="btn btn-danger btn-sm" id="clearMail">Clear My Mail</button>
        </div>
      </div>
      <div id="mailList"></div>
    </div>`;

  document.getElementById("refreshMail").onclick = loadMailbox;
  document.getElementById("clearMail").onclick = clearMailbox;
  await loadMailbox();
}

function isMailForCurrentUser(email) {
  const currentAddress = (state.user && state.user.email || "").trim().toLowerCase();
  return (email.to || []).some(recipient =>
    String(recipient.address || "").trim().toLowerCase() === currentAddress
  );
}

function visibleMailboxEmails(allEmails) {
  return allEmails.filter(isMailForCurrentUser);
}

async function loadMailbox() {
  const list = document.getElementById("mailList");
  list.innerHTML = `<div class="center" style="padding:40px;"><div class="spinner"></div></div>`;
  try {
    const res = await fetch("/mail/email", { credentials: "include" });
    if (!res.ok) throw new Error(`Error ${res.status}`);
    const allEmails = await res.json();
    // MailDev is a shared development inbox. Keep each user's view private in
    // the UI by showing only messages addressed to the signed-in user.
    const emails = visibleMailboxEmails(allEmails);

    if (!emails.length) {
      list.innerHTML = `<div class="empty-state">No emails yet</div>`;
      return;
    }

    emails.sort((a, b) => new Date(b.time) - new Date(a.time));
    list.innerHTML = emails.map(e => `
      <div class="card glass" data-id="${e.id}" style="cursor:pointer; margin-bottom:12px;">
        <div class="card-top">
          <div>
            <h3 style="margin-bottom:2px;">${escapeHtml(e.subject || "(no subject)")}</h3>
            <div class="muted" style="font-size:13px;">
              From: ${escapeHtml(formatMailAddr(e.from))} → To: ${escapeHtml(formatMailAddr(e.to))}
            </div>
          </div>
          <div class="muted" style="font-size:12px; white-space:nowrap;">${formatMailDate(e.time)}</div>
        </div>
      </div>`).join("");

    list.querySelectorAll(".card[data-id]").forEach(card => {
      card.onclick = () => openMailModal(card.dataset.id);
    });
  } catch (err) {
    reportError(err);
    list.innerHTML = `<div class="empty-state">Failed to load emails - check if MailDev is running</div>`;
  }
}

async function clearMailbox() {
  openModal(`
    <h2>Clear your mailbox?</h2>
    <p class="muted">Only emails addressed to your account will be deleted.</p>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelClear">Cancel</button>
      <button class="btn btn-danger" id="confirmClear">Clear My Mail</button>
    </div>`);
  document.getElementById("cancelClear").onclick = closeModal;
  document.getElementById("confirmClear").onclick = async () => {
    const button = document.getElementById("confirmClear");
    button.disabled = true;
    try {
      const res = await fetch("/mail/email", { credentials: "include" });
      if (!res.ok) throw new Error(`Error ${res.status}`);
      // Even administrators must only delete messages addressed to their own
      // account; the admin's broader read view must not affect this action.
      const emails = (await res.json()).filter(isMailForCurrentUser);

      // Delete the already filtered message ids one by one. MailDev has a
      // shared store, so never use its global "delete all" endpoint here.
      const results = await Promise.all(
        emails.map(email => fetch(`/mail/email/${encodeURIComponent(email.id)}`, {
          method: "DELETE",
          credentials: "include",
        }))
      );
      const failed = results.find(result => !result.ok);
      if (failed) throw new Error(`Error ${failed.status}`);

      toast(emails.length ? "Your mailbox was cleared" : "Your mailbox is already empty");
      closeModal();
      await loadMailbox();
    } catch (err) {
      reportError(err);
      button.disabled = false;
    }
  };
}

async function openMailModal(id) {
  openModal(`
    <h2>Email Message</h2>
    <div id="mailDetail" class="center" style="padding:30px;"><div class="spinner"></div></div>
    <div class="modal-actions"><button class="btn btn-glass" id="closeMail">Close</button></div>`);
  document.getElementById("closeMail").onclick = closeModal;

  try {
    const res = await fetch(`/mail/email/${id}`, { credentials: "include" });
    if (!res.ok) throw new Error(`Error ${res.status}`);
    const email = await res.json();

    const detail = document.getElementById("mailDetail");
    detail.className = "";
    detail.removeAttribute("style");
    detail.innerHTML = `
      <div class="field"><label>From</label><div>${escapeHtml(formatMailAddr(email.from))}</div></div>
      <div class="field"><label>To</label><div>${escapeHtml(formatMailAddr(email.to))}</div></div>
      <div class="field"><label>Subject</label><div>${escapeHtml(email.subject || "(no subject)")}</div></div>
      <div class="field">
        <label>Message Body</label>
        <div style="white-space:pre-wrap; background:rgba(255,255,255,0.6); border-radius:14px; padding:16px; border:1px solid rgba(120,120,128,0.22);">${escapeHtml(email.text || "(empty)")}</div>
      </div>`;
  } catch (err) {
    reportError(err);
    document.getElementById("mailDetail").innerHTML = `<div class="empty-state">Failed to load email</div>`;
  }
}

function formatMailAddr(arr) {
  if (!arr || !arr.length) return "—";
  return arr.map(a => a.name ? `${a.name} <${a.address}>` : a.address).join(", ");
}
function formatMailDate(d) {
  try { return new Date(d).toLocaleString("en-US"); } catch (e) { return d; }
}

/* ====================== admin ====================== */
const ADMIN_TABS = [
  { key: "users", label: "Users" },
  { key: "vacancies", label: "Vacancies" },
  { key: "resumes", label: "Resumes" },
  { key: "responses", label: "Applications" },
];

const adminState = { tab: "users", offset: 0, limit: 10, query: "", status: "" };

async function renderAdmin() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="view">
      <h2 class="section-title">Admin Panel</h2>
      <div class="tabs">
        ${ADMIN_TABS.map(t => `<button class="btn ${adminState.tab === t.key ? "btn-primary" : "btn-glass"} btn-sm" data-tab="${t.key}">${t.label}</button>`).join("")}
      </div>
      <div id="adminContent"></div>
    </div>`;

  app.querySelectorAll("[data-tab]").forEach(btn => {
    btn.onclick = () => {
      adminState.tab = btn.dataset.tab;
      adminState.offset = 0;
      adminState.query = "";
      adminState.status = "";
      renderAdmin();
    };
  });

  await loadAdminTab();
}

async function loadAdminTab() {
  const host = document.getElementById("adminContent");
  host.innerHTML = `<div class="center" style="padding:40px;"><div class="spinner"></div></div>`;
  try {
    if (adminState.tab === "users") await loadAdminUsers(host);
    if (adminState.tab === "vacancies") await loadAdminVacancies(host);
    if (adminState.tab === "resumes") await loadAdminResumes(host);
    if (adminState.tab === "responses") await loadAdminResponses(host);
  } catch (err) {
    reportError(err);
    host.innerHTML = `<div class="empty-state">Failed to load</div>`;
  }
}

function paginationControls(total) {
  const { offset, limit } = adminState;
  const page = Math.floor(offset / limit) + 1;
  const pages = Math.max(1, Math.ceil(total / limit));
  return `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:16px;">
      <span class="muted" style="font-size:13px;">Total: ${total} · page ${page} of ${pages}</span>
      <div style="display:flex; gap:8px;">
        <button class="btn btn-glass btn-sm" id="pgPrev" ${offset <= 0 ? "disabled" : ""}>Previous</button>
        <button class="btn btn-glass btn-sm" id="pgNext" ${offset + limit >= total ? "disabled" : ""}>Next</button>
      </div>
    </div>`;
}

function wirePagination() {
  const prev = document.getElementById("pgPrev");
  const next = document.getElementById("pgNext");
  if (prev) prev.onclick = () => { adminState.offset = Math.max(0, adminState.offset - adminState.limit); loadAdminTab(); };
  if (next) next.onclick = () => { adminState.offset += adminState.limit; loadAdminTab(); };
}

function wireAdminSearch(host, placeholder) {
  const form = host.querySelector("#adminSearchForm");
  if (!form) return;
  const input = form.querySelector("input");
  form.onsubmit = (event) => {
    event.preventDefault();
    adminState.query = input.value.trim();
    adminState.offset = 0;
    loadAdminTab();
  };
}

function adminSearchMarkup(placeholder) {
  return `
    <form id="adminSearchForm" class="panel glass" style="display:flex; gap:8px; align-items:end; margin-bottom:16px;">
      <div class="field" style="flex:1; margin:0;">
        <label>Search</label>
        <input name="q" placeholder="${placeholder}" value="${escapeAttr(adminState.query)}">
      </div>
      <button class="btn btn-primary" type="submit">Search</button>
    </form>`;
}

function confirmDelete(title, body, onConfirm) {
  openModal(`
    <h2>${title}</h2>
    <p class="muted">${body}</p>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelD">Cancel</button>
      <button class="btn btn-danger" id="confirmD">Delete</button>
    </div>`);
  document.getElementById("cancelD").onclick = closeModal;
  document.getElementById("confirmD").onclick = async () => {
    try {
      await onConfirm();
      closeModal();
      await loadAdminTab();
    } catch (err) { reportError(err); }
  };
}

/* ---- admin: users ---- */
async function loadAdminUsers(host) {
  const res = await get("/admin/users" + qs({ limit: adminState.limit, offset: adminState.offset }));
  const users = res.users || [];
  if (!users.length) { host.innerHTML = `<div class="empty-state">No users</div>`; return; }

  host.innerHTML = `
    <div class="panel glass" style="padding:8px;">
      ${users.map(u => `
        <div class="card" style="margin:8px 0;">
          <div class="card-top">
            <div>
              <h3 style="margin-bottom:2px;">${escapeHtml(u.name)}</h3>
              <div class="muted" style="font-size:13px;">${escapeHtml(u.email)}</div>
            </div>
            <span class="pill-badge">${normalizeRole(String(u.role))}</span>
          </div>
          <div style="display:flex; gap:8px; margin-top:14px; flex-wrap:wrap;">
            <button class="btn btn-glass btn-sm" data-act="edit" data-id="${u.id}">Edit</button>
            <button class="btn btn-danger btn-sm" data-act="delete" data-id="${u.id}">Delete</button>
          </div>
        </div>`).join("")}
    </div>
    ${paginationControls(res.total)}`;

  host.querySelectorAll("button[data-act]").forEach(btn => {
    const u = users.find(x => String(x.id) === btn.dataset.id);
    if (btn.dataset.act === "edit") btn.onclick = () => openAdminUserForm(u);
    if (btn.dataset.act === "delete") {
      btn.onclick = () => confirmDelete(
        "Delete User?",
        "This action cannot be undone - all their vacancies/resumes/applications will be deleted.",
        () => del(`/admin/users/${u.id}`).then(() => toast("User deleted"))
      );
    }
  });
  wirePagination();
}

function openAdminUserForm(user) {
  openModal(`
    <h2>User</h2>
    <div class="field"><label>Email</label><input value="${escapeAttr(user.email)}" disabled></div>
    <div class="field"><label>Name</label><input id="auName" value="${escapeAttr(user.name)}"></div>
    <div class="field"><label>Role</label>
      <select id="auRole">
        <option value="applicant" ${normalizeRole(String(user.role)) === "applicant" ? "selected" : ""}>Applicant</option>
        <option value="tenant" ${normalizeRole(String(user.role)) === "tenant" ? "selected" : ""}>Employer</option>
        <option value="admin" ${normalizeRole(String(user.role)) === "admin" ? "selected" : ""}>Admin</option>
      </select>
    </div>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelAU">Cancel</button>
      <button class="btn btn-primary" id="saveAU">Save</button>
    </div>`);
  document.getElementById("cancelAU").onclick = closeModal;
  document.getElementById("saveAU").onclick = async () => {
    try {
      await patch(`/admin/users/${user.id}`, {
        new_name: document.getElementById("auName").value.trim(),
        new_role: document.getElementById("auRole").value,
      });
      toast("User updated");
      closeModal();
      await loadAdminTab();
    } catch (err) { reportError(err); }
  };
}

/* ---- admin: vacancies ---- */
async function loadAdminVacancies(host) {
  const res = await get("/search/vacancies" + qs({
    title: adminState.query,
    limit: adminState.limit,
    offset: adminState.offset,
  }));

  const vacancies = res.vacancies || [];
  const total = res.total ?? vacancies.length;
  if (!vacancies.length) {
    host.innerHTML = adminSearchMarkup("Title or city") + `<div class="empty-state">No vacancies</div>`;
    wireAdminSearch(host);
    return;
  }

  host.innerHTML = `
    ${adminSearchMarkup("Title or city")}
    <div class="grid">
      ${vacancies.map(v => `
        <div class="card glass">
          <h3>${escapeHtml(v.title)}</h3>
          <div class="meta">
            <span class="chip">📍 ${escapeHtml(v.city)}</span>
            <span class="chip money">${formatMoney(v.compensation)}</span>
          </div>
          <div class="muted" style="font-size:12px; margin-top:8px;">tenant_id: ${v.tenant_id}</div>
          <div style="display:flex; gap:8px; margin-top:14px;">
            <button class="btn btn-glass btn-sm" data-act="edit" data-id="${v.id}">Edit</button>
            <button class="btn btn-danger btn-sm" data-act="delete" data-id="${v.id}">Delete</button>
          </div>
        </div>`).join("")}
    </div>
    ${paginationControls(total)}`;

  host.querySelectorAll("button[data-act]").forEach(btn => {
    const v = vacancies.find(x => String(x.id) === btn.dataset.id);
    if (btn.dataset.act === "edit") btn.onclick = () => openAdminVacancyForm(v);
    if (btn.dataset.act === "delete") {
      btn.onclick = () => confirmDelete(
        "Delete Vacancy?", "This action cannot be undone.",
        () => del(`/admin/vacancies/${v.id}`).then(() => toast("Vacancy deleted"))
      );
    }
  });
  wireAdminSearch(host);
  wirePagination();
}

function openAdminVacancyForm(v) {
  openModal(`
    <h2>Edit Vacancy</h2>
    <div class="field"><label>Job Title</label><input id="avTitle" value="${escapeAttr(v.title)}"></div>
    <div class="field"><label>City</label><input id="avCity" value="${escapeAttr(v.city)}"></div>
    <div class="field"><label>Salary</label><input id="avComp" type="number" value="${v.compensation}"></div>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelAV">Cancel</button>
      <button class="btn btn-primary" id="saveAV">Save</button>
    </div>`);
  document.getElementById("cancelAV").onclick = closeModal;
  document.getElementById("saveAV").onclick = async () => {
    try {
      await patch(`/admin/vacancies/${v.id}`, {
        new_title: document.getElementById("avTitle").value.trim(),
        new_city: document.getElementById("avCity").value.trim(),
        new_compensation: parseInt(document.getElementById("avComp").value, 10),
      });
      toast("Vacancy updated");
      closeModal();
      await loadAdminTab();
    } catch (err) { reportError(err); }
  };
}

/* ---- admin: resumes ---- */
async function loadAdminResumes(host) {
  const res = await get("/search/resumes" + qs({
    title: adminState.query,
    limit: adminState.limit,
    offset: adminState.offset,
  }));

  const resumes = res.resumes || [];
  const total = res.total ?? resumes.length;
  if (!resumes.length) {
    host.innerHTML = adminSearchMarkup("Title, city or stack") + `<div class="empty-state">No resumes</div>`;
    wireAdminSearch(host);
    return;
  }

  host.innerHTML = `
    ${adminSearchMarkup("Title, city or stack")}
    <div class="grid">
      ${resumes.map(r => `
        <div class="card glass">
          <h3>${escapeHtml(r.title)}</h3>
          <div class="meta"><span class="chip">📍 ${escapeHtml(r.city)}</span></div>
          ${r.stack ? `<div class="meta" style="margin-top:8px;"><span class="chip">🛠 ${escapeHtml(r.stack)}</span></div>` : ""}
          ${r.about ? `<div class="about">${escapeHtml(r.about)}</div>` : ""}
          <div class="muted" style="font-size:12px; margin-top:8px;">applicant_id: ${r.applicant_id}</div>
          <div style="display:flex; gap:8px; margin-top:14px;">
            <button class="btn btn-glass btn-sm" data-act="edit" data-id="${r.id}">Edit</button>
            <button class="btn btn-danger btn-sm" data-act="delete" data-id="${r.id}">Delete</button>
          </div>
        </div>`).join("")}
    </div>
    ${paginationControls(total)}`;

  host.querySelectorAll("button[data-act]").forEach(btn => {
    const r = resumes.find(x => String(x.id) === btn.dataset.id);
    if (btn.dataset.act === "edit") btn.onclick = () => openAdminResumeForm(r);
    if (btn.dataset.act === "delete") {
      btn.onclick = () => confirmDelete(
        "Delete Resume?", "This action cannot be undone.",
        () => del(`/admin/resumes/${r.id}`).then(() => toast("Resume deleted"))
      );
    }
  });
  wireAdminSearch(host);
  wirePagination();
}

function openAdminResumeForm(r) {
  openModal(`
    <h2>Edit Resume</h2>
    <div class="field"><label>Job Title</label><input id="arTitle" value="${escapeAttr(r.title)}"></div>
    <div class="field"><label>City</label><input id="arCity" value="${escapeAttr(r.city)}"></div>
    <div class="field"><label>Stack</label><input id="arStack" value="${escapeAttr(r.stack || "")}"></div>
    <div class="field"><label>About me</label><textarea id="arAbout">${escapeHtml(r.about || "")}</textarea></div>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelAR">Cancel</button>
      <button class="btn btn-primary" id="saveAR">Save</button>
    </div>`);
  document.getElementById("cancelAR").onclick = closeModal;
  document.getElementById("saveAR").onclick = async () => {
    try {
      await patch(`/admin/resumes/${r.id}`, {
        new_title: document.getElementById("arTitle").value.trim(),
        new_city: document.getElementById("arCity").value.trim(),
        new_stack: document.getElementById("arStack").value.trim(),
        new_about: document.getElementById("arAbout").value.trim(),
      });
      toast("Resume updated");
      closeModal();
      await loadAdminTab();
    } catch (err) { reportError(err); }
  };
}

/* ---- admin: responses ---- */
function responsesSearchMarkup() {
  const statuses = Object.keys(STATUS_LABELS);
  const activeStatus = adminState.status || statuses[0];
  const statusOptions = statuses
    .map(s => `<option value="${s}" ${activeStatus === s ? "selected" : ""}>${s === "send" ? "Send" : STATUS_LABELS[s]}</option>`)
    .join("");
  return `
    <form id="adminSearchForm" class="panel glass" style="display:flex; gap:8px; align-items:end; margin-bottom:16px; flex-wrap:wrap;">
      <div class="field" style="flex:1; min-width:180px; margin:0;">
        <label>Search</label>
        <input name="q" placeholder="Title or stack" value="${escapeAttr(adminState.query)}">
      </div>
      <div class="field" style="min-width:160px; margin:0;">
        <label>Status</label>
        <select name="status">
          ${statusOptions}
        </select>
      </div>
      <button class="btn btn-primary" type="submit">Search</button>
    </form>`;
}

function wireResponsesSearch(host) {
  const form = host.querySelector("#adminSearchForm");
  if (!form) return;
  form.onsubmit = (event) => {
    event.preventDefault();
    adminState.query = form.querySelector("input[name='q']").value.trim();
    adminState.status = form.querySelector("select[name='status']").value;
    adminState.offset = 0;
    loadAdminTab();
  };
}

async function loadAdminResponses(host) {
  const res = await get("/responses" + qs({
    title: adminState.query,
    status: adminState.status || Object.keys(STATUS_LABELS)[0],
    limit: adminState.limit,
    offset: adminState.offset,
  }));
  const responses = res.responses || [];
  const total = res.total ?? responses.length;

  if (!responses.length) {
    host.innerHTML = responsesSearchMarkup() + `<div class="empty-state">No applications</div>`;
    wireResponsesSearch(host);
    return;
  }

  host.innerHTML = `
    ${responsesSearchMarkup()}
    <div class="panel glass" style="padding:8px;">
      ${responses.map(r => `
        <div class="card" style="margin:8px 0;">
          <div class="card-top">
            <div>
              <div style="font-weight:700;">Application #${r.id}</div>
              <div class="muted" style="font-size:13px;">
                Applicant ID: ${r.applicant_id} · Resume ID: ${r.resume_id} · Vacancy ID: ${r.vacancy_id}
              </div>
            </div>
            <span class="status-badge status-${r.status}">${STATUS_LABELS[r.status] || r.status}</span>
          </div>
          ${r.resume ? `<div class="meta" style="margin-top:10px;">
            <span class="chip">📄 ${escapeHtml(r.resume.title)}</span>
            ${r.resume.stack ? `<span class="chip">🛠 ${escapeHtml(r.resume.stack)}</span>` : ""}
          </div>` : ""}
          <div style="margin-top:12px;">
            <button class="btn btn-danger btn-sm" data-act="delete" data-id="${r.id}">Delete</button>
          </div>
        </div>`).join("")}
    </div>
    ${paginationControls(total)}`;

  host.querySelectorAll("button[data-act]").forEach(btn => {
    btn.onclick = () => confirmDelete(
      "Delete Application?", "This action cannot be undone.",
      () => del(`/admin/responses/${btn.dataset.id}`).then(() => toast("Application deleted"))
    );
  });
  wireResponsesSearch(host);
  wirePagination();
}

/* ====================== profile ====================== */
async function renderProfile() {
  const app = document.getElementById("app");
  const role = normalizeRole(state.user.role);
  app.innerHTML = `
    <div class="view">
      <h2 class="section-title">Profile</h2>
      <div class="panel glass" style="max-width:480px;">
        <div class="field"><label>Email</label><input value="${escapeAttr(state.user.email)}" disabled></div>
        <div class="field"><label>Role</label><input value="${role}" disabled></div>
        <div class="field"><label>Name</label><input id="pName" value="${escapeAttr(state.user.name)}"></div>
        <button class="btn btn-primary" id="saveName">Save Name</button>
      </div>

      <div class="panel glass" style="max-width:480px;">
        <h3 style="margin-top:0;">Change Password</h3>
        <div class="field"><label>Current Password</label><input type="password" id="oldPass"></div>
        <div class="field"><label>New Password</label><input type="password" id="newPass"></div>
        <div class="field"><label>Repeat New Password</label><input type="password" id="repeatPass"></div>
        <button class="btn btn-primary" id="savePass">Change Password</button>
      </div>

      <div class="panel glass" style="max-width:480px;">
        <h3 style="margin-top:0; color:var(--danger);">Danger Zone</h3>
        <div class="field"><label>Password for Confirmation</label><input type="password" id="delPass"></div>
        <button class="btn btn-danger" id="deleteAcc">Delete Account</button>
      </div>
    </div>`;

  document.getElementById("saveName").onclick = async () => {
    try {
      await patch("/users/me/name", { new_name: document.getElementById("pName").value.trim() });
      await fetchMe();
      toast("Name updated");
      renderShell();
    } catch (err) { reportError(err); }
  };

  document.getElementById("savePass").onclick = async () => {
    try {
      await patch("/users/me/password", {
        old_password: document.getElementById("oldPass").value,
        new_password: document.getElementById("newPass").value,
        repeat_new_password: document.getElementById("repeatPass").value,
      });
      toast("Password changed");
      ["oldPass", "newPass", "repeatPass"].forEach(id => document.getElementById(id).value = "");
    } catch (err) { reportError(err); }
  };

  document.getElementById("deleteAcc").onclick = async () => {
    try {
      await api("DELETE", "/users/me", { password: document.getElementById("delPass").value });
      toast("Account deleted");
      state.user = null;
      setView("home");
    } catch (err) { reportError(err); }
  };
}

/* ====================== helpers ====================== */
function formatMoney(v) {
  if (v === null || v === undefined) return "—";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(v);
}
function escapeHtml(s) {
  if (s === null || s === undefined) return "";
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c]));
}
function escapeAttr(s) { return escapeHtml(s); }

/* ====================== theme ====================== */
function applyTheme(theme) {
  const isDark = theme === "dark";
  document.documentElement.classList.toggle("dark-theme", isDark);
  document.body.classList.toggle("dark-theme", isDark);
  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.querySelector(".theme-icon").innerHTML = isDark
      ? `<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.65 17.65l1.42 1.42M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.65 6.35l1.42-1.42"></path></svg>`
      : "☾";
    toggle.setAttribute("aria-label", isDark ? "Switch to light theme" : "Switch to dark theme");
    toggle.title = isDark ? "Switch to light theme" : "Switch to dark theme";
  }
}

function initTheme() {
  const savedTheme = localStorage.getItem("jj-theme");
  applyTheme(savedTheme === "dark" ? "dark" : "light");
  document.getElementById("themeToggle").onclick = () => {
    const nextTheme = document.body.classList.contains("dark-theme") ? "light" : "dark";
    localStorage.setItem("jj-theme", nextTheme);
    applyTheme(nextTheme);
  };
}

/* ====================== boot ====================== */
(async function init() {
  initTheme();
  await fetchMe();
  if (state.user) {
    setView(defaultViewForRole(state.user.role));
  } else {
    setView("home");
  }
})();