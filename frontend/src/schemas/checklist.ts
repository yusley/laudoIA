import { z } from "zod";

export const checklistAgentSchema = z.object({
  enabled: z.boolean(),
  agent_label: z.string(),
  agent_type: z.string().optional().nullable(),
  nr16_options: z.array(z.string()),
  notes: z.string().optional().nullable(),
  exposure_time: z.string().optional().nullable(),
  risk_accentuated: z.string().optional().nullable(),
  permanence_risk_areas: z.string().optional().nullable(),
});

export const checklistSchema = z.object({
  function_role: z.string().optional().nullable(),
  has_cleaning_products_contact: z.string().optional().nullable(),
  cleaning_products: z.array(z.string()),
  cleaning_products_other: z.string().optional().nullable(),
  sector: z.string().optional().nullable(),
  activity_description: z.string().optional().nullable(),
  agents: z.array(checklistAgentSchema).length(4),
  epi_supply_notes: z.string().optional().nullable(),
  epi_types: z.array(z.string()),
  epi_signed_form: z.string().optional().nullable(),
  epi_training: z.string().optional().nullable(),
  epi_supervised_use: z.string().optional().nullable(),
  documents: z.array(z.string()),
  summary_routine: z.string().optional().nullable(),
  summary_exposure: z.string().optional().nullable(),
  summary_observations: z.string().optional().nullable(),
});

export type ChecklistFormValues = z.infer<typeof checklistSchema>;
