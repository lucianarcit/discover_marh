#!/usr/bin/env python3
"""CDK App — MARH Agent Infrastructure."""

import aws_cdk as cdk

from stacks.marh_agent_stack import MarhAgentStack

app = cdk.App()

# --- Ambientes ---

env_hml = cdk.Environment(
    region="sa-east-1",
    # account será resolvido das credenciais AWS configuradas
)

# --- Stacks ---

MarhAgentStack(
    app,
    "marh-agent-hml",
    env=env_hml,
    environment="HML",
    description="MARH Agent — Homologação (Lambda + API Gateway + Secrets)",
)

# Stack de PRD será adicionado na Fase 5
# MarhAgentStack(
#     app,
#     "marh-agent-prd",
#     env=env_prd,
#     environment="PRD",
#     description="MARH Agent — Produção",
# )

app.synth()
