"""Interface de console: coleta e valida entradas, sem nenhuma regra de cálculo.

As funções de entrada e saída são injetáveis (entrada=input, saida=print),
o que permite testar a interface sem digitar nada.
"""

from datetime import datetime
from pathlib import Path
from typing import Callable

from .exportador_csv import ExportadorCSV
from .imoveis import Apartamento, Casa, Estudio, Imovel
from .orcamento import Orcamento
from .taxa_contratual import TaxaContratual


class InterfaceConsole:
    TIPOS = {"1": "Apartamento", "2": "Casa", "3": "Estúdio"}

    def __init__(self, entrada: Callable[[str], str] = input,
                 saida: Callable[[str], None] = print,
                 pasta_saida: str | Path = "saida"):
        self.entrada = entrada
        self.saida = saida
        self.pasta_saida = Path(pasta_saida)

    # ---------- leitura validada ----------
    def ler_opcao(self, pergunta: str, opcoes: dict[str, str]) -> str:
        while True:
            for chave, rotulo in opcoes.items():
                self.saida(f"  [{chave}] {rotulo}")
            resposta = self.entrada(f"{pergunta}: ").strip()
            if resposta in opcoes:
                return resposta
            self.saida(f"Opção inválida. Escolha entre: {', '.join(opcoes)}.")

    def ler_inteiro(self, pergunta: str, minimo: int, maximo: int) -> int:
        while True:
            resposta = self.entrada(f"{pergunta} ({minimo}-{maximo}): ").strip()
            if resposta.isdigit() and minimo <= int(resposta) <= maximo:
                return int(resposta)
            self.saida(f"Valor inválido. Digite um número inteiro de {minimo} a {maximo}.")

    def ler_sim_nao(self, pergunta: str) -> bool:
        while True:
            resposta = self.entrada(f"{pergunta} (s/n): ").strip().lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            self.saida("Resposta inválida. Digite 's' para sim ou 'n' para não.")

    # ---------- montagem dos objetos ----------
    def montar_imovel(self) -> Imovel:
        self.saida("\nTipo de imóvel:")
        tipo = self.ler_opcao("Escolha o tipo", self.TIPOS)
        if tipo == "3":
            while True:
                vagas = self.ler_inteiro("Quantidade de vagas (0 = nenhuma; pacote mínimo 2)",
                                         0, Estudio.MAX_VAGAS)
                try:
                    return Estudio(vagas)
                except ValueError as erro:  # ex.: 1 vaga
                    self.saida(str(erro))
        quartos = self.ler_inteiro("Número de quartos", 1, 2)
        garagem = self.ler_sim_nao("Deseja vaga de garagem (+R$ 300,00/mês)?")
        if tipo == "1":
            criancas = self.ler_sim_nao("Possui crianças?")
            return Apartamento(quartos, garagem, possui_criancas=criancas)
        return Casa(quartos, garagem)

    def montar_taxa(self) -> TaxaContratual:
        parcelas = self.ler_inteiro("Em quantas parcelas deseja pagar a taxa contratual de R$ 2.000,00",
                                    1, TaxaContratual.MAX_PARCELAS)
        return TaxaContratual(parcelas)

    # ---------- fluxo principal ----------
    def executar(self) -> None:
        self.saida("=" * 58)
        self.saida("RentSmart — Orçamento de Locação | R.M Imóveis".center(58))
        self.saida("=" * 58)
        while True:
            orcamento = Orcamento(self.montar_imovel(), self.montar_taxa())
            self.saida("\n" + orcamento.resumo())
            nome = f"projecao_{datetime.now():%Y%m%d_%H%M%S}.csv"
            caminho = ExportadorCSV().exportar(orcamento, self.pasta_saida / nome)
            self.saida(f"\nProjeção de 12 meses salva em: {caminho}")
            if not self.ler_sim_nao("\nDeseja fazer outro orçamento?"):
                self.saida("Obrigado por usar o RentSmart!")
                break
