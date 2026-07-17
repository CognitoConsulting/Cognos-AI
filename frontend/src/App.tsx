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
  status: string;
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

const emptyReportingData: ReportingData = {
  progress: [],
  manpower: [],
  materials: [],
  stock: [],
  media: [],
  access: noReportingAccess,
};

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
  const [loadingMessage, setLoadingMessage] = useState("Loading companies...");
  const [errorMessage, setErrorMessage] = useState("");

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

  const filteredData = useMemo(
    () => filterReportingData(reportingData, fromDate, toDate),
    [reportingData, fromDate, toDate],
  );

  const summaryCards = useMemo(() => buildSummaryCards(filteredData), [filteredData]);
  const analytics = useMemo(() => buildDashboardAnalytics(filteredData), [filteredData]);
  const selectedCompany = companies.find((company) => company.id === selectedCompanyId);
  const selectedProject = projects.find((project) => project.id === selectedProjectId);
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

async function apiRequest<T>(path: string, accessToken?: string): Promise<T> {
  const response = await fetch(path, {
    headers: {
      ...(accessToken
        ? { Authorization: `Bearer ${accessToken}` }
        : { "X-Platform-Admin-Token": PLATFORM_ADMIN_TOKEN }),
    },
  });

  if (!response.ok) {
    throw new ApiRequestError(response.status, response.statusText);
  }

  return response.json() as Promise<T>;
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
  const canSeeMaterials = hasLoadedAccess ? access.materials || access.stock : expectedAccess.materials;
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

function isCompanyAdmin(role: string | undefined): boolean {
  return role === "owner" || role === "admin" || role === "company_admin";
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
