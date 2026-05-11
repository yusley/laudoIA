import { api } from "./client";
import type { Question } from "../types";

export async function getQuestions(processId: number) {
  const { data } = await api.get<Question[]>(`/processes/${processId}/questions`);
  return data;
}

export async function createQuestion(processId: number, payload: Omit<Question, "id" | "process_id" | "created_at" | "updated_at">) {
  const { data } = await api.post<Question>(`/processes/${processId}/questions`, payload);
  return data;
}

export async function updateQuestion(id: number, payload: Omit<Question, "id" | "process_id" | "created_at" | "updated_at">) {
  const { data } = await api.put<Question>(`/questions/${id}`, payload);
  return data;
}

export async function deleteQuestion(id: number) {
  await api.delete(`/questions/${id}`);
}
