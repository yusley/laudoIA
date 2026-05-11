import { z } from "zod";

export const processSchema = z.object({
  process_number: z.string().min(3),
  court: z.string().min(2),
  labor_court: z.string().min(2),
  city: z.string().min(2),
  state: z.string().length(2),
  claimant: z.string().min(2),
  defendant: z.string().min(2),
  expert_name: z.string().min(2),
  expert_registry: z.string().min(2),
  report_type: z.string().min(2),
  diligence_date: z.string().optional().nullable(),
  diligence_location: z.string().optional().nullable(),
  notes: z.string().optional().nullable(),
});

export type ProcessFormValues = z.infer<typeof processSchema>;
