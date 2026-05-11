import { Link } from "react-router-dom";
import { Panel } from "../components/Panel";
import type { Process } from "../types";

type Props = {
  processes: Process[];
};

export function ProcessList({ processes }: Props) {
  return (
    <Panel
      title="Processos"
      action={
        <Link to="/processos/novo" className="rounded-full bg-ember px-4 py-2 text-white">
          Novo processo
        </Link>
      }
    >
      <div className="grid gap-4">
        {processes.map((process) => (
          <Link
            key={process.id}
            to={`/processos/${process.id}`}
            className="rounded-3xl border border-black/10 bg-white px-5 py-4 transition hover:-translate-y-0.5 hover:border-ember"
          >
            <p className="font-medium">{process.process_number}</p>
            <p className="text-sm text-stone-600">
              {process.claimant} x {process.defendant}
            </p>
            <p className="mt-2 text-xs uppercase tracking-wide text-stone-500">
              {process.city}/{process.state} • {process.report_type}
            </p>
          </Link>
        ))}
        {!processes.length && <p className="text-sm text-stone-500">Nenhum processo encontrado.</p>}
      </div>
    </Panel>
  );
}
