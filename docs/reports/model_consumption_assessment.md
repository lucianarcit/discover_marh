# Avaliação de Consumo pelo Modelo de IA

**Gerado em:** 2026-07-22 13:08:01
**APIs analisadas:** 4

---

## Matriz Consolidada

| API | Intenção possível | Dados úteis | Dados sensíveis | Estratégia | Recomendação |
|-----|------------------|-------------|-----------------|-----------|--------------|
| Consulta dos colaboradores | Listar colaboradores | nome, local, tipo entrega | CPF, email, telefone | Tool call + sanitização | APTO_SOMENTE_COM_TOOL_CALL |
| Cadastro de colaborador | Cadastrar colaborador | Confirmação de cadastro | Todos os campos de entrada | Tool call com confirmação | NECESSITA_VALIDACAO_DO_CLIENTE |
| Atualização de colaborador | Atualizar colaborador | Confirmação de atualização | Todos os campos de entrada | Tool call com confirmação dupla | NECESSITA_VALIDACAO_DO_CLIENTE |
| Exclusão de colaborador | Excluir colaborador | Confirmação de exclusão | beneficiaryId | Tool call com múltiplas confirmações | NAO_APTO |

---

## Avaliação Detalhada por API

### Consulta dos colaboradores

1. **Finalidade:** Consultar lista de colaboradores cadastrados na empresa
2. **Dados de entrada:** Token de autenticação, page (paginação), nameOrCpf (filtro opcional)
3. **Dados retornados:** Lista de colaboradores com nome, documento, local de trabalho, endereço de entrega
4. **Campos úteis para o modelo:** name, placeName, subtype, isHomeDelivery, products
5. **Campos que NÃO devem ir ao modelo:** documentNumber, email, phoneNumber, motherName, beneficiaryId, address
6. **Dados pessoais/sensíveis:** Sim — CPF, email, telefone, nome da mãe, endereço
7. **Necessidade de anonimização:** Sim — CPF, telefone, email devem ser removidos ou mascarados
8. **Necessidade de transformação:** Sim — agrupar por tipo de entrega, simplificar estrutura
9. **Intenções de usuário atendidas:** Listar colaboradores, verificar cadastro, consultar local de entrega
10. **Determinística e factual:** Sim — dados cadastrais são factuais
11. **Atual ou histórico:** Atual (reflete estado presente do cadastro)
12. **Requer consulta em tempo real:** Sim — requer consulta à API para dados atualizados
13. **Pode ser usada em RAG:** Não — dados mudam frequentemente
14. **Deve ser tool call:** Sim — deve ser usado como tool call em tempo de execução
15. **Riscos de segurança:** Exposição de PII se não sanitizado; acesso depende de permissão do interlocutor
16. **Riscos de alucinação:** Baixo se resposta é usada diretamente; alto se modelo inferir dados
17. **Regras de autorização:** Requer token válido, FNP ativo, prova de vida OK, usuário deve ser interlocutor
18. **Recomendação final:** `APTO_SOMENTE_COM_TOOL_CALL`

### Cadastro de colaborador

1. **Finalidade:** Cadastrar novo colaborador na empresa
2. **Dados de entrada:** Dados pessoais completos do colaborador (nome, CPF, data nascimento, etc.)
3. **Dados retornados:** Status 201 (criado) ou erro
4. **Campos úteis para o modelo:** Status code da operação
5. **Campos que NÃO devem ir ao modelo:** Todos os campos de entrada (PII completo)
6. **Dados pessoais/sensíveis:** Sim — todos os dados de entrada são PII
7. **Necessidade de anonimização:** N/A — operação de escrita
8. **Necessidade de transformação:** N/A
9. **Intenções de usuário atendidas:** Cadastrar novo colaborador
10. **Determinística e factual:** Sim — operação transacional
11. **Atual ou histórico:** Operação pontual (não consulta histórica)
12. **Requer consulta em tempo real:** Sim — operação de escrita em tempo real
13. **Pode ser usada em RAG:** Não
14. **Deve ser tool call:** Sim — mas com validação humana prévia
15. **Riscos de segurança:** Alto — manipula PII, pode criar registros indevidos
16. **Riscos de alucinação:** Alto — modelo NÃO deve inferir dados pessoais
17. **Regras de autorização:** Requer token, FNP, prova de vida, permissão de interlocutor
18. **Recomendação final:** `NECESSITA_VALIDACAO_DO_CLIENTE`

### Atualização de colaborador

1. **Finalidade:** Atualizar dados de um colaborador existente
2. **Dados de entrada:** beneficiaryId + dados atualizados do colaborador
3. **Dados retornados:** Status 204 (atualizado) ou erro
4. **Campos úteis para o modelo:** Status code da operação
5. **Campos que NÃO devem ir ao modelo:** Todos os campos de entrada (PII)
6. **Dados pessoais/sensíveis:** Sim
7. **Necessidade de anonimização:** N/A — operação de escrita
8. **Necessidade de transformação:** N/A
9. **Intenções de usuário atendidas:** Alterar dados de colaborador (endereço, local de entrega)
10. **Determinística e factual:** Sim
11. **Atual ou histórico:** Operação pontual
12. **Requer consulta em tempo real:** Sim
13. **Pode ser usada em RAG:** Não
14. **Deve ser tool call:** Sim — com confirmação
15. **Riscos de segurança:** Alto — pode alterar dados cadastrais indevidamente
16. **Riscos de alucinação:** Alto
17. **Regras de autorização:** Requer token, FNP, prova de vida, permissão de interlocutor
18. **Recomendação final:** `NECESSITA_VALIDACAO_DO_CLIENTE`

### Exclusão de colaborador

1. **Finalidade:** Excluir um colaborador do sistema
2. **Dados de entrada:** beneficiaryId do colaborador a excluir
3. **Dados retornados:** Status 204 (excluído) ou erro
4. **Campos úteis para o modelo:** Status code da operação
5. **Campos que NÃO devem ir ao modelo:** beneficiaryId
6. **Dados pessoais/sensíveis:** Sim — beneficiaryId identifica uma pessoa
7. **Necessidade de anonimização:** N/A
8. **Necessidade de transformação:** N/A
9. **Intenções de usuário atendidas:** Remover colaborador da empresa
10. **Determinística e factual:** Sim
11. **Atual ou histórico:** Operação irreversível
12. **Requer consulta em tempo real:** Sim
13. **Pode ser usada em RAG:** Não
14. **Deve ser tool call:** Sim — com confirmação múltipla
15. **Riscos de segurança:** Muito alto — exclusão irreversível de dados
16. **Riscos de alucinação:** Muito alto — modelo NÃO deve sugerir exclusões
17. **Regras de autorização:** Requer token, FNP, prova de vida, permissão de interlocutor
18. **Recomendação final:** `NAO_APTO`
