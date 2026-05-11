import { api } from "./client";
import type { Process } from "../types";

export async function getProcesses() {
  const { data } = await api.get<Process[]>("/processes");
  return data;
}

export async function getProcess(id: number) {
  const { data } = await api.get<Process>(`/processes/${id}`);
  return data;
}

export async function createProcess(payload: Omit<Process, "id" | "user_id" | "created_at" | "updated_at">) {
  const { data } = await api.post<Process>("/processes", payload);
  return data;
}

export async function updateProcess(
  id: number,
  payload: Omit<Process, "id" | "user_id" | "created_at" | "updated_at">,
) {
  const { data } = await api.put<Process>(`/processes/${id}`, payload);
  return data;
}

export async function deleteProcess(id: number) {
  await api.delete(`/processes/${id}`);
}
