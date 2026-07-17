import { FormEvent, useEffect, useMemo, useState } from "react";

const PLATFORM_ADMIN_TOKEN = "local-dev-platform-admin-token";
const ACCESS_TOKEN_STORAGE_KEY = "cognos_ai_access_token";

type Company = {
  id: string;
  name: string;
  status: string;
};

type Project = {
  id: string;
  company_id: string;
  name: string;
  code: string | null;
  location: string | null;
  status: string;
  start_date: string | null;
  end_date: string | null;
  timezone: string;
  created_at: string;
};

type CompanyUser = {
  id: string;
  company_id: string;
  name: string;
  phone: string;
  email: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
};

type ProjectAssignment = {
  id: string;
  project_id: string;
  user_id: string;
  role_on_project: string;
  can_enter_progress: boolean;
  can_enter_manpower: boolean;
  can_enter_materials: boolean;
  can_view_dashboard: boolean;
  created_at: string;
};

type ProjectKnowledgeUpload = {
  id: string;
  company_id: string;
  project_id: string;
  uploaded_by: string | null;
  upload_type: string;
  file_name: string;
  storage_url: string | null;
  status: string;
  error_summary: string | null;
  uploaded_at: string;
};

type KnowledgeTemplateImportResult = {
  upload_id: string;
  upload_type: string;
  status: string;
  imported_count: number;
  skipped_count: number;
  error_count: number;
  errors: string[];
};

type AuthenticatedUser = {
  id: string;
  company_id: string;
  company_name: string;
  name: string;
  phone: string;
  email: string | null;
  role: string;
};

type LoginResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in_seconds: number;
  user: AuthenticatedUser;
};

type ProgressEntry = {
  id: string;
  activity_name: string;
  location_text: string | null;
  quantity: string;
  unit_symbol: string | null;
  work_date: string;
  status: string;
};

type ManpowerEntry = {
  id: string;
  trade_name: string;
  worker_count: number;
  location_text: string | null;
  work_date: string;
  status: string;
};

type MaterialTransaction = {
  id: string;
  transaction_type: "received" | "issued";
  material_name: string;
  quantity: string;
  unit_symbol: string | null;
  location_text: string | null;
  transaction_date: string;
  proof_status: string;
};

type MaterialStockBalance = {
  id: string;
  material_name: string;
  unit_symbol: string;
  total_received: string;
  total_issued: string;
  current_balance: string;
  low_stock_threshold: string | null;
};

type MediaFile = {
  id: string;
  media_type: string;
  storage_url: string;
  file_name: string | null;
  caption: string | null;
  processing_status: string;
  created_at: string;
};

type ReportingData = {
  progress: ProgressEntry[];
  manpower: ManpowerEntry[];
  materials: MaterialTransaction[];
  stock: MaterialStockBalance[];
  media: MediaFile[];
  access: ReportingAccess;
};

type ReportingAccess = {
  progress: boolean;
  manpower: boolean;
  materials: boolean;
  stock: boolean;
  media: boolean;
};

type AnalyticsRow = {
  label: string;
  value: string;
  helper?: string;
  percent?: number;
  tone?: "normal" | "warning" | "danger";
};

type DashboardAnalytics = {
  progressByLocation: AnalyticsRow[];
  manpowerByTrade: AnalyticsRow[];
  stockHighlights: AnalyticsRow[];
  attentionItems: AnalyticsRow[];
};

const moduleDefinitions = [
  { label: "Dashboard", id: "dashboard" },
  { label: "Projects", id: "projects" },
  { label: "Team", id: "team" },
  { label: "Knowledgebase", id: "knowledgebase" },
  { label: "Progress", id: "progress" },
  { label: "Manpower", id: "manpower" },
  { label: "Materials", id: "materials" },
  { label: "Images", id: "images" },
  { label: "Exports", id: "exports" },
  { label: "Settings", id: "settings" },
] as const;

const noReportingAccess: ReportingAccess = {
  progress: false,
  manpower: false,
  materials: false,
  stock: false,
  media: false,
};

const roleOptions = [
  { value: "owner", label: "Owner" },
  { value: "company_admin", label: "Company Admin" },
  { value: "project_manager", label: "Project Manager" },
  { value: "site_engineer", label: "Site Engineer" },
  { value: "supervisor", label: "Supervisor" },
  { value: "storekeeper", label: "Storekeeper" },
];

const knowledgeTemplateOptions = [
  { value: "units", label: "Units" },
  { value: "activities", label: "Activities" },
  { value: "locations", label: "Areas / sub-areas" },
  { value: "boq", label: "BOQ / material list" },
  { value: "schedule", label: "Schedule" },
];

const emptyReportingData: ReportingData = {
  progress: [],
  manpower: [],
  materials: [],
  stock: [],
  media: [],
  access: noReportingAccess,
};

const emptyNewUserForm = {
  name: "",
  phone: "",
  email: "",
  password: "Demo12345!",
  role: "site_engineer",
};

const emptyNewProjectForm = {
  name: "",
  code: "",
  location: "",
  status: "active",
  startDate: "",
  endDate: "",
  timezone: "Asia/Kolkata",
};

function defaultAssignmentForm() {
  return {
    userId: "",
    roleOnProject: "site_engineer",
    canEnterProgress: true,
    canEnterManpower: true,
    canEnterMaterials: false,
    canViewDashboard: true,
  };
}

export function App() {
  const [accessToken, setAccessToken] = useState(
    () => localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY) ?? "",
  );
  const [currentUser, setCurrentUser] = useState<AuthenticatedUser | null>(null);
  const [loginIdentifier, setLoginIdentifier] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [companies, setCompanies] = useState<Company[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState("");
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [reportingData, setReportingData] = useState<ReportingData>(emptyReportingData);
  const [companyUsers, setCompanyUsers] = useState<CompanyUser[]>([]);
  const [projectAssignments, setProjectAssignments] = useState<ProjectAssignment[]>([]);
  const [knowledgeUploads, setKnowledgeUploads] = useState<ProjectKnowledgeUpload[]>([]);
  const [newProjectForm, setNewProjectForm] = useState(emptyNewProjectForm);
  const [newUserForm, setNewUserForm] = useState(emptyNewUserForm);
  const [assignmentForm, setAssignmentForm] = useState(defaultAssignmentForm);
  const [knowledgeTemplateType, setKnowledgeTemplateType] = useState("boq");
  const [knowledgeFile, setKnowledgeFile] = useState<File | null>(null);
  const [loadingMessage, setLoadingMessage] = useState("Loading companies...");
  const [errorMessage, setErrorMessage] = useState("");
  const [projectMessage, setProjectMessage] = useState("");
  const [projectErrorMessage, setProjectErrorMessage] = useState("");
  const [teamMessage, setTeamMessage] = useState("");
  const [teamErrorMessage, setTeamErrorMessage] = useState("");
  const [knowledgeMessage, setKnowledgeMessage] = useState("");
  const [knowledgeErrorMessage, setKnowledgeErrorMessage] = useState("");

  useEffect(() => {
    if (!accessToken) {
      setLoadingMessage("");
      setCompanies([]);
      setProjects([]);
      setReportingData(emptyReportingData);
      return;
    }

    setLoadingMessage("Loading your account...");
    loadCurrentUser(accessToken)
      .then((user) => {
        setCurrentUser(user);
        setErrorMessage("");
        setLoadingMessage("Loading companies...");
        return loadCompanies(accessToken);
      })
      .then((loadedCompanies) => {
        setCompanies(loadedCompanies);
        setSelectedCompanyId(loadedCompanies[0]?.id ?? "");
        setErrorMessage("");
        setLoadingMessage("");
      })
      .catch((error: Error) => {
        setLoadingMessage("");
        setErrorMessage(error.message);
        handleLogout();
      });
  }, [accessToken]);

  useEffect(() => {
    if (!selectedCompanyId) {
      setProjects([]);
      setSelectedProjectId("");
      setReportingData(emptyReportingData);
      return;
    }

    setLoadingMessage("Loading projects...");
    loadProjects(selectedCompanyId, accessToken)
      .then((loadedProjects) => {
        setProjects(loadedProjects);
        setSelectedProjectId(loadedProjects[0]?.id ?? "");
        setErrorMessage("");
        setLoadingMessage("");
      })
      .catch((error: Error) => {
        setLoadingMessage("");
        setErrorMessage(error.message);
      });
  }, [selectedCompanyId, accessToken]);

  useEffect(() => {
    if (!selectedCompanyId || !selectedProjectId) {
      setReportingData(emptyReportingData);
      return;
    }

    setLoadingMessage("Loading reporting records...");
    loadReportingData(selectedCompanyId, selectedProjectId, accessToken)
      .then((data) => {
        setReportingData(data);
        setErrorMessage("");
        setLoadingMessage("");
      })
      .catch((error: Error) => {
        setLoadingMessage("");
        setErrorMessage(error.message);
      });
  }, [selectedCompanyId, selectedProjectId, accessToken]);

  useEffect(() => {
    if (!selectedCompanyId || !currentUser || !isCompanyAdmin(currentUser.role)) {
      setCompanyUsers([]);
      setProjectAssignments([]);
      return;
    }

    loadCompanyUsers(selectedCompanyId, accessToken)
      .then((loadedUsers) => {
        setCompanyUsers(loadedUsers);
        setTeamErrorMessage("");
      })
      .catch((error: Error) => {
        setCompanyUsers([]);
        setTeamErrorMessage(error.message);
      });
  }, [selectedCompanyId, currentUser, accessToken]);

  useEffect(() => {
    if (!selectedCompanyId || !selectedProjectId || !currentUser || !isCompanyAdmin(currentUser.role)) {
      setProjectAssignments([]);
      return;
    }

    loadProjectAssignments(selectedCompanyId, selectedProjectId, accessToken)
      .then((loadedAssignments) => {
        setProjectAssignments(loadedAssignments);
        setTeamErrorMessage("");
      })
      .catch((error: Error) => {
        setProjectAssignments([]);
        setTeamErrorMessage(error.message);
      });
  }, [selectedCompanyId, selectedProjectId, currentUser, accessToken]);

  useEffect(() => {
    if (!selectedCompanyId || !selectedProjectId || !currentUser || !isCompanyAdmin(currentUser.role)) {
      setKnowledgeUploads([]);
      return;
    }

    loadKnowledgeUploads(selectedCompanyId, selectedProjectId, accessToken)
      .then((uploads) => {
        setKnowledgeUploads(uploads);
        setKnowledgeErrorMessage("");
      })
      .catch((error: Error) => {
        setKnowledgeUploads([]);
        setKnowledgeErrorMessage(error.message);
      });
  }, [selectedCompanyId, selectedProjectId, currentUser, accessToken]);

  const filteredData = useMemo(
    () => filterReportingData(reportingData, fromDate, toDate),
    [reportingData, fromDate, toDate],
  );

  const summaryCards = useMemo(() => buildSummaryCards(filteredData), [filteredData]);
  const analytics = useMemo(() => buildDashboardAnalytics(filteredData), [filteredData]);
  const selectedCompany = companies.find((company) => company.id === selectedCompanyId);
  const selectedProject = projects.find((project) => project.id === selectedProjectId);
  const canManageTeam = currentUser ? isCompanyAdmin(currentUser.role) : false;
  const canManageProjects = currentUser ? isCompanyAdmin(currentUser.role) : false;
  const canManageKnowledgebase = currentUser ? isCompanyAdmin(currentUser.role) : false;
  const visibleModules = useMemo(
    () => buildVisibleModules(currentUser, reportingData),
    [currentUser, reportingData],
  );

  function handleLogout() {
    localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
    setAccessToken("");
    setCurrentUser(null);
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoadingMessage("Signing in...");
    setErrorMessage("");
    try {
      const response = await login(loginIdentifier, loginPassword);
      localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, response.access_token);
      setCurrentUser(response.user);
      setAccessToken(response.access_token);
      setLoginPassword("");
      setLoadingMessage("");
    } catch (error) {
      setLoadingMessage("");
      setErrorMessage(error instanceof Error ? error.message : "Login failed.");
    }
  }

  async function handleCreateProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCompanyId) {
      return;
    }

    setProjectMessage("");
    setProjectErrorMessage("");
    try {
      const createdProject = await createCompanyProject(
        selectedCompanyId,
        accessToken,
        newProjectForm,
      );
      setProjects((existingProjects) => [createdProject, ...existingProjects]);
      setSelectedProjectId(createdProject.id);
      setNewProjectForm(emptyNewProjectForm);
      setProjectMessage(`Created project ${createdProject.name}.`);
    } catch (error) {
      setProjectErrorMessage(error instanceof Error ? error.message : "Could not create project.");
    }
  }

  async function handleCreateUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCompanyId) {
      return;
    }

    setTeamMessage("");
    setTeamErrorMessage("");
    try {
      const createdUser = await createCompanyUser(selectedCompanyId, accessToken, newUserForm);
      setCompanyUsers((existingUsers) => [createdUser, ...existingUsers]);
      setNewUserForm(emptyNewUserForm);
      setTeamMessage(`Created ${createdUser.name}.`);
    } catch (error) {
      setTeamErrorMessage(error instanceof Error ? error.message : "Could not create user.");
    }
  }

  async function handleAssignUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCompanyId || !selectedProjectId || !assignmentForm.userId) {
      return;
    }

    setTeamMessage("");
    setTeamErrorMessage("");
    try {
      const createdAssignment = await assignUserToProject(
        selectedCompanyId,
        selectedProjectId,
        accessToken,
        assignmentForm,
      );
      setProjectAssignments((existingAssignments) => [createdAssignment, ...existingAssignments]);
      setAssignmentForm(defaultAssignmentForm());
      setTeamMessage("User assigned to the selected project.");
    } catch (error) {
      setTeamErrorMessage(error instanceof Error ? error.message : "Could not assign user.");
    }
  }

  async function handleDownloadKnowledgeTemplate(templateType: string) {
    if (!selectedCompanyId) {
      return;
    }

    setKnowledgeMessage("");
    setKnowledgeErrorMessage("");
    try {
      await downloadKnowledgeTemplate(selectedCompanyId, accessToken, templateType);
      setKnowledgeMessage(`Downloaded ${templateLabel(templateType)} template.`);
    } catch (error) {
      setKnowledgeErrorMessage(
        error instanceof Error ? error.message : "Could not download template.",
      );
    }
  }

  async function handleImportKnowledgeTemplate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCompanyId || !selectedProjectId || !knowledgeFile) {
      return;
    }

    setKnowledgeMessage("");
    setKnowledgeErrorMessage("");
    try {
      const result = await importKnowledgeTemplate(
        selectedCompanyId,
        selectedProjectId,
        accessToken,
        knowledgeTemplateType,
        knowledgeFile,
        currentUser?.id,
      );
      const uploads = await loadKnowledgeUploads(selectedCompanyId, selectedProjectId, accessToken);
      setKnowledgeUploads(uploads);
      setKnowledgeFile(null);
      setKnowledgeMessage(
        `Imported ${result.imported_count} row(s), skipped ${result.skipped_count}, errors ${result.error_count}.`,
      );
      if (result.errors.length > 0) {
        setKnowledgeErrorMessage(result.errors.slice(0, 3).join(" "));
      }
    } catch (error) {
      setKnowledgeErrorMessage(
        error instanceof Error ? error.message : "Could not import template.",
      );
    }
  }

  if (!accessToken) {
    return (
      <main className="login-page">
        <section className="login-card">
          <p className="eyebrow">Cognos AI</p>
          <h1>Sign in to the construction dashboard</h1>
          <p>
            Use a demo user created by the seed script, or any user that has been given a
            password by platform admin.
          </p>

          <form className="login-form" onSubmit={handleLogin}>
            <label>
              Email or phone
              <input
                value={loginIdentifier}
                onChange={(event) => setLoginIdentifier(event.target.value)}
                placeholder="owner-demo@example.com"
                required
              />
            </label>
            <label>
              Password
              <input
                type="password"
                value={loginPassword}
                onChange={(event) => setLoginPassword(event.target.value)}
                placeholder="At least 8 characters"
                required
              />
            </label>
            <button type="submit">Sign in</button>
          </form>

          {loadingMessage ? <p className="status-message">{loadingMessage}</p> : null}
          {errorMessage ? <p className="error-message">{errorMessage}</p> : null}
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Cognos AI</p>
          <h1>Construction Intelligence</h1>
        </div>

        <nav aria-label="Primary navigation">
          {visibleModules.map((module) => (
            <a href={`#${module.id}`} key={module.id}>
              {module.label}
            </a>
          ))}
        </nav>
      </aside>

      <section className="content">
        <header className="hero">
          <div>
            <p className="eyebrow">Live reporting dashboard</p>
            <h2>Review saved site updates by company, project, and date.</h2>
            <p>
              This view reads the backend reporting records created from confirmed WhatsApp updates.
              You are signed in as {currentUser?.name ?? "a dashboard user"} with{" "}
              {formatRole(currentUser?.role)} access.
            </p>
          </div>

          <div className="filter-stack">
            <div className="signed-in-card">
              <span>
                <strong>{currentUser?.company_name ?? "Signed in"}</strong>
                <small>{roleAccessSummary(currentUser)}</small>
              </span>
              <button type="button" onClick={handleLogout}>
                Sign out
              </button>
            </div>

            <label>
              Company
              <select
                value={selectedCompanyId}
                onChange={(event) => setSelectedCompanyId(event.target.value)}
              >
                {companies.length === 0 ? <option value="">No companies yet</option> : null}
                {companies.map((company) => (
                  <option value={company.id} key={company.id}>
                    {company.name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Project
              <select
                value={selectedProjectId}
                onChange={(event) => setSelectedProjectId(event.target.value)}
              >
                {projects.length === 0 ? <option value="">No projects yet</option> : null}
                {projects.map((project) => (
                  <option value={project.id} key={project.id}>
                    {project.name}
                    {project.code ? ` (${project.code})` : ""}
                  </option>
                ))}
              </select>
            </label>

            <div className="date-row">
              <label>
                From
                <input
                  type="date"
                  value={fromDate}
                  onChange={(event) => setFromDate(event.target.value)}
                />
              </label>
              <label>
                To
                <input
                  type="date"
                  value={toDate}
                  onChange={(event) => setToDate(event.target.value)}
                />
              </label>
            </div>
          </div>
        </header>

        {loadingMessage ? <p className="status-message">{loadingMessage}</p> : null}
        {errorMessage ? <p className="error-message">{errorMessage}</p> : null}

        {canManageProjects ? (
          <ProjectManagementPanel
            projects={projects}
            selectedProject={selectedProject}
            newProjectForm={newProjectForm}
            projectMessage={projectMessage}
            projectErrorMessage={projectErrorMessage}
            onNewProjectFormChange={setNewProjectForm}
            onCreateProject={handleCreateProject}
          />
        ) : null}

        {canManageTeam ? (
          <TeamManagementPanel
            users={companyUsers}
            assignments={projectAssignments}
            selectedProject={selectedProject}
            newUserForm={newUserForm}
            assignmentForm={assignmentForm}
            teamMessage={teamMessage}
            teamErrorMessage={teamErrorMessage}
            onNewUserFormChange={setNewUserForm}
            onAssignmentFormChange={setAssignmentForm}
            onCreateUser={handleCreateUser}
            onAssignUser={handleAssignUser}
          />
        ) : null}

        {canManageKnowledgebase ? (
          <KnowledgebaseManagementPanel
            uploads={knowledgeUploads}
            selectedProject={selectedProject}
            templateType={knowledgeTemplateType}
            selectedFile={knowledgeFile}
            knowledgeMessage={knowledgeMessage}
            knowledgeErrorMessage={knowledgeErrorMessage}
            onTemplateTypeChange={setKnowledgeTemplateType}
            onFileChange={setKnowledgeFile}
            onDownloadTemplate={handleDownloadKnowledgeTemplate}
            onImportTemplate={handleImportKnowledgeTemplate}
          />
        ) : null}

        <section className="card-grid" aria-label="Summary cards">
          {summaryCards.map((card) => (
            <article className={`summary-card ${card.tone}`} key={card.label}>
              <p>{card.label}</p>
              <strong>{card.value}</strong>
            </article>
          ))}
        </section>

        <section className="dashboard-grid analytics-grid" aria-label="Project manager analytics">
          {filteredData.access.progress ? (
            <AnalyticsPanel
              title="Progress by area"
              emptyMessage="No progress quantities recorded yet."
              rows={analytics.progressByLocation}
            />
          ) : null}
          {filteredData.access.manpower ? (
            <AnalyticsPanel
              title="Manpower distribution"
              emptyMessage="No manpower records yet."
              rows={analytics.manpowerByTrade}
            />
          ) : null}
          {filteredData.access.stock ? (
            <AnalyticsPanel
              title="Material stock highlights"
              emptyMessage="No material stock balances yet."
              rows={analytics.stockHighlights}
            />
          ) : null}
          <AnalyticsPanel
            title="Needs attention"
            emptyMessage="No attention items for this selection."
            rows={analytics.attentionItems}
          />
        </section>

        <section className="dashboard-grid">
          <article className="panel">
            <h3>Selected view</h3>
            <dl className="details-list">
              <div>
                <dt>Company</dt>
                <dd>{selectedCompany?.name ?? "Not selected"}</dd>
              </div>
              <div>
                <dt>Project</dt>
                <dd>{selectedProject?.name ?? "Not selected"}</dd>
              </div>
              <div>
                <dt>Date range</dt>
                <dd>{formatDateRange(fromDate, toDate)}</dd>
              </div>
            </dl>
          </article>

          <article className="panel">
            <h3>Export</h3>
            <p>
              Download the currently loaded and filtered records as CSV files. Excel can open
              these directly.
            </p>
            <div className="button-row">
              {filteredData.access.progress ? (
                <button onClick={() => exportCsv("progress", filteredData.progress)}>
                  Export progress
                </button>
              ) : null}
              {filteredData.access.manpower ? (
                <button onClick={() => exportCsv("manpower", filteredData.manpower)}>
                  Export manpower
                </button>
              ) : null}
              {filteredData.access.materials ? (
                <button onClick={() => exportCsv("materials", filteredData.materials)}>
                  Export materials
                </button>
              ) : null}
            </div>
            {!filteredData.access.progress &&
            !filteredData.access.manpower &&
            !filteredData.access.materials ? (
              <p className="muted-note">
                No exportable reporting sections are available for this role.
              </p>
            ) : null}
          </article>
        </section>

        {filteredData.access.progress ? (
          <ReportingTable
            title="Progress"
            emptyMessage="No confirmed progress entries for this selection yet."
            columns={["Date", "Activity", "Location", "Quantity", "Status"]}
            rows={filteredData.progress.map((entry) => [
              entry.work_date,
              entry.activity_name,
              entry.location_text ?? "-",
              `${entry.quantity} ${entry.unit_symbol ?? ""}`.trim(),
              entry.status,
            ])}
          />
        ) : (
          <RestrictedPanel
            title="Progress"
            message="Your project role does not include progress reporting access."
          />
        )}

        {filteredData.access.manpower ? (
          <ReportingTable
            title="Manpower"
            emptyMessage="No manpower entries for this selection yet."
            columns={["Date", "Trade", "Workers", "Location", "Status"]}
            rows={filteredData.manpower.map((entry) => [
              entry.work_date,
              entry.trade_name,
              String(entry.worker_count),
              entry.location_text ?? "-",
              entry.status,
            ])}
          />
        ) : (
          <RestrictedPanel
            title="Manpower"
            message="Your project role does not include manpower reporting access."
          />
        )}

        {filteredData.access.materials ? (
          <ReportingTable
            title="Material movement"
            emptyMessage="No material transactions for this selection yet."
            columns={["Date", "Type", "Material", "Quantity", "Location", "Proof"]}
            rows={filteredData.materials.map((entry) => [
              entry.transaction_date,
              entry.transaction_type,
              entry.material_name,
              `${entry.quantity} ${entry.unit_symbol ?? ""}`.trim(),
              entry.location_text ?? "-",
              entry.proof_status,
            ])}
          />
        ) : (
          <RestrictedPanel
            title="Material movement"
            message="Your project role does not include material reporting access."
          />
        )}

        <section className="dashboard-grid">
          {filteredData.access.stock ? (
            <ReportingTable
              title="Material stock"
              emptyMessage="No stock balances yet."
              columns={["Material", "Received", "Issued", "Balance"]}
              rows={filteredData.stock.map((entry) => [
                entry.material_name,
                `${entry.total_received} ${entry.unit_symbol}`,
                `${entry.total_issued} ${entry.unit_symbol}`,
                `${entry.current_balance} ${entry.unit_symbol}`,
              ])}
            />
          ) : null}

          {filteredData.access.media ? (
            <ReportingTable
              title="Image/proof files"
              emptyMessage="No media files yet."
              columns={["Created", "Type", "File", "Status"]}
              rows={filteredData.media.map((entry) => [
                formatDateTime(entry.created_at),
                entry.media_type,
                entry.file_name ?? entry.caption ?? entry.storage_url,
                entry.processing_status,
              ])}
            />
          ) : null}
        </section>
      </section>
    </main>
  );
}

function AnalyticsPanel({
  title,
  emptyMessage,
  rows,
}: {
  title: string;
  emptyMessage: string;
  rows: AnalyticsRow[];
}) {
  return (
    <article className="panel analytics-panel">
      <h3>{title}</h3>
      {rows.length === 0 ? (
        <p>{emptyMessage}</p>
      ) : (
        <div className="analytics-list">
          {rows.map((row) => (
            <div className={`analytics-row ${row.tone ?? "normal"}`} key={row.label}>
              <div className="analytics-row-header">
                <span>{row.label}</span>
                <strong>{row.value}</strong>
              </div>
              {row.percent !== undefined ? (
                <div className="mini-bar" aria-hidden="true">
                  <span style={{ width: `${Math.max(4, Math.min(100, row.percent))}%` }} />
                </div>
              ) : null}
              {row.helper ? <p>{row.helper}</p> : null}
            </div>
          ))}
        </div>
      )}
    </article>
  );
}

function ReportingTable({
  title,
  emptyMessage,
  columns,
  rows,
}: {
  title: string;
  emptyMessage: string;
  columns: string[];
  rows: string[][];
}) {
  return (
    <article className="panel table-panel">
      <h3>{title}</h3>
      {rows.length === 0 ? (
        <p>{emptyMessage}</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={`${title}-${rowIndex}`}>
                  {row.map((cell, cellIndex) => (
                    <td key={`${title}-${rowIndex}-${cellIndex}`}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </article>
  );
}

function RestrictedPanel({ title, message }: { title: string; message: string }) {
  return (
    <article className="panel restricted-panel">
      <h3>{title}</h3>
      <p>{message}</p>
    </article>
  );
}

function ProjectManagementPanel({
  projects,
  selectedProject,
  newProjectForm,
  projectMessage,
  projectErrorMessage,
  onNewProjectFormChange,
  onCreateProject,
}: {
  projects: Project[];
  selectedProject: Project | undefined;
  newProjectForm: typeof emptyNewProjectForm;
  projectMessage: string;
  projectErrorMessage: string;
  onNewProjectFormChange: (form: typeof emptyNewProjectForm) => void;
  onCreateProject: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <section className="management-section" id="projects">
      <div className="section-heading">
        <p className="eyebrow">Project management</p>
        <h3>Create projects and review project setup</h3>
        <p>
          Owner/admin users can create company projects from the dashboard. Project edit and
          archive actions are planned later.
        </p>
      </div>

      {projectMessage ? <p className="status-message">{projectMessage}</p> : null}
      {projectErrorMessage ? <p className="error-message">{projectErrorMessage}</p> : null}

      <section className="dashboard-grid">
        <article className="panel">
          <h3>Add project</h3>
          <form className="stacked-form" onSubmit={onCreateProject}>
            <label>
              Project name
              <input
                value={newProjectForm.name}
                onChange={(event) =>
                  onNewProjectFormChange({ ...newProjectForm, name: event.target.value })
                }
                placeholder="Green Residency"
                required
              />
            </label>
            <label>
              Project code
              <input
                value={newProjectForm.code}
                onChange={(event) =>
                  onNewProjectFormChange({ ...newProjectForm, code: event.target.value })
                }
                placeholder="GR-001"
              />
            </label>
            <label>
              Location
              <input
                value={newProjectForm.location}
                onChange={(event) =>
                  onNewProjectFormChange({ ...newProjectForm, location: event.target.value })
                }
                placeholder="Pune"
              />
            </label>
            <div className="date-row">
              <label>
                Start date
                <input
                  type="date"
                  value={newProjectForm.startDate}
                  onChange={(event) =>
                    onNewProjectFormChange({
                      ...newProjectForm,
                      startDate: event.target.value,
                    })
                  }
                />
              </label>
              <label>
                End date
                <input
                  type="date"
                  value={newProjectForm.endDate}
                  onChange={(event) =>
                    onNewProjectFormChange({
                      ...newProjectForm,
                      endDate: event.target.value,
                    })
                  }
                />
              </label>
            </div>
            <label>
              Timezone
              <input
                value={newProjectForm.timezone}
                onChange={(event) =>
                  onNewProjectFormChange({ ...newProjectForm, timezone: event.target.value })
                }
                placeholder="Asia/Kolkata"
                required
              />
            </label>
            <label>
              Status
              <select
                value={newProjectForm.status}
                onChange={(event) =>
                  onNewProjectFormChange({ ...newProjectForm, status: event.target.value })
                }
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="completed">Completed</option>
              </select>
            </label>
            <button type="submit">Create project</button>
          </form>
        </article>

        <article className="panel">
          <h3>Selected project</h3>
          <dl className="details-list">
            <div>
              <dt>Name</dt>
              <dd>{selectedProject?.name ?? "Not selected"}</dd>
            </div>
            <div>
              <dt>Code</dt>
              <dd>{selectedProject?.code ?? "-"}</dd>
            </div>
            <div>
              <dt>Location</dt>
              <dd>{selectedProject?.location ?? "-"}</dd>
            </div>
            <div>
              <dt>Schedule</dt>
              <dd>{formatProjectSchedule(selectedProject)}</dd>
            </div>
            <div>
              <dt>Timezone</dt>
              <dd>{selectedProject?.timezone ?? "-"}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{selectedProject ? formatRole(selectedProject.status) : "-"}</dd>
            </div>
          </dl>
        </article>
      </section>

      <ReportingTable
        title="Company projects"
        emptyMessage="No projects have been created yet."
        columns={["Name", "Code", "Location", "Schedule", "Status"]}
        rows={projects.map((project) => [
          project.name,
          project.code ?? "-",
          project.location ?? "-",
          formatProjectSchedule(project),
          formatRole(project.status),
        ])}
      />
    </section>
  );
}

function KnowledgebaseManagementPanel({
  uploads,
  selectedProject,
  templateType,
  selectedFile,
  knowledgeMessage,
  knowledgeErrorMessage,
  onTemplateTypeChange,
  onFileChange,
  onDownloadTemplate,
  onImportTemplate,
}: {
  uploads: ProjectKnowledgeUpload[];
  selectedProject: Project | undefined;
  templateType: string;
  selectedFile: File | null;
  knowledgeMessage: string;
  knowledgeErrorMessage: string;
  onTemplateTypeChange: (templateType: string) => void;
  onFileChange: (file: File | null) => void;
  onDownloadTemplate: (templateType: string) => void;
  onImportTemplate: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <section className="management-section" id="knowledgebase">
      <div className="section-heading">
        <p className="eyebrow">Project knowledgebase</p>
        <h3>Download templates and import project reference data</h3>
        <p>
          Upload project areas, activities, BOQ/materials, schedules, and units so the assistant can
          validate WhatsApp entries against real project data.
        </p>
      </div>

      {knowledgeMessage ? <p className="status-message">{knowledgeMessage}</p> : null}
      {knowledgeErrorMessage ? <p className="error-message">{knowledgeErrorMessage}</p> : null}

      <section className="dashboard-grid">
        <article className="panel">
          <h3>Download sample templates</h3>
          <p>Download a template, fill it in Excel, then upload it back for the selected project.</p>
          <div className="button-row">
            {knowledgeTemplateOptions.map((option) => (
              <button
                type="button"
                key={option.value}
                onClick={() => onDownloadTemplate(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </article>

        <article className="panel">
          <h3>Import completed template</h3>
          <p>
            Selected project: <strong>{selectedProject?.name ?? "No project selected"}</strong>
          </p>
          <form className="stacked-form" onSubmit={onImportTemplate}>
            <label>
              Template type
              <select
                value={templateType}
                onChange={(event) => onTemplateTypeChange(event.target.value)}
              >
                {knowledgeTemplateOptions.map((option) => (
                  <option value={option.value} key={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Completed .xlsx file
              <input
                type="file"
                accept=".xlsx"
                onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
              />
            </label>
            <p className="muted-note">
              {selectedFile ? `Selected: ${selectedFile.name}` : "Only .xlsx files are supported."}
            </p>
            <button type="submit" disabled={!selectedProject || !selectedFile}>
              Import template
            </button>
          </form>
        </article>
      </section>

      <ReportingTable
        title="Knowledgebase upload history"
        emptyMessage="No knowledgebase templates have been uploaded for this project yet."
        columns={["Uploaded", "Type", "File", "Status", "Errors"]}
        rows={uploads.map((upload) => [
          formatDateTime(upload.uploaded_at),
          templateLabel(upload.upload_type),
          upload.file_name,
          formatRole(upload.status),
          upload.error_summary ?? "-",
        ])}
      />
    </section>
  );
}

function TeamManagementPanel({
  users,
  assignments,
  selectedProject,
  newUserForm,
  assignmentForm,
  teamMessage,
  teamErrorMessage,
  onNewUserFormChange,
  onAssignmentFormChange,
  onCreateUser,
  onAssignUser,
}: {
  users: CompanyUser[];
  assignments: ProjectAssignment[];
  selectedProject: Project | undefined;
  newUserForm: typeof emptyNewUserForm;
  assignmentForm: ReturnType<typeof defaultAssignmentForm>;
  teamMessage: string;
  teamErrorMessage: string;
  onNewUserFormChange: (form: typeof emptyNewUserForm) => void;
  onAssignmentFormChange: (form: ReturnType<typeof defaultAssignmentForm>) => void;
  onCreateUser: (event: FormEvent<HTMLFormElement>) => void;
  onAssignUser: (event: FormEvent<HTMLFormElement>) => void;
}) {
  const assignedUserIds = new Set(assignments.map((assignment) => assignment.user_id));
  const assignableUsers = users.filter((user) => !assignedUserIds.has(user.id));

  function handleAssignmentRoleChange(role: string) {
    onAssignmentFormChange({
      ...assignmentForm,
      roleOnProject: role,
      ...defaultPermissionsForRole(role),
    });
  }

  return (
    <section className="team-section" id="team">
      <div className="section-heading">
        <p className="eyebrow">Team management</p>
        <h3>Manage company users and project access</h3>
        <p>
          Owner/admin users can add team members and assign them to the selected project with
          progress, manpower, material, and dashboard permissions.
        </p>
      </div>

      {teamMessage ? <p className="status-message">{teamMessage}</p> : null}
      {teamErrorMessage ? <p className="error-message">{teamErrorMessage}</p> : null}

      <section className="dashboard-grid">
        <article className="panel">
          <h3>Add user</h3>
          <form className="stacked-form" onSubmit={onCreateUser}>
            <label>
              Name
              <input
                value={newUserForm.name}
                onChange={(event) =>
                  onNewUserFormChange({ ...newUserForm, name: event.target.value })
                }
                placeholder="Site Engineer"
                required
              />
            </label>
            <label>
              Phone / WhatsApp number
              <input
                value={newUserForm.phone}
                onChange={(event) =>
                  onNewUserFormChange({ ...newUserForm, phone: event.target.value })
                }
                placeholder="+919999999999"
                required
              />
            </label>
            <label>
              Email
              <input
                type="email"
                value={newUserForm.email}
                onChange={(event) =>
                  onNewUserFormChange({ ...newUserForm, email: event.target.value })
                }
                placeholder="user@example.com"
              />
            </label>
            <label>
              Temporary password
              <input
                type="password"
                value={newUserForm.password}
                onChange={(event) =>
                  onNewUserFormChange({ ...newUserForm, password: event.target.value })
                }
                minLength={8}
                placeholder="At least 8 characters"
              />
            </label>
            <label>
              Company role
              <select
                value={newUserForm.role}
                onChange={(event) =>
                  onNewUserFormChange({ ...newUserForm, role: event.target.value })
                }
              >
                {roleOptions.map((role) => (
                  <option value={role.value} key={role.value}>
                    {role.label}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit">Create user</button>
          </form>
        </article>

        <article className="panel">
          <h3>Assign to selected project</h3>
          <p>
            Selected project: <strong>{selectedProject?.name ?? "No project selected"}</strong>
          </p>
          <form className="stacked-form" onSubmit={onAssignUser}>
            <label>
              User
              <select
                value={assignmentForm.userId}
                onChange={(event) =>
                  onAssignmentFormChange({ ...assignmentForm, userId: event.target.value })
                }
                required
              >
                <option value="">Choose user</option>
                {assignableUsers.map((user) => (
                  <option value={user.id} key={user.id}>
                    {user.name} ({formatRole(user.role)})
                  </option>
                ))}
              </select>
            </label>
            <label>
              Project role
              <select
                value={assignmentForm.roleOnProject}
                onChange={(event) => handleAssignmentRoleChange(event.target.value)}
              >
                {roleOptions.map((role) => (
                  <option value={role.value} key={role.value}>
                    {role.label}
                  </option>
                ))}
              </select>
            </label>
            <div className="checkbox-grid">
              <label>
                <input
                  type="checkbox"
                  checked={assignmentForm.canEnterProgress}
                  onChange={(event) =>
                    onAssignmentFormChange({
                      ...assignmentForm,
                      canEnterProgress: event.target.checked,
                    })
                  }
                />
                Progress
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={assignmentForm.canEnterManpower}
                  onChange={(event) =>
                    onAssignmentFormChange({
                      ...assignmentForm,
                      canEnterManpower: event.target.checked,
                    })
                  }
                />
                Manpower
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={assignmentForm.canEnterMaterials}
                  onChange={(event) =>
                    onAssignmentFormChange({
                      ...assignmentForm,
                      canEnterMaterials: event.target.checked,
                    })
                  }
                />
                Materials
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={assignmentForm.canViewDashboard}
                  onChange={(event) =>
                    onAssignmentFormChange({
                      ...assignmentForm,
                      canViewDashboard: event.target.checked,
                    })
                  }
                />
                Dashboard
              </label>
            </div>
            <button type="submit" disabled={!selectedProject || assignableUsers.length === 0}>
              Assign user
            </button>
          </form>
        </article>
      </section>

      <section className="dashboard-grid">
        <ReportingTable
          title="Company users"
          emptyMessage="No users have been added yet."
          columns={["Name", "Role", "Phone", "Email", "Status"]}
          rows={users.map((user) => [
            user.name,
            formatRole(user.role),
            user.phone,
            user.email ?? "-",
            user.is_active ? "Active" : "Inactive",
          ])}
        />
        <ReportingTable
          title="Selected project team"
          emptyMessage="No users are assigned to this project yet."
          columns={["User", "Project role", "Progress", "Manpower", "Materials", "Dashboard"]}
          rows={assignments.map((assignment) => {
            const user = users.find((candidate) => candidate.id === assignment.user_id);
            return [
              user?.name ?? assignment.user_id,
              formatRole(assignment.role_on_project),
              yesNo(assignment.can_enter_progress),
              yesNo(assignment.can_enter_manpower),
              yesNo(assignment.can_enter_materials),
              yesNo(assignment.can_view_dashboard),
            ];
          })}
        />
      </section>
    </section>
  );
}

async function login(identifier: string, password: string): Promise<LoginResponse> {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ identifier, password }),
  });

  if (!response.ok) {
    throw new Error("Invalid email/phone or password.");
  }

  return response.json() as Promise<LoginResponse>;
}

async function loadCurrentUser(accessToken: string): Promise<AuthenticatedUser> {
  return apiRequest<AuthenticatedUser>("/api/auth/me", accessToken);
}

async function loadCompanies(accessToken: string): Promise<Company[]> {
  return apiRequest<Company[]>("/api/companies", accessToken);
}

async function loadProjects(companyId: string, accessToken: string): Promise<Project[]> {
  return apiRequest<Project[]>(`/api/companies/${companyId}/projects`, accessToken);
}

async function createCompanyProject(
  companyId: string,
  accessToken: string,
  form: typeof emptyNewProjectForm,
): Promise<Project> {
  return apiRequest<Project>(`/api/companies/${companyId}/projects`, accessToken, {
    method: "POST",
    body: JSON.stringify({
      name: form.name.trim(),
      code: form.code.trim() || null,
      location: form.location.trim() || null,
      status: form.status,
      start_date: form.startDate || null,
      end_date: form.endDate || null,
      timezone: form.timezone.trim() || "Asia/Kolkata",
    }),
  });
}

async function loadKnowledgeUploads(
  companyId: string,
  projectId: string,
  accessToken: string,
): Promise<ProjectKnowledgeUpload[]> {
  return apiRequest<ProjectKnowledgeUpload[]>(
    `/api/companies/${companyId}/projects/${projectId}/knowledge-uploads`,
    accessToken,
  );
}

async function downloadKnowledgeTemplate(
  companyId: string,
  accessToken: string,
  templateType: string,
): Promise<void> {
  const response = await fetch(`/api/companies/${companyId}/knowledgebase/templates/${templateType}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new ApiRequestError(response.status, await errorDetail(response));
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${templateType}_template.xlsx`;
  link.click();
  URL.revokeObjectURL(url);
}

async function importKnowledgeTemplate(
  companyId: string,
  projectId: string,
  accessToken: string,
  uploadType: string,
  file: File,
  uploadedBy?: string,
): Promise<KnowledgeTemplateImportResult> {
  const formData = new FormData();
  formData.append("upload_type", uploadType);
  if (uploadedBy) {
    formData.append("uploaded_by", uploadedBy);
  }
  formData.append("file", file);

  const response = await fetch(
    `/api/companies/${companyId}/projects/${projectId}/knowledge-uploads/import`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: formData,
    },
  );

  if (!response.ok) {
    throw new ApiRequestError(response.status, await errorDetail(response));
  }

  return response.json() as Promise<KnowledgeTemplateImportResult>;
}

async function loadCompanyUsers(companyId: string, accessToken: string): Promise<CompanyUser[]> {
  return apiRequest<CompanyUser[]>(`/api/companies/${companyId}/users`, accessToken);
}

async function loadProjectAssignments(
  companyId: string,
  projectId: string,
  accessToken: string,
): Promise<ProjectAssignment[]> {
  return apiRequest<ProjectAssignment[]>(
    `/api/companies/${companyId}/projects/${projectId}/users`,
    accessToken,
  );
}

async function createCompanyUser(
  companyId: string,
  accessToken: string,
  form: typeof emptyNewUserForm,
): Promise<CompanyUser> {
  return apiRequest<CompanyUser>(`/api/companies/${companyId}/users`, accessToken, {
    method: "POST",
    body: JSON.stringify({
      name: form.name.trim(),
      phone: form.phone.trim(),
      email: form.email.trim() || null,
      password: form.password.trim() || undefined,
      role: form.role,
      is_active: true,
    }),
  });
}

async function assignUserToProject(
  companyId: string,
  projectId: string,
  accessToken: string,
  form: ReturnType<typeof defaultAssignmentForm>,
): Promise<ProjectAssignment> {
  return apiRequest<ProjectAssignment>(
    `/api/companies/${companyId}/projects/${projectId}/users`,
    accessToken,
    {
      method: "POST",
      body: JSON.stringify({
        user_id: form.userId,
        role_on_project: form.roleOnProject,
        can_enter_progress: form.canEnterProgress,
        can_enter_manpower: form.canEnterManpower,
        can_enter_materials: form.canEnterMaterials,
        can_view_dashboard: form.canViewDashboard,
      }),
    },
  );
}

async function loadReportingData(
  companyId: string,
  projectId: string,
  accessToken: string,
): Promise<ReportingData> {
  const basePath = `/api/companies/${companyId}/projects/${projectId}/reporting`;
  const [progress, manpower, materials, stock, media] = await Promise.all([
    optionalApiRequest<ProgressEntry[]>(`${basePath}/progress-entries`, accessToken, []),
    optionalApiRequest<ManpowerEntry[]>(`${basePath}/manpower-entries`, accessToken, []),
    optionalApiRequest<MaterialTransaction[]>(
      `${basePath}/material-transactions`,
      accessToken,
      [],
    ),
    optionalApiRequest<MaterialStockBalance[]>(
      `${basePath}/material-stock-balances`,
      accessToken,
      [],
    ),
    optionalApiRequest<MediaFile[]>(`${basePath}/media-files`, accessToken, []),
  ]);

  return {
    progress: progress.data,
    manpower: manpower.data,
    materials: materials.data,
    stock: stock.data,
    media: media.data,
    access: {
      progress: progress.available,
      manpower: manpower.available,
      materials: materials.available,
      stock: stock.available,
      media: media.available,
    },
  };
}

async function optionalApiRequest<T>(
  path: string,
  accessToken: string,
  fallback: T,
): Promise<{ data: T; available: boolean }> {
  try {
    return { data: await apiRequest<T>(path, accessToken), available: true };
  } catch (error) {
    if (error instanceof ApiRequestError && error.status === 403) {
      return { data: fallback, available: false };
    }
    throw error;
  }
}

class ApiRequestError extends Error {
  constructor(
    public status: number,
    public statusText: string,
  ) {
    super(`API request failed: ${status} ${statusText}`);
  }
}

async function apiRequest<T>(
  path: string,
  accessToken?: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(accessToken
        ? { Authorization: `Bearer ${accessToken}` }
        : { "X-Platform-Admin-Token": PLATFORM_ADMIN_TOKEN }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new ApiRequestError(response.status, await errorDetail(response));
  }

  return response.json() as Promise<T>;
}

async function errorDetail(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") {
      return body.detail;
    }
  } catch {
    // Fall back to HTTP status text when the API does not return JSON.
  }
  return response.statusText;
}

function filterReportingData(data: ReportingData, fromDate: string, toDate: string): ReportingData {
  return {
    progress: data.progress.filter((entry) => isDateInRange(entry.work_date, fromDate, toDate)),
    manpower: data.manpower.filter((entry) => isDateInRange(entry.work_date, fromDate, toDate)),
    materials: data.materials.filter((entry) =>
      isDateInRange(entry.transaction_date, fromDate, toDate),
    ),
    stock: data.stock,
    media: data.media.filter((entry) => isDateInRange(entry.created_at.slice(0, 10), fromDate, toDate)),
    access: data.access,
  };
}

function isDateInRange(date: string, fromDate: string, toDate: string): boolean {
  if (fromDate && date < fromDate) {
    return false;
  }
  if (toDate && date > toDate) {
    return false;
  }
  return true;
}

function buildSummaryCards(data: ReportingData) {
  const totalWorkers = data.manpower.reduce((sum, entry) => sum + entry.worker_count, 0);
  const materialReceived = data.materials.filter(
    (entry) => entry.transaction_type === "received",
  ).length;
  const materialIssued = data.materials.filter((entry) => entry.transaction_type === "issued").length;

  return [
    data.access.progress
      ? { label: "Progress entries", value: String(data.progress.length), tone: "blue" }
      : null,
    data.access.manpower
      ? { label: "Manpower count", value: String(totalWorkers), tone: "green" }
      : null,
    data.access.materials
      ? { label: "Material received", value: String(materialReceived), tone: "amber" }
      : null,
    data.access.materials
      ? { label: "Material issued", value: String(materialIssued), tone: "rose" }
      : null,
  ].filter((card): card is { label: string; value: string; tone: string } => card !== null);
}

function buildDashboardAnalytics(data: ReportingData): DashboardAnalytics {
  return {
    progressByLocation: buildProgressByLocation(data.progress),
    manpowerByTrade: buildManpowerByTrade(data.manpower),
    stockHighlights: buildStockHighlights(data.stock),
    attentionItems: buildAttentionItems(data),
  };
}

function buildProgressByLocation(progress: ProgressEntry[]): AnalyticsRow[] {
  const totals = new Map<string, number>();
  for (const entry of progress) {
    const key = entry.location_text || "Unspecified area";
    totals.set(key, (totals.get(key) ?? 0) + parseQuantity(entry.quantity));
  }
  const max = Math.max(...totals.values(), 0);
  return [...totals.entries()]
    .sort(([, left], [, right]) => right - left)
    .slice(0, 5)
    .map(([label, value]) => ({
      label,
      value: formatQuantity(value),
      helper: "Total recorded quantity across selected dates",
      percent: max > 0 ? (value / max) * 100 : 0,
    }));
}

function buildManpowerByTrade(manpower: ManpowerEntry[]): AnalyticsRow[] {
  const totals = new Map<string, number>();
  for (const entry of manpower) {
    totals.set(entry.trade_name, (totals.get(entry.trade_name) ?? 0) + entry.worker_count);
  }
  const max = Math.max(...totals.values(), 0);
  return [...totals.entries()]
    .sort(([, left], [, right]) => right - left)
    .slice(0, 5)
    .map(([label, value]) => ({
      label,
      value: String(value),
      helper: "Workers recorded in selected dates",
      percent: max > 0 ? (value / max) * 100 : 0,
    }));
}

function buildStockHighlights(stock: MaterialStockBalance[]): AnalyticsRow[] {
  return stock
    .map((entry) => {
      const balance = parseQuantity(entry.current_balance);
      const threshold = entry.low_stock_threshold ? parseQuantity(entry.low_stock_threshold) : null;
      const isLow = threshold !== null && balance <= threshold;
      const isNegative = balance < 0;
      const tone: AnalyticsRow["tone"] = isNegative ? "danger" : isLow ? "warning" : "normal";
      return {
        label: entry.material_name,
        value: `${entry.current_balance} ${entry.unit_symbol}`,
        helper:
          threshold === null
            ? "No low-stock threshold set"
            : `Low-stock threshold: ${entry.low_stock_threshold} ${entry.unit_symbol}`,
        tone,
        sortValue: isNegative ? -2 : isLow ? -1 : balance,
      };
    })
    .sort((left, right) => left.sortValue - right.sortValue)
    .slice(0, 5)
    .map(({ sortValue: _sortValue, ...row }) => row);
}

function buildAttentionItems(data: ReportingData): AnalyticsRow[] {
  const items: AnalyticsRow[] = [];
  const materialsMissingProof = data.materials.filter(
    (entry) => entry.proof_status !== "attached",
  ).length;
  const negativeStock = data.stock.filter((entry) => parseQuantity(entry.current_balance) < 0).length;
  const lowStock = data.stock.filter((entry) => {
    if (!entry.low_stock_threshold) {
      return false;
    }
    return parseQuantity(entry.current_balance) <= parseQuantity(entry.low_stock_threshold);
  }).length;
  const imagesUploaded = data.media.filter((entry) => entry.media_type === "image").length;

  if (materialsMissingProof > 0) {
    items.push({
      label: "Material entries without proof",
      value: String(materialsMissingProof),
      helper: "Ask site/store team to attach delivery or issue photos",
      tone: "warning",
    });
  }
  if (negativeStock > 0) {
    items.push({
      label: "Negative stock balances",
      value: String(negativeStock),
      helper: "Stock issued is higher than stock received",
      tone: "danger",
    });
  }
  if (lowStock > 0) {
    items.push({
      label: "Low-stock materials",
      value: String(lowStock),
      helper: "Review procurement needs",
      tone: "warning",
    });
  }
  if (data.progress.length > 0 && imagesUploaded === 0) {
    items.push({
      label: "Progress without images",
      value: String(data.progress.length),
      helper: "Progress is recorded, but no proof images are available in this selection",
      tone: "warning",
    });
  }

  return items;
}

function parseQuantity(value: string | number | null): number {
  if (value === null) {
    return 0;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function formatQuantity(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(2);
}

function exportCsv(fileName: string, rows: Record<string, unknown>[]) {
  if (rows.length === 0) {
    return;
  }

  const headers = Object.keys(rows[0]);
  const csv = [
    headers.join(","),
    ...rows.map((row) => headers.map((header) => csvCell(row[header])).join(",")),
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${fileName}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

function csvCell(value: unknown): string {
  const text = value === null || value === undefined ? "" : String(value);
  return `"${text.replace(/"/g, '""')}"`;
}

function formatDateRange(fromDate: string, toDate: string): string {
  if (!fromDate && !toDate) {
    return "All dates";
  }
  if (fromDate && toDate) {
    return `${fromDate} to ${toDate}`;
  }
  return fromDate ? `From ${fromDate}` : `Until ${toDate}`;
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString();
}

function formatProjectSchedule(project: Project | undefined): string {
  if (!project) {
    return "-";
  }
  if (project.start_date && project.end_date) {
    return `${project.start_date} to ${project.end_date}`;
  }
  if (project.start_date) {
    return `From ${project.start_date}`;
  }
  if (project.end_date) {
    return `Until ${project.end_date}`;
  }
  return "Not set";
}

function templateLabel(templateType: string): string {
  return (
    knowledgeTemplateOptions.find((option) => option.value === templateType)?.label ??
    formatRole(templateType)
  );
}

function buildVisibleModules(
  user: AuthenticatedUser | null,
  data: ReportingData,
): typeof moduleDefinitions[number][] {
  if (!user) {
    return moduleDefinitions.filter((module) => module.id === "dashboard");
  }

  const access = data.access;
  const hasLoadedAccess = Object.values(access).some(Boolean);
  const expectedAccess = expectedAccessForRole(user.role);
  const canSeeProgress = hasLoadedAccess ? access.progress : expectedAccess.progress;
  const canSeeManpower = hasLoadedAccess ? access.manpower : expectedAccess.manpower;
  const canSeeMaterials = hasLoadedAccess
    ? access.materials || access.stock
    : expectedAccess.materials;
  const canSeeImages = hasLoadedAccess ? access.media : expectedAccess.media;
  const isAdmin = isCompanyAdmin(user.role);

  return moduleDefinitions.filter((module) => {
    if (module.id === "dashboard" || module.id === "projects" || module.id === "exports") {
      return true;
    }
    if (module.id === "team" || module.id === "knowledgebase" || module.id === "settings") {
      return isAdmin;
    }
    if (module.id === "progress") {
      return canSeeProgress;
    }
    if (module.id === "manpower") {
      return canSeeManpower;
    }
    if (module.id === "materials") {
      return canSeeMaterials;
    }
    if (module.id === "images") {
      return canSeeImages;
    }
    return false;
  });
}

function expectedAccessForRole(role: string): ReportingAccess {
  if (isCompanyAdmin(role) || role === "project_manager") {
    return {
      progress: true,
      manpower: true,
      materials: true,
      stock: true,
      media: true,
    };
  }
  if (role === "site_engineer" || role === "supervisor") {
    return {
      progress: true,
      manpower: true,
      materials: false,
      stock: false,
      media: true,
    };
  }
  if (role === "storekeeper") {
    return {
      progress: false,
      manpower: false,
      materials: true,
      stock: true,
      media: true,
    };
  }
  return noReportingAccess;
}

function defaultPermissionsForRole(role: string) {
  if (isCompanyAdmin(role) || role === "project_manager") {
    return {
      canEnterProgress: true,
      canEnterManpower: true,
      canEnterMaterials: true,
      canViewDashboard: true,
    };
  }
  if (role === "site_engineer" || role === "supervisor") {
    return {
      canEnterProgress: true,
      canEnterManpower: true,
      canEnterMaterials: false,
      canViewDashboard: true,
    };
  }
  if (role === "storekeeper") {
    return {
      canEnterProgress: false,
      canEnterManpower: false,
      canEnterMaterials: true,
      canViewDashboard: true,
    };
  }
  return {
    canEnterProgress: false,
    canEnterManpower: false,
    canEnterMaterials: false,
    canViewDashboard: false,
  };
}

function isCompanyAdmin(role: string | undefined): boolean {
  return role === "owner" || role === "admin" || role === "company_admin";
}

function yesNo(value: boolean): string {
  return value ? "Yes" : "No";
}

function formatRole(role: string | undefined): string {
  if (!role) {
    return "dashboard";
  }
  return role
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function roleAccessSummary(user: AuthenticatedUser | null): string {
  if (!user) {
    return "Dashboard user";
  }
  if (isCompanyAdmin(user.role)) {
    return `${formatRole(user.role)} · company, team, projects, and reports`;
  }
  if (user.role === "project_manager") {
    return "Project Manager · assigned project reports";
  }
  if (user.role === "site_engineer" || user.role === "supervisor") {
    return `${formatRole(user.role)} · progress and manpower`;
  }
  if (user.role === "storekeeper") {
    return "Storekeeper · material received and issued";
  }
  return `${formatRole(user.role)} · limited project access`;
}
