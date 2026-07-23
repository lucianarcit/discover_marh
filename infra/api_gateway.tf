# ─── API Gateway HTTP API ─────────────────────────────────────────────────────

resource "aws_apigatewayv2_api" "agent" {
  name          = "marh-agent-${local.env_lower}"
  protocol_type = "HTTP"
  description   = "MARH Agent API (${var.environment})"

  cors_configuration {
    allow_origins = var.cors_allowed_origins
    allow_methods = ["POST", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization", "X-Correlation-Id"]
    max_age       = 3600
  }
}

# ─── Stage ($default com auto-deploy) ────────────────────────────────────────

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.agent.id
  name        = "$default"
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = var.throttling_burst_limit
    throttling_rate_limit  = var.throttling_rate_limit
  }

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      method         = "$context.httpMethod"
      path           = "$context.path"
      status         = "$context.status"
      responseLength = "$context.responseLength"
      latency        = "$context.integrationLatency"
    })
  }
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name              = "/aws/apigateway/marh-agent-${local.env_lower}"
  retention_in_days = var.log_retention_days
}

# ─── Integration (Lambda) ────────────────────────────────────────────────────

resource "aws_apigatewayv2_integration" "lambda" {
  api_id             = aws_apigatewayv2_api.agent.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.agent.invoke_arn
  integration_method = "POST"
}

# ─── Routes ──────────────────────────────────────────────────────────────────

resource "aws_apigatewayv2_route" "post_chat" {
  api_id    = aws_apigatewayv2_api.agent.id
  route_key = "POST /chat"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "get_health" {
  api_id    = aws_apigatewayv2_api.agent.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# ─── Lambda Permission (API Gateway → Lambda) ────────────────────────────────

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.agent.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.agent.execution_arn}/*/*"
}
