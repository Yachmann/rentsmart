"""Hierarquia de imóveis da R.M Imóveis.

Imovel (abstrata)
├── ImovelResidencial (abstrata) -> quartos (1 ou 2) e vaga de garagem opcional
│   ├── Apartamento               -> desconto de 5% para quem não tem crianças
│   └── Casa
└── Estudio                       -> pacote de vagas (2 por R$ 250 + R$ 60 por extra)

O cálculo do aluguel segue o padrão Template Method: a classe-base define
a ordem (aluguel-base -> adicionais -> descontos) e cada subclasse informa
apenas os seus adicionais e descontos. Assim a regra de "desconto após os
adicionais" fica garantida para qualquer tipo de imóvel.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from .dinheiro import arredondar


@dataclass(frozen=True)
class ItemOrcamento:
    """Uma linha da composição do aluguel. Valor negativo = desconto."""
    descricao: str
    valor: Decimal


class Imovel(ABC):
    """Classe-base de todos os imóveis."""

    NOME_TIPO: str = ""
    ALUGUEL_BASE: Decimal = Decimal("0")

    @property
    def aluguel_base(self) -> Decimal:
        return self.ALUGUEL_BASE

    @abstractmethod
    def descricao(self) -> str:
        """Descrição curta do imóvel escolhido, usada no resumo."""

    @abstractmethod
    def _adicionais(self) -> list[ItemOrcamento]:
        """Adicionais mensais específicos do tipo de imóvel."""

    def _descontos(self, subtotal: Decimal) -> list[ItemOrcamento]:
        """Descontos aplicados sobre o subtotal (base + adicionais).
        Por padrão não há desconto; subclasses sobrescrevem se necessário."""
        return []

    def composicao_aluguel(self) -> list[ItemOrcamento]:
        """Template Method: base -> adicionais -> descontos sobre o subtotal."""
        itens = [ItemOrcamento("Aluguel-base", self.aluguel_base)]
        itens.extend(self._adicionais())
        subtotal = sum((item.valor for item in itens), Decimal("0"))
        itens.extend(self._descontos(subtotal))
        return itens

    def aluguel_mensal(self) -> Decimal:
        return arredondar(sum((i.valor for i in self.composicao_aluguel()), Decimal("0")))


class ImovelResidencial(Imovel, ABC):
    """Casa ou apartamento: 1 ou 2 quartos e uma vaga de garagem opcional."""

    QUARTOS_PERMITIDOS = (1, 2)
    VALOR_GARAGEM = Decimal("300.00")
    ADICIONAL_SEGUNDO_QUARTO: Decimal = Decimal("0")

    def __init__(self, quartos: int, garagem: bool):
        if quartos not in self.QUARTOS_PERMITIDOS:
            raise ValueError(f"{self.NOME_TIPO} deve ter 1 ou 2 quartos (informado: {quartos}).")
        self.quartos = quartos
        self.garagem = bool(garagem)

    def _adicionais(self) -> list[ItemOrcamento]:
        itens = []
        if self.quartos == 2:
            itens.append(ItemOrcamento("Adicional 2º quarto", self.ADICIONAL_SEGUNDO_QUARTO))
        if self.garagem:
            itens.append(ItemOrcamento("Vaga de garagem", self.VALOR_GARAGEM))
        return itens

    def _descricao_basica(self) -> str:
        quartos = "1 quarto" if self.quartos == 1 else "2 quartos"
        garagem = "com garagem" if self.garagem else "sem garagem"
        return f"{self.NOME_TIPO} — {quartos}, {garagem}"


class Apartamento(ImovelResidencial):
    NOME_TIPO = "Apartamento"
    ALUGUEL_BASE = Decimal("700.00")
    ADICIONAL_SEGUNDO_QUARTO = Decimal("200.00")
    PERCENTUAL_DESCONTO_SEM_CRIANCAS = Decimal("0.05")

    def __init__(self, quartos: int, garagem: bool, possui_criancas: bool):
        super().__init__(quartos, garagem)
        self.possui_criancas = bool(possui_criancas)

    def _descontos(self, subtotal: Decimal) -> list[ItemOrcamento]:
        # Decisão documentada: o desconto incide sobre base + TODOS os
        # adicionais (inclusive garagem), conforme "após a aplicação dos
        # adicionais correspondentes".
        if self.possui_criancas:
            return []
        desconto = arredondar(subtotal * self.PERCENTUAL_DESCONTO_SEM_CRIANCAS)
        return [ItemOrcamento("Desconto 5% (sem crianças)", -desconto)]

    def descricao(self) -> str:
        criancas = "com crianças" if self.possui_criancas else "sem crianças"
        return f"{self._descricao_basica()}, {criancas}"


class Casa(ImovelResidencial):
    NOME_TIPO = "Casa"
    ALUGUEL_BASE = Decimal("900.00")
    ADICIONAL_SEGUNDO_QUARTO = Decimal("250.00")

    def descricao(self) -> str:
        return self._descricao_basica()


class Estudio(Imovel):
    """Estúdio: estacionamento vendido em pacote.

    0 vagas  -> R$ 0,00
    2 vagas  -> R$ 250,00 (pacote inicial)
    n > 2    -> R$ 250,00 + R$ 60,00 por vaga além das duas
    1 vaga isolada não existe na tabela da imobiliária e é rejeitada.
    """

    NOME_TIPO = "Estúdio"
    ALUGUEL_BASE = Decimal("1200.00")
    VAGAS_NO_PACOTE = 2
    VALOR_PACOTE_VAGAS = Decimal("250.00")
    VALOR_VAGA_ADICIONAL = Decimal("60.00")
    MAX_VAGAS = 10  # limite de sanidade para entrada do usuário

    def __init__(self, vagas: int):
        if vagas != 0 and not (self.VAGAS_NO_PACOTE <= vagas <= self.MAX_VAGAS):
            raise ValueError(
                f"Estúdio aceita 0 vagas ou de {self.VAGAS_NO_PACOTE} a {self.MAX_VAGAS} "
                f"vagas (o pacote mínimo é de {self.VAGAS_NO_PACOTE}). Informado: {vagas}."
            )
        self.vagas = vagas

    def _adicionais(self) -> list[ItemOrcamento]:
        if self.vagas == 0:
            return []
        itens = [ItemOrcamento(f"Pacote de {self.VAGAS_NO_PACOTE} vagas", self.VALOR_PACOTE_VAGAS)]
        extras = self.vagas - self.VAGAS_NO_PACOTE
        if extras > 0:
            itens.append(ItemOrcamento(
                f"Vagas adicionais ({extras} x R$ 60,00)", self.VALOR_VAGA_ADICIONAL * extras
            ))
        return itens

    def descricao(self) -> str:
        vagas = "sem vagas" if self.vagas == 0 else f"{self.vagas} vagas"
        return f"{self.NOME_TIPO} — {vagas}"
