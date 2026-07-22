# 02 — Conhecimento RAG: Base de Conhecimento MARH

> **Princípio:** Este documento analisa exclusivamente os arquivos de `docs\kb\`. O conteúdo aqui não representa requisitos de construção do agente — representa **fatos de domínio, procedimentos e regras informativas** que podem alimentar a base de conhecimento RAG do agente para responder dúvidas do interlocutor de RH sobre o funcionamento do MARH.

> **Uma informação só é classificada como AVAILABLE_FOR_RAG quando:** está dentro do escopo consultivo definido no HTML do cliente; está suficientemente clara; não conflita com outra fonte; não exige dado em tempo real; não representa operação transacional proibida.

---

## Formato de cada item

| Campo | Descrição |
|---|---|
| **KB ID** | Identificador único (ex.: KB-001) |
| **Tema** | Assunto principal |
| **Informação recuperável** | O que o agente pode comunicar ao usuário sobre este tema |
| **Fonte** | Arquivo da KB |
| **Seção** | Seção ou contexto dentro do arquivo |
| **Intenções atendidas** | Perguntas do usuário que este conhecimento responde |
| **Status** | AVAILABLE_FOR_RAG / PARTIALLY_AVAILABLE / NEEDS_VALIDATION / OUT_OF_AGENT_SCOPE / CONFLICTING / POSSIBLY_OUTDATED |

---

## Tabela de conhecimento RAG

| KB ID | Tema | Informação recuperável | Fonte | Seção | Intenções atendidas | Status |
|---|---|---|---|---|---|---|
| KB-001 | Configuração de benefícios — perfis permitidos | Somente interlocutores com perfil Decisão ou Gerenciamento podem configurar benefícios. | docs\kb\1CONFIG_BENE_1.md | Configuração de benefícios | "Quem pode configurar benefícios?" / "Posso configurar benefícios?" | AVAILABLE_FOR_RAG |
| KB-002 | Configuração de benefícios — modalidades disponíveis | As modalidades disponíveis são Alimentação, Refeição e Benefícios, habilitadas individualmente. Se todas estiverem desabilitadas, não é possível realizar pedidos. | docs\kb\1CONFIG_BENE_1.md | Configuração de benefícios | "Quais benefícios posso oferecer?" / "Por que não consigo fazer pedido?" | AVAILABLE_FOR_RAG |
| KB-003 | Configuração de benefícios — habilitar não exibe no app do colaborador | Habilitar um benefício na configuração não exibe automaticamente no app do colaborador. É necessário também realizar um pedido com valor para o colaborador. | docs\kb\1CONFIG_BENE_1.md | Configuração de benefícios | "Habilitei o benefício mas o colaborador não vê nada. Por quê?" | AVAILABLE_FOR_RAG |
| KB-004 | Redes de aceitação — Alimentação | Cartão Alimentação é aceito em supermercados, armazéns, açougues, padarias, hortimercados, frios e laticínios. | docs\kb\1CONFIG_BENE_REDES.md | Redes por modalidade | "Onde posso usar o benefício de Alimentação?" | AVAILABLE_FOR_RAG |
| KB-005 | Redes de aceitação — Refeição | Cartão Refeição é aceito em restaurantes, lanchonetes, bares e padarias. | docs\kb\1CONFIG_BENE_REDES.md | Redes por modalidade | "Onde posso usar o benefício de Refeição?" | AVAILABLE_FOR_RAG |
| KB-006 | Redes de aceitação — regra de transferência proibida | Não é permitida transferência entre as contas Alimentação, Refeição e Benefícios. | docs\kb\1CONFIG_BENE_REDES.md e docs\kb\4PEDIDO_TELA.md | Regras de uso | "Posso transferir saldo entre cartões?" / "Posso usar o saldo de refeição em supermercado?" | AVAILABLE_FOR_RAG |
| KB-007 | Perfis de interlocutores — Decisão | O perfil Decisão é definido no contrato com a Alelo e não pode ser atribuído pelo sistema. Tem acesso total e gerencia os demais perfis. | docs\kb\2CADASTRO_INTERLO_PERFIS.md | Perfis de interlocutores | "Quem é o interlocutor de Decisão?" / "Como mudo o responsável principal?" | AVAILABLE_FOR_RAG |
| KB-008 | Perfis de interlocutores — Gerenciamento | O perfil Gerenciamento é atribuído pelo interlocutor de Decisão. Tem acesso a todos os menus, incluindo configuração de benefícios e pedidos. | docs\kb\2CADASTRO_INTERLO_PERFIS.md | Perfis de interlocutores | "O que o perfil Gerenciamento pode fazer?" | AVAILABLE_FOR_RAG |
| KB-009 | Perfis de interlocutores — Operação | O perfil Operação tem acesso a todos os menus exceto configuração de benefícios. | docs\kb\2CADASTRO_INTERLO_PERFIS.md | Perfis de interlocutores | "O que o perfil Operação pode fazer?" / "Por que não consigo acessar configuração de benefícios?" | AVAILABLE_FOR_RAG |
| KB-010 | Perfis de interlocutores — Financeiro | O perfil Financeiro tem acesso somente ao menu financeiro (NFs, boletos, RPS, demonstrativo). Não realiza pedidos. | docs\kb\2CADASTRO_INTERLO_PERFIS.md | Perfis de interlocutores | "O que o perfil Financeiro pode fazer?" / "Por que o financeiro não faz pedidos?" | AVAILABLE_FOR_RAG |
| KB-011 | Alteração do Interlocutor de Decisão | Para alterar o Interlocutor de Decisão é necessário acionar a Central de Atendimento. Isso não pode ser feito pelo sistema. | docs\kb\9VISUALIZAR_CONTRATOS.md | Visualizar contratos | "Como troco o interlocutor de decisão?" | AVAILABLE_FOR_RAG |
| KB-012 | Cadastro de colaborador — campos obrigatórios | Nome, CPF, data de nascimento, nome da mãe e tipo de entrega são campos obrigatórios. E-mail e telefone são importantes para o onboarding no app, mas não obrigatórios. | docs\kb\3CADASTRO_COLAB_TELA.md | Cadastro via tela | "Quais campos são obrigatórios para cadastrar um colaborador?" | AVAILABLE_FOR_RAG |
| KB-013 | Cadastro de colaborador — CPF imutável | O CPF de um colaborador não pode ser alterado após o cadastro. | docs\kb\3CADASTRO_COLAB_TELA.md | Cadastro via tela | "Como altero o CPF de um colaborador?" | AVAILABLE_FOR_RAG |
| KB-014 | Cadastro via planilha — reimportação atualiza dados | Reimportar uma planilha com CPF já cadastrado atualiza os dados do colaborador existente; não cria um duplicado. | docs\kb\3CADASTRO_COLAB_PLANILHA.md | Cadastro via planilha | "O que acontece se eu importar um colaborador já cadastrado?" | AVAILABLE_FOR_RAG |
| KB-015 | Cadastro via planilha — formato aceito | Planilhas de colaboradores devem estar em formato .xls ou .xlsx. | docs\kb\3CADASTRO_COLAB_PLANILHA.md | Cadastro via planilha | "Em qual formato devo enviar a planilha de colaboradores?" | AVAILABLE_FOR_RAG |
| KB-016 | Tags de produto dos colaboradores | A tag de produto (Tudo, Alimentação, Refeição, Benefícios) é atribuída ao colaborador apenas quando ele é incluído em um pedido, não no pré-cadastro. | docs\kb\3CADASTRO_COLAB_TAGS.md | Tags de produto | "Por que o colaborador não tem produto associado?" | AVAILABLE_FOR_RAG |
| KB-017 | Pedido — formas de criação | Um pedido pode ser criado via planilha (.xls/.xlsx) ou via tela, ambas com o mesmo fluxo de 5 etapas. | docs\kb\4PEDIDO_PLANILHA.md e docs\kb\4PEDIDO_TELA.md | Fluxo de pedido | "Como faço um pedido?" / "Quais são as etapas de um pedido?" | AVAILABLE_FOR_RAG |
| KB-018 | Pedido — etapas do fluxo | O fluxo de pedido tem 5 etapas: Forma do pedido > Colaboradores e benefícios > Forma de pagamento e crédito > Resumo > Pagamento. | docs\kb\4PEDIDO_PLANILHA.md | Fluxo de pedido | "Quais são as etapas de um pedido?" | AVAILABLE_FOR_RAG |
| KB-019 | Pagamento — único método disponível | A única forma de pagamento disponível é o boleto bancário. | docs\kb\5PAG_DISPO.md | Forma de pagamento | "Como pago um pedido?" / "Posso pagar com cartão ou PIX?" | AVAILABLE_FOR_RAG |
| KB-020 | Disponibilização — tipos | A disponibilização de créditos pode ser Automática (até 2 dias úteis após compensação do boleto) ou Agendada (data futura escolhida, boleto pago antes). | docs\kb\5PAG_DISPO.md | Tipos de disponibilização | "Quando os créditos chegam ao cartão?" / "Posso agendar a disponibilização?" | AVAILABLE_FOR_RAG |
| KB-021 | Boleto — prazo de compensação | O prazo de compensação do boleto é de até 2 dias úteis após o pagamento. | docs\kb\5PAG_DISPO_BOLETO.md | Conclusão do pedido | "Em quanto tempo o boleto é compensado?" | AVAILABLE_FOR_RAG |
| KB-022 | Modelo de cobrança — tarifas no próximo boleto | As tarifas e taxas do pedido atual são cobradas no próximo boleto, exceto no primeiro pedido. No primeiro pedido, a tarifa de emissão de cartão já vem junto com o valor dos créditos. | docs\kb\5PAG_DISPO_MODELO_COBRANCA.md | Modelo de cobrança | "Por que meu boleto tem tarifas de um pedido anterior?" / "Como funciona a cobrança de tarifas?" | AVAILABLE_FOR_RAG |
| KB-023 | Alterar data de disponibilização de créditos | É possível alterar a data de disponibilização de um pedido já pago. Pedidos aguardando pagamento não permitem alteração. Não há cobrança de tarifa para a alteração. | docs\kb\6ACOMPA_PEDIDO_ALTERAR_DATA_CREDITOS.md | Alterar data de créditos | "Posso mudar a data de disponibilização dos créditos?" | AVAILABLE_FOR_RAG |
| KB-024 | Nota Fiscal — quando é emitida | A Nota Fiscal é emitida somente após a disponibilização dos créditos nos cartões. | docs\kb\6ACOMPA_PEDIDO_BOLETO_NF.md | Boleto e Nota Fiscal | "Quando recebo a nota fiscal?" / "Por que ainda não recebi a nota fiscal?" | AVAILABLE_FOR_RAG |
| KB-025 | Status de pedidos — lista | Os status possíveis de um pedido são: Aguardando pagamento, Pagamento confirmado, Nota Fiscal Emitida, Aguardando Disponibilização, Pedido creditado, Cancelado. | docs\kb\6ACOMPA_PEDIDO_STATUS.md | Status de pedidos | "O que significa o status X do pedido?" | AVAILABLE_FOR_RAG |
| KB-026 | Cancelamento automático por boleto vencido | Pedidos com boleto não pago em até 30 dias após o vencimento são cancelados automaticamente. | docs\kb\6ACOMPA_PEDIDO_STATUS.md | Status de pedidos | "O que acontece se eu não pagar o boleto?" / "Por que meu pedido foi cancelado?" | AVAILABLE_FOR_RAG |
| KB-027 | Relatórios disponíveis — tipos | Há 4 tipos de relatórios: Sintético de Cobrança (PDF), Analítico de Cobrança (PDF), Disponibilização (PDF) e Espelho de Pedidos (Excel). | docs\kb\7RELATORIOS.md | Relatórios | "Que tipos de relatório estão disponíveis?" / "Como consulto o histórico de cobranças?" | AVAILABLE_FOR_RAG |
| KB-028 | Rastreio de cartões — acesso e busca | O rastreio de cartões está disponível em Menu Cartões > Rastreio de Cartões. É possível buscar pelo CPF do colaborador. O botão de detalhe fica indisponível enquanto a fabricação/entrega não foi iniciada. | docs\kb\8RASTREIO_CARTOES.md | Rastreio de cartões | "Como rastreio o cartão de um colaborador?" / "Onde vejo o status do cartão?" | AVAILABLE_FOR_RAG |
| KB-029 | Rastreio de cartões — status possíveis | Os status de rastreio são: Em processamento, Aguardando código de rastreio, Erro no processamento. O detalhe exibe número de rastreamento, endereço, previsão de entrega e timeline de eventos. | docs\kb\8RASTREIO_CARTOES.md | Rastreio de cartões | "O que significa 'Aguardando código de rastreio'?" | AVAILABLE_FOR_RAG |
| KB-030 | Visualizar contratos | Os contratos podem ser consultados em Administração > Contratos. Exibem número, produto, filial, status, tarifas (emissão, reemissão, entrega corporativa, residencial, disponibilização). | docs\kb\9VISUALIZAR_CONTRATOS.md | Visualizar contratos | "Como vejo meu contrato?" / "Quais são as tarifas do meu plano?" | AVAILABLE_FOR_RAG |
| KB-031 | Cadastro de filiais — responsáveis | No cadastro de filiais é possível definir até 3 responsáveis pelos cartões e até 3 responsáveis pela nota fiscal. Responsáveis não podem ser editados diretamente; é necessário remover e adicionar. | docs\kb\10CADASTRO_FILIAIS_TELA.md | Cadastro de filiais | "Como altero o responsável pelos cartões de uma filial?" | AVAILABLE_FOR_RAG |
| KB-032 | Posto de trabalho — reimportação atualiza dados | Reimportar CNPJ de posto de trabalho já cadastrado atualiza os dados existentes. Raiz do CNPJ e Final do CNPJ não podem ser editados. | docs\kb\10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md | Cadastro via planilha | "O que acontece se eu reimportar um posto de trabalho já cadastrado?" | AVAILABLE_FOR_RAG |
| KB-033 | Posto de trabalho — formato da planilha | A planilha de postos de trabalho deve estar em formato .xls ou .xlsx, com tamanho máximo de 15MB. | docs\kb\10CADASTRO_POSTO_DE_TRABALHO_PLANILHA.md | Cadastro via planilha | "Em qual formato envio a planilha de postos de trabalho?" | AVAILABLE_FOR_RAG |
| KB-034 | Faturamento descentralizado — regra de CNPJ | No faturamento descentralizado, somente filiais com a mesma raiz de CNPJ podem ser cadastradas. A exclusão total do CNPJ Contratante não está disponível. | docs\kb\faturamento-descentralizado.md | Faturamento descentralizado | "Como funciona o faturamento descentralizado?" / "Posso cadastrar filiais de empresas diferentes?" | AVAILABLE_FOR_RAG |
| KB-035 | Faturamento descentralizado — todos os boletos | No faturamento descentralizado, todos os boletos de cada CNPJ devem ser pagos para que os benefícios sejam disponibilizados integralmente. | docs\kb\faturamento-descentralizado.md | Faturamento descentralizado | "Por que apenas parte dos colaboradores recebeu crédito?" | AVAILABLE_FOR_RAG |
| KB-036 | Emissão de 2ª via — motivos válidos | Somente os motivos Perda ou Roubo são aceitos para emissão de 2ª via pelo portal. Outros motivos requerem contato com a central de atendimento. | docs\kb\manual-emissao-2via.md | Emissão de 2ª via | "Como solicito a 2ª via de cartão?" / "Posso pedir novo cartão por defeito?" | AVAILABLE_FOR_RAG |
| KB-037 | Emissão de 2ª via — cancelamento automático de cartões ativos | Ao finalizar a reemissão, os cartões ativos são cancelados automaticamente. Cartões virtuais continuam funcionando até a ativação do novo cartão físico. A reemissão não pode ser cancelada após confirmação. | docs\kb\manual-emissao-2via.md | Emissão de 2ª via | "O cartão atual é cancelado ao solicitar 2ª via?" / "Posso cancelar a solicitação de 2ª via?" | AVAILABLE_FOR_RAG |
| KB-038 | Emissão de 2ª via — prazo de entrega | O prazo de entrega da 2ª via é de 7 a 10 dias úteis após a emissão. O rastreio só fica disponível após o encaminhamento para a transportadora. | docs\kb\manual-emissao-2via.md | Emissão de 2ª via | "Em quanto tempo o novo cartão chega?" / "Por que não consigo rastrear minha 2ª via?" | AVAILABLE_FOR_RAG |
| KB-039 | Emissão de 2ª via — tarifas | As taxas de reemissão aparecem no próximo pedido. | docs\kb\manual-emissao-2via.md | Emissão de 2ª via | "Quanto custa a 2ª via?" / "Quando serei cobrado pela reemissão?" | AVAILABLE_FOR_RAG |

---

## Itens fora do escopo atual do agente (não consultivos)

Os itens abaixo contêm informações da KB que dizem respeito a **operações transacionais** — ações que o cliente especificou que o agente NÃO deve executar. Essas informações podem responder dúvidas informativas ("como funciona?"), mas o agente não deve executar essas ações.

| KB ID | Tema | Classificação | Motivo |
|---|---|---|---|
| KB-040 | Pedido — fluxo completo de criação e pagamento | OUT_OF_AGENT_SCOPE (para execução) | O agente não cria pedidos. Pode informar como o fluxo funciona. |
| KB-041 | Cancelamento de pedido | OUT_OF_AGENT_SCOPE (para execução) | O agente não cancela pedidos. Pode informar sobre o status. |
| KB-042 | Cadastro de colaborador (criação) | OUT_OF_AGENT_SCOPE (para execução) | O agente não cadastra colaboradores. |
| KB-043 | Atualização de colaborador | OUT_OF_AGENT_SCOPE (para execução) | O agente não edita colaboradores. |
| KB-044 | Exclusão de colaborador | OUT_OF_AGENT_SCOPE (para execução) | O agente não exclui colaboradores. |
| KB-045 | Solicitação de 2ª via | OUT_OF_AGENT_SCOPE (para execução) | O agente não solicita 2ª via. Pode informar como o processo funciona. |
| KB-046 | Cadastro de filiais e postos de trabalho (criação) | OUT_OF_AGENT_SCOPE (para execução) | O agente não cadastra locais de entrega. |
| KB-047 | Configuração de benefícios (modificação) | OUT_OF_AGENT_SCOPE (para execução) | O agente não configura benefícios. Pode informar quem tem permissão. |

---

*Fonte: `docs\kb\` (22 arquivos analisados) · Gerado em 2026-07-22*