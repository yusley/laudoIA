import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { updateChecklist } from "../api/checklists";
import { Input, Textarea } from "../components/Input";
import { Panel } from "../components/Panel";
import { checklistSchema, type ChecklistFormValues } from "../schemas/checklist";
import type { InspectionChecklist } from "../types";

type Props = {
  processId: number;
  checklist?: InspectionChecklist | null;
  onSaved?: () => void;
};

const CLEANING_PRODUCT_OPTIONS = [
  "Desinfetante",
  "Agua sanitaria",
  "Sabao",
  "Limpa-pedra",
  "Solvente",
  "Alcool",
  "Peroxido",
  "Amonia",
];

const AGENT_TYPE_OPTIONS = ["Agentes Fisicos", "Agentes Quimicos", "Agentes biologicos", "Nr 16"];
const NR16_OPTIONS = [
  "Inflamaveis (liquidos/gases combustiveis)",
  "Explosivos",
  "Energia eletrica (Nr 10)",
  "Seguranca pessoal/patrimonial",
  "Uso de motocicleta",
];
const EXPOSURE_OPTIONS = ["Eventual", "Habitual ou(e) intermitente", "Continuo ou(e) permanente"];
const YES_NO_OPTIONS = ["Sim", "Nao"];
const EPI_OPTIONS = [
  "Luvas",
  "Calcados",
  "Capacete",
  "Uniforme completo",
  "Uniforme incompleto",
  "Cinto de Seguranca",
  "Respiradores",
  "Mascara",
  "Oculos",
  "Opcao 10",
];
const DOCUMENT_OPTIONS = ["PGR", "LTCAT", "PCMSO", "Controle de ficha de EPI"];

const defaultValues: ChecklistFormValues = {
  function_role: "",
  has_cleaning_products_contact: "",
  cleaning_products: [],
  cleaning_products_other: "",
  sector: "",
  activity_description: "",
  agents: [
    { enabled: true, agent_label: "Qual agente especifico", agent_type: "", nr16_options: [], notes: "", exposure_time: "", risk_accentuated: "", permanence_risk_areas: "" },
    { enabled: false, agent_label: "Segundo agente especifico", agent_type: "", nr16_options: [], notes: "", exposure_time: "", risk_accentuated: "", permanence_risk_areas: "" },
    { enabled: false, agent_label: "Terceiro agente especifico", agent_type: "", nr16_options: [], notes: "", exposure_time: "", risk_accentuated: "", permanence_risk_areas: "" },
    { enabled: false, agent_label: "Quarto agente especifico", agent_type: "", nr16_options: [], notes: "", exposure_time: "", risk_accentuated: "", permanence_risk_areas: "" },
  ],
  epi_supply_notes: "",
  epi_types: [],
  epi_signed_form: "",
  epi_training: "",
  epi_supervised_use: "",
  documents: [],
  summary_routine: "",
  summary_exposure: "",
  summary_observations: "",
};

type ToggleFieldName = "cleaning_products" | "epi_types" | "documents";

function mergeChecklist(checklist?: InspectionChecklist | null): ChecklistFormValues {
  if (!checklist) {
    return defaultValues;
  }

  return {
    ...defaultValues,
    ...checklist,
    agents: checklist.agents?.length === 4 ? checklist.agents : defaultValues.agents,
    cleaning_products: checklist.cleaning_products || [],
    epi_types: checklist.epi_types || [],
    documents: checklist.documents || [],
  };
}

export function ChecklistForm({ processId, checklist, onSaved }: Props) {
  const form = useForm<ChecklistFormValues>({
    resolver: zodResolver(checklistSchema),
    defaultValues: mergeChecklist(checklist),
  });

  const agents = form.watch("agents");
  const hasCleaningProductsContact = form.watch("has_cleaning_products_contact");

  useEffect(() => {
    form.reset(mergeChecklist(checklist));
  }, [checklist, form]);

  function toggleArrayValue(field: ToggleFieldName, value: string) {
    const current = form.getValues(field);
    const next = current.includes(value) ? current.filter((item) => item !== value) : [...current, value];
    form.setValue(field, next, { shouldDirty: true, shouldValidate: true });
  }

  function toggleAgentNr16Option(index: number, value: string) {
    const current = form.getValues(`agents.${index}.nr16_options`);
    const next = current.includes(value) ? current.filter((item) => item !== value) : [...current, value];
    form.setValue(`agents.${index}.nr16_options`, next, { shouldDirty: true, shouldValidate: true });
  }

  async function onSubmit(values: ChecklistFormValues) {
    await updateChecklist(processId, values);
    onSaved?.();
  }

  return (
    <Panel title="Checklist da geracao de laudo">
      <form className="space-y-6" onSubmit={form.handleSubmit(onSubmit)}>
        <section className="grid gap-4 md:grid-cols-2">
          <div className="md:col-span-2">
            <label className="mb-2 block text-sm font-medium text-stone-700">Funcao/Cargo</label>
            <Input placeholder="Sua resposta" {...form.register("function_role")} />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-stone-700">Setor</label>
            <Input placeholder="Sua resposta" {...form.register("sector")} />
          </div>
          <div className="md:col-span-2">
            <label className="mb-2 block text-sm font-medium text-stone-700">Descricao das atividades</label>
            <Textarea rows={4} placeholder="Sua resposta" {...form.register("activity_description")} />
          </div>
        </section>

        <section className="rounded-3xl border border-black/10 p-4">
          <p className="mb-3 text-sm font-medium text-stone-800">Essa funcao tem contato a produtos de limpeza</p>
          <div className="flex flex-wrap gap-6">
            {YES_NO_OPTIONS.map((option) => (
              <label key={option} className="flex items-center gap-2 text-sm">
                <input type="radio" value={option} {...form.register("has_cleaning_products_contact")} />
                <span>{option}</span>
              </label>
            ))}
          </div>
          {hasCleaningProductsContact === "Sim" && (
            <div className="mt-4 space-y-3">
              <p className="text-sm font-medium text-stone-800">Se sim, quais</p>
              <div className="grid gap-2 md:grid-cols-2">
                {CLEANING_PRODUCT_OPTIONS.map((option) => (
                  <label key={option} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={form.watch("cleaning_products").includes(option)}
                      onChange={() => toggleArrayValue("cleaning_products", option)}
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
              <div>
                <label className="mb-2 block text-sm text-stone-700">Outro</label>
                <Input placeholder="Informe outro produto" {...form.register("cleaning_products_other")} />
              </div>
            </div>
          )}
        </section>

        <section className="space-y-4">
          {agents.map((agent, index) => {
            const isPrimaryAgent = index === 0;
            const isEnabled = isPrimaryAgent || agent.enabled;
            const currentType = form.watch(`agents.${index}.agent_type`);
            return (
              <div key={agent.agent_label} className="rounded-3xl border border-black/10 p-4">
                <div className="mb-4 flex items-center justify-between gap-4">
                  <h3 className="font-display text-xl">{agent.agent_label}</h3>
                  {!isPrimaryAgent && (
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={agent.enabled}
                        onChange={(event) => form.setValue(`agents.${index}.enabled`, event.target.checked, { shouldDirty: true })}
                      />
                      <span>Preencher este agente</span>
                    </label>
                  )}
                </div>

                {isEnabled && (
                  <div className="space-y-4">
                    <div>
                      <p className="mb-3 text-sm font-medium text-stone-800">Tipo de agente/risco nr 15 ou n16</p>
                      <div className="grid gap-2 md:grid-cols-2">
                        {AGENT_TYPE_OPTIONS.map((option) => (
                          <label key={option} className="flex items-center gap-2 text-sm">
                            <input type="radio" value={option} {...form.register(`agents.${index}.agent_type` as const)} />
                            <span>{option}</span>
                          </label>
                        ))}
                      </div>
                    </div>

                    {currentType === "Nr 16" && (
                      <div className="rounded-2xl bg-stone-50 p-4">
                        <p className="mb-3 text-sm font-medium text-stone-800">Periculosidade</p>
                        <div className="grid gap-2">
                          {NR16_OPTIONS.map((option) => (
                            <label key={option} className="flex items-center gap-2 text-sm">
                              <input
                                type="checkbox"
                                checked={form.watch(`agents.${index}.nr16_options`).includes(option)}
                                onChange={() => toggleAgentNr16Option(index, option)}
                              />
                              <span>{option}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}

                    <div>
                      <label className="mb-2 block text-sm font-medium text-stone-700">Sobre esse agente</label>
                      <Textarea rows={3} placeholder="Sua resposta" {...form.register(`agents.${index}.notes` as const)} />
                    </div>

                    <div>
                      <p className="mb-3 text-sm font-medium text-stone-800">Tempo de Exposicao do agente</p>
                      <div className="grid gap-2">
                        {EXPOSURE_OPTIONS.map((option) => (
                          <label key={option} className="flex items-center gap-2 text-sm">
                            <input type="radio" value={option} {...form.register(`agents.${index}.exposure_time` as const)} />
                            <span>{option}</span>
                          </label>
                        ))}
                      </div>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2">
                      <div>
                        <label className="mb-2 block text-sm font-medium text-stone-700">
                          A atividade envolve risco acentuado?
                        </label>
                        <select
                          className="w-full rounded-2xl border border-black/10 bg-white px-4 py-3"
                          {...form.register(`agents.${index}.risk_accentuated` as const)}
                        >
                          <option value="">Escolher</option>
                          <option value="Sim">Sim</option>
                          <option value="Nao">Nao</option>
                          <option value="Nao informado">Nao informado</option>
                        </select>
                      </div>
                      <div>
                        <label className="mb-2 block text-sm font-medium text-stone-700">
                          A permanencia em areas de risco?
                        </label>
                        <select
                          className="w-full rounded-2xl border border-black/10 bg-white px-4 py-3"
                          {...form.register(`agents.${index}.permanence_risk_areas` as const)}
                        >
                          <option value="">Escolher</option>
                          <option value="Sim">Sim</option>
                          <option value="Nao">Nao</option>
                          <option value="Nao informado">Nao informado</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </section>

        <section className="rounded-3xl border border-black/10 p-4">
          <h3 className="mb-4 font-display text-xl">EPI</h3>
          <div className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-medium text-stone-700">Houve fornecimento</label>
              <Input placeholder="Sua resposta" {...form.register("epi_supply_notes")} />
            </div>
            <div>
              <p className="mb-3 text-sm font-medium text-stone-800">Tipo de EPIs</p>
              <div className="grid gap-2 md:grid-cols-2">
                {EPI_OPTIONS.map((option) => (
                  <label key={option} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={form.watch("epi_types").includes(option)}
                      onChange={() => toggleArrayValue("epi_types", option)}
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <label className="mb-2 block text-sm font-medium text-stone-700">Ficha assinada</label>
                <select className="w-full rounded-2xl border border-black/10 bg-white px-4 py-3" {...form.register("epi_signed_form")}>
                  <option value="">Escolher</option>
                  <option value="Sim">Sim</option>
                  <option value="Nao">Nao</option>
                </select>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-stone-700">
                  Treinamento de guarda, uso e conservacao
                </label>
                <div className="flex flex-wrap gap-6 pt-3">
                  {YES_NO_OPTIONS.map((option) => (
                    <label key={option} className="flex items-center gap-2 text-sm">
                      <input type="radio" value={option} {...form.register("epi_training")} />
                      <span>{option}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-stone-700">Uso fiscalizado</label>
                <select className="w-full rounded-2xl border border-black/10 bg-white px-4 py-3" {...form.register("epi_supervised_use")}>
                  <option value="">Escolher</option>
                  <option value="Sim">Sim</option>
                  <option value="Nao">Nao</option>
                </select>
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-3xl border border-black/10 p-4">
          <h3 className="mb-4 font-display text-xl">Documentos</h3>
          <div className="grid gap-2 md:grid-cols-2">
            {DOCUMENT_OPTIONS.map((option) => (
              <label key={option} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.watch("documents").includes(option)}
                  onChange={() => toggleArrayValue("documents", option)}
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
        </section>

        <section className="rounded-3xl border border-black/10 p-4">
          <h3 className="mb-4 font-display text-xl">Resumo tecnico da situacao</h3>
          <div className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-medium text-stone-700">Rotina</label>
              <Textarea rows={3} placeholder="Sua resposta" {...form.register("summary_routine")} />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-stone-700">Exposicao</label>
              <Textarea rows={3} placeholder="Sua resposta" {...form.register("summary_exposure")} />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-stone-700">Observacoes</label>
              <Textarea rows={3} placeholder="Sua resposta" {...form.register("summary_observations")} />
            </div>
          </div>
        </section>

        <div>
          <button type="submit" disabled={form.formState.isSubmitting} className="rounded-full bg-ink px-5 py-3 text-sand">
            {form.formState.isSubmitting ? "Salvando checklist..." : "Salvar checklist"}
          </button>
        </div>
      </form>
    </Panel>
  );
}
