import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";

const PLATFORM_ADMIN_TOKEN = "local-dev-platform-admin-token";
const ACCESS_TOKEN_STORAGE_KEY = "cognos_ai_access_token";

type Company = {
  id: string;
  name: string;
  status: string;
  ai_key_mode: string;
  ai_subscription_enabled: boolean;
  created_at: string;
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

type DailySummarySetting = {
  id: string;
  company_id: string;
  project_id: string;
  enabled: boolean;
  send_time_local: string;
  timezone: string;
  recipient_scope: string;
  created_at: string;
  updated_at: string;
};

type DailySummaryPreview = {
  project_id: string;
  summary_date: string;
  summary_text: string;
  recipient_count: number;
  send_time_local: string;
  timezone: string;
};

type DailySummaryMessage = {
  id: string;
  company_id: string;
  project_id: string;
  summary_date: string;
  summary_text: string;
  recipient_user_id: string | null;
  recipient_phone: string | null;
  whatsapp_message_id: string | null;
  delivery_status: string;
  trigger_type: string;
  triggered_by_user_id: string | null;
  created_at: string;
};

type DailySummarySendResult = {
  project_id: string;
  summary_date: string;
  recipient_count: number;
  sent_count: number;
  skipped_count: number;
  messages: DailySummaryMessage[];
};

type WhatsAppAuditMessage = {
  id: string;
  company_id: string | null;
  user_id: string | null;
  phone: string | null;
  direction: "inbound" | "outbound" | string;
  message_text: string | null;
  provider_name: string;
  provider_message_id: string | null;
  provider_account_id: string | null;
  processing_status: string;
  received_at: string;
};

type WhatsAppProviderAccount = {
  id: string;
  company_id: string;
  provider_name: string;
  provider_account_id: string | null;
  webhook_url: string | null;
  phone_number_id: string | null;
  status: string;
  created_at: string;
};

type VoiceNote = {
  id: string;
  company_id: string;
  project_id: string | null;
  uploaded_by: string | null;
  source_whatsapp_message_id: string | null;
  storage_url: string;
  file_name: string | null;
  provider_media_id: string | null;
  mime_type: string | null;
  transcription_status: string;
  transcription_provider: string | null;
  transcript_text: string | null;
  transcript_language: string | null;
  error_message: string | null;
  captured_at: string | null;
  created_at: string;
};

type AssistantParseResult = {
  id: string;
  company_id: string | null;
  user_id: string | null;
  whatsapp_message_id: string;
  intent: string;
  confidence: string;
  input_language: string | null;
  extracted_data: Record<string, unknown>;
  missing_fields: string[];
  validation_status: string;
  assistant_summary: string | null;
  next_action: string;
  created_at: string;
};

type AssistantConversationState = {
  id: string;
  company_id: string | null;
  user_id: string | null;
  whatsapp_message_id: string;
  parse_result_id: string;
  status: string;
  pending_intent: string;
  pending_data: Record<string, unknown>;
  missing_fields: string[];
  confirmation_prompt: string | null;
  last_user_message: string | null;
  created_at: string;
  updated_at: string;
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
  linked_entity_type: string | null;
  linked_entity_id: string | null;
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

type SummaryCard = {
  label: string;
  value: string;
  helper: string;
  tone: string;
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
  { label: "WhatsApp", id: "whatsapp" },
  { label: "Assistant", id: "assistant" },
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

const emptyDailySummaryForm = {
  enabled: true,
  sendTimeLocal: "19:00",
  timezone: "Asia/Kolkata",
  recipientScope: "dashboard_users",
};

const emptyWhatsAppProviderForm = {
  providerName: "generic",
  providerAccountId: "local-test-account",
  phoneNumberId: "local-test-number",
  webhookUrl: "",
  status: "active",
};

const emptyAiConfigurationForm = {
  aiKeyMode: "platform_managed",
  aiSubscriptionEnabled: false,
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
  const [dailySummarySetting, setDailySummarySetting] = useState<DailySummarySetting | null>(null);
  const [dailySummaryPreview, setDailySummaryPreview] = useState<DailySummaryPreview | null>(null);
  const [dailySummaryMessages, setDailySummaryMessages] = useState<DailySummaryMessage[]>([]);
  const [whatsAppProviderAccounts, setWhatsAppProviderAccounts] = useState<WhatsAppProviderAccount[]>([]);
  const [whatsAppMessages, setWhatsAppMessages] = useState<WhatsAppAuditMessage[]>([]);
  const [voiceNotes, setVoiceNotes] = useState<VoiceNote[]>([]);
  const [assistantParseResults, setAssistantParseResults] = useState<AssistantParseResult[]>([]);
  const [assistantConversationStates, setAssistantConversationStates] = useState<
    AssistantConversationState[]
  >([]);
  const [dailySummaryForm, setDailySummaryForm] = useState(emptyDailySummaryForm);
  const [whatsAppProviderForm, setWhatsAppProviderForm] = useState(emptyWhatsAppProviderForm);
  const [aiConfigurationForm, setAiConfigurationForm] = useState(emptyAiConfigurationForm);
  const [dailySummaryDate, setDailySummaryDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [loadingMessage, setLoadingMessage] = useState("Loading companies...");
  const [errorMessage, setErrorMessage] = useState("");
  const [projectMessage, setProjectMessage] = useState("");
  const [projectErrorMessage, setProjectErrorMessage] = useState("");
  const [teamMessage, setTeamMessage] = useState("");
  const [teamErrorMessage, setTeamErrorMessage] = useState("");
  const [knowledgeMessage, setKnowledgeMessage] = useState("");
  const [knowledgeErrorMessage, setKnowledgeErrorMessage] = useState("");
  const [dailySummaryMessage, setDailySummaryMessage] = useState("");
  const [dailySummaryErrorMessage, setDailySummaryErrorMessage] = useState("");
  const [whatsAppMessage, setWhatsAppMessage] = useState("");
  const [whatsAppErrorMessage, setWhatsAppErrorMessage] = useState("");
  const [mediaAccessMessage, setMediaAccessMessage] = useState("");
  const [mediaAccessErrorMessage, setMediaAccessErrorMessage] = useState("");
  const [assistantMessage, setAssistantMessage] = useState("");
  const [assistantErrorMessage, setAssistantErrorMessage] = useState("");
  const [aiConfigurationMessage, setAiConfigurationMessage] = useState("");
  const [aiConfigurationErrorMessage, setAiConfigurationErrorMessage] = useState("");

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

  useEffect(() => {
    if (!selectedCompanyId || !selectedProjectId || !currentUser || !isCompanyAdmin(currentUser.role)) {
      setDailySummarySetting(null);
      setDailySummaryPreview(null);
      setDailySummaryMessages([]);
      return;
    }

    loadDailySummaryWorkspace(selectedCompanyId, selectedProjectId, accessToken, dailySummaryDate)
      .then(({ setting, preview, messages }) => {
        setDailySummarySetting(setting);
        setDailySummaryPreview(preview);
        setDailySummaryMessages(messages);
        setDailySummaryForm(formFromDailySummarySetting(setting));
        setDailySummaryErrorMessage("");
      })
      .catch((error: Error) => {
        setDailySummarySetting(null);
        setDailySummaryPreview(null);
        setDailySummaryMessages([]);
        setDailySummaryErrorMessage(error.message);
      });
  }, [selectedCompanyId, selectedProjectId, currentUser, accessToken, dailySummaryDate]);

  useEffect(() => {
    if (!selectedCompanyId || !currentUser || !isCompanyAdmin(currentUser.role)) {
      setWhatsAppProviderAccounts([]);
      setWhatsAppMessages([]);
      setVoiceNotes([]);
      return;
    }

    loadWhatsAppWorkspace(selectedCompanyId, accessToken)
      .then(({ providerAccounts, messages, voiceNotes }) => {
        setWhatsAppProviderAccounts(providerAccounts);
        setWhatsAppMessages(messages);
        setVoiceNotes(voiceNotes);
        setWhatsAppErrorMessage("");
      })
      .catch((error: Error) => {
        setWhatsAppProviderAccounts([]);
        setWhatsAppMessages([]);
        setVoiceNotes([]);
        setWhatsAppErrorMessage(error.message);
      });
  }, [selectedCompanyId, currentUser, accessToken]);

  useEffect(() => {
    if (!selectedCompanyId || !currentUser || !isCompanyAdmin(currentUser.role)) {
      setAssistantParseResults([]);
      setAssistantConversationStates([]);
      return;
    }

    loadAssistantAuditWorkspace(selectedCompanyId, accessToken)
      .then(({ parseResults, conversationStates }) => {
        setAssistantParseResults(parseResults);
        setAssistantConversationStates(conversationStates);
        setAssistantErrorMessage("");
      })
      .catch((error: Error) => {
        setAssistantParseResults([]);
        setAssistantConversationStates([]);
        setAssistantErrorMessage(error.message);
      });
  }, [selectedCompanyId, currentUser, accessToken]);

  useEffect(() => {
    const company = companies.find((candidate) => candidate.id === selectedCompanyId);
    if (!company) {
      setAiConfigurationForm(emptyAiConfigurationForm);
      return;
    }

    setAiConfigurationForm(formFromCompanyAISettings(company));
    setAiConfigurationMessage("");
    setAiConfigurationErrorMessage("");
  }, [companies, selectedCompanyId]);

  const filteredData = useMemo(
    () => filterReportingData(reportingData, fromDate, toDate),
    [reportingData, fromDate, toDate],
  );

  const summaryCards = useMemo(() => buildSummaryCards(filteredData), [filteredData]);
  const analytics = useMemo(() => buildDashboardAnalytics(filteredData), [filteredData]);
  const reportingHealth = useMemo(
    () => buildReportingHealth(filteredData),
    [filteredData],
  );
  const selectedCompany = companies.find((company) => company.id === selectedCompanyId);
  const selectedProject = projects.find((project) => project.id === selectedProjectId);
  const canManageTeam = currentUser ? isCompanyAdmin(currentUser.role) : false;
  const canManageProjects = currentUser ? isCompanyAdmin(currentUser.role) : false;
  const canManageKnowledgebase = currentUser ? isCompanyAdmin(currentUser.role) : false;
  const canManageDailySummary = currentUser ? isCompanyAdmin(currentUser.role) : false;
  const canViewWhatsAppAudit = currentUser ? isCompanyAdmin(currentUser.role) : false;
  const canViewAssistantAudit = currentUser ? isCompanyAdmin(currentUser.role) : false;
  const canManageAiConfiguration = currentUser ? isCompanyAdmin(currentUser.role) : false;
  const canExportWorkbook =
    filteredData.access.progress ||
    filteredData.access.manpower ||
    filteredData.access.materials ||
    filteredData.access.stock ||
    filteredData.access.media;
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

  async function handleSaveDailySummarySettings(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCompanyId || !selectedProjectId) {
      return;
    }

    setDailySummaryMessage("");
    setDailySummaryErrorMessage("");
    try {
      const setting = await updateDailySummarySetting(
        selectedCompanyId,
        selectedProjectId,
        accessToken,
        dailySummaryForm,
      );
      const preview = await previewDailySummary(
        selectedCompanyId,
        selectedProjectId,
        accessToken,
        dailySummaryDate,
      );
      setDailySummarySetting(setting);
      setDailySummaryPreview(preview);
      setDailySummaryForm(formFromDailySummarySetting(setting));
      setDailySummaryMessage("Daily summary settings saved.");
    } catch (error) {
      setDailySummaryErrorMessage(
        error instanceof Error ? error.message : "Could not save daily summary settings.",
      );
    }
  }

  async function handleRefreshDailySummaryPreview() {
    if (!selectedCompanyId || !selectedProjectId) {
      return;
    }

    setDailySummaryMessage("");
    setDailySummaryErrorMessage("");
    try {
      const preview = await previewDailySummary(
        selectedCompanyId,
        selectedProjectId,
        accessToken,
        dailySummaryDate,
      );
      setDailySummaryPreview(preview);
      setDailySummaryMessage("Daily summary preview refreshed.");
    } catch (error) {
      setDailySummaryErrorMessage(
        error instanceof Error ? error.message : "Could not refresh daily summary preview.",
      );
    }
  }

  async function handleSendDailySummaryNow() {
    if (!selectedCompanyId || !selectedProjectId) {
      return;
    }

    setDailySummaryMessage("");
    setDailySummaryErrorMessage("");
    try {
      const result = await sendDailySummaryNow(
        selectedCompanyId,
        selectedProjectId,
        accessToken,
        dailySummaryDate,
      );
      const messages = await loadDailySummaryMessages(
        selectedCompanyId,
        selectedProjectId,
        accessToken,
      );
      setDailySummaryMessages(messages);
      setDailySummaryMessage(
        `Daily summary sent to ${result.sent_count} recipient(s), skipped ${result.skipped_count}.`,
      );
    } catch (error) {
      setDailySummaryErrorMessage(
        error instanceof Error ? error.message : "Could not send daily summary.",
      );
    }
  }

  async function handleRefreshWhatsAppMessages() {
    if (!selectedCompanyId) {
      return;
    }

    setWhatsAppMessage("");
    setWhatsAppErrorMessage("");
    try {
      const { providerAccounts, messages, voiceNotes } = await loadWhatsAppWorkspace(
        selectedCompanyId,
        accessToken,
      );
      setWhatsAppProviderAccounts(providerAccounts);
      setWhatsAppMessages(messages);
      setVoiceNotes(voiceNotes);
      setWhatsAppMessage(
        `Loaded ${providerAccounts.length} provider account(s), ${messages.length} message(s), and ${voiceNotes.length} voice note(s).`,
      );
    } catch (error) {
      setWhatsAppErrorMessage(
        error instanceof Error ? error.message : "Could not load WhatsApp messages.",
      );
    }
  }

  async function handleOpenProjectMedia(mediaFile: MediaFile) {
    if (!selectedCompanyId || !selectedProjectId) {
      return;
    }

    setMediaAccessMessage("");
    setMediaAccessErrorMessage("");
    try {
      await openAuthenticatedMedia(
        `/api/companies/${selectedCompanyId}/projects/${selectedProjectId}/reporting/media-files/${mediaFile.id}/access`,
        accessToken,
        mediaFileDisplayName(mediaFile),
        "open",
      );
      setMediaAccessMessage(`Opened ${mediaFileDisplayName(mediaFile)}.`);
    } catch (error) {
      setMediaAccessErrorMessage(
        error instanceof Error ? error.message : "Could not open the media file.",
      );
    }
  }

  async function handleDownloadProjectMedia(mediaFile: MediaFile) {
    if (!selectedCompanyId || !selectedProjectId) {
      return;
    }

    setMediaAccessMessage("");
    setMediaAccessErrorMessage("");
    try {
      await openAuthenticatedMedia(
        `/api/companies/${selectedCompanyId}/projects/${selectedProjectId}/reporting/media-files/${mediaFile.id}/access`,
        accessToken,
        mediaFileDisplayName(mediaFile),
        "download",
      );
      setMediaAccessMessage(`Downloaded ${mediaFileDisplayName(mediaFile)}.`);
    } catch (error) {
      setMediaAccessErrorMessage(
        error instanceof Error ? error.message : "Could not download the media file.",
      );
    }
  }

  async function handleOpenVoiceNote(voiceNote: VoiceNote) {
    if (!selectedCompanyId) {
      return;
    }

    setWhatsAppMessage("");
    setWhatsAppErrorMessage("");
    try {
      await openAuthenticatedMedia(
        `/api/companies/${selectedCompanyId}/whatsapp/voice-notes/${voiceNote.id}/access`,
        accessToken,
        voiceNoteDisplayName(voiceNote),
        "open",
      );
      setWhatsAppMessage(`Opened ${voiceNoteDisplayName(voiceNote)}.`);
    } catch (error) {
      setWhatsAppErrorMessage(
        error instanceof Error ? error.message : "Could not open the voice note.",
      );
    }
  }

  async function handleDownloadVoiceNote(voiceNote: VoiceNote) {
    if (!selectedCompanyId) {
      return;
    }

    setWhatsAppMessage("");
    setWhatsAppErrorMessage("");
    try {
      await openAuthenticatedMedia(
        `/api/companies/${selectedCompanyId}/whatsapp/voice-notes/${voiceNote.id}/access`,
        accessToken,
        voiceNoteDisplayName(voiceNote),
        "download",
      );
      setWhatsAppMessage(`Downloaded ${voiceNoteDisplayName(voiceNote)}.`);
    } catch (error) {
      setWhatsAppErrorMessage(
        error instanceof Error ? error.message : "Could not download the voice note.",
      );
    }
  }

  async function handleRefreshAssistantAudit() {
    if (!selectedCompanyId) {
      return;
    }

    setAssistantMessage("");
    setAssistantErrorMessage("");
    try {
      const { parseResults, conversationStates } = await loadAssistantAuditWorkspace(
        selectedCompanyId,
        accessToken,
      );
      setAssistantParseResults(parseResults);
      setAssistantConversationStates(conversationStates);
      setAssistantMessage(
        `Loaded ${parseResults.length} parse result(s) and ${conversationStates.length} conversation state(s).`,
      );
    } catch (error) {
      setAssistantErrorMessage(
        error instanceof Error ? error.message : "Could not load assistant audit records.",
      );
    }
  }

  async function handleSaveAiConfiguration(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCompanyId) {
      return;
    }

    setAiConfigurationMessage("");
    setAiConfigurationErrorMessage("");
    try {
      const updatedCompany = await updateCompanyAISettings(
        selectedCompanyId,
        accessToken,
        aiConfigurationForm,
      );
      setCompanies((existingCompanies) =>
        existingCompanies.map((company) =>
          company.id === updatedCompany.id ? updatedCompany : company,
        ),
      );
      setAiConfigurationForm(formFromCompanyAISettings(updatedCompany));
      setAiConfigurationMessage("AI configuration saved.");
    } catch (error) {
      setAiConfigurationErrorMessage(
        error instanceof Error ? error.message : "Could not save AI configuration.",
      );
    }
  }

  async function handleCreateWhatsAppProviderAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCompanyId) {
      return;
    }

    setWhatsAppMessage("");
    setWhatsAppErrorMessage("");
    try {
      const providerAccount = await createWhatsAppProviderAccount(
        selectedCompanyId,
        accessToken,
        whatsAppProviderForm,
      );
      setWhatsAppProviderAccounts((existingAccounts) => [providerAccount, ...existingAccounts]);
      setWhatsAppProviderForm({
        ...emptyWhatsAppProviderForm,
        providerName: whatsAppProviderForm.providerName,
      });
      setWhatsAppMessage(`Created ${formatRole(providerAccount.provider_name)} provider account.`);
    } catch (error) {
      setWhatsAppErrorMessage(
        error instanceof Error ? error.message : "Could not create WhatsApp provider account.",
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

        {canManageAiConfiguration ? (
          <AiConfigurationPanel
            selectedCompany={selectedCompany}
            form={aiConfigurationForm}
            aiConfigurationMessage={aiConfigurationMessage}
            aiConfigurationErrorMessage={aiConfigurationErrorMessage}
            onFormChange={setAiConfigurationForm}
            onSaveSettings={handleSaveAiConfiguration}
          />
        ) : null}

        {canManageDailySummary ? (
          <DailySummaryManagementPanel
            selectedProject={selectedProject}
            setting={dailySummarySetting}
            preview={dailySummaryPreview}
            messages={dailySummaryMessages}
            form={dailySummaryForm}
            summaryDate={dailySummaryDate}
            dailySummaryMessage={dailySummaryMessage}
            dailySummaryErrorMessage={dailySummaryErrorMessage}
            onFormChange={setDailySummaryForm}
            onSummaryDateChange={setDailySummaryDate}
            onSaveSettings={handleSaveDailySummarySettings}
            onRefreshPreview={handleRefreshDailySummaryPreview}
            onSendNow={handleSendDailySummaryNow}
          />
        ) : null}

        {canViewWhatsAppAudit ? (
          <WhatsAppAuditPanel
            providerAccounts={whatsAppProviderAccounts}
            providerForm={whatsAppProviderForm}
            messages={whatsAppMessages}
            voiceNotes={voiceNotes}
            whatsAppMessage={whatsAppMessage}
            whatsAppErrorMessage={whatsAppErrorMessage}
            onProviderFormChange={setWhatsAppProviderForm}
            onCreateProviderAccount={handleCreateWhatsAppProviderAccount}
            onRefresh={handleRefreshWhatsAppMessages}
            onOpenVoiceNote={handleOpenVoiceNote}
            onDownloadVoiceNote={handleDownloadVoiceNote}
          />
        ) : null}

        {canViewAssistantAudit ? (
          <AssistantAuditPanel
            parseResults={assistantParseResults}
            conversationStates={assistantConversationStates}
            assistantMessage={assistantMessage}
            assistantErrorMessage={assistantErrorMessage}
            onRefresh={handleRefreshAssistantAudit}
          />
        ) : null}

        <section className="section-heading reporting-heading" id="dashboard">
          <div>
            <p className="eyebrow">Reporting workspace</p>
            <h3>Project manager view</h3>
            <p>
              Focused view of confirmed field updates for the selected project and date range.
            </p>
          </div>
          <div className="health-row" aria-label="Reporting health">
            {reportingHealth.map((item) => (
              <span className={`health-pill ${item.tone}`} key={item.label}>
                {item.label}: {item.value}
              </span>
            ))}
          </div>
        </section>

        <section className="card-grid" aria-label="Summary cards">
          {summaryCards.map((card) => (
            <article className={`summary-card ${card.tone}`} key={card.label}>
              <p>{card.label}</p>
              <strong>{card.value}</strong>
              <span>{card.helper}</span>
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
              Download the currently loaded and filtered records as one Excel workbook with
              separate sheets for each report section you can access.
            </p>
            <div className="button-row">
              <button
                type="button"
                disabled={!canExportWorkbook}
                onClick={() =>
                  exportExcelWorkbook({
                    company: selectedCompany,
                    project: selectedProject,
                    data: filteredData,
                    fromDate,
                    toDate,
                  })
                }
              >
                Export Excel workbook
              </button>
            </div>
            {!canExportWorkbook ? (
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
            helper="Confirmed progress updates from WhatsApp or reporting APIs."
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
            message="Your project role does not include progress reporting access. Ask an owner/admin if this looks wrong."
          />
        )}

        {filteredData.access.manpower ? (
          <ReportingTable
            title="Manpower"
            emptyMessage="No manpower entries for this selection yet."
            helper="Labor counts grouped by date, trade, and location."
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
            message="Your project role does not include manpower reporting access. Ask an owner/admin if this looks wrong."
          />
        )}

        {filteredData.access.materials ? (
          <ReportingTable
            title="Material movement"
            emptyMessage="No material transactions for this selection yet."
            helper="Material received and issued records, including proof status."
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
            message="Your project role does not include material reporting access. Ask an owner/admin if this looks wrong."
          />
        )}

        <section className="dashboard-grid">
          {filteredData.access.stock ? (
            <ReportingTable
              title="Material stock"
              emptyMessage="No stock balances yet."
              helper="Current stock position calculated from received and issued movement."
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
            <div>
              {mediaAccessMessage ? <p className="status-message">{mediaAccessMessage}</p> : null}
              {mediaAccessErrorMessage ? (
                <p className="error-message">{mediaAccessErrorMessage}</p>
              ) : null}
              <ReportingTable
                title="Image/proof files"
                emptyMessage="No media files yet."
                helper="Image and proof records linked to project reporting activity."
                columns={["Created", "Type", "File", "Linked to", "Status"]}
                rows={filteredData.media.map((entry) => [
                  formatDateTime(entry.created_at),
                  entry.media_type,
                  <MediaActionCell
                    label={mediaFileDisplayName(entry)}
                    onOpen={() => handleOpenProjectMedia(entry)}
                    onDownload={() => handleDownloadProjectMedia(entry)}
                  />,
                  formatMediaLink(entry),
                  entry.processing_status,
                ])}
              />
            </div>
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
  helper,
  columns,
  rows,
}: {
  title: string;
  emptyMessage: string;
  helper?: string;
  columns: string[];
  rows: ReactNode[][];
}) {
  return (
    <article className="panel table-panel">
      <div className="table-title-row">
        <div>
          <h3>{title}</h3>
          {helper ? <p>{helper}</p> : null}
        </div>
        <span>
          {rows.length} {rows.length === 1 ? "row" : "rows"}
        </span>
      </div>
      {rows.length === 0 ? (
        <div className="empty-state">
          <strong>No records found</strong>
          <p>{emptyMessage}</p>
        </div>
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

function MediaActionCell({
  label,
  onOpen,
  onDownload,
}: {
  label: string;
  onOpen: () => void;
  onDownload: () => void;
}) {
  return (
    <div className="media-action-cell">
      <span title={label}>{truncateText(label, 44)}</span>
      <div className="media-action-buttons">
        <button type="button" onClick={onOpen}>
          Open
        </button>
        <button type="button" onClick={onDownload}>
          Download
        </button>
      </div>
    </div>
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

function AiConfigurationPanel({
  selectedCompany,
  form,
  aiConfigurationMessage,
  aiConfigurationErrorMessage,
  onFormChange,
  onSaveSettings,
}: {
  selectedCompany: Company | undefined;
  form: typeof emptyAiConfigurationForm;
  aiConfigurationMessage: string;
  aiConfigurationErrorMessage: string;
  onFormChange: (form: typeof emptyAiConfigurationForm) => void;
  onSaveSettings: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <section className="management-section" id="settings">
      <div className="section-heading reporting-heading">
        <div>
          <p className="eyebrow">AI settings</p>
          <h3>Configure company AI usage</h3>
          <p>
            Choose whether this company uses Cognos AI&apos;s platform-managed AI keys or its own
            company-owned AI setup. Actual secret entry/storage is intentionally deferred until the
            secure key vault work is added.
          </p>
        </div>
        <div className="health-row" aria-label="AI settings status">
          <span className="health-pill">{formatRole(form.aiKeyMode)}</span>
          <span className={`health-pill ${form.aiSubscriptionEnabled ? "normal" : "warning"}`}>
            AI insights {form.aiSubscriptionEnabled ? "enabled" : "off"}
          </span>
        </div>
      </div>

      {aiConfigurationMessage ? <p className="status-message">{aiConfigurationMessage}</p> : null}
      {aiConfigurationErrorMessage ? (
        <p className="error-message">{aiConfigurationErrorMessage}</p>
      ) : null}

      <section className="dashboard-grid">
        <article className="panel">
          <h3>Company AI configuration</h3>
          <p>
            Selected company: <strong>{selectedCompany?.name ?? "No company selected"}</strong>
          </p>
          <form className="stacked-form" onSubmit={onSaveSettings}>
            <label>
              AI key mode
              <select
                value={form.aiKeyMode}
                onChange={(event) =>
                  onFormChange({ ...form, aiKeyMode: event.target.value })
                }
              >
                <option value="platform_managed">Platform-managed keys</option>
                <option value="company_owned">Company-owned keys</option>
              </select>
            </label>
            <label className="inline-check">
              <input
                type="checkbox"
                checked={form.aiSubscriptionEnabled}
                onChange={(event) =>
                  onFormChange({
                    ...form,
                    aiSubscriptionEnabled: event.target.checked,
                  })
                }
              />
              Enable AI insights for this company
            </label>
            <button type="submit" disabled={!selectedCompany}>
              Save AI settings
            </button>
          </form>
        </article>

        <article className="panel">
          <h3>What this means</h3>
          <p>
            Platform-managed mode is the easiest pilot option: Cognos AI owns and manages the model
            credentials behind the scenes.
          </p>
          <p>
            Company-owned mode is for customers who want their own AI billing, procurement, or data
            governance path. In this foundation, the mode can be selected, but real API keys are not
            collected yet.
          </p>
          <p className="muted-note">
            Next secure step: encrypted secret storage, masked key display, key validation, and
            audit logging for changes.
          </p>
        </article>
      </section>
    </section>
  );
}

function DailySummaryManagementPanel({
  selectedProject,
  setting,
  preview,
  messages,
  form,
  summaryDate,
  dailySummaryMessage,
  dailySummaryErrorMessage,
  onFormChange,
  onSummaryDateChange,
  onSaveSettings,
  onRefreshPreview,
  onSendNow,
}: {
  selectedProject: Project | undefined;
  setting: DailySummarySetting | null;
  preview: DailySummaryPreview | null;
  messages: DailySummaryMessage[];
  form: typeof emptyDailySummaryForm;
  summaryDate: string;
  dailySummaryMessage: string;
  dailySummaryErrorMessage: string;
  onFormChange: (form: typeof emptyDailySummaryForm) => void;
  onSummaryDateChange: (summaryDate: string) => void;
  onSaveSettings: (event: FormEvent<HTMLFormElement>) => void;
  onRefreshPreview: () => void;
  onSendNow: () => void;
}) {
  return (
    <section className="management-section" id="daily-summary-settings">
      <div className="section-heading reporting-heading">
        <div>
          <p className="eyebrow">Daily WhatsApp summary</p>
          <h3>Configure automatic project summaries</h3>
          <p>
            Control the daily project summary sent on WhatsApp. The MVP default is 7:00 PM in the
            project&apos;s local timezone.
          </p>
        </div>
        <div className="health-row" aria-label="Daily summary status">
          <span className={`health-pill ${form.enabled ? "normal" : "warning"}`}>
            {form.enabled ? "Enabled" : "Disabled"}
          </span>
          <span className="health-pill">Recipients: {preview?.recipient_count ?? 0}</span>
        </div>
      </div>

      {dailySummaryMessage ? <p className="status-message">{dailySummaryMessage}</p> : null}
      {dailySummaryErrorMessage ? (
        <p className="error-message">{dailySummaryErrorMessage}</p>
      ) : null}

      <section className="dashboard-grid">
        <article className="panel">
          <h3>Summary settings</h3>
          <p>
            Selected project: <strong>{selectedProject?.name ?? "No project selected"}</strong>
          </p>
          <form className="stacked-form" onSubmit={onSaveSettings}>
            <label className="inline-check">
              <input
                type="checkbox"
                checked={form.enabled}
                onChange={(event) => onFormChange({ ...form, enabled: event.target.checked })}
              />
              Send automatic daily summary
            </label>
            <label>
              Send time
              <input
                type="time"
                value={form.sendTimeLocal}
                onChange={(event) =>
                  onFormChange({ ...form, sendTimeLocal: event.target.value })
                }
                required
              />
            </label>
            <label>
              Timezone
              <input
                value={form.timezone}
                onChange={(event) => onFormChange({ ...form, timezone: event.target.value })}
                placeholder="Asia/Kolkata"
                required
              />
            </label>
            <label>
              Recipients
              <select
                value={form.recipientScope}
                onChange={(event) =>
                  onFormChange({ ...form, recipientScope: event.target.value })
                }
              >
                <option value="dashboard_users">Project users with dashboard access</option>
              </select>
            </label>
            <button type="submit" disabled={!selectedProject}>
              Save summary settings
            </button>
          </form>
          {setting ? (
            <p className="muted-note">
              Last updated {formatDateTime(setting.updated_at)}. Scheduler sends once per project
              per local date.
            </p>
          ) : null}
        </article>

        <article className="panel">
          <h3>Preview and send</h3>
          <p>
            Preview the WhatsApp text before sending it. Manual send uses the same outbound audit
            path as the automatic scheduler.
          </p>
          <div className="stacked-form">
            <label>
              Summary date
              <input
                type="date"
                value={summaryDate}
                onChange={(event) => onSummaryDateChange(event.target.value)}
              />
            </label>
            <div className="button-row">
              <button type="button" disabled={!selectedProject} onClick={onRefreshPreview}>
                Refresh preview
              </button>
              <button type="button" disabled={!selectedProject || !preview} onClick={onSendNow}>
                Send now
              </button>
            </div>
          </div>
        </article>
      </section>

      <article className="panel">
        <div className="table-title-row">
          <div>
            <h3>WhatsApp summary preview</h3>
            <p>
              Date: {preview?.summary_date ?? summaryDate} · Send time:{" "}
              {preview ? formatTime(preview.send_time_local) : form.sendTimeLocal} · Timezone:{" "}
              {preview?.timezone ?? form.timezone}
            </p>
          </div>
          <span>{preview?.recipient_count ?? 0} recipient(s)</span>
        </div>
        <pre className="summary-preview">{preview?.summary_text ?? "Choose a project to preview the daily WhatsApp summary."}</pre>
      </article>

      <ReportingTable
        title="Daily summary send history"
        emptyMessage="No daily summaries have been sent for this project yet."
        helper="Each row is one recipient message logged by the summary system."
        columns={["Created", "Date", "Recipient", "Status", "Trigger"]}
        rows={messages.map((message) => [
          formatDateTime(message.created_at),
          message.summary_date,
          message.recipient_phone ?? "-",
          formatRole(message.delivery_status),
          formatRole(message.trigger_type),
        ])}
      />
    </section>
  );
}

function WhatsAppAuditPanel({
  providerAccounts,
  providerForm,
  messages,
  voiceNotes,
  whatsAppMessage,
  whatsAppErrorMessage,
  onProviderFormChange,
  onCreateProviderAccount,
  onRefresh,
  onOpenVoiceNote,
  onDownloadVoiceNote,
}: {
  providerAccounts: WhatsAppProviderAccount[];
  providerForm: typeof emptyWhatsAppProviderForm;
  messages: WhatsAppAuditMessage[];
  voiceNotes: VoiceNote[];
  whatsAppMessage: string;
  whatsAppErrorMessage: string;
  onProviderFormChange: (form: typeof emptyWhatsAppProviderForm) => void;
  onCreateProviderAccount: (event: FormEvent<HTMLFormElement>) => void;
  onRefresh: () => void;
  onOpenVoiceNote: (voiceNote: VoiceNote) => void;
  onDownloadVoiceNote: (voiceNote: VoiceNote) => void;
}) {
  const auditCards = buildWhatsAppAuditCards(messages);

  return (
    <section className="management-section" id="whatsapp">
      <div className="section-heading reporting-heading">
        <div>
          <p className="eyebrow">WhatsApp audit</p>
          <h3>Review inbound and outbound message logs</h3>
          <p>
            Use this during pilots to confirm whether WhatsApp messages were received, parsed,
            queued, simulated, sent, or blocked because of user/provider issues.
          </p>
        </div>
        <div className="button-row">
          <button type="button" onClick={onRefresh}>
            Refresh messages
          </button>
        </div>
      </div>

      {whatsAppMessage ? <p className="status-message">{whatsAppMessage}</p> : null}
      {whatsAppErrorMessage ? <p className="error-message">{whatsAppErrorMessage}</p> : null}

      <section className="dashboard-grid">
        <article className="panel">
          <h3>Add provider account</h3>
          <p>
            Use `generic` for local testing. When Meta WhatsApp Cloud API details are final, add a
            `meta_cloud_api` account with the phone number ID/provider account ID.
          </p>
          <form className="stacked-form" onSubmit={onCreateProviderAccount}>
            <label>
              Provider
              <select
                value={providerForm.providerName}
                onChange={(event) =>
                  onProviderFormChange({ ...providerForm, providerName: event.target.value })
                }
              >
                <option value="generic">Generic / local test</option>
                <option value="meta_cloud_api">Meta WhatsApp Cloud API</option>
                <option value="test">Test provider</option>
              </select>
            </label>
            <label>
              Provider account ID
              <input
                value={providerForm.providerAccountId}
                onChange={(event) =>
                  onProviderFormChange({
                    ...providerForm,
                    providerAccountId: event.target.value,
                  })
                }
                placeholder="local-test-account"
              />
            </label>
            <label>
              Phone number ID
              <input
                value={providerForm.phoneNumberId}
                onChange={(event) =>
                  onProviderFormChange({
                    ...providerForm,
                    phoneNumberId: event.target.value,
                  })
                }
                placeholder="Meta phone number ID or local-test-number"
              />
            </label>
            <label>
              Webhook URL
              <input
                value={providerForm.webhookUrl}
                onChange={(event) =>
                  onProviderFormChange({ ...providerForm, webhookUrl: event.target.value })
                }
                placeholder="https://example.com/webhooks/whatsapp/meta_cloud_api"
              />
            </label>
            <label>
              Status
              <select
                value={providerForm.status}
                onChange={(event) =>
                  onProviderFormChange({ ...providerForm, status: event.target.value })
                }
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </label>
            <button type="submit">Create provider account</button>
          </form>
        </article>

        <ReportingTable
          title="Provider accounts"
          emptyMessage="No WhatsApp provider accounts have been configured yet."
          helper="Provider configuration used to connect inbound webhooks and outbound message logs."
          columns={["Provider", "Account ID", "Phone number ID", "Status", "Created"]}
          rows={providerAccounts.map((account) => [
            formatRole(account.provider_name),
            account.provider_account_id ?? "-",
            account.phone_number_id ?? "-",
            formatRole(account.status),
            formatDateTime(account.created_at),
          ])}
        />
      </section>

      <section className="card-grid" aria-label="WhatsApp audit summary">
        {auditCards.map((card) => (
          <article className={`summary-card ${card.tone}`} key={card.label}>
            <p>{card.label}</p>
            <strong>{card.value}</strong>
            <span>{card.helper}</span>
          </article>
        ))}
      </section>

      <ReportingTable
        title="WhatsApp message log"
        emptyMessage="No WhatsApp messages have been logged for this company yet."
        helper="Company-level audit trail for inbound webhooks and outbound assistant/system replies."
        columns={["Received", "Direction", "Phone", "Status", "Provider", "Message"]}
        rows={messages.map((message) => [
          formatDateTime(message.received_at),
          formatRole(message.direction),
          message.phone ?? "-",
          formatRole(message.processing_status),
          message.provider_name,
          truncateText(message.message_text ?? "-", 90),
        ])}
      />

      <ReportingTable
        title="Voice note log"
        emptyMessage="No WhatsApp voice notes have been logged for this company yet."
        helper="Voice/audio submissions, transcript status, and transcript text when available."
        columns={["Created", "Status", "Provider", "Transcript", "Media"]}
        rows={voiceNotes.map((voiceNote) => [
          formatDateTime(voiceNote.created_at),
          formatRole(voiceNote.transcription_status),
          voiceNote.transcription_provider ?? "-",
          truncateText(voiceNote.transcript_text ?? voiceNote.error_message ?? "-", 90),
          <MediaActionCell
            label={voiceNoteDisplayName(voiceNote)}
            onOpen={() => onOpenVoiceNote(voiceNote)}
            onDownload={() => onDownloadVoiceNote(voiceNote)}
          />,
        ])}
      />
    </section>
  );
}

function AssistantAuditPanel({
  parseResults,
  conversationStates,
  assistantMessage,
  assistantErrorMessage,
  onRefresh,
}: {
  parseResults: AssistantParseResult[];
  conversationStates: AssistantConversationState[];
  assistantMessage: string;
  assistantErrorMessage: string;
  onRefresh: () => void;
}) {
  const auditCards = buildAssistantAuditCards(parseResults, conversationStates);

  return (
    <section className="management-section" id="assistant">
      <div className="section-heading reporting-heading">
        <div>
          <p className="eyebrow">Assistant audit</p>
          <h3>Review what the AI assistant understood</h3>
          <p>
            Use this during pilots to see how WhatsApp updates were interpreted, whether fields
            were missing, and which conversations still need confirmation or cleanup.
          </p>
        </div>
        <div className="button-row">
          <button type="button" onClick={onRefresh}>
            Refresh assistant audit
          </button>
        </div>
      </div>

      {assistantMessage ? <p className="status-message">{assistantMessage}</p> : null}
      {assistantErrorMessage ? <p className="error-message">{assistantErrorMessage}</p> : null}

      <section className="card-grid" aria-label="Assistant audit summary">
        {auditCards.map((card) => (
          <article className={`summary-card ${card.tone}`} key={card.label}>
            <p>{card.label}</p>
            <strong>{card.value}</strong>
            <span>{card.helper}</span>
          </article>
        ))}
      </section>

      <ReportingTable
        title="Assistant parse results"
        emptyMessage="No assistant parse results have been stored for this company yet."
        helper="Every row shows one WhatsApp message interpretation before it is confirmed, corrected, or saved."
        columns={["Created", "Intent", "Confidence", "Language", "Validation", "Next action", "Summary"]}
        rows={parseResults.map((result) => [
          formatDateTime(result.created_at),
          formatRole(result.intent),
          formatConfidence(result.confidence),
          result.input_language ? formatRole(result.input_language) : "-",
          formatRole(result.validation_status),
          formatRole(result.next_action),
          truncateText(result.assistant_summary ?? summarizeObject(result.extracted_data), 100),
        ])}
      />

      <ReportingTable
        title="Assistant conversation states"
        emptyMessage="No active or historical assistant conversation states have been stored yet."
        helper="Shows follow-up conversations where the assistant asked for confirmation, missing fields, project selection, or another next step."
        columns={["Updated", "Status", "Pending intent", "Missing fields", "Last user message", "Assistant prompt"]}
        rows={conversationStates.map((state) => [
          formatDateTime(state.updated_at),
          formatRole(state.status),
          formatRole(state.pending_intent),
          formatMissingFields(state.missing_fields),
          truncateText(state.last_user_message ?? "-", 80),
          truncateText(state.confirmation_prompt ?? summarizeObject(state.pending_data), 100),
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

async function openAuthenticatedMedia(
  path: string,
  accessToken: string,
  fileName: string,
  action: "open" | "download",
): Promise<void> {
  let pendingWindow: Window | null = null;
  if (action === "open") {
    pendingWindow = window.open("", "_blank");
    if (pendingWindow) {
      pendingWindow.opener = null;
      pendingWindow.document.title = "Opening media";
      pendingWindow.document.body.textContent = "Opening media...";
    }
  }

  try {
    const response = await fetch(path, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      throw new ApiRequestError(response.status, await errorDetail(response));
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    if (action === "download") {
      triggerBrowserDownload(url, fileName);
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      return;
    }

    if (pendingWindow && !pendingWindow.closed) {
      pendingWindow.location.href = url;
      setTimeout(() => URL.revokeObjectURL(url), 60000);
      return;
    }

    triggerBrowserDownload(url, fileName);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (error) {
    if (pendingWindow && !pendingWindow.closed) {
      pendingWindow.close();
    }
    throw error;
  }
}

function triggerBrowserDownload(url: string, fileName: string) {
  const link = document.createElement("a");
  link.href = url;
  link.download = safeMediaFileName(fileName || "cognos-ai-media");
  link.click();
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

async function loadDailySummaryWorkspace(
  companyId: string,
  projectId: string,
  accessToken: string,
  summaryDate: string,
): Promise<{
  setting: DailySummarySetting;
  preview: DailySummaryPreview;
  messages: DailySummaryMessage[];
}> {
  const [setting, preview, messages] = await Promise.all([
    loadDailySummarySetting(companyId, projectId, accessToken),
    previewDailySummary(companyId, projectId, accessToken, summaryDate),
    loadDailySummaryMessages(companyId, projectId, accessToken),
  ]);
  return { setting, preview, messages };
}

async function updateCompanyAISettings(
  companyId: string,
  accessToken: string,
  form: typeof emptyAiConfigurationForm,
): Promise<Company> {
  return apiRequest<Company>(`/api/companies/${companyId}/ai-settings`, accessToken, {
    method: "PUT",
    body: JSON.stringify({
      ai_key_mode: form.aiKeyMode,
      ai_subscription_enabled: form.aiSubscriptionEnabled,
    }),
  });
}

async function loadDailySummarySetting(
  companyId: string,
  projectId: string,
  accessToken: string,
): Promise<DailySummarySetting> {
  return apiRequest<DailySummarySetting>(
    `/api/companies/${companyId}/projects/${projectId}/daily-summary/settings`,
    accessToken,
  );
}

async function updateDailySummarySetting(
  companyId: string,
  projectId: string,
  accessToken: string,
  form: typeof emptyDailySummaryForm,
): Promise<DailySummarySetting> {
  return apiRequest<DailySummarySetting>(
    `/api/companies/${companyId}/projects/${projectId}/daily-summary/settings`,
    accessToken,
    {
      method: "PUT",
      body: JSON.stringify({
        enabled: form.enabled,
        send_time_local: normalizeTimeForApi(form.sendTimeLocal),
        timezone: form.timezone.trim() || "Asia/Kolkata",
        recipient_scope: form.recipientScope,
      }),
    },
  );
}

async function previewDailySummary(
  companyId: string,
  projectId: string,
  accessToken: string,
  summaryDate: string,
): Promise<DailySummaryPreview> {
  const params = summaryDate ? `?summary_date=${encodeURIComponent(summaryDate)}` : "";
  return apiRequest<DailySummaryPreview>(
    `/api/companies/${companyId}/projects/${projectId}/daily-summary/preview${params}`,
    accessToken,
  );
}

async function sendDailySummaryNow(
  companyId: string,
  projectId: string,
  accessToken: string,
  summaryDate: string,
): Promise<DailySummarySendResult> {
  return apiRequest<DailySummarySendResult>(
    `/api/companies/${companyId}/projects/${projectId}/daily-summary/send-now`,
    accessToken,
    {
      method: "POST",
      body: JSON.stringify({
        summary_date: summaryDate || null,
        trigger_type: "manual_dashboard",
      }),
    },
  );
}

async function loadDailySummaryMessages(
  companyId: string,
  projectId: string,
  accessToken: string,
): Promise<DailySummaryMessage[]> {
  return apiRequest<DailySummaryMessage[]>(
    `/api/companies/${companyId}/projects/${projectId}/daily-summary/messages`,
    accessToken,
  );
}

async function loadWhatsAppMessages(
  companyId: string,
  accessToken: string,
): Promise<WhatsAppAuditMessage[]> {
  return apiRequest<WhatsAppAuditMessage[]>(
    `/api/companies/${companyId}/whatsapp/messages`,
    accessToken,
  );
}

async function loadWhatsAppProviderAccounts(
  companyId: string,
  accessToken: string,
): Promise<WhatsAppProviderAccount[]> {
  return apiRequest<WhatsAppProviderAccount[]>(
    `/api/companies/${companyId}/whatsapp/provider-accounts`,
    accessToken,
  );
}

async function loadVoiceNotes(
  companyId: string,
  accessToken: string,
): Promise<VoiceNote[]> {
  return apiRequest<VoiceNote[]>(
    `/api/companies/${companyId}/whatsapp/voice-notes`,
    accessToken,
  );
}

async function loadWhatsAppWorkspace(
  companyId: string,
  accessToken: string,
): Promise<{
  providerAccounts: WhatsAppProviderAccount[];
  messages: WhatsAppAuditMessage[];
  voiceNotes: VoiceNote[];
}> {
  const [providerAccounts, messages, voiceNotes] = await Promise.all([
    loadWhatsAppProviderAccounts(companyId, accessToken),
    loadWhatsAppMessages(companyId, accessToken),
    loadVoiceNotes(companyId, accessToken),
  ]);
  return { providerAccounts, messages, voiceNotes };
}

async function loadAssistantParseResults(
  companyId: string,
  accessToken: string,
): Promise<AssistantParseResult[]> {
  return apiRequest<AssistantParseResult[]>(
    `/api/companies/${companyId}/assistant/parse-results`,
    accessToken,
  );
}

async function loadAssistantConversationStates(
  companyId: string,
  accessToken: string,
): Promise<AssistantConversationState[]> {
  return apiRequest<AssistantConversationState[]>(
    `/api/companies/${companyId}/assistant/conversation-states`,
    accessToken,
  );
}

async function loadAssistantAuditWorkspace(
  companyId: string,
  accessToken: string,
): Promise<{
  parseResults: AssistantParseResult[];
  conversationStates: AssistantConversationState[];
}> {
  const [parseResults, conversationStates] = await Promise.all([
    loadAssistantParseResults(companyId, accessToken),
    loadAssistantConversationStates(companyId, accessToken),
  ]);
  return { parseResults, conversationStates };
}

async function createWhatsAppProviderAccount(
  companyId: string,
  accessToken: string,
  form: typeof emptyWhatsAppProviderForm,
): Promise<WhatsAppProviderAccount> {
  return apiRequest<WhatsAppProviderAccount>(
    `/api/companies/${companyId}/whatsapp/provider-accounts`,
    accessToken,
    {
      method: "POST",
      body: JSON.stringify({
        provider_name: form.providerName,
        provider_account_id: form.providerAccountId.trim() || null,
        phone_number_id: form.phoneNumberId.trim() || null,
        webhook_url: form.webhookUrl.trim() || null,
        status: form.status,
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

function buildSummaryCards(data: ReportingData): SummaryCard[] {
  const totalWorkers = data.manpower.reduce((sum, entry) => sum + entry.worker_count, 0);
  const materialReceived = data.materials.filter(
    (entry) => entry.transaction_type === "received",
  ).length;
  const materialIssued = data.materials.filter((entry) => entry.transaction_type === "issued").length;

  return [
    data.access.progress
      ? {
          label: "Progress entries",
          value: String(data.progress.length),
          helper: "Confirmed work updates",
          tone: "blue",
        }
      : null,
    data.access.manpower
      ? {
          label: "Manpower count",
          value: String(totalWorkers),
          helper: "Workers across selected dates",
          tone: "green",
        }
      : null,
    data.access.materials
      ? {
          label: "Material received",
          value: String(materialReceived),
          helper: "Received transactions",
          tone: "amber",
        }
      : null,
    data.access.materials
      ? {
          label: "Material issued",
          value: String(materialIssued),
          helper: "Issued transactions",
          tone: "rose",
        }
      : null,
  ].filter((card): card is SummaryCard => card !== null);
}

function buildReportingHealth(data: ReportingData) {
  const missingProof = data.materials.filter((entry) => entry.proof_status !== "attached").length;
  const lowStock = data.stock.filter((entry) => {
    if (!entry.low_stock_threshold) {
      return false;
    }
    return parseQuantity(entry.current_balance) <= parseQuantity(entry.low_stock_threshold);
  }).length;
  const negativeStock = data.stock.filter((entry) => parseQuantity(entry.current_balance) < 0).length;
  const mediaCount = data.media.length;

  return [
    {
      label: "Proof gaps",
      value: data.access.materials ? String(missingProof) : "Restricted",
      tone: !data.access.materials ? "normal" : missingProof > 0 ? "warning" : "normal",
    },
    {
      label: "Low stock",
      value: data.access.stock ? String(lowStock) : "Restricted",
      tone: !data.access.stock
        ? "normal"
        : negativeStock > 0
          ? "danger"
          : lowStock > 0
            ? "warning"
            : "normal",
    },
    {
      label: "Images",
      value: data.access.media ? String(mediaCount) : "Restricted",
      tone: !data.access.media ? "normal" : mediaCount > 0 ? "normal" : "warning",
    },
  ];
}

function buildWhatsAppAuditCards(messages: WhatsAppAuditMessage[]): SummaryCard[] {
  const inbound = messages.filter((message) => message.direction === "inbound").length;
  const outbound = messages.filter((message) => message.direction === "outbound").length;
  const unknownUsers = messages.filter(
    (message) => message.processing_status === "unknown_user",
  ).length;
  const queued = messages.filter((message) => message.processing_status === "queued").length;

  return [
    {
      label: "Total messages",
      value: String(messages.length),
      helper: "Inbound and outbound logs",
      tone: "blue",
    },
    {
      label: "Inbound",
      value: String(inbound),
      helper: "Messages received from WhatsApp",
      tone: "green",
    },
    {
      label: "Outbound",
      value: String(outbound),
      helper: "Assistant/system replies logged",
      tone: "amber",
    },
    {
      label: "Needs attention",
      value: String(unknownUsers + queued),
      helper: "Unknown users or queued provider sends",
      tone: unknownUsers + queued > 0 ? "rose" : "green",
    },
  ];
}

function buildAssistantAuditCards(
  parseResults: AssistantParseResult[],
  conversationStates: AssistantConversationState[],
): SummaryCard[] {
  const awaitingConfirmation = conversationStates.filter(
    (state) => state.status === "awaiting_confirmation",
  ).length;
  const missingInformation = conversationStates.filter(
    (state) =>
      state.status === "awaiting_missing_information" ||
      state.missing_fields.length > 0,
  ).length;
  const attentionStatuses = new Set([
    "awaiting_project_selection",
    "permission_denied",
    "redirected",
    "unsupported_intent",
  ]);
  const needsAttention = conversationStates.filter((state) =>
    attentionStatuses.has(state.status),
  ).length;

  return [
    {
      label: "Parsed messages",
      value: String(parseResults.length),
      helper: "WhatsApp messages interpreted by assistant",
      tone: "blue",
    },
    {
      label: "Awaiting confirmation",
      value: String(awaitingConfirmation),
      helper: "Users still need to say yes/correct details",
      tone: awaitingConfirmation > 0 ? "amber" : "green",
    },
    {
      label: "Missing information",
      value: String(missingInformation),
      helper: "Assistant asked users for more details",
      tone: missingInformation > 0 ? "amber" : "green",
    },
    {
      label: "Needs attention",
      value: String(needsAttention),
      helper: "Project selection, permission, or unsupported-flow issues",
      tone: needsAttention > 0 ? "rose" : "green",
    },
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

type WorkbookCell = string | number | boolean | null | undefined;

type WorkbookSheet = {
  name: string;
  rows: WorkbookCell[][];
};

function exportExcelWorkbook({
  company,
  project,
  data,
  fromDate,
  toDate,
}: {
  company: Company | undefined;
  project: Project | undefined;
  data: ReportingData;
  fromDate: string;
  toDate: string;
}) {
  const sheets: WorkbookSheet[] = [
    {
      name: "Summary",
      rows: [
        ["Company", company?.name ?? "Not selected"],
        ["Project", project?.name ?? "Not selected"],
        ["Project code", project?.code ?? "-"],
        ["Date range", formatDateRange(fromDate, toDate)],
        ["Generated at", new Date().toLocaleString()],
        [],
        ["Sheet", "Rows"],
        ["Progress", data.access.progress ? data.progress.length : "Restricted"],
        ["Manpower", data.access.manpower ? data.manpower.length : "Restricted"],
        ["Material movement", data.access.materials ? data.materials.length : "Restricted"],
        ["Material stock", data.access.stock ? data.stock.length : "Restricted"],
        ["Image/proof files", data.access.media ? data.media.length : "Restricted"],
      ],
    },
  ];

  if (data.access.progress) {
    sheets.push({
      name: "Progress",
      rows: [
        ["Date", "Activity", "Location", "Quantity", "Unit", "Status"],
        ...data.progress.map((entry) => [
          entry.work_date,
          entry.activity_name,
          entry.location_text ?? "",
          parseQuantity(entry.quantity),
          entry.unit_symbol ?? "",
          entry.status,
        ]),
      ],
    });
  }

  if (data.access.manpower) {
    sheets.push({
      name: "Manpower",
      rows: [
        ["Date", "Trade", "Workers", "Location", "Status"],
        ...data.manpower.map((entry) => [
          entry.work_date,
          entry.trade_name,
          entry.worker_count,
          entry.location_text ?? "",
          entry.status,
        ]),
      ],
    });
  }

  if (data.access.materials) {
    sheets.push({
      name: "Material Movement",
      rows: [
        ["Date", "Type", "Material", "Quantity", "Unit", "Location", "Proof"],
        ...data.materials.map((entry) => [
          entry.transaction_date,
          entry.transaction_type,
          entry.material_name,
          parseQuantity(entry.quantity),
          entry.unit_symbol ?? "",
          entry.location_text ?? "",
          entry.proof_status,
        ]),
      ],
    });
  }

  if (data.access.stock) {
    sheets.push({
      name: "Material Stock",
      rows: [
        ["Material", "Received", "Issued", "Balance", "Unit", "Low-stock threshold"],
        ...data.stock.map((entry) => [
          entry.material_name,
          parseQuantity(entry.total_received),
          parseQuantity(entry.total_issued),
          parseQuantity(entry.current_balance),
          entry.unit_symbol,
          entry.low_stock_threshold ? parseQuantity(entry.low_stock_threshold) : "",
        ]),
      ],
    });
  }

  if (data.access.media) {
    sheets.push({
      name: "Media Proof",
      rows: [
        ["Created", "Type", "File", "Caption", "Storage URL", "Linked To", "Status"],
        ...data.media.map((entry) => [
          formatDateTime(entry.created_at),
          entry.media_type,
          entry.file_name ?? "",
          entry.caption ?? "",
          entry.storage_url,
          formatMediaLink(entry),
          entry.processing_status,
        ]),
      ],
    });
  }

  const workbookBytes = buildXlsxWorkbook(sheets);
  const workbookBuffer = workbookBytes.buffer.slice(
    workbookBytes.byteOffset,
    workbookBytes.byteOffset + workbookBytes.byteLength,
  ) as ArrayBuffer;
  const blob = new Blob([workbookBuffer], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${safeFileName(project?.code || project?.name || "cognos-ai-report")}.xlsx`;
  link.click();
  URL.revokeObjectURL(url);
}

function buildXlsxWorkbook(sheets: WorkbookSheet[]): Uint8Array {
  const worksheetFiles = sheets.map((sheet, index) => ({
    path: `xl/worksheets/sheet${index + 1}.xml`,
    content: worksheetXml(sheet),
  }));
  const files = [
    { path: "[Content_Types].xml", content: contentTypesXml(sheets.length) },
    { path: "_rels/.rels", content: rootRelationshipsXml() },
    { path: "xl/workbook.xml", content: workbookXml(sheets) },
    { path: "xl/_rels/workbook.xml.rels", content: workbookRelationshipsXml(sheets.length) },
    ...worksheetFiles,
  ];
  return zipFiles(files);
}

function contentTypesXml(sheetCount: number): string {
  const sheetOverrides = Array.from({ length: sheetCount }, (_, index) => {
    const sheetNumber = index + 1;
    return `<Override PartName="/xl/worksheets/sheet${sheetNumber}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`;
  }).join("");
  return xmlDocument(
    `<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>${sheetOverrides}</Types>`,
  );
}

function rootRelationshipsXml(): string {
  return xmlDocument(
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
  );
}

function workbookXml(sheets: WorkbookSheet[]): string {
  const sheetXml = sheets
    .map(
      (sheet, index) =>
        `<sheet name="${xmlEscape(safeSheetName(sheet.name))}" sheetId="${index + 1}" r:id="rId${index + 1}"/>`,
    )
    .join("");
  return xmlDocument(
    `<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>${sheetXml}</sheets></workbook>`,
  );
}

function workbookRelationshipsXml(sheetCount: number): string {
  const relationships = Array.from({ length: sheetCount }, (_, index) => {
    const sheetNumber = index + 1;
    return `<Relationship Id="rId${sheetNumber}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${sheetNumber}.xml"/>`;
  }).join("");
  return xmlDocument(
    `<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">${relationships}</Relationships>`,
  );
}

function worksheetXml(sheet: WorkbookSheet): string {
  const rows = sheet.rows
    .map((row, rowIndex) => {
      const rowNumber = rowIndex + 1;
      const cells = row
        .map((cell, cellIndex) => cellXml(cell, `${columnName(cellIndex + 1)}${rowNumber}`))
        .join("");
      return `<row r="${rowNumber}">${cells}</row>`;
    })
    .join("");
  return xmlDocument(
    `<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>${rows}</sheetData></worksheet>`,
  );
}

function cellXml(cell: WorkbookCell, reference: string): string {
  if (cell === null || cell === undefined || cell === "") {
    return `<c r="${reference}"/>`;
  }
  if (typeof cell === "number" && Number.isFinite(cell)) {
    return `<c r="${reference}"><v>${cell}</v></c>`;
  }
  if (typeof cell === "boolean") {
    return `<c r="${reference}" t="b"><v>${cell ? 1 : 0}</v></c>`;
  }
  return `<c r="${reference}" t="inlineStr"><is><t>${xmlEscape(String(cell))}</t></is></c>`;
}

function columnName(columnNumber: number): string {
  let name = "";
  let remaining = columnNumber;
  while (remaining > 0) {
    const modulo = (remaining - 1) % 26;
    name = String.fromCharCode(65 + modulo) + name;
    remaining = Math.floor((remaining - modulo) / 26);
  }
  return name;
}

function xmlDocument(body: string): string {
  return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>${body}`;
}

function xmlEscape(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function safeSheetName(name: string): string {
  return name.replace(/[\[\]:*?/\\]/g, " ").slice(0, 31) || "Sheet";
}

function mediaFileDisplayName(entry: MediaFile): string {
  return (
    entry.file_name?.trim() ||
    entry.caption?.trim() ||
    `${entry.media_type || "media"}-${entry.id}`
  );
}

function voiceNoteDisplayName(entry: VoiceNote): string {
  return (
    entry.file_name?.trim() ||
    entry.provider_media_id?.trim() ||
    `voice-note-${entry.id}`
  );
}

function safeMediaFileName(name: string): string {
  return (
    name
      .trim()
      .replace(/[<>:"/\\|?*\x00-\x1F]+/g, "-")
      .replace(/\s+/g, " ")
      .replace(/^-+|-+$/g, "")
      .slice(0, 180) || "cognos-ai-media"
  );
}

function safeFileName(name: string): string {
  return (
    name.trim().replace(/[^a-z0-9-_]+/gi, "-").replace(/^-+|-+$/g, "").toLowerCase() ||
    "cognos-ai-report"
  );
}

function truncateText(value: string, maxLength: number): string {
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength - 1)}…`;
}

function formatConfidence(value: string): string {
  const parsed = Number(value);
  if (Number.isFinite(parsed)) {
    const normalized = parsed <= 1 ? parsed * 100 : parsed;
    return `${Math.round(normalized)}%`;
  }
  return formatRole(value);
}

function formatMissingFields(fields: string[]): string {
  if (fields.length === 0) {
    return "-";
  }
  return fields.map(formatRole).join(", ");
}

function summarizeObject(value: Record<string, unknown>): string {
  const entries = Object.entries(value);
  if (entries.length === 0) {
    return "-";
  }
  return entries
    .slice(0, 4)
    .map(([key, item]) => `${formatRole(key)}: ${String(item)}`)
    .join("; ");
}

function zipFiles(files: { path: string; content: string }[]): Uint8Array {
  const encoder = new TextEncoder();
  const encodedFiles = files.map((file) => ({
    path: file.path,
    nameBytes: encoder.encode(file.path),
    data: encoder.encode(file.content),
  }));
  const localParts: Uint8Array[] = [];
  const centralParts: Uint8Array[] = [];
  let offset = 0;

  for (const file of encodedFiles) {
    const crc = crc32(file.data);
    const localHeader = new Uint8Array(30);
    const localView = new DataView(localHeader.buffer);
    localView.setUint32(0, 0x04034b50, true);
    localView.setUint16(4, 20, true);
    localView.setUint16(6, 0, true);
    localView.setUint16(8, 0, true);
    localView.setUint16(10, 0, true);
    localView.setUint16(12, 0, true);
    localView.setUint32(14, crc, true);
    localView.setUint32(18, file.data.length, true);
    localView.setUint32(22, file.data.length, true);
    localView.setUint16(26, file.nameBytes.length, true);
    localView.setUint16(28, 0, true);
    localParts.push(localHeader, file.nameBytes, file.data);

    const centralHeader = new Uint8Array(46);
    const centralView = new DataView(centralHeader.buffer);
    centralView.setUint32(0, 0x02014b50, true);
    centralView.setUint16(4, 20, true);
    centralView.setUint16(6, 20, true);
    centralView.setUint16(8, 0, true);
    centralView.setUint16(10, 0, true);
    centralView.setUint16(12, 0, true);
    centralView.setUint16(14, 0, true);
    centralView.setUint32(16, crc, true);
    centralView.setUint32(20, file.data.length, true);
    centralView.setUint32(24, file.data.length, true);
    centralView.setUint16(28, file.nameBytes.length, true);
    centralView.setUint16(30, 0, true);
    centralView.setUint16(32, 0, true);
    centralView.setUint16(34, 0, true);
    centralView.setUint16(36, 0, true);
    centralView.setUint32(38, 0, true);
    centralView.setUint32(42, offset, true);
    centralParts.push(centralHeader, file.nameBytes);

    offset += localHeader.length + file.nameBytes.length + file.data.length;
  }

  const centralDirectorySize = centralParts.reduce((sum, part) => sum + part.length, 0);
  const endRecord = new Uint8Array(22);
  const endView = new DataView(endRecord.buffer);
  endView.setUint32(0, 0x06054b50, true);
  endView.setUint16(4, 0, true);
  endView.setUint16(6, 0, true);
  endView.setUint16(8, encodedFiles.length, true);
  endView.setUint16(10, encodedFiles.length, true);
  endView.setUint32(12, centralDirectorySize, true);
  endView.setUint32(16, offset, true);
  endView.setUint16(20, 0, true);

  return concatenateBytes([...localParts, ...centralParts, endRecord]);
}

function concatenateBytes(parts: Uint8Array[]): Uint8Array {
  const totalLength = parts.reduce((sum, part) => sum + part.length, 0);
  const output = new Uint8Array(totalLength);
  let offset = 0;
  for (const part of parts) {
    output.set(part, offset);
    offset += part.length;
  }
  return output;
}

function crc32(data: Uint8Array): number {
  let crc = 0xffffffff;
  for (const byte of data) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) {
      crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
    }
  }
  return (crc ^ 0xffffffff) >>> 0;
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

function formatMediaLink(entry: MediaFile): string {
  if (!entry.linked_entity_type) {
    return "Project proof";
  }
  const labels: Record<string, string> = {
    progress_entry: "Progress entry",
    manpower_entry: "Manpower entry",
    material_transaction: "Material entry",
    whatsapp_message: "Project proof",
  };
  return labels[entry.linked_entity_type] ?? formatRole(entry.linked_entity_type);
}

function formatTime(value: string): string {
  return value.slice(0, 5);
}

function normalizeTimeForApi(value: string): string {
  return value.length === 5 ? `${value}:00` : value;
}

function formFromDailySummarySetting(setting: DailySummarySetting): typeof emptyDailySummaryForm {
  return {
    enabled: setting.enabled,
    sendTimeLocal: formatTime(setting.send_time_local),
    timezone: setting.timezone,
    recipientScope: setting.recipient_scope,
  };
}

function formFromCompanyAISettings(company: Company): typeof emptyAiConfigurationForm {
  return {
    aiKeyMode: company.ai_key_mode,
    aiSubscriptionEnabled: company.ai_subscription_enabled,
  };
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
    if (
      module.id === "team" ||
      module.id === "knowledgebase" ||
      module.id === "whatsapp" ||
      module.id === "assistant" ||
      module.id === "settings"
    ) {
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
