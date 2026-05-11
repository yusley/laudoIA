export type Process = {
  id: number;
  user_id: number;
  process_number: string;
  court: string;
  labor_court: string;
  city: string;
  state: string;
  claimant: string;
  defendant: string;
  expert_name: string;
  expert_registry: string;
  report_type: string;
  diligence_date?: string | null;
  diligence_location?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at?: string | null;
};

export type ChecklistAgent = {
  enabled: boolean;
  agent_label: string;
  agent_type?: string | null;
  nr16_options: string[];
  notes?: string | null;
  exposure_time?: string | null;
  risk_accentuated?: string | null;
  permanence_risk_areas?: string | null;
};

export type InspectionChecklist = {
  id?: number | null;
  process_id: number;
  function_role?: string | null;
  has_cleaning_products_contact?: string | null;
  cleaning_products: string[];
  cleaning_products_other?: string | null;
  sector?: string | null;
  activity_description?: string | null;
  agents: ChecklistAgent[];
  epi_supply_notes?: string | null;
  epi_types: string[];
  epi_signed_form?: string | null;
  epi_training?: string | null;
  epi_supervised_use?: string | null;
  documents: string[];
  summary_routine?: string | null;
  summary_exposure?: string | null;
  summary_observations?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type DocumentItem = {
  id: number;
  process_id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_type: string;
  document_category: string;
  extracted_text?: string | null;
  created_at: string;
};

export type Question = {
  id: number;
  process_id: number;
  party: string;
  question_number: string;
  question_text: string;
  generated_answer?: string | null;
  manual_answer?: string | null;
  created_at: string;
  updated_at?: string | null;
};

export type ReportSection = {
  id: number;
  section_order: number;
  title: string;
  content: string;
  created_at: string;
  updated_at?: string | null;
};

export type Report = {
  id: number;
  process_id: number;
  title: string;
  content: string;
  status: string;
  created_at: string;
  updated_at?: string | null;
  sections: ReportSection[];
};

export type User = {
  id: number;
  name: string;
  email: string;
  is_admin: boolean;
  created_at: string;
};

export type WalletTransaction = {
  id: number;
  type: string;
  amount: string;
  balance_after: string;
  reference_type?: string | null;
  reference_id?: string | null;
  description?: string | null;
  created_at: string;
};

export type Wallet = {
  id: number;
  user_id: number;
  balance_credit: string;
  reserved_credit: string;
  lifetime_purchased_credit: string;
  lifetime_used_credit: string;
  created_at: string;
  updated_at?: string | null;
  transactions: WalletTransaction[];
};

export type CreditPackage = {
  id: number;
  name: string;
  credit_amount: string;
  price_brl: string;
  estimated_report_capacity: number;
  price_per_estimated_report_brl: string;
  is_active: boolean;
};

export type Payment = {
  id: number;
  provider: string;
  status: string;
  amount_brl: string;
  credit_amount: string;
  checkout_url?: string | null;
  external_reference: string;
  created_at: string;
  updated_at?: string | null;
};

export type UsageEvent = {
  id: number;
  action: string;
  model: string;
  is_paid_model: boolean;
  openrouter_cost_credit: string;
  openrouter_cost_usd: string;
  exchange_rate_usd_brl: string;
  openrouter_cost_brl: string;
  platform_revenue_brl: string;
  platform_margin_brl: string;
  platform_cost_credit: string;
  status: string;
  error_message?: string | null;
  created_at: string;
};
