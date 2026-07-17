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
