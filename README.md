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

-- 2. Criação do Banco de Dados
CREATE DATABASE db_SGI;
GO

USE db_SGI;
GO

-- 3. Tabelas Base (Parte 1)
CREATE TABLE Categoria (
    id_categoria INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);
GO

CREATE TABLE Fornecedor (
    id_fornecedor INT IDENTITY(1,1) PRIMARY KEY,
    razao_social VARCHAR(150) NOT NULL,
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL
);
GO

CREATE TABLE Produto (
    id_produto INT IDENTITY(1,1) PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    nome_comercial VARCHAR(150) NOT NULL,
    fabricante VARCHAR(100) NOT NULL,
    classificacao VARCHAR(20) NOT NULL CHECK(classificacao IN ('Hardware', 'Software', 'Periférico')),
    especificacao_tecnica VARCHAR(MAX),
    modalidade_licenciamento VARCHAR(50) DEFAULT 'N/A',
    preco_venda DECIMAL(10,2) NOT NULL CHECK(preco_venda > 0),
    quantidade_estoque INT NOT NULL DEFAULT 0 CHECK(quantidade_estoque >= 0),
    ponto_reposicao INT NOT NULL DEFAULT 5 CHECK(ponto_reposicao >= 0),
    localizacao VARCHAR(100) NOT NULL,
    id_categoria INT NOT NULL,
    id_fornecedor INT NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria),
    FOREIGN KEY (id_fornecedor) REFERENCES Fornecedor(id_fornecedor)
);
GO

CREATE TABLE Movimentacao (
    id_movimentacao INT IDENTITY(1,1) PRIMARY KEY,
    id_produto INT NOT NULL,
    tipo_operacao VARCHAR(10) NOT NULL CHECK(tipo_operacao IN ('Entrada', 'Saída')),
    quantidade INT NOT NULL CHECK(quantidade > 0),
    data_hora DATETIME DEFAULT GETDATE(),
    justificativa VARCHAR(MAX) NOT NULL,
    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto)
);
GO

-- 4. Tabelas Novas (Parte 2 - Vendas e Usuários)
CREATE TABLE Usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    nome_completo VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    perfil_acesso VARCHAR(20) NOT NULL CHECK (perfil_acesso IN ('OPERADOR', 'GERENTE')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('ATIVO', 'INATIVO')) DEFAULT 'ATIVO',
    data_criacao DATETIME DEFAULT GETDATE()
);
GO

CREATE TABLE Vendas (
    id_venda INT IDENTITY(1,1) PRIMARY KEY,
    numero_pedido VARCHAR(50) NOT NULL UNIQUE,
    data_hora DATETIME DEFAULT GETDATE(),
    cliente_nome VARCHAR(150) NOT NULL,
    cliente_documento VARCHAR(20) NOT NULL,
    forma_pagamento VARCHAR(30) NOT NULL CHECK (forma_pagamento IN ('PIX', 'CARTAO_CREDITO', 'BOLETO_FATURADO')),
    valor_total DECIMAL(10,2) NOT NULL CHECK (valor_total >= 0),
    status_venda VARCHAR(20) NOT NULL CHECK (status_venda IN ('CONCLUIDA', 'CANCELADA')) DEFAULT 'CONCLUIDA',
    usuario_id INT NOT NULL,
    CONSTRAINT FK_Venda_Usuario FOREIGN KEY (usuario_id) REFERENCES Usuarios(id_usuario)
);
GO

CREATE TABLE Itens_Venda (
    id_item INT IDENTITY(1,1) PRIMARY KEY,
    venda_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade_vendida INT NOT NULL CHECK (quantidade_vendida > 0),
    preco_unitario_praticado DECIMAL(10,2) NOT NULL CHECK (preco_unitario_praticado > 0),
    subtotal_item DECIMAL(10,2) NOT NULL CHECK (subtotal_item > 0),
    CONSTRAINT FK_Item_Venda FOREIGN KEY (venda_id) REFERENCES Vendas(id_venda),
    CONSTRAINT FK_Item_Produto FOREIGN KEY (produto_id) REFERENCES Produto(id_produto)
);
GO

-- 5. Cargas Iniciais (DML)
INSERT INTO Categoria (nome) VALUES 
('Processamento'), ('Armazenamento'), ('Suítes de Escritório'), ('Sistemas Operacionais');
GO

INSERT INTO Fornecedor (razao_social, cnpj, telefone, email) VALUES 
('Distribuidora Tech Brasil Ltda', '12.345.678/0001-90', '(11) 3000-1000', 'contato@techbrasil.com.br'),
('Global Software Licensing Inc', '98.765.432/0001-10', '(21) 2555-4000', 'vendas@globalsoftware.com'),
('Hardware Central Distribuição', '45.678.901/0001-23', '(31) 3222-8000', 'comercial@hardwarecentral.com');
GO

INSERT INTO Produto (sku, nome_comercial, fabricante, classificacao, especificacao_tecnica, modalidade_licenciamento, preco_venda, quantidade_estoque, ponto_reposicao, localizacao, id_categoria, id_fornecedor) VALUES 
('HW-PROC-I7', 'Processador Intel Core i7-13700K', 'Intel', 'Hardware', '16 Núcleos / 24 Threads / 3.4GHz', 'N/A', 2499.90, 8, 3, 'Bancada A-01', 1, 1),
('HW-SSD-1TB', 'SSD NVMe 1TB Kingston NV2', 'Kingston', 'Hardware', 'Leitura 3500MB/s / Gravação 2100MB/s', 'N/A', 450.00, 2, 5, 'Prateleira B-03', 2, 3),
('HW-SSD-500', 'SSD SATA III 500GB Crucial', 'Crucial', 'Hardware', 'Leitura 540MB/s / Gravação 500MB/s', 'N/A', 280.00, 15, 4, 'Prateleira B-04', 2, 3),
('SW-M365-BUS', 'Microsoft 365 Business Standard', 'Microsoft', 'Software', 'Licença para 1 usuário / Pacote Office', 'Assinatura Anual', 750.00, 20, 5, 'Cofre Digital - Servidor 01', 3, 2),
('SW-WIN-11PRO', 'Windows 11 Pro ESD', 'Microsoft', 'Software', 'Licença digital perpétua OEM/ESD', 'Perpétua/ESD', 990.00, 3, 4, 'Cofre Digital - Servidor 01', 4, 2),
('PER-KBD-MECH', 'Teclado Mecânico USB Redragon', 'Redragon', 'Periférico', 'Switch Blue / RGB / ABNT2', 'N/A', 220.00, 12, 3, 'Prateleira C-02', 1, 1);
GO

INSERT INTO Usuarios (nome_completo, email, senha_hash, perfil_acesso, status) VALUES 
('Carlos Operador', ' ', '123456', 'OPERADOR', 'ATIVO'),
('Ana Gerente', 'gerente@techstore.com', '123456', 'GERENTE', 'ATIVO');
GO

INSERT INTO Vendas (numero_pedido, cliente_nome, cliente_documento, forma_pagamento, valor_total, status_venda, usuario_id) VALUES 
('PED-2026-0001', 'Empresa Cliente Exemplo S.A.', '12.345.678/0001-01', 'PIX', 900.00, 'CONCLUIDA', 1);
GO

INSERT INTO Itens_Venda (venda_id, produto_id, quantidade_vendida, preco_unitario_praticado, subtotal_item) VALUES 
(1, 2, 2, 450.00, 900.00);
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