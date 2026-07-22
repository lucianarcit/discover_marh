"""Gera relatórios consolidados após a execução dos testes.

Uso:
    python scripts/generate_api_report.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from discover_alelo.config import get_project_root
from discover_alelo.sanitization import sanitize


def main() -> None:
    root = get_project_root()

    print("=" * 60)
    print("  GERAÇÃO DE RELATÓRIOS - Discover Alelo")
    print("=" * 60)
    print()

    # Localiza a execução mais recente
    runs_dir = root / "artifacts" / "api_runs"
    if not runs_dir.exists():
        print("❌ Nenhuma execução encontrada. Execute primeiro: python scripts/run_api_tests.py")
        sys.exit(1)

    run_dirs = sorted(runs_dir.iterdir(), reverse=True)
    if not run_dirs:
        print("❌ Nenhuma pasta de execução encontrada.")
        sys.exit(1)

    latest_run = run_dirs[0]
    print(f"📁 Usando execução: {latest_run.name}")

    # Carrega dados
    summary_path = latest_run / "execution_summary.json"
    responses_path = latest_run / "sanitized_responses.json"

    if not summary_path.exists():
        print("❌ execution_summary.json não encontrado.")
        sys.exit(1)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    responses = []
    if responses_path.exists():
        responses = json.loads(responses_path.read_text(encoding="utf-8"))

    # Carrega inventário original
    inventory_path = root / "artifacts" / "api_inventory" / "gestao_colaboradores_apis.json"
    inventory = []
    if inventory_path.exists():
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))

    # 1. Gera api_test_report.md
    print("\n1. Gerando relatório de testes...")
    _generate_test_report(root, summary, responses, inventory, latest_run.name)

    # 2. Gera model_consumption_assessment.md
    print("2. Gerando avaliação de consumo pelo modelo...")
    _generate_model_assessment(root, inventory, responses)

    # 3. Gera model_data_catalog.json
    print("3. Gerando catálogo de dados para modelo...")
    _generate_data_catalog(root, inventory, responses)

    print()
    print("=" * 60)
    print("  Relatórios gerados com sucesso.")
    print("=" * 60)


def _generate_test_report(
    root: Path,
    summary: dict,
    responses: list,
    inventory: list,
    run_name: str,
) -> None:
    """Gera docs/reports/api_test_report.md"""
    report_dir = root / "docs" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "api_test_report.md"

    executed = [r for r in responses if r.get("execution_status") not in ("SKIPPED_SAFETY", "SKIPPED_NO_SAMPLE")]
    skipped = [r for r in responses if r.get("execution_status") in ("SKIPPED_SAFETY", "SKIPPED_NO_SAMPLE")]

    lines = [
        "# Relatório de Testes de API - Gestão de Colaboradores",
        "",
        f"**Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Execução:** `{run_name}`",
        f"**Ambiente:** {summary.get('environment', 'homologacao')}",
        f"**Autenticação:** OAuth2 Bearer Token (refresh_token grant)",
        "",
        "---",
        "",
        "## Resumo Geral",
        "",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| Total de operações | {summary.get('total_operations', 0)} |",
        f"| Sucessos | {summary.get('successes', 0)} |",
        f"| Falhas | {summary.get('failures', 0)} |",
        f"| Ignoradas (segurança) | {summary.get('skipped_safety', 0)} |",
        f"| Ignoradas (sem exemplo) | {summary.get('skipped_no_sample', 0)} |",
        f"| Duração total | {summary.get('total_duration_ms', 0)}ms |",
        f"| Status codes encontrados | {summary.get('status_codes_found', [])} |",
        "",
        "---",
        "",
        "## APIs Executadas",
        "",
        "| Operação | Método | Status HTTP | Resultado | Duração |",
        "|----------|--------|-------------|-----------|---------|",
    ]

    for r in executed:
        icon = "✅" if r.get("success") else "❌"
        lines.append(
            f"| {r.get('operation_name', 'N/A')} | {r.get('method', '')} | "
            f"{r.get('status_code', 'N/A')} | {icon} {r.get('execution_status', '')} | "
            f"{r.get('duration_ms', 0)}ms |"
        )

    lines.extend([
        "",
        "## APIs Não Executadas",
        "",
        "| Operação | Método | Motivo |",
        "|----------|--------|--------|",
    ])

    for r in skipped:
        lines.append(
            f"| {r.get('operation_name', 'N/A')} | {r.get('method', '')} | "
            f"{r.get('error_message', 'Operação mutável')} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Localização dos Artefatos",
        "",
        f"- Resumo: `artifacts/api_runs/{run_name}/execution_summary.json`",
        f"- Respostas sanitizadas: `artifacts/api_runs/{run_name}/sanitized_responses.json`",
        f"- Schemas: `artifacts/api_runs/{run_name}/schemas.json`",
        f"- Individual: `artifacts/api_runs/{run_name}/individual/`",
        "",
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"   ✅ {report_path.relative_to(root)}")


def _generate_model_assessment(
    root: Path, inventory: list, responses: list
) -> None:
    """Gera docs/reports/model_consumption_assessment.md"""
    report_dir = root / "docs" / "reports"
    report_path = report_dir / "model_consumption_assessment.md"

    lines = [
        "# Avaliação de Consumo pelo Modelo de IA",
        "",
        f"**Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**APIs analisadas:** {len(inventory)}",
        "",
        "---",
        "",
        "## Matriz Consolidada",
        "",
        "| API | Intenção possível | Dados úteis | Dados sensíveis | Estratégia | Recomendação |",
        "|-----|------------------|-------------|-----------------|-----------|--------------|",
    ]

    assessments = []
    for op in inventory:
        assessment = _assess_operation(op)
        assessments.append(assessment)
        lines.append(
            f"| {op.get('operation_name', '')} | "
            f"{assessment['intent']} | "
            f"{assessment['useful_data']} | "
            f"{assessment['sensitive_data']} | "
            f"{assessment['strategy']} | "
            f"{assessment['recommendation']} |"
        )

    lines.extend(["", "---", "", "## Avaliação Detalhada por API", ""])

    for op, assessment in zip(inventory, assessments):
        lines.extend([
            f"### {op.get('operation_name', 'N/A')}",
            "",
            f"1. **Finalidade:** {assessment['purpose']}",
            f"2. **Dados de entrada:** {assessment['input_data']}",
            f"3. **Dados retornados:** {assessment['output_data']}",
            f"4. **Campos úteis para o modelo:** {assessment['useful_fields']}",
            f"5. **Campos que NÃO devem ir ao modelo:** {assessment['restricted_fields']}",
            f"6. **Dados pessoais/sensíveis:** {assessment['pii_present']}",
            f"7. **Necessidade de anonimização:** {assessment['needs_anonymization']}",
            f"8. **Necessidade de transformação:** {assessment['needs_transformation']}",
            f"9. **Intenções de usuário atendidas:** {assessment['user_intents']}",
            f"10. **Determinística e factual:** {assessment['deterministic']}",
            f"11. **Atual ou histórico:** {assessment['temporal']}",
            f"12. **Requer consulta em tempo real:** {assessment['real_time']}",
            f"13. **Pode ser usada em RAG:** {assessment['rag_candidate']}",
            f"14. **Deve ser tool call:** {assessment['tool_call']}",
            f"15. **Riscos de segurança:** {assessment['security_risks']}",
            f"16. **Riscos de alucinação:** {assessment['hallucination_risks']}",
            f"17. **Regras de autorização:** {assessment['auth_rules']}",
            f"18. **Recomendação final:** `{assessment['recommendation']}`",
            "",
        ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"   ✅ {report_path.relative_to(root)}")


def _assess_operation(op: dict) -> dict:
    """Avalia uma operação para consumo por modelo de IA."""
    method = op.get("method", "")
    name = op.get("operation_name", "").lower()

    is_get = method == "GET"
    is_mutating = method in ("POST", "PUT", "PATCH", "DELETE")

    # Análise baseada no tipo de operação
    if "consulta" in name or "listar" in name or is_get:
        return {
            "purpose": "Consultar lista de colaboradores cadastrados na empresa",
            "input_data": "Token de autenticação, page (paginação), nameOrCpf (filtro opcional)",
            "output_data": "Lista de colaboradores com nome, documento, local de trabalho, endereço de entrega",
            "useful_fields": "name, placeName, subtype, isHomeDelivery, products",
            "restricted_fields": "documentNumber, email, phoneNumber, motherName, beneficiaryId, address",
            "pii_present": "Sim — CPF, email, telefone, nome da mãe, endereço",
            "needs_anonymization": "Sim — CPF, telefone, email devem ser removidos ou mascarados",
            "needs_transformation": "Sim — agrupar por tipo de entrega, simplificar estrutura",
            "user_intents": "Listar colaboradores, verificar cadastro, consultar local de entrega",
            "deterministic": "Sim — dados cadastrais são factuais",
            "temporal": "Atual (reflete estado presente do cadastro)",
            "real_time": "Sim — requer consulta à API para dados atualizados",
            "rag_candidate": "Não — dados mudam frequentemente",
            "tool_call": "Sim — deve ser usado como tool call em tempo de execução",
            "security_risks": "Exposição de PII se não sanitizado; acesso depende de permissão do interlocutor",
            "hallucination_risks": "Baixo se resposta é usada diretamente; alto se modelo inferir dados",
            "auth_rules": "Requer token válido, FNP ativo, prova de vida OK, usuário deve ser interlocutor",
            "intent": "Listar colaboradores",
            "useful_data": "nome, local, tipo entrega",
            "sensitive_data": "CPF, email, telefone",
            "strategy": "Tool call + sanitização",
            "recommendation": "APTO_SOMENTE_COM_TOOL_CALL",
        }
    elif "cadastro" in name:
        return {
            "purpose": "Cadastrar novo colaborador na empresa",
            "input_data": "Dados pessoais completos do colaborador (nome, CPF, data nascimento, etc.)",
            "output_data": "Status 201 (criado) ou erro",
            "useful_fields": "Status code da operação",
            "restricted_fields": "Todos os campos de entrada (PII completo)",
            "pii_present": "Sim — todos os dados de entrada são PII",
            "needs_anonymization": "N/A — operação de escrita",
            "needs_transformation": "N/A",
            "user_intents": "Cadastrar novo colaborador",
            "deterministic": "Sim — operação transacional",
            "temporal": "Operação pontual (não consulta histórica)",
            "real_time": "Sim — operação de escrita em tempo real",
            "rag_candidate": "Não",
            "tool_call": "Sim — mas com validação humana prévia",
            "security_risks": "Alto — manipula PII, pode criar registros indevidos",
            "hallucination_risks": "Alto — modelo NÃO deve inferir dados pessoais",
            "auth_rules": "Requer token, FNP, prova de vida, permissão de interlocutor",
            "intent": "Cadastrar colaborador",
            "useful_data": "Confirmação de cadastro",
            "sensitive_data": "Todos os campos de entrada",
            "strategy": "Tool call com confirmação",
            "recommendation": "NECESSITA_VALIDACAO_DO_CLIENTE",
        }
    elif "atualiza" in name:
        return {
            "purpose": "Atualizar dados de um colaborador existente",
            "input_data": "beneficiaryId + dados atualizados do colaborador",
            "output_data": "Status 204 (atualizado) ou erro",
            "useful_fields": "Status code da operação",
            "restricted_fields": "Todos os campos de entrada (PII)",
            "pii_present": "Sim",
            "needs_anonymization": "N/A — operação de escrita",
            "needs_transformation": "N/A",
            "user_intents": "Alterar dados de colaborador (endereço, local de entrega)",
            "deterministic": "Sim",
            "temporal": "Operação pontual",
            "real_time": "Sim",
            "rag_candidate": "Não",
            "tool_call": "Sim — com confirmação",
            "security_risks": "Alto — pode alterar dados cadastrais indevidamente",
            "hallucination_risks": "Alto",
            "auth_rules": "Requer token, FNP, prova de vida, permissão de interlocutor",
            "intent": "Atualizar colaborador",
            "useful_data": "Confirmação de atualização",
            "sensitive_data": "Todos os campos de entrada",
            "strategy": "Tool call com confirmação dupla",
            "recommendation": "NECESSITA_VALIDACAO_DO_CLIENTE",
        }
    else:  # DELETE / Exclusão
        return {
            "purpose": "Excluir um colaborador do sistema",
            "input_data": "beneficiaryId do colaborador a excluir",
            "output_data": "Status 204 (excluído) ou erro",
            "useful_fields": "Status code da operação",
            "restricted_fields": "beneficiaryId",
            "pii_present": "Sim — beneficiaryId identifica uma pessoa",
            "needs_anonymization": "N/A",
            "needs_transformation": "N/A",
            "user_intents": "Remover colaborador da empresa",
            "deterministic": "Sim",
            "temporal": "Operação irreversível",
            "real_time": "Sim",
            "rag_candidate": "Não",
            "tool_call": "Sim — com confirmação múltipla",
            "security_risks": "Muito alto — exclusão irreversível de dados",
            "hallucination_risks": "Muito alto — modelo NÃO deve sugerir exclusões",
            "auth_rules": "Requer token, FNP, prova de vida, permissão de interlocutor",
            "intent": "Excluir colaborador",
            "useful_data": "Confirmação de exclusão",
            "sensitive_data": "beneficiaryId",
            "strategy": "Tool call com múltiplas confirmações",
            "recommendation": "NAO_APTO",
        }


def _generate_data_catalog(root: Path, inventory: list, responses: list) -> None:
    """Gera artifacts/api_inventory/model_data_catalog.json"""
    catalog_dir = root / "artifacts" / "api_inventory"
    catalog_path = catalog_dir / "model_data_catalog.json"

    catalog = []
    for op in inventory:
        entry = _build_catalog_entry(op)
        catalog.append(entry)

    catalog_path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"   ✅ {catalog_path.relative_to(root)}")


def _build_catalog_entry(op: dict) -> dict:
    """Constrói uma entrada do catálogo de dados para modelo."""
    method = op.get("method", "")
    name = op.get("operation_name", "").lower()

    is_get = method == "GET"

    if "consulta" in name or is_get:
        return {
            "operation_name": op.get("operation_name", ""),
            "possible_user_intents": [
                "Listar colaboradores da empresa",
                "Verificar se colaborador está cadastrado",
                "Consultar local de entrega do colaborador",
                "Ver quantidade total de colaboradores",
            ],
            "useful_response_fields": [
                "total", "content[].name", "content[].placeName",
                "content[].subtype", "content[].isHomeDelivery",
                "content[].shippingAddressName", "pageable",
            ],
            "restricted_fields": [
                "content[].documentNumber", "content[].email",
                "content[].phoneNumber", "content[].motherName",
                "content[].beneficiaryId", "content[].beneficiaryIdEncrypted",
                "content[].address",
            ],
            "pii_fields": [
                "documentNumber", "email", "phoneNumber",
                "motherName", "beneficiaryId", "address.postalCode",
            ],
            "requires_real_time_call": True,
            "rag_candidate": False,
            "tool_call_candidate": True,
            "required_transformations": [
                "Remover campos PII antes de apresentar ao usuário",
                "Paginar resultados",
                "Filtrar por nome quando solicitado",
            ],
            "authorization_requirements": [
                "Token OAuth2 válido",
                "FNP (device fingerprint) ativo",
                "Prova de vida OK",
                "Usuário deve ser interlocutor da empresa",
            ],
            "recommendation": "APTO_SOMENTE_COM_TOOL_CALL",
            "notes": "Operação segura de consulta. Dados pessoais devem ser sanitizados antes de exibir.",
        }
    elif "cadastro" in name:
        return {
            "operation_name": op.get("operation_name", ""),
            "possible_user_intents": [
                "Cadastrar novo colaborador",
                "Adicionar beneficiário na empresa",
            ],
            "useful_response_fields": ["status_code"],
            "restricted_fields": [
                "documentNumber", "motherName", "email",
                "phoneNumber", "birthDate", "address",
            ],
            "pii_fields": [
                "documentNumber", "motherName", "email",
                "phoneNumber", "birthDate", "name",
                "address.postalCode", "address.street",
            ],
            "requires_real_time_call": True,
            "rag_candidate": False,
            "tool_call_candidate": True,
            "required_transformations": [
                "Validar dados antes de enviar",
                "Confirmar com o usuário antes de executar",
            ],
            "authorization_requirements": [
                "Token OAuth2 válido",
                "FNP ativo",
                "Prova de vida OK",
                "Permissão de interlocutor",
            ],
            "recommendation": "NECESSITA_VALIDACAO_DO_CLIENTE",
            "notes": "Operação de criação. Alto risco de PII. Requer confirmação explícita do usuário.",
        }
    elif "atualiza" in name:
        return {
            "operation_name": op.get("operation_name", ""),
            "possible_user_intents": [
                "Atualizar dados do colaborador",
                "Mudar local de entrega",
                "Corrigir informações cadastrais",
            ],
            "useful_response_fields": ["status_code"],
            "restricted_fields": [
                "documentNumber", "motherName", "email",
                "phoneNumber", "birthDate", "address", "beneficiaryId",
            ],
            "pii_fields": [
                "documentNumber", "motherName", "email",
                "phoneNumber", "birthDate", "name",
            ],
            "requires_real_time_call": True,
            "rag_candidate": False,
            "tool_call_candidate": True,
            "required_transformations": [
                "Identificar campo a atualizar",
                "Confirmar alteração com o usuário",
            ],
            "authorization_requirements": [
                "Token OAuth2 válido",
                "FNP ativo",
                "Prova de vida OK",
                "Permissão de interlocutor",
            ],
            "recommendation": "NECESSITA_VALIDACAO_DO_CLIENTE",
            "notes": "Operação de atualização. Requer beneficiaryId de consulta prévia.",
        }
    else:
        return {
            "operation_name": op.get("operation_name", ""),
            "possible_user_intents": [
                "Remover colaborador da empresa",
                "Excluir cadastro de beneficiário",
            ],
            "useful_response_fields": ["status_code"],
            "restricted_fields": ["beneficiaryId"],
            "pii_fields": ["beneficiaryId"],
            "requires_real_time_call": True,
            "rag_candidate": False,
            "tool_call_candidate": False,
            "required_transformations": [
                "Confirmar exclusão múltiplas vezes",
                "Verificar se colaborador não tem pedidos pendentes",
            ],
            "authorization_requirements": [
                "Token OAuth2 válido",
                "FNP ativo",
                "Prova de vida OK",
                "Permissão de interlocutor",
            ],
            "recommendation": "NAO_APTO",
            "notes": "Operação de exclusão irreversível. NÃO deve ser acessível pelo modelo sem supervisão humana.",
        }


if __name__ == "__main__":
    main()
