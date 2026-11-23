"""Testes das regras comerciais. Execute: python -m unittest -v"""

import csv
import tempfile
import unittest
from decimal import Decimal as D
from pathlib import Path

from rentsmart import Apartamento, Casa, Estudio, ExportadorCSV, Orcamento, TaxaContratual
from rentsmart.interface import InterfaceConsole


class TestApartamento(unittest.TestCase):
    def test_base_com_criancas(self):
        self.assertEqual(Apartamento(1, False, True).aluguel_mensal(), D("700.00"))

    def test_dois_quartos(self):
        self.assertEqual(Apartamento(2, False, True).aluguel_mensal(), D("900.00"))

    def test_desconto_sem_criancas_apos_adicionais(self):
        # (700 + 200 + 300) * 0,95 = 1.140,00
        self.assertEqual(Apartamento(2, True, False).aluguel_mensal(), D("1140.00"))

    def test_desconto_so_base(self):
        self.assertEqual(Apartamento(1, False, False).aluguel_mensal(), D("665.00"))

    def test_quartos_invalidos(self):
        with self.assertRaises(ValueError):
            Apartamento(3, False, True)


class TestCasa(unittest.TestCase):
    def test_base(self):
        self.assertEqual(Casa(1, False).aluguel_mensal(), D("900.00"))

    def test_dois_quartos_garagem(self):
        self.assertEqual(Casa(2, True).aluguel_mensal(), D("1450.00"))

    def test_casa_nao_tem_desconto(self):
        self.assertFalse(any(i.valor < 0 for i in Casa(2, True).composicao_aluguel()))


class TestEstudio(unittest.TestCase):
    def test_sem_vagas(self):
        self.assertEqual(Estudio(0).aluguel_mensal(), D("1200.00"))

    def test_pacote_duas_vagas(self):
        self.assertEqual(Estudio(2).aluguel_mensal(), D("1450.00"))

    def test_vagas_adicionais(self):
        # 1200 + 250 + 3 * 60 = 1.630,00
        self.assertEqual(Estudio(5).aluguel_mensal(), D("1630.00"))

    def test_uma_vaga_invalida(self):
        with self.assertRaises(ValueError):
            Estudio(1)


class TestTaxaContratual(unittest.TestCase):
    def test_parcelas_somam_total(self):
        for n in range(1, 6):
            self.assertEqual(sum(TaxaContratual(n).parcelas()), D("2000.00"), n)

    def test_tres_parcelas(self):
        self.assertEqual(TaxaContratual(3).parcelas(), [D("666.66"), D("666.66"), D("666.68")])

    def test_limites(self):
        for n in (0, 6):
            with self.assertRaises(ValueError):
                TaxaContratual(n)


class TestOrcamento(unittest.TestCase):
    def setUp(self):
        self.orc = Orcamento(Apartamento(2, True, False), TaxaContratual(3))

    def test_projecao_12_meses(self):
        proj = self.orc.projecao()
        self.assertEqual(len(proj), 12)
        self.assertEqual(proj[0].total_mes, D("1806.66"))
        self.assertEqual(proj[2].total_mes, D("1806.68"))
        self.assertEqual(proj[3].parcela_taxa, D("0.00"))
        self.assertEqual(proj[-1].acumulado, D("15680.00"))  # 12 * 1140 + 2000

    def test_csv(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = ExportadorCSV().exportar(self.orc, Path(pasta) / "p.csv")
            with caminho.open(encoding="utf-8-sig") as f:
                linhas = list(csv.reader(f, delimiter=";"))
        self.assertEqual(len(linhas), 13)  # cabeçalho + 12 meses
        self.assertEqual(linhas[-1][-1], "15.680,00")


class TestInterface(unittest.TestCase):
    def test_fluxo_com_entradas_invalidas(self):
        # tipo inválido, estúdio, 1 vaga (rejeitada), 3 vagas, 9 parcelas (inválido), 2, não repetir
        respostas = iter(["9", "3", "1", "3", "9", "2", "n"])
        saidas = []
        with tempfile.TemporaryDirectory() as pasta:
            InterfaceConsole(lambda _: next(respostas), saidas.append, pasta).executar()
            self.assertEqual(len(list(Path(pasta).glob("*.csv"))), 1)
        texto = "\n".join(saidas)
        self.assertIn("Opção inválida", texto)
        self.assertIn("pacote mínimo", texto)
        self.assertIn("R$ 1.510,00", texto)  # 1200 + 250 + 60


if __name__ == "__main__":
    unittest.main()
