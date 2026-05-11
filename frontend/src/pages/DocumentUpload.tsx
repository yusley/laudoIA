import { useState } from "react";
import { deleteDocument, uploadDocument } from "../api/documents";
import { Panel } from "../components/Panel";
import type { DocumentItem } from "../types";

const categories = ["NR-15", "NR-16", "FDS/FISPQ", "Quesitos", "Prova emprestada", "Modelo de laudo", "Foto", "Outro"];

type Props = {
  processId: number;
  documents: DocumentItem[];
  onRefresh: () => Promise<void>;
};

export function DocumentUpload({ processId, documents, onRefresh }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [category, setCategory] = useState(categories[0]);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!file) return;
    setLoading(true);
    try {
      await uploadDocument(processId, file, category);
      setFile(null);
      await onRefresh();
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: number) {
    await deleteDocument(id);
    await onRefresh();
  }

  return (
    <Panel title="Documentos">
      <p className="mb-4 text-sm text-stone-600">
        Os arquivos enviados sao processados para extracao de conteudo e nao ficam armazenados no servidor.
      </p>
      <form className="mb-5 grid gap-3 md:grid-cols-[1fr_220px_160px]" onSubmit={handleSubmit}>
        <input
          type="file"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
          className="rounded-2xl border border-dashed border-black/20 bg-white px-4 py-3"
        />
        <select
          value={category}
          onChange={(event) => setCategory(event.target.value)}
          className="rounded-2xl border border-black/10 bg-white px-4 py-3"
        >
          {categories.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <button type="submit" disabled={loading || !file} className="rounded-2xl bg-moss px-4 py-3 text-white">
          {loading ? "Enviando..." : "Upload"}
        </button>
      </form>

      <div className="space-y-3">
        {documents.map((document) => (
          <div key={document.id} className="rounded-2xl border border-black/10 p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-medium">{document.original_filename}</p>
                <p className="text-sm text-stone-600">{`${document.document_category} - ${document.file_type}`}</p>
                <p className="mt-1 text-xs uppercase tracking-[0.2em] text-stone-400">
                  Processado sem armazenamento do original
                </p>
                {document.extracted_text && (
                  <p className="mt-2 text-sm text-stone-700">{document.extracted_text.slice(0, 400)}</p>
                )}
              </div>
              <button onClick={() => handleDelete(document.id)} className="text-sm text-red-600">
                Excluir
              </button>
            </div>
          </div>
        ))}
        {!documents.length && <p className="text-sm text-stone-500">Nenhum documento processado.</p>}
      </div>
    </Panel>
  );
}
