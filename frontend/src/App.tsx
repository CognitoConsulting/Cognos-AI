import { useEffect, useMemo, useState } from "react";

const PLATFORM_ADMIN_TOKEN = "local-dev-platform-admin-token";

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

const modules = [
  "Dashboard",
  "Projects",
  "Team",
  "Knowledgebase",
  "Progress",
  "Manpower",
  "Materials",
  "Images",
  "Exports",
  "Settings",
];

const emptyReportingData: ReportingData = {
  progress: [],
  manpower: [],
  materials: [],
  stock: [],
  media: [],
};

export function App() {
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
    loadCompanies()
      .then((loadedCompanies) => {
        setCompanies(loadedCompanies);
        setSelectedCompanyId(loadedCompanies[0]?.id ?? "");
        setErrorMessage("");
        setLoadingMessage("");
      })
      .catch((error: Error) => {
        setLoadingMessage("");
        setErrorMessage(error.message);
      });
  }, []);

  useEffect(() => {
    if (!selectedCompanyId) {
      setProjects([]);
      setSelectedProjectId("");
      setReportingData(emptyReportingData);
      return;
    }

    setLoadingMessage("Loading projects...");
    loadProjects(selectedCompanyId)
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
  }, [selectedCompanyId]);

  useEffect(() => {
    if (!selectedCompanyId || !selectedProjectId) {
      setReportingData(emptyReportingData);
      return;
    }

    setLoadingMessage("Loading reporting records...");
    loadReportingData(selectedCompanyId, selectedProjectId)
      .then((data) => {
        setReportingData(data);
        setErrorMessage("");
        setLoadingMessage("");
      })
      .catch((error: Error) => {
        setLoadingMessage("");
        setErrorMessage(error.message);
      });
  }, [selectedCompanyId, selectedProjectId]);

  const filteredData = useMemo(
    () => filterReportingData(reportingData, fromDate, toDate),
    [reportingData, fromDate, toDate],
  );

  const summaryCards = useMemo(() => buildSummaryCards(filteredData), [filteredData]);
  const analytics = useMemo(() => buildDashboardAnalytics(filteredData), [filteredData]);
  const selectedCompany = companies.find((company) => company.id === selectedCompanyId);
  const selectedProject = projects.find((project) => project.id === selectedProjectId);

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Cognos AI</p>
          <h1>Construction Intelligence</h1>
        </div>

        <nav aria-label="Primary navigation">
          {modules.map((module) => (
            <a href={`#${module.toLowerCase()}`} key={module}>
              {module}
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
              This view reads the backend reporting records created from confirmed WhatsApp
              updates. It is still using the local platform-admin token until real login is added.
            </p>
          </div>

          <div className="filter-stack">
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
          <AnalyticsPanel
            title="Progress by area"
            emptyMessage="No progress quantities recorded yet."
            rows={analytics.progressByLocation}
          />
          <AnalyticsPanel
            title="Manpower distribution"
            emptyMessage="No manpower records yet."
            rows={analytics.manpowerByTrade}
          />
          <AnalyticsPanel
            title="Material stock highlights"
            emptyMessage="No material stock balances yet."
            rows={analytics.stockHighlights}
          />
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
              <button onClick={() => exportCsv("progress", filteredData.progress)}>
                Export progress
              </button>
              <button onClick={() => exportCsv("manpower", filteredData.manpower)}>
                Export manpower
              </button>
              <button onClick={() => exportCsv("materials", filteredData.materials)}>
                Export materials
              </button>
            </div>
          </article>
        </section>

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

        <section className="dashboard-grid">
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

async function loadCompanies(): Promise<Company[]> {
  return apiRequest<Company[]>("/api/companies");
}

async function loadProjects(companyId: string): Promise<Project[]> {
  return apiRequest<Project[]>(`/api/companies/${companyId}/projects`);
}

async function loadReportingData(companyId: string, projectId: string): Promise<ReportingData> {
  const basePath = `/api/companies/${companyId}/projects/${projectId}/reporting`;
  const [progress, manpower, materials, stock, media] = await Promise.all([
    apiRequest<ProgressEntry[]>(`${basePath}/progress-entries`),
    apiRequest<ManpowerEntry[]>(`${basePath}/manpower-entries`),
    apiRequest<MaterialTransaction[]>(`${basePath}/material-transactions`),
    apiRequest<MaterialStockBalance[]>(`${basePath}/material-stock-balances`),
    apiRequest<MediaFile[]>(`${basePath}/media-files`),
  ]);

  return { progress, manpower, materials, stock, media };
}

async function apiRequest<T>(path: string): Promise<T> {
  const response = await fetch(path, {
    headers: {
      "X-Platform-Admin-Token": PLATFORM_ADMIN_TOKEN,
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
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
    { label: "Progress entries", value: String(data.progress.length), tone: "blue" },
    { label: "Manpower count", value: String(totalWorkers), tone: "green" },
    { label: "Material received", value: String(materialReceived), tone: "amber" },
    { label: "Material issued", value: String(materialIssued), tone: "rose" },
  ];
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
