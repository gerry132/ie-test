resource "aws_kms_key" "ie_domain_key" {
  description = "IE domain key"
}

resource "aws_codeartifact_domain" "ie_codeartifact" {
  domain = "${var.environment_name}"
}

resource "aws_codeartifact_repository" "python" {
  repository = "python"
  domain     = aws_codeartifact_domain.ie_codeartifact.domain

  external_connections {
    external_connection_name = "public:pypi"
  } 
}
