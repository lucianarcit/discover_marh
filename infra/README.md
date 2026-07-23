# Infraestrutura — MARH Agent (Terraform)

## Pré-requisitos

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5
- AWS CLI configurado (`aws configure`)
- Conta AWS com permissões para criar Lambda, API Gateway, IAM, Secrets Manager

## Estrutura

```
infra/
├── main.tf             # Provider, backend, versões
├── variables.tf        # Variáveis de entrada
├── locals.tf           # Valores locais derivados
├── lambda.tf           # Lambda + IAM Role + CloudWatch
├── api_gateway.tf      # HTTP API + rotas + integração
├── secrets.tf          # Secrets Manager
├── outputs.tf          # Outputs (URL, ARN, etc.)
└── terraform.tfvars    # Valores para HML
```

## Comandos

```bash
cd infra

terraform init          # Inicializa providers e backend
terraform plan          # Mostra o que será criado/alterado
terraform apply         # Aplica as mudanças na AWS
terraform destroy       # Remove todos os recursos
```

## Primeiro deploy

```bash
cd infra
terraform init
terraform plan
terraform apply
```

O output mostrará a URL da API:
```
api_url = "https://abc123.execute-api.sa-east-1.amazonaws.com"
```

## Backend remoto (opcional, recomendado)

Para salvar o state no S3 (colaboração em equipe):

1. Criar bucket S3 e DynamoDB table para locks
2. Descomentar o bloco `backend "s3"` em `main.tf`
3. Rodar `terraform init -migrate-state`
