"""Exporta a projeção de 12 meses para CSV.

Formato pensado para abrir direto no Excel em português: separador ';',
decimal com vírgula e codificação UTF-8 com BOM (acentos corretos).
"""

import csv
from pathlib import Path

from .dinheiro import formatar_brl
from .orcamento import Orcamento


class ExportadorCSV:
    CABECALHO = ["mes", "aluguel", "parcela_taxa_contratual", "total_mes", "total_acumulado"]

    def __init__(self, separador: str = ";"):
        self.separador = separador

    def exportar(self, orcamento: Orcamento, caminho: str | Path) -> Path:
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=self.separador)
            escritor.writerow(self.CABECALHO)
            for linha in orcamento.projecao():
                escritor.writerow([
                    linha.mes,
                    formatar_brl(linha.aluguel, com_simbolo=False),
                    formatar_brl(linha.parcela_taxa, com_simbolo=False),
                    formatar_brl(linha.total_mes, com_simbolo=False),
                    formatar_brl(linha.acumulado, com_simbolo=False),
                ])
        return caminho
