from typing import List, Dict, Union, Optional
import seaborn as sns
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

class DashboardService:
    """
    Serviço para geração de dashboards e visualização de métricas de vendas.
    """

    def __init__(self, output_dir: str = "reports"):
        """
        Inicializa o serviço de dashboard.
        
        Args:
            output_dir (str): Diretório para salvar os gráficos gerados
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._setup_style()

    def _setup_style(self) -> None:
        """Configura o estilo padrão dos gráficos"""
        sns.set_theme(style="whitegrid")
        plt.style.use('seaborn')

    def plot_sales_trend(
        self,
        sales_data: Union[List, pd.DataFrame],
        title: str = "Tendência de Vendas",
        x_label: str = "Período",
        y_label: str = "Vendas (R$)",
        save: bool = True,
        show: bool = True,
        fig_size: tuple = (12, 6)
    ) -> Optional[str]:
        """
        Plota e/ou salva o gráfico de tendência de vendas.

        Args:
            sales_data: Dados de vendas em lista ou DataFrame
            title: Título do gráfico
            x_label: Label do eixo X
            y_label: Label do eixo Y
            save: Se True, salva o gráfico
            show: Se True, exibe o gráfico
            fig_size: Tamanho da figura (largura, altura)

        Returns:
            Optional[str]: Caminho do arquivo salvo se save=True
        """
        try:
            # Converte para DataFrame se necessário
            df = pd.DataFrame(sales_data) if not isinstance(sales_data, pd.DataFrame) else sales_data
            
            plt.figure(figsize=fig_size)
            
            # Plotagem com mais detalhes
            sns.lineplot(data=df, markers=True, dashes=False)
            
            # Configurações do gráfico
            plt.title(title, pad=20, fontsize=14)
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.xticks(rotation=45)
            
            # Ajusta o layout
            plt.tight_layout()

            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"sales_trend_{timestamp}.png"
                filepath = self.output_dir / filename
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                logger.info(f"Gráfico salvo em: {filepath}")

            if show:
                plt.show()
            else:
                plt.close()

            return str(filepath) if save else None

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico: {str(e)}")
            raise

    def __str__(self) -> str:
        return f"DashboardService(output_dir={self.output_dir})"
