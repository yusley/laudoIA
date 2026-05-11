import { api } from "./client";
import type { Report } from "../types";

export type AIModelOption = {
  id: string;
  name: string;
  tier: "free" | "paid";
};

export const AI_MODEL_OPTIONS: AIModelOption[] = [
  { id: "openrouter/free", name: "OpenRouter Free Router", tier: "free" },
  { id: "openrouter/owl-alpha", name: "Owl Alpha", tier: "free" },
  { id: "minimax/minimax-m2.5:free", name: "MiniMax M2.5", tier: "free" },
  { id: "qwen/qwen3-next-80b-a3b-instruct:free", name: "Qwen3 Next 80B A3B Instruct", tier: "free" },
  { id: "qwen/qwen3-coder:free", name: "Qwen3 Coder 480B A35B", tier: "free" },
  { id: "meta-llama/llama-3.3-70b-instruct:free", name: "Llama 3.3 70B Instruct", tier: "free" },
  { id: "inclusionai/ling-2.6-1t:free", name: "Ling-2.6-1T", tier: "free" },
  { id: "openai/gpt-4o-mini", name: "OpenAI GPT-4o Mini", tier: "paid" },
  { id: "openai/gpt-4.1-mini", name: "OpenAI GPT-4.1 Mini", tier: "paid" },
  { id: "anthropic/claude-3.5-sonnet", name: "Anthropic Claude 3.5 Sonnet", tier: "paid" },
  { id: "google/gemini-2.0-flash", name: "Google Gemini 2.0 Flash", tier: "paid" },
  { id: "deepseek/deepseek-chat", name: "DeepSeek Chat", tier: "paid" },
];

export async function getReports(processId: number) {
  const { data } = await api.get<Report[]>(`/processes/${processId}/reports`);
  return data;
}

export async function getReport(id: number) {
  const { data } = await api.get<Report>(`/reports/${id}`);
  return data;
}

export async function generateReport(
  processId: number,
  payload: { model?: string; temperature: number; extra_instructions?: string },
) {
  const { data } = await api.post<Report>(`/processes/${processId}/reports/generate`, payload);
  return data;
}

export async function updateReport(
  reportId: number,
  payload: { title: string; content: string; status: string; sections: { title: string; content: string }[] },
) {
  const { data } = await api.put<Report>(`/reports/${reportId}`, payload);
  return data;
}

export async function regenerateSection(
  reportId: number,
  sectionId: number,
  payload: { model?: string; temperature: number; extra_instructions?: string },
) {
  const { data } = await api.post<Report>(`/reports/${reportId}/sections/${sectionId}/regenerate`, payload);
  return data;
}

export function getExportUrl(reportId: number, format: "docx" | "pdf") {
  return `${api.defaults.baseURL}/reports/${reportId}/export/${format}`;
}

export async function downloadReportExport(reportId: number, format: "docx" | "pdf") {
  const response = await api.get(`/reports/${reportId}/export/${format}`, {
    responseType: "blob",
  });

  const blob = new Blob([response.data], {
    type:
      format === "docx"
        ? "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        : "application/pdf",
  });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `laudo-${reportId}.${format}`;
  link.click();
  window.URL.revokeObjectURL(url);
}
