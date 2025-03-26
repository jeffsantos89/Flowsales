# Arquitetura de Sharding

## Objetivo
Distribuir a carga entre múltiplas instâncias do banco de dados para melhorar a escalabilidade.

## Estratégia
- **Consistência:** Cada shard contém um subconjunto dos dados.
- **Distribuição:** Baseada no `userId % total_shards`.

## Benefícios
- Aumenta a capacidade de leitura e escrita.
- Reduz contenção de recursos.

## Desafios
- Complexidade na consulta distribuída.
- Backup e restore mais sofisticados.
