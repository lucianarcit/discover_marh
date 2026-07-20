# Interlocutores (Usuários do Sistema)

## Descrição
Documento que descreve os perfis de acesso dos interlocutores no Sistema de Pedidos Alelo: Decisão (acesso total, definido em contrato), Gerenciamento (configurações e pedidos), Operação (pedidos sem acesso à configuração de benefícios) e Financeiro (acesso restrito ao menu financeiro). Inclui uma tabela comparativa com as funções e responsabilidades de cada perfil.

**Nível de confidencialidade:** Uso interno

## Perfis de Usuário do Sistema (Tipos de Interlocutor)

### Decisão
- Responsável autorizado pela empresa no contrato.
- Tem poderes para **conceder, liberar e efetuar a manutenção de acesso** ao Sistema de Pedidos para os outros interlocutores.
- Tem acesso a **todos os menus** do Sistema de Pedidos.

### Gerenciamento
- Autorizado pelo interlocutor de Decisão.
- Faz **configurações de benefícios, pedidos, solicitações de cartões, senhas, cancelamento**, etc.
- Acesso a **todos os menus** do Sistema de Pedidos.

### Operação
- Autorizado pela Empresa/RH e pelo interlocutor de Decisão.
- Efetua **pedidos, solicitações de cartões, senhas, cancelamento**, etc.
- Acesso a todos os menus do Sistema de Pedidos, **exceto a configuração do benefício**.

### Financeiro
- Autorizado pelo interlocutor de Decisão.
- Acesso ao **menu financeiro** que engloba: cobranças emitidas (NFs, boleto), RPS, demonstrativo fiscal, informe de rendimento.
- **Não tem acesso** para fazer pedidos nem cadastro de colaborador e de local de entrega.

---

## Tabela de Funções e Responsabilidades por Perfil

| Funções / Responsabilidades         | Decisão | Gerenciamento | Operação | Financeiro |
|-------------------------------------|:-------:|:-------------:|:--------:|:----------:|
| Autorizado pela empresa             | ✅      |               |          |            |
| Manutenção de acesso para outros perfis | ✅  |               |          |            |
| Configurações de benefícios         | ✅      | ✅            |          |            |
| Efetuar Pedidos                     | ✅      | ✅            | ✅       |            |
| Solicitações de cartões             | ✅      | ✅            | ✅       |            |
| Solicitações de senhas              | ✅      | ✅            | ✅       |            |
| Cancelamentos                       | ✅      | ✅            | ✅       |            |
| Acesso ao Menu Financeiro           | ✅      | ✅            | ✅       | ✅         |
