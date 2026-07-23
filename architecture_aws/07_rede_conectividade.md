# 07 — Rede e Conectividade

**Projeto:** MARH Consultive Agent POC  
**Data:** 2026-07-23  
**Região AWS:** sa-east-1  
**Status:** DRAFT

---

## 1. Visão Geral

O agente opera com a topologia de rede mais simples possível: Lambda fora de VPC, comunicando-se com todos os serviços via endpoints HTTPS regionais públicos.

---

## 2. Opção 1 — Lambda Fora de VPC (RECOMENDADA para POC)

### 2.1 Topologia

```
                    ┌─────────────────────────────────────┐
                    │          AWS sa-east-1               │
                    │                                     │
API MARH ──HTTPS──▶│  Lambda Function URL                │
                    │       │                             │
                    │       ├──HTTPS──▶ Bedrock           │
                    │       ├──HTTPS──▶ S3                │
                    │       ├──HTTPS──▶ S3 Vectors        │
                    │       ├──HTTPS──▶ KB (Bedrock)      │
                    │       ├──HTTPS──▶ Secrets Manager   │
                    │       ├──HTTPS──▶ CloudWatch        │
                    │       └──HTTPS──▶ KMS               │
                    │                                     │
                    └─────────────────────────────────────┘
                            │
                            ├──HTTPS──▶ ma-hr-orch (externo)
                            │
```

### 2.2 Características

| Aspecto | Detalhe |
|---|---|
| VPC | Nenhuma |
| Subnets | Nenhuma |
| NAT Gateway | Nenhum |
| Security Groups | Não aplicável |
| Internet Gateway | Não aplicável (Lambda tem acesso à internet por padrão) |
| Cold start impact | Nenhum (sem ENI attachment) |
| Custo de rede | $0/mês |

### 2.3 Vantagens

- ✅ Zero custo de infraestrutura de rede
- ✅ Sem cold start adicional (ENI attachment leva ~1-2s em VPC)
- ✅ Simplicidade operacional
- ✅ Todos os serviços AWS acessíveis nativamente
- ✅ ma-hr-orch acessível via HTTPS (endpoint público)
- ✅ Menor superfície de configuração (menos chance de erro)

### 2.4 Limitações

- ⚠️ Sem controle de egress (Lambda pode acessar qualquer IP)
- ⚠️ Sem network-level isolation
- ⚠️ Não atende requisitos de compliance que exijam VPC (ex: PCI-DSS)

### 2.5 Mitigação das Limitações

| Limitação | Mitigação |
|---|---|
| Sem controle de egress | Allowlist de endpoints no código; sem URLs dinâmicas |
| Sem network isolation | IAM policies restritivas; validação em cada camada |
| Compliance | POC não requer PCI-DSS; avaliar para produção |

---

## 3. Opção 2 — Lambda em VPC (Referência para Produção)

### 3.1 Topologia

```
                    ┌──────────────────────────────────────────────┐
                    │          AWS sa-east-1 — VPC                  │
                    │                                              │
                    │  ┌──────────── Private Subnet ──────────┐   │
                    │  │                                       │   │
API MARH ──HTTPS──▶│  │  Lambda                               │   │
                    │  │    │                                   │   │
                    │  │    ├──▶ VPC Endpoint: Bedrock          │   │
                    │  │    ├──▶ VPC Endpoint: S3               │   │
                    │  │    ├──▶ VPC Endpoint: Secrets Manager  │   │
                    │  │    ├──▶ VPC Endpoint: CloudWatch       │   │
                    │  │    ├──▶ VPC Endpoint: KMS              │   │
                    │  │    │                                   │   │
                    │  │    └──▶ NAT Gateway ──▶ IGW ──▶ ma-hr-orch
                    │  │                                       │   │
                    │  └───────────────────────────────────────┘   │
                    └──────────────────────────────────────────────┘
```

### 3.2 Componentes Necessários

| Componente | Quantidade | Custo Mensal |
|---|---|---|
| NAT Gateway | 1 (mínimo) ou 2 (HA) | $45 — $90 |
| VPC Endpoints (Interface) | 5 (Bedrock, Secrets, CW, KMS, S3 API) | $50 — $75 |
| VPC Endpoint (Gateway) | 1 (S3) | $0 |
| Subnets privadas | 2 (multi-AZ) | $0 |
| Security Groups | 2-3 | $0 |
| **Total** | — | **$95 — $165/mês** |

### 3.3 Impacto no Cold Start

| Cenário | Cold Start Sem VPC | Cold Start Com VPC |
|---|---|---|
| Primeira invocação | ~300ms | ~1.5-3s (+ENI) |
| Após period inativo | ~300ms | ~1.5-3s (+ENI) |
| Warm invocation | ~5ms | ~5ms |

---

## 4. Comparação de Custos

| Item | Opção 1 (Sem VPC) | Opção 2 (Com VPC) |
|---|---|---|
| NAT Gateway (fixo) | $0 | $45/mês (1 AZ) |
| NAT Gateway (dados) | $0 | ~$5/mês (processamento) |
| VPC Endpoints | $0 | ~$55/mês (5 endpoints) |
| Cold start adicional | 0s | +1-2s |
| Complexidade operacional | Baixa | Alta |
| **Total mensal rede** | **$0** | **~$105/mês** |
| **Total anual rede** | **$0** | **~$1.260/ano** |

---

## 5. Decisão: Sem VPC para o POC

### 5.1 Justificativa

| Critério | Sem VPC | Com VPC | Vencedor |
|---|---|---|---|
| Custo | $0/mês | $105/mês | Sem VPC |
| Latência (cold start) | 300ms | 1.5-3s | Sem VPC |
| Simplicidade | Alta | Baixa | Sem VPC |
| Segurança de rede | Adequada para POC | Superior | Com VPC |
| Compliance (PCI/SOC2) | Não atende | Atende | Com VPC |
| Tempo de setup | 0 | 2-4h | Sem VPC |

### 5.2 Pré-condições para Funcionar Sem VPC

1. ✅ ma-hr-orch é acessível via HTTPS público (confirmado)
2. ✅ Bedrock tem endpoint público regional em sa-east-1
3. ✅ S3, Secrets Manager, CloudWatch — todos acessíveis sem VPC
4. ✅ Não há requisito de compliance que exija VPC no POC

### 5.3 Critérios para Migrar para VPC (Produção)

Migrar para VPC se qualquer uma destas condições for verdadeira:
- Requisito de compliance (PCI-DSS, SOC2 Type II)
- ma-hr-orch migrar para rede privada (Private Link)
- Necessidade de controlar egress por IP
- Dados classificados como "altamente sensíveis" pelo time de segurança

---

## 6. Endpoints Utilizados

| Serviço | Endpoint | Protocolo | Porta |
|---|---|---|---|
| Bedrock Runtime | `bedrock-runtime.sa-east-1.amazonaws.com` | HTTPS | 443 |
| Bedrock Agent Runtime | `bedrock-agent-runtime.sa-east-1.amazonaws.com` | HTTPS | 443 |
| S3 | `s3.sa-east-1.amazonaws.com` | HTTPS | 443 |
| Secrets Manager | `secretsmanager.sa-east-1.amazonaws.com` | HTTPS | 443 |
| KMS | `kms.sa-east-1.amazonaws.com` | HTTPS | 443 |
| CloudWatch Logs | `logs.sa-east-1.amazonaws.com` | HTTPS | 443 |
| X-Ray | `xray.sa-east-1.amazonaws.com` | HTTPS | 443 |
| ma-hr-orch | `https://api.ma-hr-orch.alelo.com.br` (exemplo) | HTTPS | 443 |

---

## 7. Referência de Diagrama

Diagrama detalhado disponível em:  
`diagrams/08_rede.mmd`

---

## 8. DNS e Resolução

- Lambda fora de VPC usa o resolver DNS padrão da AWS
- Todos os endpoints são resolvidos via DNS público da AWS
- Não há necessidade de Route 53 Private Hosted Zones
- Não há necessidade de DNS customizado

---

## 9. Requisitos de Firewall (ma-hr-orch)

Para que a Lambda acesse o ma-hr-orch, o seguinte deve ser permitido no lado do ma-hr-orch:

| Origem | Destino | Porta | Protocolo | Nota |
|---|---|---|---|---|
| IPs AWS sa-east-1 (range) | ma-hr-orch endpoint | 443 | HTTPS | Range de IPs da AWS pode mudar |
| Lambda Function (IP variável) | ma-hr-orch endpoint | 443 | HTTPS | IP não fixo sem NAT |

**Recomendação:** ma-hr-orch deve autenticar via token/header, não por IP (pois Lambda fora de VPC não tem IP fixo).
