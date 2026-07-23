"""Stack principal do MARH Agent.

Recursos provisionados:
  - Lambda function (Python 3.12, 512 MB, 30s)
  - API Gateway HTTP API com throttling
  - IAM role com least privilege
  - Secrets Manager (credenciais ma-hr-orch)
  - CloudWatch Log Group com retenção de 30 dias
  - X-Ray tracing
"""

from __future__ import annotations

import aws_cdk as cdk
from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as integrations,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct


class MarhAgentStack(Stack):
    """Infraestrutura do agente MARH."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        environment: str,  # "HML" ou "PRD"
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env_lower = environment.lower()

        # --- Secrets Manager (placeholder para credenciais ma-hr-orch) ---

        self.secret = secretsmanager.Secret(
            self,
            "MaHrOrchSecret",
            secret_name=f"marh-agent/{env_lower}/ma-hr-orch-credentials",
            description="Credenciais para API ma-hr-orch (preenchidas manualmente)",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"api_key":"PLACEHOLDER","base_url":"PLACEHOLDER"}',
                generate_string_key="rotation_token",
            ),
        )

        # --- CloudWatch Log Group ---

        self.log_group = logs.LogGroup(
            self,
            "LambdaLogGroup",
            log_group_name=f"/aws/lambda/marh-agent-{env_lower}",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # --- IAM Role para a Lambda ---

        self.lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            role_name=f"marh-agent-{env_lower}-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Role para a Lambda do agente MARH",
        )

        # Permissões básicas: logs + X-Ray
        self.lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        self.lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess")
        )

        # Permissão para ler secrets
        self.secret.grant_read(self.lambda_role)

        # Permissão para Bedrock (Fase 3+, já preparada)
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                sid="BedrockInvoke",
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:Retrieve",
                    "bedrock:RetrieveAndGenerate",
                ],
                resources=["*"],  # Restringir ao model/KB específico na Fase 3
            )
        )

        # --- Lambda Function ---

        # O código-fonte está em poc_marh_agent/backend/src/
        # O handler espera o módulo marh_agent no raiz do pacote.
        # Em produção, o CI/CD empacota src/ + dependências num zip.
        # Para CDK local, apontamos direto para src/ (dev/mock).
        self.function = lambda_.Function(
            self,
            "MarhAgentFunction",
            function_name=f"marh-agent-{env_lower}",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="marh_agent.api.lambda_handler.lambda_handler",
            code=lambda_.Code.from_asset(
                path="../poc_marh_agent/backend/src",
                exclude=[
                    "**/__pycache__/**",
                    "*.pyc",
                    "*.egg-info/**",
                ],
            ),
            memory_size=512,
            timeout=Duration.seconds(30),
            role=self.lambda_role,
            log_group=self.log_group,
            tracing=lambda_.Tracing.ACTIVE,  # X-Ray
            environment={
                "AGENT_MODE": "MOCK_LOCAL",  # Fase 1: mock; Fase 2+: INTEGRATED
                "ENVIRONMENT": environment,
                "LOG_LEVEL": "INFO",
                "MAX_MESSAGE_LENGTH": "2000",
                "MA_HR_ORCH_BASE_URL": "",
                "MA_HR_ORCH_TIMEOUT_SECONDS": "10",
                "BEDROCK_REGION": "sa-east-1",
                "BEDROCK_MODEL_ID": "anthropic.claude-3-haiku-20240307-v1:0",
                "BEDROCK_KNOWLEDGE_BASE_ID": "",
                "CORS_ALLOWED_ORIGINS": "https://meualelo-webviews-hml.siteteste.inf.br",
            },
        )

        # --- API Gateway HTTP API ---

        self.http_api = apigwv2.HttpApi(
            self,
            "MarhAgentApi",
            api_name=f"marh-agent-{env_lower}",
            description=f"MARH Agent API ({environment})",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_origins=[
                    "https://meualelo-webviews-hml.siteteste.inf.br",
                ],
                allow_methods=[
                    apigwv2.CorsHttpMethod.POST,
                    apigwv2.CorsHttpMethod.OPTIONS,
                ],
                allow_headers=["Content-Type", "Authorization", "X-Correlation-Id"],
                max_age=Duration.hours(1),
            ),
        )

        # Throttling (previne abuso)
        cfn_stage = self.http_api.default_stage.node.default_child
        cfn_stage.add_property_override(
            "DefaultRouteSettings.ThrottlingBurstLimit", 50
        )
        cfn_stage.add_property_override(
            "DefaultRouteSettings.ThrottlingRateLimit", 100
        )

        # Rota POST /chat → Lambda
        lambda_integration = integrations.HttpLambdaIntegration(
            "ChatIntegration",
            handler=self.function,
        )

        self.http_api.add_routes(
            path="/chat",
            methods=[apigwv2.HttpMethod.POST],
            integration=lambda_integration,
        )

        # Rota GET /health → Lambda
        self.http_api.add_routes(
            path="/health",
            methods=[apigwv2.HttpMethod.GET],
            integration=lambda_integration,
        )

        # --- Outputs ---

        cdk.CfnOutput(
            self,
            "ApiUrl",
            value=self.http_api.api_endpoint,
            description="URL base da API (API Gateway)",
        )

        cdk.CfnOutput(
            self,
            "LambdaFunctionName",
            value=self.function.function_name,
            description="Nome da Lambda function",
        )

        cdk.CfnOutput(
            self,
            "SecretArn",
            value=self.secret.secret_arn,
            description="ARN do secret com credenciais ma-hr-orch",
        )
