# 📊 Projeto 10 — Dashboard de Vendas

Projeto desenvolvido em Python com integração ao MongoDB, utilizando **Aggregation Pipeline** para processar dados de vendas por categoria e Matplotlib para gerar gráficos automaticamente.

## 🎯 Objetivo

Desenvolver um dashboard de vendas capaz de inserir dados de demonstração no banco de dados, agrupar informações por categoria, calcular faturamento e quantidade de produtos vendidos e exportar os resultados em um gráfico PNG.

O projeto também utiliza operações idempotentes, garantindo que a execução repetida não gere registros duplicados.

## 🛠️ Tecnologias utilizadas

- **Python** — Linguagem de programação.
- **MongoDB** — Armazenamento dos dados.
- **PyMongo** — Integração entre Python e MongoDB.
- **Matplotlib** — Criação e exportação de gráficos.
- **Pathlib** — Manipulação de caminhos de arquivos.

## 📚 Conceitos aplicados

- `$group` — Agrupamento das vendas por categoria.
- `$sum` — Cálculo do faturamento e das unidades vendidas.
- `$sort` — Ordenação das categorias pelo faturamento.
- `upsert` — Inserção de registros caso ainda não existam.
- `$setOnInsert` — Preenchimento dos dados somente na criação do registro.
- `create_index` — Criação de índice único para evitar duplicações.
- `matplotlib` — Geração de gráficos em Python.

## 📂 Estrutura do projeto

```text
projeto/
│
├── conexao.py
│
├── __init__.py
├── main.py
└── grafico_vendas.png
```

## ⚙️ Funcionamento

O projeto realiza as seguintes operações:

1. Conecta ao banco de dados MongoDB.
2. Cria um índice único para o campo `codigo`.
3. Insere cinco vendas de exemplo.
4. Utiliza `upsert` para impedir a duplicação dos registros.
5. Executa uma Aggregation Pipeline para agrupar as vendas por categoria.
6. Calcula o faturamento e a quantidade de unidades vendidas.
7. Exibe um relatório no terminal.
8. Gera um gráfico de barras e salva o resultado em PNG.

## ▶️ Como executar

Instale as dependências necessárias:

```bash
python -m pip install -r requirements.txt
```

Execute o projeto a partir da raiz do repositório:

```bash
python -m p10_dashboard.main
```

**Importante:** É necessário ter o MongoDB configurado e o arquivo `conexao.py` preparado para estabelecer a conexão com o banco de dados.

## 📈 Resultado esperado

O programa apresenta um relatório de vendas por categoria, contendo:

- Nome da categoria.
- Quantidade de unidades vendidas.
- Faturamento de cada categoria.
- Faturamento geral.

Além disso, gera automaticamente o arquivo:

`p10_dashboard/grafico_vendas.png`

O gráfico apresenta barras representando o faturamento de cada categoria.

## 🧪 Teste de idempotência

Uma das características principais do projeto é a idempotência.

Ao executar o programa várias vezes, as cinco vendas de demonstração não são duplicadas, pois cada registro possui um código único e utiliza a operação `upsert`.

## 🚀 Desafios extras

- [ ] Filtrar vendas por período.
- [ ] Exibir os cinco produtos mais vendidos.
- [ ] Gerar um relatório em PDF.

## 🗄️ Conferência no MongoDB Compass

Para verificar os dados armazenados:

1. Abra o MongoDB Compass.
2. Acesse o banco de dados `laboratorio_python`.
3. Localize a coleção `vendas_p10`.
4. Confira os cinco registros inseridos.
5. Execute o programa novamente e verifique se não houve duplicação.

---

**Projeto 10 — Dashboard de Vendas**

Desenvolvido como parte de um laboratório de estudos em Python e MongoDB, com foco em agregação de dados, persistência e visualização de informações.
