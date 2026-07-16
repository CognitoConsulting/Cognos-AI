const summaryCards = [
  { label: "Progress entries today", value: "24", tone: "blue" },
  { label: "Manpower today", value: "148", tone: "green" },
  { label: "Materials received", value: "6", tone: "amber" },
  { label: "Needs review", value: "3", tone: "rose" },
];

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

export function App() {
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
            <p className="eyebrow">MVP dashboard foundation</p>
            <h2>Daily site reporting, validated against project knowledge.</h2>
            <p>
              Capture progress, manpower, material movement, images, and voice
              updates through WhatsApp. Review everything by project and date.
            </p>
          </div>

          <div className="project-filter">
            <label htmlFor="project">Project view</label>
            <select id="project" defaultValue="all">
              <option value="all">All selected projects</option>
              <option value="green-residency">Green Residency</option>
              <option value="tower-a">Tower A</option>
            </select>
          </div>
        </header>

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
            <h3>Plan vs actual</h3>
            <div className="bar-track">
              <span style={{ width: "68%" }} />
            </div>
            <p>68% of planned work is recorded as complete for selected areas.</p>
          </article>

          <article className="panel">
            <h3>Tomorrow&apos;s activities</h3>
            <ul>
              <li>Tower A Floor 3 plastering</li>
              <li>Block B brickwork balance</li>
              <li>Basement waterproofing inspection</li>
            </ul>
          </article>

          <article className="panel">
            <h3>Material stock</h3>
            <ul>
              <li>Cement: 80 bags</li>
              <li>Steel: 2.4 tons</li>
              <li>Tiles: 420 boxes</li>
            </ul>
          </article>

          <article className="panel">
            <h3>AI insights</h3>
            <p>
              Available for AI subscribers. This section will highlight unusual
              delays, missing updates, and potential material risks.
            </p>
          </article>
        </section>
      </section>
    </main>
  );
}

