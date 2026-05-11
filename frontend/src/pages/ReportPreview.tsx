import { downloadReportExport } from "../api/reports";
import { Panel } from "../components/Panel";
import type { Report } from "../types";

type Props = {
  report: Report | null;
};

export function ReportPreview({ report }: Props) {
  if (!report) {
    return (
      <Panel title="Preview do laudo">
        <p className="text-sm text-stone-500">O preview aparecera aqui apos a geracao do laudo.</p>
      </Panel>
    );
  }

  return (
    <Panel
      title="Preview do laudo"
      action={
        <div className="flex gap-2">
          <button
            onClick={() => void downloadReportExport(report.id, "docx")}
            className="rounded-full bg-ink px-4 py-2 text-sand"
          >
            Exportar DOCX
          </button>
          <button
            onClick={() => void downloadReportExport(report.id, "pdf")}
            className="rounded-full bg-ember px-4 py-2 text-white"
          >
            Exportar PDF
          </button>
        </div>
      }
    >
      <div className="space-y-5">
        {report.sections.map((section) => (
          <article key={section.id}>
            <h3 className="mb-2 font-display text-xl">{section.title}</h3>
            <p className="whitespace-pre-wrap text-sm leading-7 text-stone-700">{section.content}</p>
          </article>
        ))}
      </div>
    </Panel>
  );
}
