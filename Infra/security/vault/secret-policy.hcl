path "secret/data/flowsale/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/flowsale/*" {
  capabilities = ["list"]
}
// docker-compose build && docker-compose up -d
// kubectl apply -f namespace.yaml
// kubectl apply -f peer-authentication.yaml
// kubectl apply -f authorization-policy.yaml
//helm repo add hashicorp https://helm.releases.hashicorp.com
//helm install vault hashicorp/vault -n vault --create-namespace -f vault-values.yaml
//kubectl exec -n vault -it vault-0 -- vault policy write sellflux-policy /vault/file/secret-policy.hcl
