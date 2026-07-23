# POC MARH Agent — Frontend

Interface web local para o **Agente Consultivo MARH (Alelo)**.

Reprodução controlada das telas de referência para validação de UX e
arquitetura de integração. **Sem dados reais. Sem deploy. Sem credenciais.**

---

## Origem das referências visuais

| Tela | Referência |
|---|---|
| Home (Espaço RH) | https://home-rh-poc.web.app/index.html |
| Chat (ChatAlelo) | https://home-rh-poc.web.app/chat-alelo.html |

A implementação é uma reprodução controlada para fins de POC. Nenhum código
proprietário, credencial, token ou dado real foi reutilizado.

---

## Como executar

```bash
cd C:\proj\discover_alelo\poc_marh_agent\frontend
python -m http.server 8080
```

Abrir no navegador:

- **Home:** http://localhost:8080/index.html
- **Chat:** http://localhost:8080/chat-alelo.html

> Requer Python 3. Alternativas: `npx serve .` ou `npx http-server -p 8080`

---

## Como alternar mock / backend real

Editar [`assets/js/config.js`](assets/js/config.js):

```js
const CONFIG = Object.freeze({
  USE_MOCK_AGENT: true,   // ← false para usar backend real
  AGENT_API_URL: "http://localhost:8000/chat",
  ...
});
```

| `USE_MOCK_AGENT` | Comportamento |
|---|---|
| `true` (padrão) | MockAgent local, sem HTTP. Badge laranja: **MOCK LOCAL** |
| `false` + localhost | POST para `AGENT_API_URL`. Badge verde: **BACKEND LOCAL** |
| `false` + AWS URL | POST para endpoint HML. Badge azul: **AWS HML** |

---

## Estrutura dos arquivos

```
frontend/
├── index.html              # Home — Espaço RH
├── chat-alelo.html         # Tela do ChatAlelo
├── assets/
│   ├── css/
│   │   ├── common.css      # Variáveis, reset, componentes compartilhados
│   │   ├── home.css        # Estilos da home
│   │   └── chat.css        # Estilos do chat
│   ├── js/
│   │   ├── config.js       # Configuração da POC (modo, URLs, allowlists)
│   │   ├── mock-agent.js   # Respostas sintéticas sem HTTP
│   │   ├── api-client.js   # Interface abstrata mock/backend
│   │   ├── home.js         # Lógica da home
│   │   └── chat.js         # Lógica do chat
│   └── images/             # Assets locais (vazio na POC)
├── fixtures/
│   ├── orders.json         # Dados sintéticos de pedidos
│   └── collaborators.json  # Dados sintéticos de colaboradores
├── REFERENCE_ANALYSIS.md   # Análise das telas de referência
└── README.md               # Este arquivo
```

---

## Funcionalidades implementadas

### Home
- [x] Header Espaço RH com indicador de ambiente
- [x] Hero banner verde-petróleo
- [x] Card ChatAlelo com badge "Novo" e CTA
- [x] Grid de 4 atalhos (Novo pedido, Emissão, Colaboradores, Relatórios)
- [x] Lista de últimos pedidos (dados sintéticos)
- [x] Modal de detalhes de pedido
- [x] Botão "Ver mais"
- [x] Responsividade mobile/tablet/desktop

### Chat
- [x] Header com voltar, título, status online, avatar, badge de ambiente
- [x] Saudação "Olá!" + "Por onde começamos?" + "Descubra como posso te ajudar"
- [x] 6 sugestões adaptadas (sem ações transacionais)
- [x] Área de mensagens com scroll automático
- [x] Bolhas usuário (petróleo, direita) e agente (branco, esquerda)
- [x] Indicador de digitação (3 pontos animados)
- [x] Componente `list_navigation` para deeplinks
- [x] Campo de texto auto-resize
- [x] Botão envio (desabilitado quando vazio)
- [x] Enter envia, Shift+Enter nova linha
- [x] Botão de anexo com bottom sheet
- [x] Menu de anexos (galeria, câmera, arquivo)
- [x] Toast "Envio de anexos não faz parte desta POC"
- [x] Aria-live para leitores de tela
- [x] Escape fecha menus

### MockAgent (7 intenções)
- [x] `Consultar pedido {número}` — retorna dados sintéticos
- [x] `Qual foi o último pedido?` — retorna pedido 342671 sintético
- [x] `Pedidos com status pago` — retorna lista sintética
- [x] `Consultar colaborador` — instrução de busca
- [x] `Cancele o pedido {número}` — bloqueia e redireciona
- [x] `O que posso fazer?` — lista de capacidades
- [x] Mensagem desconhecida — fallback amigável

---

## Funcionalidades não implementadas (fora do escopo)

- Upload real de arquivos
- Acesso à câmera ou galeria
- Autenticação
- Backend real (USE_MOCK_AGENT = false está preparado, mas sem servidor)
- Histórico persistente de conversa
- Múltiplas sessões
- Notificações push

---

## Contrato esperado do backend

### Request (POST /chat)

```json
{
  "company_id": "empresa-sintetica-001",
  "user_id": "usuario-sintetico-001",
  "session_id": "sessao-sintetica-001",
  "message": "Consultar pedido 342671",
  "environment": "HML"
}
```

### Response

```json
{
  "correlation_id": "uuid",
  "intent_id": "INT-003",
  "flow": "API_ONLY",
  "message": "Encontrei o pedido 342671...",
  "navigation": {
    "type": "list_navigation",
    "route_id": "ROUTE-ORDER-DETAIL",
    "label": "Ver detalhes do pedido",
    "route_suffix": "342671",
    "webview_url": "https://meualelo-webviews-hml.siteteste.inf.br/#/order-detail/342671",
    "deeplink": "meualelo://app/webview?url=...&isModal=false&showNavbar=false&authRequired=true"
  }
}
```

O campo `navigation` é opcional. Quando presente, o frontend renderiza o
componente `list_navigation`. O campo `message` é sempre obrigatório.

---

## Comportamento de deeplink

### No desktop (POC local)
O esquema `meualelo://` não é suportado pelo navegador desktop. O componente
`list_navigation` abre a `webview_url` equivalente em nova aba.

O deeplink real fica armazenado em `data-deeplink` para uso futuro no app.

### No app nativo (produção futura)
O app intercepta o deeplink `meualelo://app/webview?url=...` e abre a webview
internamente, respeitando os parâmetros `isModal`, `showNavbar` e `authRequired`.

### Padrão de URL de navegação
```
meualelo://app/webview?url={URL_ENCODED}&isModal=false&showNavbar=false&authRequired=true
```

Bases por ambiente:
- HML: `https://meualelo-webviews-hml.siteteste.inf.br/`
- PRD: `https://meualelo-webviews.alelo.com.br/`

---

## Segurança implementada

- CSP via meta tag em ambas as páginas
- `textContent` para todas as mensagens (nunca `innerHTML` com input externo)
- Allowlist de hosts para URLs de webview (`config.js`)
- Allowlist de route_ids para Navigation Builder
- `company_id` / `user_id` / `session_id` sempre sintéticos e fixos
- Nenhum `eval`
- Nenhum script externo
- Nenhum token no `localStorage`
- Nenhum dado sensível em `console.log`
- Ações transacionais bloqueadas no MockAgent

---

## Limitações restantes

- Fontes do sistema (sem Inter via CDN) — visual muito próximo, não idêntico
- Sem ícones Alelo oficiais — substituídos por SVGs heroicons equivalentes
- Sem temas claro/escuro
- Sem internacionalização
- Sem testes automatizados (validação manual conforme checklist)
