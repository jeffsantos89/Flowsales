kubectl apply -f prometheus-grafana/
kubectl apply -f elk-stack/
kubectl apply -f opentelemetry/
kubectl apply -f zabbix-configmap.yaml
kubectl apply -f zabbix-deployment.yaml
kubectl apply -f zabbix-service.yaml
# Terraform
terraform init
terraform plan -var-file=prod/variables.tfvars
terraform apply -var-file=prod/variables.tfvars

# Pipeline (acionado automaticamente pelo GitHub)
git push origin main