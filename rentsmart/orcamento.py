"""Orçamento: junta o imóvel e a taxa contratual e produz resumo e projeção."""

from dataclasses import dataclass
from decimal import Decimal

from .dinheiro import formatar_brl
from .imoveis import Imovel
from .taxa_contratual import TaxaContratual


@dataclass(frozen=True)
class LinhaProjecao:
    mes: int
    aluguel: Decimal
    parcela_taxa: Decimal
    total_mes: Decimal
    acumulado: Decimal


class Orcamento:
    MESES_PROJECAO = 12
    LARGURA = 58

    def __init__(self, imovel: Imovel, taxa: TaxaContratual):
        self.imovel = imovel
        self.taxa = taxa

    @property
    def aluguel_mensal(self) -> Decimal:
        return self.imovel.aluguel_mensal()

    def projecao(self, meses: int = MESES_PROJECAO) -> list[LinhaProjecao]:
        linhas, acumulado = [], Decimal("0.00")
        for mes in range(1, meses + 1):
            parcela = self.taxa.parcela_do_mes(mes)
            total = self.aluguel_mensal + parcela
            acumulado += total
            linhas.append(LinhaProjecao(mes, self.aluguel_mensal, parcela, total, acumulado))
        return linhas

    def total_aluguel_periodo(self, meses: int = MESES_PROJECAO) -> Decimal:
        return self.aluguel_mensal * meses

    def total_periodo(self, meses: int = MESES_PROJECAO) -> Decimal:
        return self.projecao(meses)[-1].acumulado

    # ---------- apresentação ----------
    def _linha(self, rotulo: str, valor: str) -> str:
        pontos = "." * max(2, self.LARGURA - 4 - len(rotulo) - len(valor) - 2)
        return f"  {rotulo} {pontos} {valor}"

    def resumo(self) -> str:
        w, sep = self.LARGURA, "-" * (self.LARGURA - 4)
        out = ["=" * w, "RENTSMART — ORÇAMENTO DE LOCAÇÃO".center(w), "R.M Imóveis".center(w), "=" * w,
               f"Imóvel: {self.imovel.descricao()}", "", "ALUGUEL MENSAL"]
        for item in self.imovel.composicao_aluguel():
            out.append(self._linha(item.descricao, formatar_brl(item.valor)))
        out += [f"  {sep}", self._linha("Aluguel mensal", formatar_brl(self.aluguel_mensal)), "",
                "TAXA CONTRATUAL (cobrança à parte, não integra o aluguel)",
                self._linha("Valor total", formatar_brl(self.taxa.valor)),
                self._linha("Parcelamento", f"{self.taxa.num_parcelas}x")]
        for i, p in enumerate(self.taxa.parcelas(), start=1):
            out.append(self._linha(f"Parcela {i} (mês {i})", formatar_brl(p)))
        n = self.MESES_PROJECAO
        out += ["", f"PRIMEIRO ANO ({n} MESES)",
                self._linha(f"Aluguel ({n} x {formatar_brl(self.aluguel_mensal)})",
                            formatar_brl(self.total_aluguel_periodo())),
                self._linha("Taxa contratual", formatar_brl(self.taxa.valor)),
                f"  {sep}",
                self._linha("Total previsto no 1º ano", formatar_brl(self.total_periodo())),
                "=" * w]
        return "\n".join(out)
