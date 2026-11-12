"""Dashboard de vendas com interface grafica Tkinter."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from conexao import banco


# Coleção usada exclusivamente pelo Projeto 10.
vendas = banco['vendas_p10']
# O índice impede que o mesmo código de venda seja cadastrado duas vezes.
vendas.create_index('codigo', unique=True)


def adicionar(codigo, categoria, produto, quantidade, preco_centavos):
    """Insere uma venda apenas se o código ainda não existir."""
    vendas.update_one(
        {'codigo': codigo},
        {'$setOnInsert': {
            'codigo': codigo, 'categoria': categoria, 'produto': produto,
            'quantidade': quantidade, 'total_centavos': quantidade * preco_centavos,
            'data': datetime.now(timezone.utc)
        }},
        upsert=True
    )


def inserir_dados_demo():
    """Cadastra cinco vendas de exemplo de forma idempotente."""
    dados = [
        ('V001', 'Informática', 'Teclado', 2, 8990),
        ('V002', 'Informática', 'Mouse', 4, 4590),
        ('V003', 'Papelaria', 'Caderno', 5, 2490),
        ('V004', 'Papelaria', 'Caneta', 20, 350),
        ('V005', 'Informática', 'Monitor', 1, 89900),
    ]
    for venda in dados:
        adicionar(*venda)

    # Datas diferentes tornam o filtro por período demonstrável.
    # O update não cria registros nem altera os valores das vendas.
    datas_demo = {
        'V001': datetime(2026, 1, 15, tzinfo=timezone.utc),
        'V002': datetime(2026, 3, 20, tzinfo=timezone.utc),
        'V003': datetime(2026, 6, 10, tzinfo=timezone.utc),
        'V004': datetime(2026, 9, 5, tzinfo=timezone.utc),
        'V005': datetime(2026, 11, 12, tzinfo=timezone.utc),
    }
    for codigo, data in datas_demo.items():
        vendas.update_one({'codigo': codigo}, {'$set': {'data': data}})


def consultar(data_inicio, data_fim):
    """Consulta totais por categoria e os cinco produtos mais vendidos."""
    inicio = datetime.strptime(data_inicio, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    fim = datetime.strptime(data_fim, '%Y-%m-%d').replace(tzinfo=timezone.utc) + timedelta(days=1)
    if inicio >= fim:
        raise ValueError('A data inicial deve ser anterior à data final.')
    filtro = {'data': {'$gte': inicio, '$lt': fim}}
    # Pipeline 1: filtra o período, agrupa por categoria e soma os valores.
    categorias = list(vendas.aggregate([
        {'$match': filtro},
        {'$group': {'_id': '$categoria', 'faturamento': {'$sum': '$total_centavos'},
                    'unidades': {'$sum': '$quantidade'}}},
        {'$sort': {'faturamento': -1}}
    ]))
    # Pipeline 2: agrupa produtos pela quantidade e limita aos cinco primeiros.
    produtos = list(vendas.aggregate([
        {'$match': filtro},
        {'$group': {'_id': '$produto', 'unidades': {'$sum': '$quantidade'}}},
        {'$sort': {'unidades': -1}}, {'$limit': 5}
    ]))
    return categorias, produtos


def gerar_grafico(categorias):
    """Cria o gráfico de faturamento e salva um arquivo PNG."""
    destino = Path(__file__).with_name('grafico_vendas.png')
    plt.figure(figsize=(9, 5))
    plt.bar([d['_id'] for d in categorias], [d['faturamento'] / 100 for d in categorias])
    plt.ylabel('Faturamento (R$)')
    plt.title('Vendas por categoria')
    plt.tight_layout()
    plt.savefig(destino, dpi=150)
    plt.close()
    return destino


def gerar_pdf(categorias, produtos, data_inicio, data_fim):
    """Monta e salva o relatório PDF com tabelas e totais."""
    destino = Path(__file__).with_name('relatorio_vendas.pdf')
    doc = SimpleDocTemplate(str(destino), pagesize=A4)
    estilos = getSampleStyleSheet()
    conteudo = [Paragraph('RELATÓRIO DE VENDAS', estilos['Title']), Spacer(1, .5 * cm),
                 Paragraph(f'Período: {data_inicio} até {data_fim}', estilos['Normal']),
                 Spacer(1, .5 * cm), Paragraph('Vendas por categoria', estilos['Heading2'])]
    tabela = [['Categoria', 'Unidades', 'Faturamento']]
    tabela += [[str(x['_id']), str(x['unidades']), f"R$ {x['faturamento'] / 100:.2f}"] for x in categorias]
    if len(tabela) == 1:
        tabela.append(['Nenhuma venda encontrada', '-', '-'])
    tabela_obj = Table(tabela, colWidths=[7 * cm, 4 * cm, 5 * cm])
    tabela_obj.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                    ('ALIGN', (1, 1), (-1, -1), 'CENTER')]))
    conteudo.extend([tabela_obj, Spacer(1, .5 * cm), Paragraph('Cinco produtos mais vendidos', estilos['Heading2'])])
    tabela_produtos = [['Produto', 'Unidades']]
    tabela_produtos += [[str(x['_id']), str(x['unidades'])] for x in produtos]
    if len(tabela_produtos) == 1:
        tabela_produtos.append(['Nenhum produto encontrado', '-'])
    conteudo.append(Table(tabela_produtos, colWidths=[8 * cm, 8 * cm]))
    doc.build(conteudo)
    return destino


class Dashboard(tk.Tk):
    """Janela principal da aplicação feita com Tkinter."""
    def __init__(self):
        super().__init__()
        self.title('Projeto 10 • Dashboard de Vendas')
        self.geometry('820x620')
        self.resizable(False, False)
        self.configure(bg='#f4f7fb')
        self._montar_tela()

    def _montar_tela(self):
        # Define o tema visual, cores e estilos dos componentes da janela.
        estilo = ttk.Style(self)
        estilo.theme_use('clam')
        estilo.configure('Card.TFrame', background='white')
        estilo.configure('Title.TLabel', background='#173b67', foreground='white', font=('Segoe UI', 22, 'bold'))
        estilo.configure('Subtitle.TLabel', background='#173b67', foreground='#dbeafe', font=('Segoe UI', 10))
        estilo.configure('Field.TLabel', background='white', foreground='#334155', font=('Segoe UI', 10, 'bold'))
        estilo.configure('Accent.TButton', background='#2563eb', foreground='white', font=('Segoe UI', 10, 'bold'), padding=(18, 9))
        estilo.map('Accent.TButton', background=[('active', '#1d4ed8')])

        topo = tk.Frame(self, bg='#173b67', height=118)
        topo.pack(fill='x')
        ttk.Label(topo, text='Dashboard de Vendas', style='Title.TLabel').pack(anchor='w', padx=28, pady=(22, 2))
        ttk.Label(topo, text='Análise de vendas por categoria • MongoDB + Python', style='Subtitle.TLabel').pack(anchor='w', padx=30)

        frame = ttk.Frame(self, style='Card.TFrame', padding=20)
        frame.pack(fill='x', padx=28, pady=22)
        ttk.Label(frame, text='PERÍODO DA CONSULTA', style='Field.TLabel').grid(row=0, column=0, columnspan=4, sticky='w', pady=(0, 12))
        ttk.Label(frame, text='Data inicial', style='Field.TLabel').grid(row=1, column=0, padx=(0, 8), sticky='w')
        self.inicio = ttk.Entry(frame, width=16, font=('Segoe UI', 10))
        self.inicio.insert(0, datetime.now().strftime('%Y-%m-01'))
        self.inicio.grid(row=1, column=1, padx=(0, 20))
        ttk.Label(frame, text='Data final', style='Field.TLabel').grid(row=1, column=2, padx=(0, 8), sticky='w')
        self.fim = ttk.Entry(frame, width=16, font=('Segoe UI', 10))
        self.fim.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.fim.grid(row=1, column=3, padx=(0, 20))
        ttk.Button(frame, text='Gerar relatório', style='Accent.TButton', command=self.gerar).grid(row=1, column=4)

        resultado = ttk.Frame(self, style='Card.TFrame', padding=16)
        resultado.pack(fill='both', expand=True, padx=28, pady=(0, 22))
        ttk.Label(resultado, text='RESULTADO', style='Field.TLabel').pack(anchor='w', pady=(0, 8))
        self.saida = tk.Text(resultado, height=18, state='disabled', font=('Consolas', 10),
                             bg='#f8fafc', fg='#1e293b', relief='flat', padx=14, pady=12,
                             highlightthickness=1, highlightbackground='#dbe3ef')
        self.saida.pack(fill='both', expand=True)

    def gerar(self):
        """Executa a consulta e atualiza a área de resultados da tela."""
        try:
            # Os dados de demonstração não são duplicados graças ao índice/upsert.
            inserir_dados_demo()
            # Lê as datas da tela e executa as duas agregações no MongoDB.
            categorias, produtos = consultar(self.inicio.get().strip(), self.fim.get().strip())
            # Cada consulta também atualiza os arquivos de saída do projeto.
            grafico = gerar_grafico(categorias)
            pdf = gerar_pdf(categorias, produtos, self.inicio.get(), self.fim.get())
            total = sum(x['faturamento'] for x in categorias) / 100
            linhas = ['RELATÓRIO DE VENDAS POR CATEGORIA', '']
            linhas += [f"{x['_id']}: {x['unidades']} unidades | R$ {x['faturamento'] / 100:.2f}" for x in categorias]
            linhas += [f'\nFaturamento geral: R$ {total:.2f}', '', 'CINCO PRODUTOS MAIS VENDIDOS']
            linhas += [f"{x['_id']}: {x['unidades']} unidades" for x in produtos]
            linhas += [f'\nGráfico: {grafico}', f'PDF: {pdf}']
            # O campo é desbloqueado apenas durante a atualização do texto.
            self.saida.config(state='normal')
            self.saida.delete('1.0', tk.END)
            self.saida.insert(tk.END, '\n'.join(linhas) if linhas else 'Sem dados no período.')
            self.saida.config(state='disabled')
        except Exception as erro:
            # Exibe falhas de data, conexão ou geração dos arquivos em uma janela.
            messagebox.showerror('Erro', str(erro))


# Cria a janela e mantém a aplicação aberta aguardando eventos do usuário.
if __name__ == '__main__':
    Dashboard().mainloop()
