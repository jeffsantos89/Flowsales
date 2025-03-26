import joblib
import os
import json
from datetime import datetime
import logging
from typing import Any, Dict, Optional
import hashlib
from pathlib import Path
import shutil

class ModelRegistryError(Exception):
    """Exceção customizada para erros do ModelRegistry"""
    pass

class ModelRegistry:
    """
    Gerenciador avançado de modelos de Machine Learning com suporte a versionamento,
    metadados e validação.
    """
    def __init__(self, model_dir: str = "models/", enable_versioning: bool = True):
        """
        Inicializa o registro de modelos.
        
        Args:
            model_dir: Diretório base para armazenamento dos modelos
            enable_versioning: Ativa o controle de versões dos modelos
        """
        self.base_dir = Path(model_dir)
        self.enable_versioning = enable_versioning
        self.logger = logging.getLogger(__name__)
        
        # Configuração inicial
        self._setup_directory()
        self._setup_logging()

    def _setup_directory(self) -> None:
        """Configura a estrutura de diretórios necessária"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        (self.base_dir / "metadata").mkdir(exist_ok=True)
        if self.enable_versioning:
            (self.base_dir / "versions").mkdir(exist_ok=True)

    def _setup_logging(self) -> None:
        """Configura o sistema de logging"""
        logging.basicConfig(level=logging.INFO)

    def _generate_model_hash(self, model: Any) -> str:
        """Gera um hash único para o modelo"""
        model_bytes = joblib.dumps(model)
        return hashlib.md5(model_bytes).hexdigest()

    def save_model(self, model: Any, model_name: str, metadata: Dict = None) -> str:
        """
        Salva um modelo com seus metadados.
        
        Args:
            model: O modelo a ser salvo
            model_name: Nome do modelo
            metadata: Dicionário com metadados do modelo
        
        Returns:
            str: Versão do modelo salvo
        """
        try:
            # Gera versão baseada em timestamp e hash
            version = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self._generate_model_hash(model)[:8]}"
            
            # Prepara metadados
            metadata = metadata or {}
            metadata.update({
                "version": version,
                "created_at": datetime.now().isoformat(),
                "model_name": model_name
            })

            # Define caminhos
            model_path = self.base_dir / "versions" / f"{model_name}_{version}.pkl"
            metadata_path = self.base_dir / "metadata" / f"{model_name}_{version}.json"
            latest_path = self.base_dir / f"{model_name}_latest.pkl"

            # Salva modelo e metadados
            joblib.dump(model, model_path)
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            # Atualiza versão mais recente
            shutil.copy(model_path, latest_path)

            self.logger.info(f"Modelo {model_name} (versão {version}) salvo com sucesso")
            return version

        except Exception as e:
            self.logger.error(f"Erro ao salvar modelo {model_name}: {str(e)}")
            raise ModelRegistryError(f"Falha ao salvar modelo: {str(e)}")

    def load_model(self, model_name: str, version: Optional[str] = None) -> Any:
        """
        Carrega um modelo específico.
        
        Args:
            model_name: Nome do modelo
            version: Versão específica do modelo (opcional)
        
        Returns:
            O modelo carregado
        """
        try:
            if version:
                model_path = self.base_dir / "versions" / f"{model_name}_{version}.pkl"
            else:
                model_path = self.base_dir / f"{model_name}_latest.pkl"

            if not model_path.exists():
                raise FileNotFoundError(f"Modelo não encontrado: {model_path}")

            model = joblib.load(model_path)
            self.logger.info(f"Modelo {model_name} carregado com sucesso")
            return model

        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo {model_name}: {str(e)}")
            raise ModelRegistryError(f"Falha ao carregar modelo: {str(e)}")

    def get_model_metadata(self, model_name: str, version: Optional[str] = None) -> Dict:
        """
        Recupera os metadados de um modelo.
        
        Args:
            model_name: Nome do modelo
            version: Versão específica do modelo (opcional)
        
        Returns:
            Dict: Metadados do modelo
        """
        try:
            if version:
                metadata_path = self.base_dir / "metadata" / f"{model_name}_{version}.json"
            else:
                # Encontra a versão mais recente
                metadata_files = list((self.base_dir / "metadata").glob(f"{model_name}_*.json"))
                if not metadata_files:
                    raise FileNotFoundError(f"Nenhum metadado encontrado para {model_name}")
                metadata_path = sorted(metadata_files)[-1]

            with open(metadata_path) as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Erro ao recuperar metadados do modelo {model_name}: {str(e)}")
            raise ModelRegistryError(f"Falha ao recuperar metadados: {str(e)}")
