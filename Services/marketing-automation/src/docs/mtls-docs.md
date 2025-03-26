# Configuração de mTLS

## O que é mTLS?
Mutual TLS (mTLS) garante que tanto o cliente quanto o servidor se autentiquem mutuamente antes de estabelecerem uma conexão segura.

---

## Configuração
1. Gere o certificado:
   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

## Crie o secret no Kubernetes
kubectl create secret tls mtls-cert --cert=cert.pem --key=key.pem

## Aplique o Ingress
kubectl apply -f mtls-config.yaml
 
 ## Para testar o mTLS
curl -vk --cert cert.pem --key key.pem https://api.sellflux.com.br/api/leads
