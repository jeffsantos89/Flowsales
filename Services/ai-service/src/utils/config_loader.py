import os
import json
import yaml
import logging
from dotenv import load_dotenv
from typing import Any, Dict, Optional

class ConfigLoader:
    """Carrega configurações de diferentes fontes (JSON, YAML, .env)"""

    def __init__(self, config_files: Optional[list] = None):
        load_dotenv()
        self.config_files = config_files or ["config.yaml"]
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        config = {}
        for config_file in self.config_files:
            if not os.path.exists(config_file):
                logging.warning(f"Config file {config_file} does not exist.")
                continue

            try:
                with open(config_file, "r") as f:
                    if config_file.endswith(".json"):
                        config.update(json.load(f))
                    elif config_file.endswith(".yaml") or config_file.endswith(".yml"):
                        config.update(yaml.safe_load(f))
            except Exception as e:
                logging.error(f"Failed to load config file {config_file}: {e}")
        return config

    def get(self, key: str, default: Any = None) -> Any:
        return os.getenv(key) or self.config.get(key, default)

    def validate_config(self, required_keys: list) -> bool:
        missing_keys = [key for key in required_keys if key not in self.config]
        if missing_keys:
            logging.error(f"Missing required config keys: {missing_keys}")
            return False
        return True

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Exemplo de uso
config_files = ["config.yaml", "config.json"]
config = ConfigLoader(config_files=config_files)

# Validação de configuração
required_keys = ["database_url", "api_key"]
if not config.validate_config(required_keys):
    raise ValueError("Configuração inválida. Verifique os logs para mais detalhes.")
