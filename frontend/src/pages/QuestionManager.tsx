import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { createQuestion, deleteQuestion, updateQuestion } from "../api/questions";
import { Input, Textarea } from "../components/Input";
import { Panel } from "../components/Panel";
import { questionSchema } from "../schemas/question";
import type { Question } from "../types";

type Props = {
  processId: number;
  questions: Question[];
  onRefresh: () => Promise<void>;
};

type QuestionFormValues = {
  party: string;
  question_number: string;
  question_text: string;
  generated_answer?: string | null;
  manual_answer?: string | null;
};

export function QuestionManager({ processId, questions, onRefresh }: Props) {
  const form = useForm<QuestionFormValues>({
    resolver: zodResolver(questionSchema),
    defaultValues: {
      party: "reclamante",
      question_number: "",
      question_text: "",
      generated_answer: "",
      manual_answer: "",
    },
  });

  async function handleCreate(values: QuestionFormValues) {
    await createQuestion(processId, values);
    form.reset({ party: "reclamante", question_number: "", question_text: "", generated_answer: "", manual_answer: "" });
    await onRefresh();
  }

  async function handleDelete(id: number) {
    await deleteQuestion(id);
    await onRefresh();
  }

  async function handleManualAnswerSave(question: Question, manual_answer: string) {
    await updateQuestion(question.id, {
      party: question.party,
      question_number: question.question_number,
      question_text: question.question_text,
      generated_answer: question.generated_answer || "",
      manual_answer,
    });
    await onRefresh();
  }

  return (
    <Panel title="Quesitos">
      <form className="mb-6 grid gap-3 md:grid-cols-4" onSubmit={form.handleSubmit(handleCreate)}>
        <select className="rounded-2xl border border-black/10 bg-white px-4 py-3" {...form.register("party")}>
          <option value="reclamante">Reclamante</option>
          <option value="reclamada">Reclamada</option>
          <option value="juizo">Juizo</option>
        </select>
        <Input placeholder="Numero do quesito" {...form.register("question_number")} />
        <div className="md:col-span-2">
          <Input placeholder="Pergunta" {...form.register("question_text")} />
        </div>
        <div className="md:col-span-4">
          <button type="submit" className="rounded-full bg-ink px-4 py-2 text-sand">
            Adicionar quesito
          </button>
        </div>
      </form>

      <div className="space-y-4">
        {questions.map((question) => (
          <article key={question.id} className="rounded-2xl border border-black/10 p-4">
            <div className="mb-3 flex items-center justify-between gap-4">
              <div>
                <p className="font-medium">
                  {question.question_number}. {question.question_text}
                </p>
                <p className="text-xs uppercase tracking-wide text-stone-500">{question.party}</p>
              </div>
              <button onClick={() => handleDelete(question.id)} className="text-sm text-red-600">
                Excluir
              </button>
            </div>
            <p className="mb-3 rounded-2xl bg-stone-50 p-3 text-sm text-stone-700">
              {question.generated_answer || "Resposta gerada ainda nao disponivel."}
            </p>
            <Textarea
              rows={4}
              defaultValue={question.manual_answer || ""}
              placeholder="Resposta editada manualmente"
              onBlur={(event) => void handleManualAnswerSave(question, event.target.value)}
            />
          </article>
        ))}
        {!questions.length && <p className="text-sm text-stone-500">Cadastre os quesitos do processo.</p>}
      </div>
    </Panel>
  );
}
