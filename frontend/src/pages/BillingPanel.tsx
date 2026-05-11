import { useState } from "react";
import { createCheckout } from "../api/billing";
import { Panel } from "../components/Panel";
import type { CreditPackage, Payment, UsageEvent, Wallet } from "../types";

type Props = {
  wallet: Wallet | null;
  packages: CreditPackage[];
  payments: Payment[];
  usageEvents: UsageEvent[];
  onRefresh: () => Promise<void>;
};

export function BillingPanel({ wallet, packages, payments, usageEvents, onRefresh }: Props) {
  const [loadingPackageId, setLoadingPackageId] = useState<number | null>(null);

  async function handleCheckout(creditPackageId: number) {
    setLoadingPackageId(creditPackageId);
    try {
      const payment = await createCheckout(creditPackageId);
      if (payment.checkout_url) {
        window.open(payment.checkout_url, "_blank", "noopener,noreferrer");
      }
      await onRefresh();
    } finally {
      setLoadingPackageId(null);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <Panel title="Carteira de creditos">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl bg-stone-100 p-4">
            <p className="text-xs uppercase tracking-wide text-stone-500">Saldo disponivel</p>
            <p className="mt-2 text-3xl font-semibold">{wallet?.balance_credit ?? "0.0000"}</p>
            <p className="mt-1 text-xs text-stone-500">
              1 credito equivale a aproximadamente 1 laudo completo em modelo pago.
            </p>
          </div>
          <div className="rounded-2xl bg-stone-100 p-4">
            <p className="text-xs uppercase tracking-wide text-stone-500">Reservado</p>
            <p className="mt-2 text-3xl font-semibold">{wallet?.reserved_credit ?? "0.0000"}</p>
          </div>
          <div className="rounded-2xl bg-stone-100 p-4">
            <p className="text-xs uppercase tracking-wide text-stone-500">Total comprado</p>
            <p className="mt-2 text-xl font-semibold">{wallet?.lifetime_purchased_credit ?? "0.0000"}</p>
          </div>
          <div className="rounded-2xl bg-stone-100 p-4">
            <p className="text-xs uppercase tracking-wide text-stone-500">Total utilizado</p>
            <p className="mt-2 text-xl font-semibold">{wallet?.lifetime_used_credit ?? "0.0000"}</p>
          </div>
        </div>
      </Panel>

      <Panel title="Comprar creditos">
        <p className="mb-4 text-sm text-stone-600">
          A quantidade de laudos e uma media aproximada. O consumo real pode variar pelo tamanho dos documentos,
          modelo escolhido e regeneracoes de secoes.
        </p>
        <div className="space-y-3">
          {packages.map((item) => (
            <div key={item.id} className="flex items-center justify-between gap-4 rounded-2xl border border-black/10 p-4">
              <div>
                <p className="font-medium">{item.name}</p>
                <p className="text-sm text-stone-600">
                  R$ {item.price_brl} - {item.credit_amount} creditos
                </p>
                <p className="text-sm font-medium text-stone-800">
                  Mais ou menos {item.estimated_report_capacity} laudos
                </p>
                <p className="text-xs text-stone-500">
                  Media: R$ {item.price_per_estimated_report_brl} por laudo estimado
                </p>
              </div>
              <button
                onClick={() => void handleCheckout(item.id)}
                disabled={loadingPackageId === item.id}
                className="rounded-full bg-ember px-4 py-2 text-white disabled:opacity-60"
              >
                {loadingPackageId === item.id ? "Abrindo..." : "Comprar"}
              </button>
            </div>
          ))}
        </div>
      </Panel>

      <Panel title="Pagamentos recentes">
        <div className="space-y-3">
          {payments.slice(0, 5).map((payment) => (
            <div key={payment.id} className="rounded-2xl border border-black/10 p-4">
              <p className="font-medium">
                R$ {payment.amount_brl} - {payment.credit_amount} creditos
              </p>
              <p className="text-sm text-stone-600">{payment.status}</p>
            </div>
          ))}
          {!payments.length && <p className="text-sm text-stone-500">Nenhum pagamento registrado.</p>}
        </div>
      </Panel>

      <Panel title="Uso recente de IA">
        <div className="space-y-3">
          {usageEvents.slice(0, 5).map((event) => (
            <div key={event.id} className="rounded-2xl border border-black/10 p-4">
              <p className="font-medium">
                {event.model} - {event.action}
              </p>
              <p className="text-sm text-stone-600">
                Custo plataforma: {event.platform_cost_credit} - {event.status}
              </p>
              <p className="text-xs text-stone-500">
                OpenRouter: US$ {event.openrouter_cost_usd} / R$ {event.openrouter_cost_brl} - Receita: R${" "}
                {event.platform_revenue_brl} - Margem: R$ {event.platform_margin_brl}
              </p>
            </div>
          ))}
          {!usageEvents.length && <p className="text-sm text-stone-500">Nenhum consumo registrado ainda.</p>}
        </div>
      </Panel>
    </div>
  );
}
