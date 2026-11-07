"""Projeto 10: agregacao de vendas e exportacao de grafico PNG."""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys

# Permite localizar o conexao.py na pasta principal
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from conexao import banco


# --------------------------------------------------
# COLECAO DE VENDAS
# --------------------------------------------------

vendas = banco['vendas_p10']
vendas.create_index('codigo', unique=True)


# --------------------------------------------------
# FUNCAO ORIGINAL PARA ADICIONAR VENDAS
# --------------------------------------------------

def adicionar(codigo, categoria, produto, quantidade, preco_centavos):
    vendas.update_one(
        {'codigo': codigo},
        {'$setOnInsert': {
            'codigo': codigo,
            'categoria': categoria,
            'produto': produto,
            'quantidade': quantidade,
            'total_centavos': quantidade * preco_centavos,
            'data': datetime.now(timezone.utc)
        }},
        upsert=True
    )


# --------------------------------------------------
# CINCO VENDAS DE DEMONSTRACAO
# --------------------------------------------------

# Executar novamente nao duplica estas vendas.

adicionar('V001', 'Informática', 'Teclado', 2, 8990)
adicionar('V002', 'Informática', 'Mouse', 4, 4590)
adicionar('V003', 'Papelaria', 'Caderno', 5, 2490)
adicionar('V004', 'Papelaria', 'Caneta', 20, 350)
adicionar('V005', 'Informática', 'Monitor', 1, 89900)


# --------------------------------------------------
# DESAFIO 1: FILTRAR VENDAS POR PERIODO
# --------------------------------------------------

print('\nFILTRO DE VENDAS POR PERIODO')

data_inicio = input('Digite a data inicial (AAAA-MM-DD): ')
data_fim = input('Digite a data final (AAAA-MM-DD): ')

inicio = datetime.strptime(
    data_inicio, '%Y-%m-%d'
).replace(tzinfo=timezone.utc)

fim = datetime.strptime(
    data_fim, '%Y-%m-%d'
).replace(tzinfo=timezone.utc) + timedelta(days=1)

if inicio >= fim:
    print('Periodo invalido.')
    raise SystemExit(0)

filtro = {
    'data': {
        '$gte': inicio,
        '$lt': fim
    }
}


# --------------------------------------------------
# PIPELINE ORIGINAL COM O FILTRO DE PERIODO
# --------------------------------------------------

pipeline = [
    {'$match': filtro},
    {'$group': {
        '_id': '$categoria',
        'faturamento': {'$sum': '$total_centavos'},
        'unidades': {'$sum': '$quantidade'}
    }},
    {'$sort': {'faturamento': -1}}
]

dados = list(vendas.aggregate(pipeline))

if not dados:
    print('Sem dados de vendas.')

print('RELATÓRIO DE VENDAS POR CATEGORIA')

for item in dados:
    print(
        f"{item['_id']}: {item['unidades']} unidades | "
        f"R$ {item['faturamento']/100:.2f}"
    )

print(
    f"Faturamento geral: "
    f"R$ {sum(i['faturamento'] for i in dados)/100:.2f}"
)


# --------------------------------------------------
# DESAFIO 2: CINCO PRODUTOS MAIS VENDIDOS
# --------------------------------------------------

pipeline_produtos = [
    {'$match': filtro},
    {'$group': {
        '_id': '$produto',
        'unidades': {'$sum': '$quantidade'}
    }},
    {'$sort': {'unidades': -1}},
    {'$limit': 5}
]

produtos = list(vendas.aggregate(pipeline_produtos))

print('\nCINCO PRODUTOS MAIS VENDIDOS')

for item in produtos:
    print(f"{item['_id']}: {item['unidades']} unidades")


# --------------------------------------------------
# GRAFICO ORIGINAL
# --------------------------------------------------

plt.figure(figsize=(9, 5))

plt.bar(
    [d['_id'] for d in dados],
    [d['faturamento']/100 for d in dados]
)

plt.ylabel('Faturamento (R$)')
plt.title('Vendas por categoria')
plt.tight_layout()

destino = Path(__file__).with_name('grafico_vendas.png')
plt.savefig(destino, dpi=150)
plt.close()

print(f'Gráfico gerado: {destino}')


# --------------------------------------------------
# DESAFIO 3: GERAR PDF DO RELATORIO
# --------------------------------------------------

arquivo_pdf = Path(__file__).with_name('relatorio_vendas.pdf')

documento = SimpleDocTemplate(
    str(arquivo_pdf),
    pagesize=A4
)

estilos = getSampleStyleSheet()
conteudo = []

# Titulo e periodo

conteudo.append(
    Paragraph('RELATORIO DE VENDAS', estilos['Title'])
)

conteudo.append(Spacer(1, 0.5 * cm))

conteudo.append(
    Paragraph(
        f'Periodo consultado: {data_inicio} ate {data_fim}',
        estilos['Normal']
    )
)

conteudo.append(Spacer(1, 0.5 * cm))


# Tabela de vendas por categoria

conteudo.append(
    Paragraph('Vendas por categoria', estilos['Heading2'])
)

tabela_categorias = [
    ['Categoria', 'Unidades', 'Faturamento']
]

for item in dados:
    tabela_categorias.append([
        str(item['_id']),
        str(item['unidades']),
        f"R$ {item['faturamento']/100:.2f}"
    ])

if not dados:
    tabela_categorias.append([
        'Nenhuma venda encontrada', '-', '-'
    ])

tabela = Table(
    tabela_categorias,
    colWidths=[7 * cm, 4 * cm, 5 * cm]
)

tabela.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ('PADDING', (0, 0), (-1, -1), 8)
]))

conteudo.append(tabela)

conteudo.append(Spacer(1, 0.5 * cm))


# Faturamento geral

faturamento_geral = sum(
    item['faturamento'] for item in dados
)

conteudo.append(
    Paragraph(
        f'<b>Faturamento geral: R$ {faturamento_geral/100:.2f}</b>',
        estilos['Normal']
    )
)

conteudo.append(Spacer(1, 0.7 * cm))


# Tabela dos cinco produtos mais vendidos

conteudo.append(
    Paragraph(
        'Cinco produtos mais vendidos',
        estilos['Heading2']
    )
)

tabela_produtos = [
    ['Produto', 'Unidades vendidas']
]

for item in produtos:
    tabela_produtos.append([
        str(item['_id']),
        str(item['unidades'])
    ])

if not produtos:
    tabela_produtos.append([
        'Nenhum produto encontrado', '-'
    ])

tabela2 = Table(
    tabela_produtos,
    colWidths=[8 * cm, 8 * cm]
)

tabela2.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ('PADDING', (0, 0), (-1, -1), 8)
]))

conteudo.append(tabela2)


# Criar o arquivo PDF

documento.build(conteudo)

print(f'\nPDF gerado: {arquivo_pdf}')

print('\nRelatorio finalizado com sucesso!')

#------------------------------------------
#PARA TEXTE!!!!!!
#Data inicial: 2026-01-01
#Data final: 2026-12-31
#------------------------------------------