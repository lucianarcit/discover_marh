# Infraestrutura — MARH Agent

CDK Python para provisionar o agente MARH na AWS.

## Pré-requisitos

- Python 3.12+
- AWS CDK CLI (`npm install -g aws-cdk`)
- Conta AWS com credenciais configuradas
- Bootstrap feito na conta/região (`cdk bootstrap aws://ACCOUNT/sa-east-1`)

## Comandos

```bash
cd infra
pip install -r requirements.txt

cdk synth          # Gera o CloudFormation template
cdk diff           # Mostra diferenças com o deploy atual
cdk deploy         # Deploy na AWS
cdk destroy        # Remove todos os recursos
```

## Stacks

| Stack | Recursos |
|-------|----------|
| `marh-agent-hml` | Lambda, API Gateway, IAM, Secrets Manager, CloudWatch, X-Ray |
