# 1️⃣ Criar uma nova migração (exemplo: adicionando uma nova tabela)
alembic revision --autogenerate -m "add_new_table"

# 2️⃣ Aplicar todas as migrações
alembic upgrade head

# 3️⃣ Reverter a última migração
alembic downgrade -1

# 4️⃣ Visualizar status das migrações
alembic history

# 5️⃣ Rodar Alembic em um ambiente específico (caso use `.env`)
alembic -c alembic.ini upgrade head
