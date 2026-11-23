"""Taxa contratual: cobrança única, separada do aluguel, em até 5 parcelas."""

from decimal import Decimal, ROUND_DOWN

from .dinheiro import CENTAVO


class TaxaContratual:
    VALOR_PADRAO = Decimal("2000.00")
    MAX_PARCELAS = 5

    def __init__(self, num_parcelas: int, valor: Decimal = VALOR_PADRAO):
        if not (1 <= num_parcelas <= self.MAX_PARCELAS):
            raise ValueError(
                f"A taxa contratual pode ser paga em 1 a {self.MAX_PARCELAS} parcelas "
                f"(informado: {num_parcelas})."
            )
        self.valor = Decimal(valor)
        self.num_parcelas = num_parcelas

    def parcelas(self) -> list[Decimal]:
        """Divide a taxa em parcelas que somam EXATAMENTE o valor total.

        As primeiras parcelas são truncadas em centavos e o resíduo vai para a
        última. Ex.: R$ 2.000,00 em 3x -> 666,66 + 666,66 + 666,68.
        """
        base = (self.valor / self.num_parcelas).quantize(CENTAVO, rounding=ROUND_DOWN)
        ultima = self.valor - base * (self.num_parcelas - 1)
        return [base] * (self.num_parcelas - 1) + [ultima]

    def parcela_do_mes(self, mes: int) -> Decimal:
        """Valor da parcela da taxa no mês informado (1-based); 0 fora do parcelamento."""
        if 1 <= mes <= self.num_parcelas:
            return self.parcelas()[mes - 1]
        return Decimal("0.00")
