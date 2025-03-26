# Documentação da API com Redocly

Este serviço utiliza a biblioteca Redoc para gerar documentação interativa baseada em OpenAPI.

## Como acessar?
- Versão local: http://localhost:8000/docs
- Produção: https://api.aiservice.com/docs

### Como testar endpoints?
1. Autentique-se via `/auth/login`
2. Gere previsões em `/predict`
3. Integre com marketplaces via `/marketplace`
## Arquitetura e Tecnologias

### Stack Tecnológica
- **Backend**: FastAPI/Python
- **Documentação**: OpenAPI 3.0
- **Interface**: Redoc UI
- **Autenticação**: JWT Bearer

### Recursos Principais
- Swagger UI alternativo: `/swagger`
- Schemas JSON: `/openapi.json`
- Métricas: `/metrics`
- Health Check: `/health`

## Guia de Desenvolvimento

### Pré-requisitos
```bash
python >= 3.8
pip >= 21.0
```

### Setup Local
1. Clone o repositório
2. Instale dependências: `pip install -r requirements.txt`
3. Configure variáveis: `cp .env.example .env`
4. Execute: `uvicorn main:app --reload`

## Segurança e Boas Práticas
- Rate Limiting implementado
- Validação de payload
- Logging estruturado
- Caching opcional
- CORS configurado