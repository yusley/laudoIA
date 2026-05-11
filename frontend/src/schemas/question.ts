import { z } from "zod";

export const questionSchema = z.object({
  party: z.string().min(2),
  question_number: z.string().min(1),
  question_text: z.string().min(5),
  generated_answer: z.string().optional().nullable(),
  manual_answer: z.string().optional().nullable(),
});
