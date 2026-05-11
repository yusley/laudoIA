import { Route, Routes } from "react-router-dom";
import { useEffect, useState } from "react";
import { getCreditPackages, getPayments, getUsageEvents, getWallet } from "../api/billing";
import { Layout } from "../components/Layout";
import { ProtectedRoute } from "../components/ProtectedRoute";
import { Dashboard } from "../pages/Dashboard";
import { Login } from "../pages/Login";
import { ProcessDetail } from "../pages/ProcessDetail";
import { ProcessForm } from "../pages/ProcessForm";
import { ProcessList } from "../pages/ProcessList";
import { useAuth } from "../hooks/useAuth";
import { getProcesses } from "../api/processes";
import { getReports } from "../api/reports";
import type { CreditPackage, Payment, Process, Report, UsageEvent, Wallet } from "../types";

function AppShell() {
  const { user, setUser, loading } = useAuth();
  const [processes, setProcesses] = useState<Process[]>([]);
  const [reportsByProcess, setReportsByProcess] = useState<Record<number, Report[]>>({});
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [creditPackages, setCreditPackages] = useState<CreditPackage[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [usageEvents, setUsageEvents] = useState<UsageEvent[]>([]);

  async function loadDashboardData() {
    const [processData, walletData, packageData, paymentData, usageData] = await Promise.all([
      getProcesses(),
      getWallet(),
      getCreditPackages(),
      getPayments(),
      getUsageEvents(),
    ]);
    setProcesses(processData);
    setWallet(walletData);
    setCreditPackages(packageData);
    setPayments(paymentData);
    setUsageEvents(usageData);

    const reportEntries = await Promise.all(
      processData.map(async (process) => [process.id, await getReports(process.id)] as const),
    );
    setReportsByProcess(Object.fromEntries(reportEntries));
  }

  useEffect(() => {
    if (!user) return;
    void loadDashboardData();
  }, [user]);

  return (
    <Routes>
      <Route path="/login" element={<Login setUser={setUser} />} />
      <Route
        path="/"
        element={
          <ProtectedRoute user={user} loading={loading}>
            {user ? <Layout user={user} /> : <div />}
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={
            <Dashboard
              processes={processes}
              reportsByProcess={reportsByProcess}
              wallet={wallet}
              packages={creditPackages}
              payments={payments}
              usageEvents={usageEvents}
              onRefreshBilling={loadDashboardData}
            />
          }
        />
        <Route path="processos" element={<ProcessList processes={processes} />} />
        <Route path="processos/novo" element={<ProcessForm onSaved={loadDashboardData} />} />
        <Route path="processos/:id" element={<ProcessDetail user={user} />} />
      </Route>
    </Routes>
  );
}

export function AppRoutes() {
  return <AppShell />;
}
