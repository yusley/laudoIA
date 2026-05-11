import { api } from "./client";
import type { CreditPackage, Payment, UsageEvent, Wallet } from "../types";

export async function getWallet() {
  const { data } = await api.get<Wallet>("/billing/wallet");
  return data;
}

export async function getCreditPackages() {
  const { data } = await api.get<CreditPackage[]>("/billing/packages");
  return data;
}

export async function createCheckout(creditPackageId: number) {
  const { data } = await api.post<Payment>("/billing/checkout", {
    credit_package_id: creditPackageId,
  });
  return data;
}

export async function getPayments() {
  const { data } = await api.get<Payment[]>("/billing/payments");
  return data;
}

export async function getUsageEvents() {
  const { data } = await api.get<UsageEvent[]>("/billing/usage");
  return data;
}
