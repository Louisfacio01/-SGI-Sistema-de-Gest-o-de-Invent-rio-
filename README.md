# 📦 SGI - Sistema de Gestão de Inventário

Sistema web para controle e gestão de estoque de ativos de TI, desenvolvido com Python (Flask) e SQL Server.

## 🛠️ Tecnologias Utilizadas
* Linguagem: Python 3.x
* Framework Web: Flask
* Banco de Dados: SQL Server (SQLEXPRESS)
* Driver de Conexão: pyodbc (ODBC Driver 17 for SQL Server)
* Frontend: HTML5, CSS3 e Jinja2 (Motor de templates do Flask)

## 🚀 Passo a Passo Completo para Execução

Siga a ordem dos comandos abaixo para rodar o projeto do zero na sua máquina local.

### 1. Clonar o Repositório
Abra o terminal (Prompt de Comando, PowerShell ou Terminal do VS Code) e execute:
git clone https://github.com/Louisfacio01/-SGI-Sistema-de-Gest-o-de-Invent-rio-.git
cd -SGI-Sistema-de-Gest-o-de-Invent-rio-

### 2. Instalar as Dependências no Terminal
Rode os comandos abaixo no terminal para instalar as bibliotecas do Python necessárias (Flask e pyodbc):
pip install flask pyodbc
*(Nota: Certifique-se de que o seu computador possui o ODBC Driver 17 for SQL Server instalado).*

### 3. Configurar e Criar o Banco de Dados (SQL Server)
1. Abra o SQL Server Management Studio (SSMS) ou conecte-se via extensão SQL Server (mssql) no VS Code na sua instância local (.\SQLEXPRESS).
2. Abra uma nova janela de consulta (New Query).
3. Copie o script SQL completo abaixo, cole e clique em Executar (Execute):

CREATE DATABASE db_SGI;
GO

USE db_SGI;
GO

CREATE TABLE Categoria (
    id_categoria INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT
);
GO

CREATE TABLE Fornecedor (
    id_fornecedor INT IDENTITY(1,1) PRIMARY KEY,
    razao_social VARCHAR(150) NOT NULL,
    cnpj VARCHAR(20) NOT NULL UNIQUE,
    contato VARCHAR(50),
    telefone VARCHAR(20)
);
GO

CREATE TABLE Produto (
    id_produto INT IDENTITY(1,1) PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    nome_comercial VARCHAR(150) NOT NULL,
    fabricante VARCHAR(100) NOT NULL,
    classificacao VARCHAR(50) NOT NULL,
    especificacao_tecnica TEXT,
    modalidade_licenciamento VARCHAR(50),
    preco_venda DECIMAL(10,2) NOT NULL CHECK (preco_venda >= 0),
    quantidade_estoque INT NOT NULL CHECK (quantidade_estoque >= 0),
    ponto_reposicao INT NOT NULL CHECK (ponto_reposicao >= 0),
    localizacao VARCHAR(50) NOT NULL,
    id_categoria INT NOT NULL,
    id_fornecedor INT NOT NULL,
    CONSTRAINT FK_Produto_Categoria FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria),
    CONSTRAINT FK_Produto_Fornecedor FOREIGN KEY (id_fornecedor) REFERENCES Fornecedor(id_fornecedor)
);
GO

CREATE TABLE Movimentacao (
    id_movimentacao INT IDENTITY(1,1) PRIMARY KEY,
    id_produto INT NOT NULL,
    tipo_operacao VARCHAR(20) NOT NULL CHECK (tipo_operacao IN ('Entrada', 'Saída')),
    quantidade INT NOT NULL CHECK (quantidade > 0),
    data_hora DATETIME DEFAULT GETDATE(),
    justificativa TEXT NOT NULL,
    CONSTRAINT FK_Movimentacao_Produto FOREIGN KEY (id_produto) REFERENCES Produto(id_produto)
);
GO

INSERT INTO Categoria (nome, descricao) VALUES 
('Hardware', 'Componentes internos de computadores'),
('Periféricos', 'Acessórios e dispositivos externos'),
('Software', 'Licenças de sistemas operacionais e aplicativos');
GO

INSERT INTO Fornecedor (razao_social, cnpj, contato, telefone) VALUES 
('TechDistribuidora S.A.', '12.345.678/0001-99', 'Carlos Silva', '(11) 98888-7777'),
('Global Softwares Ltda', '98.765.432/0001-11', 'Ana Souza', '(11) 97777-6666');
GO

INSERT INTO Produto (sku, nome_comercial, fabricante, classificacao, especificacao_tecnica, modalidade_licenciamento, preco_venda, quantidade_estoque, ponto_reposicao, localizacao, id_categoria, id_fornecedor) VALUES 
('HW-SSD-1TB', 'SSD NVMe 1TB', 'Kingston', 'Hardware', 'Leitura 3500MB/s', 'N/A', 450.00, 2, 5, 'Cofre A1', 1, 1),
('SW-WIN-PRO', 'Windows 11 Pro', 'Microsoft', 'Software', 'Licença OEM 64-bits', 'Perpétua', 890.00, 15, 3, 'Digital', 3, 2);
GO

### 4. Iniciar a Aplicação
Com o banco de dados criado e os pacotes instalados, rode a aplicação no terminal:
python app.py

Abra o seu navegador e acesse: http://localhost:5000

## 📌 Rotas do Sistema
* / (GET): Lista todos os produtos cadastrados com junção de Categoria e Fornecedor (INNER JOIN).
* /produto/novo (GET/POST): Carrega formulário e cadastra novos ativos no estoque (INSERT INTO).
* /movimentacao (GET/POST): Controla entradas e saídas de produtos com validação de saldo disponível (UPDATE + INSERT).
* /produto/excluir-selecionado (POST): Exclui registros de movimentação e produto de forma segura (DELETE).
* /produto/excluir-pagina (GET/POST): Interface gráfica dedicada para remoção de produtos.