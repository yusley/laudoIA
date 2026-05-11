import { useEffect, useState } from "react";
import axios from "axios";
import { AI_MODEL_OPTIONS, generateReport, regenerateSection, updateReport } from "../api/reports";
import { Input, Textarea } from "../components/Input";
import { Panel } from "../components/Panel";
import type { Report, User, Wallet } from "../types";

type Props = {
  processId: number;
  report: Report | null;
  wallet: Wallet | null;
  user: User | null;
  onRefresh: () => Promise<void>;
};

export function ReportEditor({ processId, report, wallet, user, onRefresh }: Props) {
  const [model, setModel] = useState(AI_MODEL_OPTIONS[0].id);
  const [temperature, setTemperature] = useState(0.2);
  const [extraInstructions, setExtraInstructions] = useState("");
  const [loading, setLoading] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState("draft");
  const [sections, setSections] = useState<Report["sections"]>([]);

  useEffect(() => {
    setTitle(report?.title || "");
    setStatus(report?.status || "draft");
    setSections(report?.sections || []);
  }, [report]);

  useEffect(() => {
    if (!loading) {
      setElapsedSeconds(0);
      return;
    }
    const interval = window.setInterval(() => {
      setElapsedSeconds((current) => current + 1);
    }, 1000);
    return () => window.clearInterval(interval);
  }, [loading]);

  function getApiErrorMessage(error: unknown, fallback: string) {
    if (axios.isAxiosError(error)) {
      if (error.code === "ECONNABORTED") {
        return "A geracao demorou demais e foi interrompida. Tente novamente ou escolha um modelo pago mais estavel.";
      }
      const detail = error.response?.data?.detail;
      if (typeof detail === "string" && detail.trim()) {
        return detail;
      }
    }
    if (error instanceof Error && error.message) {
      return error.message;
    }
    return fallback;
  }

  async function handleGenerate() {
    const selectedModel = AI_MODEL_OPTIONS.find((item) => item.id === model);
    const balance = Number(wallet?.balance_credit || 0);
    if (!user?.is_admin && selectedModel?.tier === "paid" && balance < 1) {
      setError("Saldo insuficiente para gerar laudo com modelo pago. Cada laudo completo consome pelo menos 1 credito.");
      return;
    }
    setLoading(true);
    try {
      setError("");
      setElapsedSeconds(0);
      await generateReport(processId, {
        model,
        temperature: Number(temperature),
        extra_instructions: extraInstructions,
      });
      await onRefresh();
    } catch (error) {
      setError(getApiErrorMessage(error, "Nao foi possivel gerar o laudo."));
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    if (!report) return;
    await updateReport(report.id, {
      title,
      content: sections.map((section) => `# ${section.title}\n${section.content}`).join("\n\n"),
      status,
      sections: sections.map((section) => ({ title: section.title, content: section.content })),
    });
    await onRefresh();
  }

  async function handleRegenerate(sectionId: number) {
    if (!report) return;
    setLoading(true);
    try {
      setError("");
      setElapsedSeconds(0);
      await regenerateSection(report.id, sectionId, {
        model,
        temperature: Number(temperature),
        extra_instructions: extraInstructions,
      });
      await onRefresh();
    } catch (error) {
      setError(getApiErrorMessage(error, "Nao foi possivel regenerar a secao."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Panel title="Geracao e edicao do laudo">
      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <select value={model} onChange={(event) => setModel(event.target.value)} className="rounded-2xl border border-black/10 bg-white px-4 py-3">
          {AI_MODEL_OPTIONS.map((item) => (
            <option
              key={item.id}
              value={item.id}
              disabled={!user?.is_admin && item.tier === "paid" && Number(wallet?.balance_credit || 0) < 1}
            >
              [{item.tier === "free" ? "FREE" : "PAGO"}] {item.name}
            </option>
          ))}
        </select>
        <Input
          type="number"
          step="0.1"
          min="0"
          max="2"
          value={temperature}
          onChange={(event) => setTemperature(Number(event.target.value))}
        />
        <button onClick={handleGenerate} disabled={loading} className="rounded-2xl bg-ember px-4 py-3 text-white">
          {loading ? `Gerando... ${elapsedSeconds}s` : report ? "Gerar nova versao" : "Gerar laudo"}
        </button>
      </div>

      {loading && (
        <p className="mb-4 text-sm text-stone-600">
          A IA esta processando o laudo. Modelos gratuitos podem levar mais tempo ou tentar outro provedor automaticamente.
        </p>
      )}

      <p className="mb-4 text-xs text-stone-500">
        Modelos `FREE` podem ficar temporariamente indisponiveis por limite do provedor no OpenRouter.
      </p>
      <p className="mb-4 text-xs text-stone-500">
        {user?.is_admin
          ? "Perfil admin: modelos pagos liberados."
          : `Saldo atual: ${wallet?.balance_credit ?? "0.0000"} creditos. Laudo completo em modelo pago consome pelo menos 1 credito.`}
      </p>

      <Textarea
        rows={4}
        value={extraInstructions}
        onChange={(event) => setExtraInstructions(event.target.value)}
        placeholder="Instrucoes extras para a IA"
        className="mb-6"
      />

      {error && <p className="mb-4 text-sm text-red-600">{error}</p>}

      {!report && <p className="text-sm text-stone-500">Gere o primeiro laudo para iniciar a edicao por secoes.</p>}

      {report && (
        <div className="space-y-4">
          <Input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />
          {sections.map((section, index) => (
            <div key={section.id} className="rounded-2xl border border-black/10 p-4">
              <div className="mb-3 flex items-center justify-between gap-4">
                <strong>{section.title}</strong>
                <button onClick={() => handleRegenerate(section.id)} className="text-sm text-ember">
                  Regenerar secao
                </button>
              </div>
              <Textarea
                rows={10}
                value={section.content}
                onChange={(event) => {
                  setSections((current) =>
                    current.map((item, itemIndex) =>
                      itemIndex === index ? { ...item, content: event.target.value } : item,
                    ),
                  );
                }}
              />
            </div>
          ))}
          <div className="flex gap-3">
            <button onClick={handleSave} className="rounded-full bg-ink px-5 py-3 text-sand">
              Salvar rascunho
            </button>
            <button
              onClick={async () => {
                if (!report) return;
                await updateReport(report.id, {
                  title,
                  content: sections.map((section) => `# ${section.title}\n${section.content}`).join("\n\n"),
                  status: "final",
                  sections: sections.map((section) => ({ title: section.title, content: section.content })),
                });
                await onRefresh();
              }}
              className="rounded-full bg-moss px-5 py-3 text-white"
            >
              Marcar como finalizado
            </button>
          </div>
        </div>
      )}
    </Panel>
  );
}
