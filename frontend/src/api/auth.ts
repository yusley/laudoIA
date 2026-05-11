import { api } from "./client";
import type { User } from "../types";

export async function login(email: string, password: string) {
  const { data } = await api.post<{ access_token: string; token_type: string }>("/auth/login", {
    email,
    password,
  });
  return data;
}

export async function register(name: string, email: string, password: string) {
  const { data } = await api.post<User>("/auth/register", { name, email, password });
  return data;
}

export async function me() {
  const { data } = await api.get<User>("/auth/me");
  return data;
}
