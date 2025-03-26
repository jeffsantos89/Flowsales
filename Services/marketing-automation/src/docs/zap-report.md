# OWASP ZAP Security Report

## Resumo
- Vulnerabilidades Críticas: 0
- Vulnerabilidades Altas: 2
- Vulnerabilidades Médias: 5
- Vulnerabilidades Baixas: 3

## Detalhes
- **SQL Injection:** Encontrada em `/api/login`. Recomendação: Parametrizar consultas SQL.
- **Cross-Site Scripting (XSS):** Encontrada em `/api/comments`. Recomendação: Sanitizar entradas.

## Próximos Passos
- Corrigir vulnerabilidades críticas imediatamente.
- Reavaliar políticas de segurança no Kubernetes.
