# Probe — 01. Identidade e Região AWS

**Data:** 2026-07-23
**Região obrigatória:** sa-east-1

## Resultado

| Item | Valor |
|---|---|
| Account | `4453****79` (mascarado) |
| UserId | `AROAW****K:u***@****.com` (mascarado) |
| Role | `AWSReservedSSO_AdministratorAccess_****` (mascarado) |
| Principal | SSO federado (e-mail corporativo mascarado) |
| Região configurada | `sa-east-1` |
| Status | **OK** |

## Observações

- Credencial via AWS SSO com AdministratorAccess — acesso amplo à conta.
- Perfil `connect-poc` existe no config com `us-east-1`, mas **não foi utilizado** neste probe.
- Todas as chamadas usaram exclusivamente `region_name='sa-east-1'`.
- Account ID completo não registrado neste documento.
