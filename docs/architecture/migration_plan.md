# Plano de Migração

**Data:** 2026-07-22  
**Status:** Em andamento

---

## Tabela de Migração

| Origem Atual | Destino Proposto | Ação | Motivo | Risco | Status |
|-------------|------------------|------|--------|-------|--------|
| `docs/cliente/Gestao_de_Colaboradores.html` | `docs/client/Gestao_de_Colaboradores.html` | COPIAR | Padronizar nome da pasta (inglês) | Baixo | ✅ Referenciado no novo código |
| `docs/cliente/*.html` | `docs/client/` | COPIAR | Padronizar estrutura | Baixo | 📋 Pendente |
| `docs/tests/apis/get_token.txt` | `.local/curls/get_token.txt` | COPIAR | Arquivo com credenciais em local seguro | Médio | 📋 Pendente |
| `docs/tests/request_sample.txt` | `.local/curls/request_sample.txt` | COPIAR | Arquivo com credenciais | Médio | 📋 Pendente |
| `docs/sample/user_hml.txt` | `.local/user_hml.txt` | COPIAR | Credenciais de teste | Médio | 📋 Pendente |
| `docs/tests/test_ma_hr_orchi.py` | Referência apenas | MANTER | Código legado (substituído por `src/`) | Nenhum | ✅ Mantido |
| `docs/discover/` | `docs/architecture/legacy/discover/` | MANTER NO LOCAL | Documentação histórica | Nenhum | 📋 Opcional |
| `docs/discover2/` | `docs/architecture/legacy/discover2/` | MANTER NO LOCAL | Documentação histórica | Nenhum | 📋 Opcional |
| `docs/desenhos/` | `docs/architecture/diagrams/` | MANTER NO LOCAL | Diagramas de referência | Nenhum | 📋 Opcional |
| `docs/kb/` | `docs/kb/` | MANTER | Knowledge base ativa | Nenhum | ✅ Sem alteração |
| `docs/_referencia_alelo_faq_ciandt/` | Sem migração | MANTER | Já ignorado pelo Git | Nenhum | ✅ |

---

## Observações

1. **Nenhum arquivo original foi apagado.** A nova estrutura coexiste com a antiga.
2. O código novo em `src/discover_alelo/` referencia `docs/cliente/` como fallback.
3. Arquivos candidatos à remoção devem ser validados manualmente antes de excluir.
4. A migração de pastas como `discover/` e `discover2/` é cosmética e pode ser feita depois.

---

## Próximos Passos (Requerem Validação Humana)

- [ ] Confirmar que os relatórios gerados estão corretos.
- [ ] Atualizar `ALELO_REFRESH_TOKEN` no `.env` com token válido.
- [ ] Re-executar `run_api_tests.py` com token novo.
- [ ] Validar se os dados retornados pela API GET estão completos.
- [ ] Decidir se as pastas `discover/` e `discover2/` devem ser movidas.
- [ ] Avaliar remoção dos arquivos antigos em `docs/tests/`.
