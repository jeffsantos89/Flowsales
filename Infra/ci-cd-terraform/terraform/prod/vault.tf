terraform {
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "~> 3.25.0"
    }
  }
}

provider "vault" {
  address = "https://vault.flowsale.com.br"
  token   = var.vault_token
}

data "vault_generic_secret" "db_creds" {
  path = "secret/data/flowsale/database"
}

output "db_username" {
  value = data.vault_generic_secret.db_creds.data["username"]
}

output "db_password" {
  sensitive = true
  value     = data.vault_generic_secret.db_creds.data["password"]
}
