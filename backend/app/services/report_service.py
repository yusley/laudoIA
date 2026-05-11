import json
import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.billing import UsageEvent
from app.models.process import Process
from app.models.question import Question
from app.models.report import Report, ReportSection
from app.models.user import User
from app.services.ai_service import generate_text
from app.services.wallet_service import (
    calculate_usage_financials,
    ensure_wallet,
    is_paid_model,
    release_reservation,
    reserve_for_paid_model,
    settle_usage_cost,
)

SYSTEM_PROMPT = """Voce e um perito judicial especialista em Engenharia de Seguranca do Trabalho e Higiene Ocupacional, com atuacao na Justica do Trabalho.

Elabore um laudo tecnico pericial completo, formal, tecnico, imparcial e estruturado, com base nos documentos fornecidos, nos quesitos apresentados, nas Normas Regulamentadoras NR-15 e NR-16 e nos modelos de laudos anexados.

O laudo deve conter:
1. Dados do processo e das partes
2. Objeto do laudo
3. Metodologia, tecnica de avaliacao e equipamentos
4. Inspecao pericial
5. Ambiente de trabalho
6. Atividades desenvolvidas
7. Equipamentos de protecao individual
8. Analise de insalubridade conforme NR-15
9. Analise de periculosidade conforme NR-16, se aplicavel
10. Respostas aos quesitos da reclamante
11. Respostas aos quesitos da reclamada
12. Respostas aos quesitos do juizo, se houver
13. Conclusao
14. Termo de encerramento

Regras:
- Nao invente dados ausentes.
- Quando faltar informacao, declare a limitacao tecnica.
- Diferencie avaliacao qualitativa e quantitativa.
- Responda todos os quesitos individualmente.
- Use linguagem pericial formal.
- Fundamente a analise com base normativa.
- Trate prova emprestada como documento de apoio, quando informada.
- Explique agentes quimicos, fisicos e biologicos quando forem citados.
- Para agentes quimicos, considerar FDS/FISPQ, vias de absorcao, frequencia, duracao e enquadramento normativo.
- Para bisfenol, diferenciar fenol, BPA, BPS e compostos organicos, evitando enquadramento automatico sem fundamentacao.
- Quando houver checklist extraido de imagens, considere expressamente todas as opcoes listadas, inclusive as desmarcadas, distinguindo o que estava selecionado do que apenas aparecia como alternativa.

Retorne o laudo com titulos numerados, no formato markdown simples, usando uma secao por topico principal.
"""

SECTION_TITLES = [
    "Dados do processo e das partes",
    "Objeto do laudo",
    "Metodologia, tecnica de avaliacao e equipamentos",
    "Inspecao pericial",
    "Ambiente de trabalho",
    "Atividades desenvolvidas",
    "Equipamentos de protecao individual",
    "Analise de insalubridade conforme NR-15",
    "Analise de periculosidade conforme NR-16",
    "Respostas aos quesitos da reclamante",
    "Respostas aos quesitos da reclamada",
    "Respostas aos quesitos do juizo",
    "Conclusao",
    "Termo de encerramento",
]

CHECKLIST_REFERENCE = """
Checklist pericial de referencia:
- Tipo de pericia: Direta; Por similaridade.
- Contato com produtos de limpeza: Sim; Nao.
- Se sim, quais: Desinfetante; Agua sanitaria; Sabao; Limpa-pedra; Solvente; Alcool; Peroxido; Amonia; Outro.
- Tipo de agente/risco nr 15 ou nr16: Agentes Fisicos; Agentes Quimicos; Agentes biologicos; Nr 16.
- Nr 16 / Periculosidade: Inflamaveis (liquidos/gases combustiveis); Explosivos; Energia eletrica (Nr 10); Seguranca pessoal/patrimonial; Uso de motocicleta.
- Tempo de exposicao do agente: Eventual; Habitual ou(e) intermitente; Continuo ou(e) permanente.
- Perguntas complementares: A atividade envolve risco acentuado?; A permanencia em areas de risco?
- Fluxo de agentes adicionais: Terceiro agente especifico; Quarto agente especifico; Nao ha mais agentes.
- Tipo de EPIs: Luvas; Calcados; Capacete; Uniforme completo; Uniforme incompleto; Cinto de Seguranca; Respiradores; Mascara; Oculos; Opcao 10.
- Ficha assinada: Sim; Nao.
- Treinamento de guarda, uso e conservacao: Sim; Nao.
- Uso fiscalizado: Sim; Nao.
- Documentos: PGR; LTCAT; PCMSO; Controle de ficha de EPI.
- Anexos: Fotos.
- Resumo tecnico da situacao: Rotina; Exposicao; Observacoes.
""".strip()


def _stringify_list(items: list[str]) -> str:
    cleaned = [item.strip() for item in items if isinstance(item, str) and item.strip()]
    return ", ".join(cleaned) if cleaned else "Nao informado"


def _format_checklist_for_prompt(process: Process) -> str:
    checklist = process.inspection_checklist
    if not checklist or not isinstance(checklist.checklist_data, dict):
        return "Sem checklist estruturado cadastrado."

    data = checklist.checklist_data
    agents = data.get("agents") or []
    active_agents = [item for item in agents if isinstance(item, dict) and item.get("enabled")]

    lines = [
        f"- Funcao/cargo: {data.get('function_role') or 'Nao informado'}",
        f"- Contato com produtos de limpeza: {data.get('has_cleaning_products_contact') or 'Nao informado'}",
        f"- Produtos de limpeza assinalados: {_stringify_list(data.get('cleaning_products') or [])}",
        f"- Outro produto informado: {data.get('cleaning_products_other') or 'Nao informado'}",
        f"- Setor: {data.get('sector') or 'Nao informado'}",
        f"- Descricao das atividades: {data.get('activity_description') or 'Nao informado'}",
    ]

    if active_agents:
        for index, agent in enumerate(active_agents, start=1):
            lines.extend(
                [
                    f"- Agente {index} ({agent.get('agent_label') or 'Agente especifico'}):",
                    f"  Tipo: {agent.get('agent_type') or 'Nao informado'}",
                    f"  Opcoes NR 16: {_stringify_list(agent.get('nr16_options') or [])}",
                    f"  Sobre esse agente: {agent.get('notes') or 'Nao informado'}",
                    f"  Tempo de exposicao: {agent.get('exposure_time') or 'Nao informado'}",
                    f"  Atividade envolve risco acentuado?: {agent.get('risk_accentuated') or 'Nao informado'}",
                    f"  Permanencia em areas de risco?: {agent.get('permanence_risk_areas') or 'Nao informado'}",
                ]
            )
    else:
        lines.append("- Agentes especificos: Nao informados.")

    lines.extend(
        [
            f"- Houve fornecimento de EPI: {data.get('epi_supply_notes') or 'Nao informado'}",
            f"- Tipos de EPI: {_stringify_list(data.get('epi_types') or [])}",
            f"- Ficha assinada: {data.get('epi_signed_form') or 'Nao informado'}",
            f"- Treinamento de guarda, uso e conservacao: {data.get('epi_training') or 'Nao informado'}",
            f"- Uso fiscalizado: {data.get('epi_supervised_use') or 'Nao informado'}",
            f"- Documentos assinalados: {_stringify_list(data.get('documents') or [])}",
            f"- Resumo tecnico / rotina: {data.get('summary_routine') or 'Nao informado'}",
            f"- Resumo tecnico / exposicao: {data.get('summary_exposure') or 'Nao informado'}",
            f"- Resumo tecnico / observacoes: {data.get('summary_observations') or 'Nao informado'}",
        ]
    )

    return "\n".join(lines)


def build_report_prompt(process: Process) -> str:
    document_chunks = []
    for document in process.documents:
        extracted = (document.extracted_text or "").strip()[:7000]
        document_chunks.append(
            f"Categoria: {document.document_category}\nArquivo: {document.original_filename}\nConteudo:\n{extracted or '[Sem texto extraido]'}"
        )

    grouped_questions: dict[str, list[Question]] = {"reclamante": [], "reclamada": [], "juizo": []}
    for question in process.questions:
        grouped_questions.setdefault(question.party, []).append(question)

    question_text = "\n\n".join(
        f"{party.upper()}:\n" + "\n".join(
            f"{item.question_number}. {item.question_text}" for item in questions
        )
        for party, questions in grouped_questions.items()
        if questions
    )

    return f"""
Dados do processo:
- Numero do processo: {process.process_number}
- Tribunal: {process.court}
- Vara: {process.labor_court}
- Cidade/UF: {process.city}/{process.state}
- Reclamante: {process.claimant}
- Reclamada: {process.defendant}
- Perito: {process.expert_name}
- CREA/registro: {process.expert_registry}
- Tipo de laudo: {process.report_type}
- Data da diligencia: {process.diligence_date or 'Nao informada'}
- Local da diligencia: {process.diligence_location or 'Nao informado'}
- Observacoes gerais: {process.notes or 'Sem observacoes'}

Quesitos cadastrados:
{question_text or 'Sem quesitos cadastrados.'}

Documentos extraidos:
{chr(10).join(document_chunks) or 'Sem documentos anexados.'}

Checklist estruturado cadastrado no sistema:
{_format_checklist_for_prompt(process)}

Orientacao sobre checklist anexado por imagem:
- Se houver transcricao de checklist em imagens, trate esse conteudo como fonte primaria da inspecao pericial.
- Ao mencionar checkbox, radio, select ou listas de EPI/agentes/documentos, preserve todas as opcoes visiveis e identifique o estado marcado/desmarcado quando estiver presente.

Opcoes esperadas no checklist:
{CHECKLIST_REFERENCE}
""".strip()


def split_into_sections(content: str) -> list[tuple[str, str]]:
    lines = content.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_title = "Introducao"
    buffer: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            if buffer:
                sections.append((current_title, buffer))
            current_title = stripped.lstrip("# ").strip()
            buffer = []
        else:
            buffer.append(line)

    if buffer:
        sections.append((current_title, buffer))

    normalized = [(title, "\n".join(body).strip()) for title, body in sections if title or body]
    if len(normalized) <= 1:
        normalized = []
        for order, title in enumerate(SECTION_TITLES, start=1):
            normalized.append((f"{order}. {title}", "Secao nao estruturada automaticamente."))
    return normalized


async def generate_report_for_process(
    db: Session,
    user: User,
    process: Process,
    model: str | None = None,
    temperature: float = 0.2,
    extra_instructions: str | None = None,
) -> Report:
    user_prompt = build_report_prompt(process)
    if extra_instructions:
        user_prompt = f"{user_prompt}\n\nInstrucoes extras do usuario:\n{extra_instructions}"

    wallet = ensure_wallet(db, user)
    requested_model = model or "openrouter/free"
    reservation_reference = uuid.uuid4().hex
    reserved_amount = (
        Decimal("0")
        if user.is_admin
        else reserve_for_paid_model(db, wallet, requested_model, reservation_reference, "report_generate")
    )
    db.commit()

    try:
        ai_result = await generate_text(
            SYSTEM_PROMPT,
            user_prompt,
            model=model,
            temperature=temperature,
            user_tag=f"app_user_{user.id}",
        )
    except Exception:
        release_reservation(db, wallet, reserved_amount, reservation_reference, requested_model)
        db.commit()
        raise

    financials = calculate_usage_financials(ai_result.model, ai_result.cost_credit, "report_generate")
    platform_cost = Decimal("0") if user.is_admin else financials.platform_cost_credit
    settle_usage_cost(db, wallet, platform_cost, reserved_amount, reservation_reference, ai_result.model)

    report = Report(
        process_id=process.id,
        title=f"Laudo Pericial - Processo {process.process_number}",
        content=ai_result.content,
        status="draft",
    )
    db.add(report)
    db.flush()

    for index, (title, body) in enumerate(split_into_sections(ai_result.content), start=1):
        db.add(
            ReportSection(
                report_id=report.id,
                section_order=index,
                title=title,
                content=body,
            )
        )

    for question in process.questions:
        if not question.generated_answer:
            question.generated_answer = "Resposta contemplada no laudo gerado. Revise e ajuste se necessario."

    db.add(
        UsageEvent(
            user_id=user.id,
            process_id=process.id,
            report_id=report.id,
            action="report_generate",
            model=ai_result.model,
            is_paid_model=is_paid_model(ai_result.model),
            openrouter_user_tag=ai_result.user_tag,
            prompt_tokens=ai_result.prompt_tokens,
            completion_tokens=ai_result.completion_tokens,
            reasoning_tokens=ai_result.reasoning_tokens,
            cached_tokens=ai_result.cached_tokens,
            openrouter_cost_credit=ai_result.cost_credit,
            openrouter_cost_usd=financials.openrouter_cost_usd,
            exchange_rate_usd_brl=financials.exchange_rate_usd_brl,
            openrouter_cost_brl=financials.openrouter_cost_brl,
            platform_revenue_brl=Decimal("0") if user.is_admin else financials.platform_revenue_brl,
            platform_margin_brl=Decimal("0") if user.is_admin else financials.platform_margin_brl,
            platform_cost_credit=platform_cost,
            status="success",
            raw_usage_json=json.dumps(ai_result.raw_response, ensure_ascii=True),
        )
    )

    db.commit()
    db.refresh(report)
    return report


async def regenerate_section(
    db: Session,
    user: User,
    report: Report,
    section: ReportSection,
    model: str | None = None,
    temperature: float = 0.2,
) -> ReportSection:
    process = report.process
    prompt = (
        f"{build_report_prompt(process)}\n\n"
        f"Regenere apenas a secao '{section.title}', mantendo coerencia com o laudo e com foco tecnico."
    )
    wallet = ensure_wallet(db, user)
    requested_model = model or "openrouter/free"
    reservation_reference = uuid.uuid4().hex
    reserved_amount = (
        Decimal("0")
        if user.is_admin
        else reserve_for_paid_model(db, wallet, requested_model, reservation_reference, "section_regenerate")
    )
    db.commit()
    try:
        ai_result = await generate_text(
            SYSTEM_PROMPT,
            prompt,
            model=model,
            temperature=temperature,
            user_tag=f"app_user_{user.id}",
        )
    except Exception:
        release_reservation(db, wallet, reserved_amount, reservation_reference, requested_model)
        db.commit()
        raise

    financials = calculate_usage_financials(ai_result.model, ai_result.cost_credit, "section_regenerate")
    platform_cost = Decimal("0") if user.is_admin else financials.platform_cost_credit
    settle_usage_cost(db, wallet, platform_cost, reserved_amount, reservation_reference, ai_result.model)
    section.content = ai_result.content
    report.content = "\n\n".join(
        f"# {item.title}\n{item.content}" for item in sorted(report.sections, key=lambda value: value.section_order)
    )
    db.add(
        UsageEvent(
            user_id=user.id,
            process_id=process.id,
            report_id=report.id,
            action="section_regenerate",
            model=ai_result.model,
            is_paid_model=is_paid_model(ai_result.model),
            openrouter_user_tag=ai_result.user_tag,
            prompt_tokens=ai_result.prompt_tokens,
            completion_tokens=ai_result.completion_tokens,
            reasoning_tokens=ai_result.reasoning_tokens,
            cached_tokens=ai_result.cached_tokens,
            openrouter_cost_credit=ai_result.cost_credit,
            openrouter_cost_usd=financials.openrouter_cost_usd,
            exchange_rate_usd_brl=financials.exchange_rate_usd_brl,
            openrouter_cost_brl=financials.openrouter_cost_brl,
            platform_revenue_brl=Decimal("0") if user.is_admin else financials.platform_revenue_brl,
            platform_margin_brl=Decimal("0") if user.is_admin else financials.platform_margin_brl,
            platform_cost_credit=platform_cost,
            status="success",
            raw_usage_json=json.dumps(ai_result.raw_response, ensure_ascii=True),
        )
    )
    db.add(section)
    db.add(report)
    db.commit()
    db.refresh(section)
    return section
