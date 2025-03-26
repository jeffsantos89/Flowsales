"""${message}

Revisão ID: ${up_revision}
Revisão Anterior: ${down_revision or 'None'}
Criação: ${create_date}
"""

from alembic import op
import sqlalchemy as sa
import logging
import time
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry, stop_after_attempt, wait_exponential

# Revisão Identificadores
revision = "${up_revision}"
down_revision = ${repr(down_revision)} if ${repr(down_revision)} != "None" else None
branch_labels = None
depends_on = None

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def log_migration(action: str):
    """Log de ações durante a migração."""
    logger.info(f"📌 [Migração {revision} - {down_revision}] {action}")

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_connection():
    """Obtém uma conexão com o banco de dados com retry."""
    try:
        return op.get_bind()
    except Exception as e:
        logger.warning(f"⚠️ Falha ao conectar no banco: {e}")
        raise

def execute_with_transaction(func):
    """Decorator para execução segura dentro de transação."""
    def wrapper(*args, **kwargs):
        connection = get_connection()
        trans = connection.begin()
        try:
            result = func(*args, **kwargs)
            trans.commit()
            return result
        except Exception as e:
            trans.rollback()
            logger.error(f"❌ Falha na transação: {e}")
            raise
    return wrapper

def table_exists(table_name: str) -> bool:
    """Verifica se uma tabela existe antes de aplicar migrações."""
    try:
        result = op.get_bind().execute(
            f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');"
        ).scalar()
        return result
    except SQLAlchemyError as e:
        log_migration(f"❌ Erro ao verificar tabela `{table_name}`: {e}")
        return False

def index_exists(table_name: str, index_name: str) -> bool:
    """Verifica se um índice já existe na tabela antes de criar."""
    try:
        bind = op.get_bind()
        inspector = sa.inspect(bind)
        indexes = [i['name'] for i in inspector.get_indexes(table_name)]
        return index_name in indexes
    except SQLAlchemyError as e:
        log_migration(f"❌ Erro ao verificar índice `{index_name}` em `{table_name}`: {e}")
        return False

@execute_with_transaction
def safe_create_index(table_name: str, index_name: str, columns: list):
    """Cria um índice de forma segura, evitando duplicação."""
    if not index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns)
        log_migration(f"✔️ Índice `{index_name}` criado em `{table_name}`")
    else:
        log_migration(f"⚠️ Índice `{index_name}` já existe em `{table_name}`, ignorando.")

class MigrationContext:
    """Gerencia o contexto da migração, monitorando tempo e falhas."""
    
    def __init__(self, operation_type: str):
        self.operation_type = operation_type
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        log_migration(f"⏳ Iniciando {self.operation_type}...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type:
            log_migration(f"❌ {self.operation_type} falhou após {duration:.2f}s")
        else:
            log_migration(f"✅ {self.operation_type} concluído em {duration:.2f}s")

def upgrade():
    """Executa a migração de upgrade."""
    with MigrationContext("Upgrade"):
        if not table_exists('tabela_exemplo'):
            log_migration("⚠️ A tabela 'tabela_exemplo' não existe. Abortando migração.")
            return

        with op.batch_alter_table('tabela_exemplo') as batch_op:
            batch_op.add_column(sa.Column('nova_coluna', sa.String(length=255), nullable=True))
            log_migration("✔️ Coluna 'nova_coluna' adicionada com sucesso.")

            safe_create_index('tabela_exemplo', 'idx_nova_coluna', ['nova_coluna'])

def downgrade():
    """Executa a reversão da migração (downgrade)."""
    with MigrationContext("Downgrade"):
        with op.batch_alter_table('tabela_exemplo') as batch_op:
            batch_op.drop_index('idx_nova_coluna')
            log_migration("✔️ Índice 'idx_nova_coluna' removido com sucesso.")

            batch_op.drop_column('nova_coluna')
            log_migration("✔️ Coluna 'nova_coluna' removida com sucesso.")
