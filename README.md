# RentSmart — Orçamento de Locação (R.M Imóveis)

Aplicação de console em Python que calcula o orçamento de locação de imóveis da
R.M Imóveis aplicando as regras comerciais da empresa, exibe o resumo detalhado
e gera um arquivo **CSV com a projeção dos 12 primeiros meses** do contrato.

Trabalho da disciplina *Algorithmic Thinking & Introduction to Object-Oriented Programming*.

## Requisitos

- Python **3.10 ou superior** (usa `list[...]` e `str | Path` nas anotações de tipo)
- Nenhuma biblioteca externa — apenas a biblioteca padrão (`decimal`, `csv`, `abc`, `dataclasses`)

## Como executar

```bash
git clone https://github.com/Yachmann/rentsmart.git
cd rentsmart
python main.py
```

O programa pergunta o tipo de imóvel, as opções de cada tipo e o número de parcelas
da taxa contratual. Ao final, mostra o orçamento e salva o CSV em `saida/projecao_AAAAMMDD_HHMMSS.csv`.

### Rodar os testes

```bash
python -m unittest -v
```

São 18 testes cobrindo todas as regras de preço, o parcelamento da taxa, a projeção,
o CSV e o fluxo da interface com entradas inválidas.

## Regras de negócio implementadas

| Item | Apartamento | Casa | Estúdio |
|---|---|---|---|
| Aluguel-base | R$ 700,00 | R$ 900,00 | R$ 1.200,00 |
| 2º quarto | + R$ 200,00 | + R$ 250,00 | não se aplica |
| Estacionamento | 1 vaga: + R$ 300,00 | 1 vaga: + R$ 300,00 | pacote de 2 vagas: R$ 250,00 + R$ 60,00 por vaga extra |
| Desconto | 5% se não tiver crianças | — | — |

**Taxa contratual:** R$ 2.000,00, cobrada à parte do aluguel, em 1 a 5 parcelas mensais.

### Decisões de interpretação

O enunciado deixa alguns pontos abertos. As escolhas adotadas foram:

1. **Base do desconto de 5%:** incide sobre o aluguel-base **mais todos os adicionais, inclusive a garagem**
   ("após a aplicação dos adicionais correspondentes"). Exemplo: apartamento com 2 quartos e garagem,
   sem crianças: (700 + 200 + 300) × 0,95 = **R$ 1.140,00**.
2. **Vagas do estúdio:** 0 vagas ou de 2 a 10 vagas. Uma vaga isolada não existe na tabela e é rejeitada.
   O limite de 10 é apenas uma validação de sanidade.
3. **Garagem de casa e apartamento:** sim ou não (no máximo uma vaga, conforme o enunciado).
4. **Parcelas da taxa:** as primeiras parcelas são truncadas em centavos e o resíduo vai para a última,
   para a soma fechar exatamente em R$ 2.000,00 (3x = 666,66 + 666,66 + 666,68).
   As parcelas são cobradas nos meses 1 a *n*.
5. **Valores monetários** são calculados com `Decimal`, não `float`, para não haver erro de centavos.

## Estrutura do projeto

```
rentsmart/
├── main.py                     # ponto de entrada
├── rentsmart/
│   ├── dinheiro.py             # arredondamento e formatação em R$
│   ├── imoveis.py              # Imovel (abstrata) → ImovelResidencial → Apartamento, Casa; Estudio
│   ├── taxa_contratual.py      # TaxaContratual (parcelamento)
│   ├── orcamento.py            # Orcamento (resumo e projeção de 12 meses)
│   ├── exportador_csv.py       # ExportadorCSV
│   └── interface.py            # InterfaceConsole (entradas e validação)
├── tests/test_regras.py        # testes automatizados
├── exemplos/                   # CSV de exemplo gerado pelo sistema
└── docs/                       # fluxograma e diagrama de classes
```

## Formato do CSV

Separador `;`, decimais com vírgula e codificação UTF-8 com BOM, para abrir direto no Excel em português.

```
mes;aluguel;parcela_taxa_contratual;total_mes;total_acumulado
1;1.140,00;666,66;1.806,66;1.806,66
...
12;1.140,00;0,00;1.140,00;15.680,00
```

## Links

- Repositório: https://github.com/Yachmann/rentsmart
- Vídeo pitch: _(link do YouTube — a ser adicionado)_
