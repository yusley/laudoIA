import { getWallet } from "../api/billing";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getChecklist } from "../api/checklists";
import { getDocuments } from "../api/documents";
import { getProcess } from "../api/processes";
import { getQuestions } from "../api/questions";
import { getReports } from "../api/reports";
import { ChecklistForm } from "./ChecklistForm";
import { DocumentUpload } from "./DocumentUpload";
import { ProcessForm } from "./ProcessForm";
import { QuestionManager } from "./QuestionManager";
import { ReportEditor } from "./ReportEditor";
import { ReportPreview } from "./ReportPreview";
import type { DocumentItem, InspectionChecklist, Process, Question, Report, User, Wallet } from "../types";

type Props = {
  user: User | null;
};

export function ProcessDetail({ user }: Props) {
  const { id } = useParams();
  const processId = Number(id);

  const [process, setProcess] = useState<Process | null>(null);
  const [checklist, setChecklist] = useState<InspectionChecklist | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadAll() {
    setLoading(true);
    try {
      const [processData, checklistData, documentData, questionData, reportData, walletData] = await Promise.all([
        getProcess(processId),
        getChecklist(processId),
        getDocuments(processId),
        getQuestions(processId),
        getReports(processId),
        getWallet(),
      ]);
      setProcess(processData);
      setChecklist(checklistData);
      setDocuments(documentData);
      setQuestions(questionData);
      setReports(reportData);
      setWallet(walletData);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAll();
  }, [processId]);

  if (loading) {
    return <div>Carregando processo...</div>;
  }

  if (!process) {
    return <div>Processo nao encontrado.</div>;
  }

  const latestReport = reports[0] || null;

  return (
    <div className="space-y-6">
      <ProcessForm process={process} onSaved={loadAll} />
      <ChecklistForm processId={processId} checklist={checklist} onSaved={loadAll} />
      <DocumentUpload processId={processId} documents={documents} onRefresh={loadAll} />
      <QuestionManager processId={processId} questions={questions} onRefresh={loadAll} />
      <ReportEditor processId={processId} report={latestReport} wallet={wallet} user={user} onRefresh={loadAll} />
      <ReportPreview report={latestReport} />
    </div>
  );
}
