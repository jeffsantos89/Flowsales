from alembic import command
from alembic.config import Config
import os
import argparse
import logging
from typing import Optional
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MigrationManager:
    def __init__(self):
        self.alembic_cfg = self._get_alembic_config()

    @staticmethod
    def _get_alembic_config() -> Config:
        """Retorna a configuração do Alembic."""
        config_path = Path(__file__).parent / "alembic.ini"
        if not config_path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        return Config(str(config_path))

    def upgrade(self) -> None:
        """Executa upgrade das migrações para a última versão."""
        try:
            logger.info("Iniciando upgrade das migrações...")
            command.upgrade(self.alembic_cfg, "head")
            logger.info("Upgrade concluído com sucesso")
        except Exception as e:
            logger.error(f"Erro durante upgrade: {e}")
            raise

    def downgrade(self, revision: str = 'base') -> None:
        """Executa downgrade das migrações para uma revisão específica."""
        try:
            logger.info(f"Iniciando downgrade para revisão: {revision}")
            command.downgrade(self.alembic_cfg, revision)
            logger.info("Downgrade concluído com sucesso")
        except Exception as e:
            logger.error(f"Erro durante downgrade: {e}")
            raise

    def check_status(self) -> None:
        """Verifica o status atual das migrações."""
        try:
            logger.info("Verificando status das migrações...")
            command.current(self.alembic_cfg)
            command.history(self.alembic_cfg)
            logger.info("Verificação de status concluída")
        except Exception as e:
            logger.error(f"Erro ao verificar status: {e}")
            raise

def parse_arguments() -> argparse.Namespace:
    """Configura e processa argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description='Ferramenta de gerenciamento de migrações de banco de dados',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--action',
        choices=['upgrade', 'downgrade', 'status'],
        default='upgrade',
        help='Ação de migração a ser executada'
    )
    parser.add_argument(
        '--revision',
        default='head',
        help='Revisão para downgrade'
    )
    return parser.parse_args()

def main() -> None:
    """Função principal do script."""
    try:
        args = parse_arguments()
        manager = MigrationManager()

        actions = {
            'upgrade': manager.upgrade,
            'downgrade': lambda: manager.downgrade(args.revision),
            'status': manager.check_status
        }

        action = actions.get(args.action)
        if action:
            action()
        else:
            raise ValueError(f"Ação não suportada: {args.action}")

    except Exception as e:
        logger.error(f"Erro fatal durante a execução: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
    import os
import argparse
from alembic import command
from alembic.config import Config

def get_alembic_config() -> Config:
    return Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))

def run_migrations() -> None:
    cfg = get_alembic_config()
    command.upgrade(cfg, "head")

def downgrade_migrations(revision='base') -> None:
    try:
        cfg = get_alembic_config()
        command.downgrade(cfg, revision)
    except Exception as e:
        print(f"Error during downgrade: {e}")

def verify_migration_status() -> None:
    try:
        cfg = get_alembic_config()
        command.current(cfg)
        command.history(cfg)
    except Exception as e:
        print(f"Error checking migration status: {e}")

def main():
    parser = argparse.ArgumentParser(description='Database migration CLI')
    parser.add_argument('--action', choices=['upgrade', 'downgrade', 'status'],
                        default='upgrade', help='Migration action to perform')
    parser.add_argument('--revision', default='head',
                        help='Target revision for downgrade')

    args = parser.parse_args()

    try:
        if args.action == 'upgrade':
            run_migrations()
        elif args.action == 'downgrade':
            downgrade_migrations(args.revision)
        elif args.action == 'status':
            verify_migration_status()
    except Exception as e:
        print(f"Migration failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
import os
import argparse
from alembic import command
from alembic.config import Config

def get_alembic_config() -> Config:
    return Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))

def run_migrations() -> None:
    cfg = get_alembic_config()
    command.upgrade(cfg, "head")

def downgrade_migrations(revision='base') -> None:
    try:
        cfg = get_alembic_config()
        command.downgrade(cfg, revision)
    except Exception as e:
        print(f"Error during downgrade: {e}")

def verify_migration_status() -> None:
    try:
        cfg = get_alembic_config()
        command.current(cfg)
        command.history(cfg)
    except Exception as e:
        print(f"Error checking migration status: {e}")

def main():
    parser = argparse.ArgumentParser(description='Database migration CLI')
    parser.add_argument('--action', choices=['upgrade', 'downgrade', 'status'],
                        default='upgrade', help='Migration action to perform')
    parser.add_argument('--revision', default='head',
                        help='Target revision for downgrade')

    args = parser.parse_args()

    try:
        if args.action == 'upgrade':
            run_migrations()
        elif args.action == 'downgrade':
            downgrade_migrations(args.revision)
        elif args.action == 'status':
            verify_migration_status()
    except Exception as e:
        print(f"Migration failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
