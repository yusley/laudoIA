import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { createProcess, updateProcess } from "../api/processes";
import { Input, Textarea } from "../components/Input";
import { Panel } from "../components/Panel";
import { processSchema, type ProcessFormValues } from "../schemas/process";
import type { Process } from "../types";

type Props = {
  process?: Process;
  onSaved?: () => void;
};

const defaultValues: ProcessFormValues = {
  process_number: "",
  court: "",
  labor_court: "",
  city: "",
  state: "",
  claimant: "",
  defendant: "",
  expert_name: "",
  expert_registry: "",
  report_type: "insalubridade",
  diligence_date: "",
  diligence_location: "",
  notes: "",
};

export function ProcessForm({ process, onSaved }: Props) {
  const navigate = useNavigate();
  const form = useForm<ProcessFormValues>({
    resolver: zodResolver(processSchema),
    defaultValues: process
      ? {
          ...process,
          diligence_date: process.diligence_date || "",
          diligence_location: process.diligence_location || "",
          notes: process.notes || "",
        }
      : defaultValues,
  });

  async function onSubmit(values: ProcessFormValues) {
    const payload = {
      ...values,
      diligence_date: values.diligence_date || null,
      diligence_location: values.diligence_location || null,
      notes: values.notes || null,
    };

    if (process) {
      await updateProcess(process.id, payload);
      onSaved?.();
    } else {
      const created = await createProcess(payload);
      navigate(`/processos/${created.id}`);
    }
  }

  return (
    <Panel title={process ? "Editar processo" : "Novo processo"}>
      <form className="grid gap-4 md:grid-cols-2" onSubmit={form.handleSubmit(onSubmit)}>
        <Input placeholder="Numero do processo" {...form.register("process_number")} />
        <Input placeholder="Tribunal" {...form.register("court")} />
        <Input placeholder="Vara" {...form.register("labor_court")} />
        <Input placeholder="Cidade" {...form.register("city")} />
        <Input placeholder="UF" maxLength={2} {...form.register("state")} />
        <Input placeholder="Reclamante" {...form.register("claimant")} />
        <Input placeholder="Reclamada" {...form.register("defendant")} />
        <Input placeholder="Nome do perito" {...form.register("expert_name")} />
        <Input placeholder="CREA/registro" {...form.register("expert_registry")} />
        <select className="rounded-2xl border border-black/10 bg-white px-4 py-3" {...form.register("report_type")}>
          <option value="insalubridade">Insalubridade</option>
          <option value="periculosidade">Periculosidade</option>
          <option value="ambos">Ambos</option>
        </select>
        <Input type="date" {...form.register("diligence_date")} />
        <div className="md:col-span-2">
          <Input placeholder="Local da diligencia" {...form.register("diligence_location")} />
        </div>
        <div className="md:col-span-2">
          <Textarea rows={5} placeholder="Observacoes gerais" {...form.register("notes")} />
        </div>
        <div className="md:col-span-2">
          <button
            type="submit"
            disabled={form.formState.isSubmitting}
            className="rounded-full bg-ink px-5 py-3 text-sand"
          >
            {form.formState.isSubmitting ? "Salvando..." : "Salvar processo"}
          </button>
        </div>
      </form>
    </Panel>
  );
}
