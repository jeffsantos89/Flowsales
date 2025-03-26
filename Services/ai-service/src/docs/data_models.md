# Modelos de Dados - Documentação Técnica

## Visão Geral
Este documento descreve as estruturas de dados principais utilizadas no sistema.

## Modelo Relacional

### Tabela `users`
| Campo      | Tipo         | Restrições    | Descrição                            |
|------------|--------------|---------------|---------------------------------------|
| id         | INTEGER      | PK, NOT NULL  | Identificador único do usuário       |
| name       | VARCHAR(255) | NOT NULL      | Nome completo do usuário             |
| email      | VARCHAR(255) | UNIQUE        | Endereço de e-mail para contato     |
| created_at | TIMESTAMP    | NOT NULL      | Data/hora de criação do registro     |
| updated_at | TIMESTAMP    | NOT NULL      | Data/hora da última atualização      |
| status     | ENUM         | NOT NULL      | Status do usuário (ativo/inativo)    |

### Tabela `predictions`
| Campo        | Tipo         | Restrições           | Descrição                         |
|--------------|--------------|----------------------|-----------------------------------|
| id           | INTEGER      | PK, NOT NULL         | Identificador único da previsão   |
| user_id      | INTEGER      | FK, NOT NULL         | Referência à tabela users         |
| result       | JSONB        | NOT NULL             | Resultado estruturado da IA       |
| model_version| VARCHAR(50)  | NOT NULL             | Versão do modelo utilizado        |
| created_at   | TIMESTAMP    | NOT NULL             | Data/hora de criação              |
| confidence   | DECIMAL      | NOT NULL             | Índice de confiança (0-1)         |
| status       | ENUM         | NOT NULL             | Status do processamento           |

## Índices
- users_email_idx (UNIQUE) em users(email)
- predictions_user_id_idx em predictions(user_id)
- predictions_created_at_idx em predictions(created_at)

## Relacionamentos
- predictions.user_id → users.id (ON DELETE CASCADE)

## Notas de Implementação
- Todos os timestamps são armazenados em UTC
- O campo result em predictions utiliza compressão JSONB
- Backups incrementais a cada 6 horas
