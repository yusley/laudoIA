import { api } from "./client";
import type { DocumentItem } from "../types";

export async function getDocuments(processId: number) {
  const { data } = await api.get<DocumentItem[]>(`/processes/${processId}/documents`);
  return data;
}

export async function uploadDocument(processId: number, file: File, documentCategory: string) {
  const form = new FormData();
  form.append("file", file);
  form.append("document_category", documentCategory);
  const { data } = await api.post<DocumentItem>(`/processes/${processId}/documents`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function deleteDocument(id: number) {
  await api.delete(`/documents/${id}`);
}
