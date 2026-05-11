import { api } from "./client";
import type { InspectionChecklist } from "../types";

export async function getChecklist(processId: number) {
  const { data } = await api.get<InspectionChecklist>(`/processes/${processId}/checklist`);
  return data;
}

export async function updateChecklist(
  processId: number,
  payload: Omit<InspectionChecklist, "id" | "process_id" | "created_at" | "updated_at">,
) {
  const { data } = await api.put<InspectionChecklist>(`/processes/${processId}/checklist`, payload);
  return data;
}
