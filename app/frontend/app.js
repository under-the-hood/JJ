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
    const message = formatDetail(data && data.detail) || (data && data.message) || `Ошибка ${res.status}`;
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
  toast(err.message || "Что-то пошло не так", "error");
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
const NAV_BY_ROLE = {
  applicant: [
    { key: "search-vacancies", label: "Поиск вакансий" },
    { key: "my-resumes", label: "Мои резюме" },
    { key: "profile", label: "Профиль" },
  ],
  tenant: [
    { key: "search-resumes", label: "Поиск резюме" },
    { key: "my-vacancies", label: "Мои вакансии" },
    { key: "profile", label: "Профиль" },
  ],
  admin: [
    { key: "profile", label: "Профиль" },
  ],
};

function renderShell() {
  const navHost = document.getElementById("nav");
  const authHost = document.getElementById("authArea");

  if (!state.user) {
    navHost.innerHTML = "";
    authHost.innerHTML = `
      <button class="btn btn-glass btn-sm" id="navLogin">Войти</button>
      <button class="btn btn-primary btn-sm" id="navRegister">Регистрация</button>`;
    authHost.querySelector("#navLogin").onclick = () => setView("login");
    authHost.querySelector("#navRegister").onclick = () => setView("register");
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
      <button class="btn btn-glass btn-sm" id="navLogout">Выйти</button>`;
    authHost.querySelector("#navLogout").onclick = logout;
  }

  document.querySelector(".brand").onclick = () => setView(state.user ? (normalizeRole(state.user.role) === "tenant" ? "search-resumes" : "search-vacancies") : "home");
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
      case "profile": await renderProfile(); break;
      default: renderHome();
    }
  } catch (err) {
    reportError(err);
    app.innerHTML = `<div class="empty-state">Не удалось загрузить страницу</div>`;
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
  // No dedicated logout endpoint on the backend — clearing local state is enough
  // for the UI; the cookie will simply stop being sent as "authenticated" once
  // the token naturally expires. If you add a logout endpoint later, call it here.
  state.user = null;
  toast("Вы вышли из аккаунта");
  setView("home");
}

function renderHome() {
  document.getElementById("app").innerHTML = `
    <div class="view">
      <div class="hero">
        <h1>Найди работу.<br>Найди человека.</h1>
        <p>JJ — платформа для соискателей и работодателей: поиск вакансий, резюме и отклики в одном месте.</p>
        <div style="margin-top:28px; display:flex; gap:12px; justify-content:center;">
          <button class="btn btn-primary" id="heroRegister">Начать</button>
          <button class="btn btn-glass" id="heroLogin">У меня уже есть аккаунт</button>
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
        <h2 class="section-title">Вход</h2>
        <div class="field"><label>Email</label><input type="email" id="email"></div>
        <div class="field"><label>Пароль</label><input type="password" id="password"></div>
        <button class="btn btn-primary" id="submitLogin" style="width:100%;">Войти</button>
        <p class="muted" style="text-align:center; margin-top:16px; font-size:14px;">
          Нет аккаунта? <a href="#" id="goRegister">Зарегистрироваться</a>
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
      toast("Добро пожаловать!");
      setView(normalizeRole(state.user.role) === "tenant" ? "search-resumes" : "search-vacancies");
    } catch (err) { reportError(err); }
  };
}

function renderRegister() {
  document.getElementById("app").innerHTML = `
    <div class="view center" style="padding-top:20px;">
      <div class="panel glass" style="max-width:440px; width:100%;">
        <h2 class="section-title">Регистрация</h2>
        <div class="field"><label>Я хочу</label>
          <select id="role">
            <option value="applicant">Искать работу</option>
            <option value="tenant">Нанимать сотрудников</option>
          </select>
        </div>
        <div class="field"><label>Имя</label><input id="name" placeholder="3–15 символов, буквы"></div>
        <div class="field"><label>Email</label><input type="email" id="email"></div>
        <div class="field"><label>Пароль</label><input type="password" id="password" placeholder="8–25 символов"></div>
        <div class="field"><label>Повторите пароль</label><input type="password" id="repeat_password"></div>
        <button class="btn btn-primary" id="submitRegister" style="width:100%;">Создать аккаунт</button>
        <p class="muted" style="text-align:center; margin-top:16px; font-size:14px;">
          Уже есть аккаунт? <a href="#" id="goLogin">Войти</a>
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
      toast("Аккаунт создан, теперь войдите");
      setView("login");
    } catch (err) { reportError(err); }
  };
}

/* ====================== search: vacancies (applicant) ====================== */
async function renderSearchVacancies() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="view">
      <h2 class="section-title">Поиск вакансий</h2>
      <div class="panel glass">
        <div class="form-row">
          <div class="field"><label>Должность</label><input id="fTitle" placeholder="Python developer"></div>
          <div class="field"><label>Город</label><input id="fCity" placeholder="Almaty"></div>
          <div class="field"><label>Зарплата от</label><input id="fComp" type="number" min="0"></div>
        </div>
        <button class="btn btn-primary" id="doSearch">Искать</button>
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
        results.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Ничего не найдено</div>`;
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
          <button class="btn btn-primary btn-sm" style="margin-top:16px;" data-id="${v.id}" data-title="${escapeAttr(v.title)}">Откликнуться</button>
        </div>`).join("");
      results.querySelectorAll("button[data-id]").forEach(btn => {
        btn.onclick = () => openApplyModal(btn.dataset.id, btn.dataset.title);
      });
    } catch (err) {
      reportError(err);
      results.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Не удалось загрузить</div>`;
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
      <h2>Нужно резюме</h2>
      <p class="muted">Чтобы откликнуться, сначала создайте резюме в разделе «Мои резюме».</p>
      <div class="modal-actions"><button class="btn btn-glass" id="closeM">Закрыть</button></div>`);
    document.getElementById("closeM").onclick = closeModal;
    return;
  }

  openModal(`
    <h2>Отклик на «${escapeHtml(vacancyTitle)}»</h2>
    <div class="field"><label>Резюме</label>
      <select id="resumeSelect">
        ${myResumes.map(r => `<option value="${r.id}">${escapeHtml(r.title)}</option>`).join("")}
      </select>
    </div>
    <div class="field"><label>Сопроводительное письмо</label>
      <textarea id="coverLetter" maxlength="100" placeholder="Пара слов о себе (до 100 символов)"></textarea>
    </div>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelApply">Отмена</button>
      <button class="btn btn-primary" id="submitApply">Отправить</button>
    </div>`);

  document.getElementById("cancelApply").onclick = closeModal;
  document.getElementById("submitApply").onclick = async () => {
    try {
      await post(`/responses/vacancies/${vacancyId}`, {
        resume_id: parseInt(document.getElementById("resumeSelect").value, 10),
        cover_letter: document.getElementById("coverLetter").value.trim(),
      });
      toast("Отклик отправлен!");
      closeModal();
    } catch (err) { reportError(err); }
  };
}

/* ====================== search: resumes (tenant) ====================== */
async function renderSearchResumes() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="view">
      <h2 class="section-title">Поиск резюме</h2>
      <div class="panel glass">
        <div class="form-row">
          <div class="field"><label>Должность</label><input id="fTitle" placeholder="FastAPI developer"></div>
          <div class="field"><label>Город</label><input id="fCity" placeholder="Almaty"></div>
          <div class="field"><label>Стек</label><input id="fStack" placeholder="Python, FastAPI"></div>
        </div>
        <button class="btn btn-primary" id="doSearch">Искать</button>
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
        results.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Ничего не найдено</div>`;
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
        </div>`).join("");
    } catch (err) {
      reportError(err);
      results.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Не удалось загрузить</div>`;
    }
  };

  document.getElementById("doSearch").onclick = runSearch;
  [document.getElementById("fTitle"), document.getElementById("fCity"), document.getElementById("fStack")]
    .forEach(el => el.addEventListener("keydown", e => { if (e.key === "Enter") runSearch(); }));

  await runSearch();
}

/* ====================== my vacancies (tenant) ====================== */
async function renderMyVacancies() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="view">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
        <h2 class="section-title" style="margin:0;">Мои вакансии</h2>
        <button class="btn btn-primary" id="createBtn">+ Новая вакансия</button>
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
      list.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">У вас пока нет вакансий</div>`;
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
          <button class="btn btn-glass btn-sm" data-act="responses" data-id="${v.id}" data-title="${escapeAttr(v.title)}">Отклики</button>
          <button class="btn btn-glass btn-sm" data-act="edit" data-id="${v.id}">Редактировать</button>
          <button class="btn btn-danger btn-sm" data-act="delete" data-id="${v.id}">Удалить</button>
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
    list.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Не удалось загрузить</div>`;
  }
}

function openVacancyForm(existing) {
  const isEdit = !!existing;
  openModal(`
    <h2>${isEdit ? "Редактировать вакансию" : "Новая вакансия"}</h2>
    <div class="field"><label>Должность</label><input id="vTitle" value="${isEdit ? escapeAttr(existing.title) : ""}" placeholder="4–30 символов"></div>
    <div class="field"><label>Город</label><input id="vCity" value="${isEdit ? escapeAttr(existing.city) : ""}"></div>
    <div class="field"><label>Зарплата</label><input id="vComp" type="number" min="0" value="${isEdit ? existing.compensation : ""}"></div>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelV">Отмена</button>
      <button class="btn btn-primary" id="saveV">${isEdit ? "Сохранить" : "Создать"}</button>
    </div>`);

  document.getElementById("cancelV").onclick = closeModal;
  document.getElementById("saveV").onclick = async () => {
    const title = document.getElementById("vTitle").value.trim();
    const city = document.getElementById("vCity").value.trim();
    const compensation = parseInt(document.getElementById("vComp").value, 10);
    try {
      if (isEdit) {
        await patch(`/vacancies/${existing.id}`, { new_title: title, new_city: city, new_compensation: compensation });
        toast("Вакансия обновлена");
      } else {
        await post("/vacancies", { title, city, compensation });
        toast("Вакансия создана");
      }
      closeModal();
      await loadMyVacancies();
    } catch (err) { reportError(err); }
  };
}

async function deleteVacancy(id) {
  openModal(`
    <h2>Удалить вакансию?</h2>
    <p class="muted">Это действие нельзя отменить.</p>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelD">Отмена</button>
      <button class="btn btn-danger" id="confirmD">Удалить</button>
    </div>`);
  document.getElementById("cancelD").onclick = closeModal;
  document.getElementById("confirmD").onclick = async () => {
    try {
      await del(`/vacancies/${id}`);
      toast("Вакансия удалена");
      closeModal();
      await loadMyVacancies();
    } catch (err) { reportError(err); }
  };
}

const STATUS_LABELS = {
  send: "Отправлен", viewed: "Просмотрен", shortlisted: "В шортлисте",
  interview: "Собеседование", hired: "Оффер", rejected: "Отказ",
};

async function openResponsesModal(vacancyId, title) {
  openModal(`
    <h2>Отклики: ${escapeHtml(title)}</h2>
    <div id="respList" class="center" style="padding:30px;"><div class="spinner"></div></div>
    <div class="modal-actions"><button class="btn btn-glass" id="closeR">Закрыть</button></div>`);
  document.getElementById("closeR").onclick = closeModal;

  try {
    const responses = await get(`/responses/vacancies/${vacancyId}`);
    const host = document.getElementById("respList");
    if (!responses.length) {
      host.innerHTML = `<div class="empty-state">Пока нет откликов</div>`;
      return;
    }
    host.innerHTML = responses.map(r => `
      <div class="card glass" style="margin-bottom:12px;">
        <div class="card-top">
          <div>
            <h3 style="margin-bottom:2px;">${escapeHtml(r.user.name)}</h3>
            <div class="muted" style="font-size:13px;">${escapeHtml(r.user.email)}</div>
          </div>
          <span class="status-badge status-${r.status}">${STATUS_LABELS[r.status] || r.status}</span>
        </div>
        <div class="meta" style="margin-top:10px;"><span class="chip">📄 ${escapeHtml(r.resume.title)}</span></div>
        ${r.cover_letter ? `<div class="about">${escapeHtml(r.cover_letter)}</div>` : ""}
        <div class="field" style="margin-top:14px; margin-bottom:0;">
          <select data-resp="${r.id}">
            ${Object.keys(STATUS_LABELS).filter(s => s !== "send").map(s =>
              `<option value="${s}" ${s === r.status ? "selected" : ""}>${STATUS_LABELS[s]}</option>`).join("")}
          </select>
        </div>
      </div>`).join("");

    host.querySelectorAll("select[data-resp]").forEach(sel => {
      sel.onchange = async () => {
        try {
          await patch(`/responses/${sel.dataset.resp}/status`, { status: sel.value });
          toast("Статус обновлён");
        } catch (err) { reportError(err); }
      };
    });
  } catch (err) {
    reportError(err);
    document.getElementById("respList").innerHTML = `<div class="empty-state">Не удалось загрузить</div>`;
  }
}

/* ====================== my resumes (applicant) ====================== */
async function renderMyResumes() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="view">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
        <h2 class="section-title" style="margin:0;">Мои резюме</h2>
        <button class="btn btn-primary" id="createBtn">+ Новое резюме</button>
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
      list.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">У вас пока нет резюме</div>`;
      return;
    }
    list.innerHTML = resumes.map(r => `
      <div class="card glass">
        <h3>${escapeHtml(r.title)}</h3>
        <div class="meta"><span class="chip">📍 ${escapeHtml(r.city)}</span></div>
        ${r.stack ? `<div class="meta" style="margin-top:8px;"><span class="chip">🛠 ${escapeHtml(r.stack)}</span></div>` : ""}
        ${r.about ? `<div class="about">${escapeHtml(r.about)}</div>` : ""}
        <div style="display:flex; gap:8px; margin-top:16px;">
          <button class="btn btn-glass btn-sm" data-act="edit" data-id="${r.id}">Редактировать</button>
          <button class="btn btn-danger btn-sm" data-act="delete" data-id="${r.id}">Удалить</button>
        </div>
      </div>`).join("");

    list.querySelectorAll("button[data-act]").forEach(btn => {
      const id = btn.dataset.id;
      if (btn.dataset.act === "edit") btn.onclick = () => openResumeForm(resumes.find(r => String(r.id) === id));
      if (btn.dataset.act === "delete") btn.onclick = () => deleteResume(id);
    });
  } catch (err) {
    reportError(err);
    list.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">Не удалось загрузить</div>`;
  }
}

function openResumeForm(existing) {
  const isEdit = !!existing;
  openModal(`
    <h2>${isEdit ? "Редактировать резюме" : "Новое резюме"}</h2>
    <div class="field"><label>Должность</label><input id="rTitle" value="${isEdit ? escapeAttr(existing.title) : ""}"></div>
    <div class="field"><label>Город</label><input id="rCity" value="${isEdit ? escapeAttr(existing.city) : ""}"></div>
    <div class="field"><label>Стек</label><input id="rStack" value="${isEdit ? escapeAttr(existing.stack) : ""}" placeholder="Python, FastAPI, PostgreSQL"></div>
    <div class="field"><label>О себе</label><textarea id="rAbout">${isEdit ? escapeHtml(existing.about || "") : ""}</textarea></div>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelR">Отмена</button>
      <button class="btn btn-primary" id="saveR">${isEdit ? "Сохранить" : "Создать"}</button>
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
        toast("Резюме обновлено");
      } else {
        await post("/resumes", { title, city, stack, about });
        toast("Резюме создано");
      }
      closeModal();
      await loadMyResumes();
    } catch (err) { reportError(err); }
  };
}

async function deleteResume(id) {
  openModal(`
    <h2>Удалить резюме?</h2>
    <p class="muted">Это действие нельзя отменить.</p>
    <div class="modal-actions">
      <button class="btn btn-glass" id="cancelD">Отмена</button>
      <button class="btn btn-danger" id="confirmD">Удалить</button>
    </div>`);
  document.getElementById("cancelD").onclick = closeModal;
  document.getElementById("confirmD").onclick = async () => {
    try {
      await del(`/resumes/${id}`);
      toast("Резюме удалено");
      closeModal();
      await loadMyResumes();
    } catch (err) { reportError(err); }
  };
}

/* ====================== profile ====================== */
async function renderProfile() {
  const app = document.getElementById("app");
  const role = normalizeRole(state.user.role);
  app.innerHTML = `
    <div class="view">
      <h2 class="section-title">Профиль</h2>
      <div class="panel glass" style="max-width:480px;">
        <div class="field"><label>Email</label><input value="${escapeAttr(state.user.email)}" disabled></div>
        <div class="field"><label>Роль</label><input value="${role}" disabled></div>
        <div class="field"><label>Имя</label><input id="pName" value="${escapeAttr(state.user.name)}"></div>
        <button class="btn btn-primary" id="saveName">Сохранить имя</button>
      </div>

      <div class="panel glass" style="max-width:480px;">
        <h3 style="margin-top:0;">Сменить пароль</h3>
        <div class="field"><label>Текущий пароль</label><input type="password" id="oldPass"></div>
        <div class="field"><label>Новый пароль</label><input type="password" id="newPass"></div>
        <div class="field"><label>Повторите новый пароль</label><input type="password" id="repeatPass"></div>
        <button class="btn btn-primary" id="savePass">Сменить пароль</button>
      </div>

      <div class="panel glass" style="max-width:480px;">
        <h3 style="margin-top:0; color:var(--danger);">Опасная зона</h3>
        <div class="field"><label>Пароль для подтверждения</label><input type="password" id="delPass"></div>
        <button class="btn btn-danger" id="deleteAcc">Удалить аккаунт</button>
      </div>
    </div>`;

  document.getElementById("saveName").onclick = async () => {
    try {
      await patch("/users/me/name", { new_name: document.getElementById("pName").value.trim() });
      await fetchMe();
      toast("Имя обновлено");
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
      toast("Пароль изменён");
      ["oldPass", "newPass", "repeatPass"].forEach(id => document.getElementById(id).value = "");
    } catch (err) { reportError(err); }
  };

  document.getElementById("deleteAcc").onclick = async () => {
    try {
      await api("DELETE", "/users/me", { password: document.getElementById("delPass").value });
      toast("Аккаунт удалён");
      state.user = null;
      setView("home");
    } catch (err) { reportError(err); }
  };
}

/* ====================== helpers ====================== */
function formatMoney(v) {
  if (v === null || v === undefined) return "—";
  return new Intl.NumberFormat("ru-RU").format(v) + " ₸";
}
function escapeHtml(s) {
  if (s === null || s === undefined) return "";
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c]));
}
function escapeAttr(s) { return escapeHtml(s); }

/* ====================== boot ====================== */
(async function init() {
  await fetchMe();
  if (state.user) {
    setView(normalizeRole(state.user.role) === "tenant" ? "search-resumes" : "search-vacancies");
  } else {
    setView("home");
  }
})();