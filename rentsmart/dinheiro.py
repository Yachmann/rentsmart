"""Funções utilitárias para valores monetários.

Todos os cálculos usam Decimal (e não float) para evitar erros de
representação binária, como 0.1 + 0.2 != 0.3, que fariam o total do
contrato não fechar em centavos.
"""

from decimal import Decimal, ROUND_HALF_UP

CENTAVO = Decimal("0.01")


def arredondar(valor: Decimal) -> Decimal:
    """Arredonda para centavos (meio para cima)."""
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def formatar_brl(valor: Decimal, com_simbolo: bool = True) -> str:
    """Formata no padrão brasileiro: 1234.5 -> 'R$ 1.234,50'."""
    valor = arredondar(valor)
    sinal = "-" if valor < 0 else ""
    texto = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sinal}R$ {texto}" if com_simbolo else f"{sinal}{texto}"
