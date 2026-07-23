# Análise de Referências — POC MARH Agent Frontend

Referências inspecionadas:
- https://home-rh-poc.web.app/index.html
- https://home-rh-poc.web.app/chat-alelo.html

Data de análise: 2026-07-23

---

## 1. Componentes encontrados

### index.html (Espaço RH)

| Componente | Descrição |
|---|---|
| Header | Barra fixa com logo "Espaço RH", título e status |
| Hero banner | Fundo gradiente verde-petróleo escuro, título grande, subtítulo |
| Card ChatAlelo | Card em destaque com ícone, badge "Novo", CTA verde |
| Grid de atalhos | 4 botões: Novo pedido, Emissão, Colaboradores, Relatórios |
| Seção Últimos Pedidos | Lista de pedidos com status e valor |
| Botão "Ver mais" | Link para lista completa |

### chat-alelo.html (ChatAlelo)

| Componente | Descrição |
|---|---|
| Header | Barra verde-petróleo com botão voltar, "ChatAlelo", avatar "AI" |
| Seção de boas-vindas | Ícone, "Olá!", "Por onde começamos?", subtítulo |
| Grid de sugestões | 6 cards clicáveis com ícone emoji + texto |
| Área de mensagens | Scroll, suporte a mensagens de usuário e agente |
| Bolhas de mensagem | Usuário: azul-petróleo direita; Agente: branco esquerda |
| Indicador de digitação | 3 pontos animados em bolha |
| Navigation card | Card verde claro com seta para webview |
| Campo de texto | Textarea auto-resize com placeholder |
| Botão envio | Circular, ativo ao digitar, desabilitado quando vazio |
| Botão anexo | Circular cinza, abre bottom sheet |
| Menu de anexos | Bottom sheet com 3 opções + cancelar |
| Indicador de ambiente | Badge colorida: MOCK LOCAL / BACKEND LOCAL / AWS HML |

---

## 2. Comportamentos observados

| Comportamento | Implementado |
|---|---|
| Click no card ChatAlelo navega para chat-alelo.html | ✅ |
| Sugestões preenchem o input e enviam automaticamente | ✅ |
| Enter envia mensagem (Shift+Enter = nova linha) | ✅ |
| Loading com 3 pontos animados durante resposta | ✅ |
| Botão envio desabilitado com input vazio | ✅ |
| Scroll automático para última mensagem | ✅ |
| Bottom sheet de anexos abre/fecha | ✅ |
| Escape fecha menus | ✅ |
| Mensagens de agente com suporte a **negrito** básico | ✅ |
| Componente de navegação com deeplink no data-attribute | ✅ |
| Toast de aviso para ações indisponíveis | ✅ |
| Modal de detalhes de pedido na home | ✅ |
| Indicador de ambiente em ambas as telas | ✅ |

---

## 3. Assets necessários

A implementação usa apenas:
- SVGs inline (sem hotlink externo)
- Fontes do sistema (Inter, -apple-system, Segoe UI, etc.)
- CSS local
- JS vanilla

Nenhum asset externo de produção foi utilizado.

---

## 4. Paleta de cores (derivada da identidade visual Alelo)

| Variável | Valor | Uso |
|---|---|---|
| `--color-navy` | `#12333b` | Header, fundo botão envio, bolha usuário |
| `--color-navy-soft` | `#1a4149` | Gradiente hero, card ChatAlelo header |
| `--color-green` | `#087a63` | Primário, botões CTA, status |
| `--color-green-bright` | `#0b9476` | Acento, hover |
| `--color-green-light` | `#0fa882` | Status online |
| `--color-mint` | `#eaf6f1` | Fundo cards nav, fundo ícone |
| `--color-orange` | `#f28c45` | Badge "Novo", anel hero decorativo |
| `--color-ink` | `#1e2d32` | Texto principal |
| `--color-muted` | `#617278` | Texto secundário |
| `--color-paper` | `#f7faf9` | Background geral |

Fonte derivada de: `docs/cliente/Rotas_hr_space.html` (mesmo design system).

---

## 5. Diferenças inevitáveis em relação à referência

| Diferença | Motivo |
|---|---|
| Sem fontes Google Fonts via CDN | Evita dependência externa; usa fontes do sistema |
| Sem Firebase / analytics | Integrações removidas por segurança |
| Sem autenticação real | POC sem backend |
| Sem service worker | Não necessário para POC local |
| Cores extraídas analiticamente | A CSS minificada original não é reutilizada |
| Logo textual (SVG inline) | Sem hotlink de imagem de produção |

---

## 6. Funcionalidades mantidas

- Layout mobile-first fiel à referência
- Header verde-petróleo escuro em ambas as telas
- Card ChatAlelo com badge "Novo"
- Grid de 4 atalhos
- Seção de últimos pedidos
- Saudação + "Por onde começamos?" + sugestões
- Bottom sheet de anexos com 3 opções
- Indicador de digitação animado
- Componente de navegação (list_navigation)
- Indicador de ambiente visível

---

## 7. Funcionalidades simuladas (mock)

- Respostas do agente (MockAgent local)
- Dados de pedidos (sintéticos — `SYNTHETIC_TEST_DATA`)
- Dados de colaboradores (sintéticos)
- Delay de resposta (600–1400ms aleatório)
- URLs de webview (base HML com rotas sintéticas)

---

## 8. Funcionalidades removidas por segurança

| Funcionalidade | Motivo da remoção |
|---|---|
| Autenticação Firebase | Credenciais de produção |
| Google Analytics | Privacidade / rastreamento |
| Service Workers | Não necessário, poderia cachear dados |
| Upload real de arquivos | Fora do escopo da POC |
| Acesso à câmera/galeria | Permissões de navegador não solicitadas |
| Chamadas a endpoints reais | Sem backend nesta etapa |
| Tokens / API keys | Nunca incluídos |
| company_id via conversa | Bloqueado — sempre sintético e fixo |

---

## 9. Adaptações de texto (ações transacionais → informativas)

| Original (referência) | Adaptado (POC) |
|---|---|
| "Adicionar novos colaboradores" | "Como cadastrar colaboradores?" |
| "Solicitar 2ª via do cartão" | "Consultar colaborador" |
| Qualquer ação de criação/cancelamento | Redirecionada para consulta |
