import { Link } from "react-router-dom";
import { Panel } from "../components/Panel";
import type { CreditPackage, Payment, Process, Report, UsageEvent, Wallet } from "../types";
import { BillingPanel } from "./BillingPanel";

type Props = {
  processes: Process[];
  reportsByProcess: Record<number, Report[]>;
  wallet: Wallet | null;
  packages: CreditPackage[];
  payments: Payment[];
  usageEvents: UsageEvent[];
  onRefreshBilling: () => Promise<void>;
};

export function Dashboard({
  processes,
  reportsByProcess,
  wallet,
  packages,
  payments,
  usageEvents,
  onRefreshBilling,
}: Props) {
  const allReports = Object.values(reportsByProcess).flat();
  const draftCount = allReports.filter((report) => report.status === "draft").length;
  const finalCount = allReports.filter((report) => report.status === "final").length;

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-6">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-ember">Painel pericial</p>
          <h1 className="font-display text-4xl">Visao geral dos processos e laudos</h1>
        </div>
        <Link to="/processos/novo" className="rounded-full bg-ink px-5 py-3 text-sand">
          Novo processo
        </Link>
      </div>

      <div className="grid gap-5 md:grid-cols-4">
        <Panel title="Processos">{processes.length}</Panel>
        <Panel title="Laudos em rascunho">{draftCount}</Panel>
        <Panel title="Laudos finalizados">{finalCount}</Panel>
        <Panel title="Ultimos cadastros">{processes.slice(0, 3).length}</Panel>
      </div>

      <Panel title="Ultimos processos">
        <div className="space-y-3">
          {processes.slice(0, 5).map((process) => (
            <Link
              key={process.id}
              to={`/processos/${process.id}`}
              className="flex items-center justify-between rounded-2xl border border-black/10 px-4 py-3 hover:border-ember"
            >
              <div>
                <p className="font-medium">{process.process_number}</p>
                <p className="text-sm text-stone-600">
                  {process.claimant} x {process.defendant}
                </p>
              </div>
              <span className="text-sm uppercase text-stone-500">{process.report_type}</span>
            </Link>
          ))}
          {!processes.length && <p className="text-sm text-stone-500">Nenhum processo cadastrado ainda.</p>}
        </div>
      </Panel>

      <BillingPanel
        wallet={wallet}
        packages={packages}
        payments={payments}
        usageEvents={usageEvents}
        onRefresh={onRefreshBilling}
      />
    </div>
  );
}
