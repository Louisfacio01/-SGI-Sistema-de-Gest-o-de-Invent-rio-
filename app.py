from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyodbc

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
app.secret_key = "techstore_secret_key"

def get_db_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=.\\SQLEXPRESS;"
        "DATABASE=db_SGI;"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)

# ---------------------------------------------------------
# ROTAS DE AUTENTICAÇÃO E RBAC
# ---------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nome_completo, perfil_acesso, senha_hash FROM Usuarios WHERE email = ? AND status = 'ATIVO'", (email,))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario and usuario[3] == senha: # Comparação acadêmica simples
            session["usuario_id"] = usuario[0]
            session["nome"] = usuario[1]
            session["perfil"] = usuario[2]
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("index"))
        else:
            flash("E-mail ou senha incorretos.", "danger")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada com sucesso.", "success")
    return redirect(url_for("login"))

# ---------------------------------------------------------
# ROTA PRINCIPAL (CATÁLOGO)
# ---------------------------------------------------------
@app.route("/")
def index():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            p.id_produto, p.sku, p.nome_comercial, p.fabricante,
            c.nome AS categoria, f.razao_social AS fornecedor,
            p.preco_venda, p.quantidade_estoque,
            p.localizacao, p.modalidade_licenciamento
        FROM Produto p
        INNER JOIN Categoria c ON p.id_categoria = c.id_categoria
        INNER JOIN Fornecedor f ON p.id_fornecedor = f.id_fornecedor
        ORDER BY p.id_produto DESC
    """
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    produtos = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return render_template("index.html", produtos=produtos)

# ---------------------------------------------------------
# CADASTRAR NOVO PRODUTO
# ---------------------------------------------------------
@app.route("/produto/novo", methods=["GET", "POST"])
def novo_produto():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        try:
            sku = request.form["sku"].strip()
            nome_comercial = request.form["nome_comercial"].strip()
            fabricante = request.form["fabricante"].strip()
            classificacao = request.form["classificacao"]
            especificacao_tecnica = request.form.get("especificacao_tecnica", "")
            modalidade_licenciamento = request.form.get("modalidade_licenciamento", "N/A")
            preco_venda = float(request.form["preco_venda"])
            quantidade_estoque = int(request.form["quantidade_estoque"])
            localizacao = request.form["localizacao"].strip()
            id_categoria = int(request.form["id_categoria"])
            id_fornecedor = int(request.form["id_fornecedor"])

            cursor.execute("""
                INSERT INTO Produto (sku, nome_comercial, fabricante, classificacao, especificacao_tecnica,
                                     modalidade_licenciamento, preco_venda, quantidade_estoque,
                                     localizacao, id_categoria, id_fornecedor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sku, nome_comercial, fabricante, classificacao, especificacao_tecnica,
                  modalidade_licenciamento, preco_venda, quantidade_estoque,
                  localizacao, id_categoria, id_fornecedor))
            
            conn.commit()
            flash("Ativo cadastrado com sucesso!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            conn.rollback()
            flash(f"Erro ao inserir no SQL Server: {e}", "danger")
            return redirect(url_for("novo_produto"))
        finally:
            conn.close()

    cursor.execute("SELECT id_categoria, nome FROM Categoria ORDER BY nome")
    categorias = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_fornecedor, razao_social FROM Fornecedor ORDER BY razao_social")
    fornecedores = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    return render_template("form_produto.html", categorias=categorias, fornecedores=fornecedores)

# ---------------------------------------------------------
# MOVIMENTAÇÃO DE ESTOQUE
# ---------------------------------------------------------
@app.route('/movimentacao', methods=['GET', 'POST'])
def movimentacao():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        id_produto = int(request.form["id_produto"])
        tipo_operacao = request.form["tipo_operacao"]
        quantidade = int(request.form["quantidade"])
        justificativa = request.form["justificativa"].strip()

        cursor.execute("SELECT quantidade_estoque FROM Produto WHERE id_produto = ?", (id_produto,))
        row = cursor.fetchone()
        
        if not row:
            flash("Produto não encontrado.", "danger")
            conn.close()
            return redirect(url_for("movimentacao"))

        saldo_atual = row[0]

        if tipo_operacao == "Saída" and quantidade > saldo_atual:
            flash(f"Operação Bloqueada: Saldo insuficiente. Disponível: {saldo_atual} unidades.", "danger")
            conn.close()
            return redirect(url_for("movimentacao"))

        novo_saldo = saldo_atual + quantidade if tipo_operacao == "Entrada" else saldo_atual - quantidade

        try:
            cursor.execute("UPDATE Produto SET quantidade_estoque = ? WHERE id_produto = ?", (novo_saldo, id_produto))
            cursor.execute("""
                INSERT INTO Movimentacao (id_produto, tipo_operacao, quantidade, justificativa)
                VALUES (?, ?, ?, ?)
            """, (id_produto, tipo_operacao, quantidade, justificativa))
            conn.commit()
            flash("Movimentação consolidada com sucesso!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            conn.rollback()
            flash(f"Erro ao processar movimentação: {e}", "danger")
        finally:
            conn.close()

    cursor.execute("SELECT id_produto, sku, nome_comercial, quantidade_estoque FROM Produto ORDER BY nome_comercial")
    produtos = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return render_template("form_movimentacao.html", produtos=produtos)

# ---------------------------------------------------------
# CHECKOUT TRANSACIONAL (GARANTIA ACID)
# ---------------------------------------------------------
@app.route("/venda/checkout", methods=["GET", "POST"])
def checkout():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == "POST":
        cliente_nome = request.form["cliente_nome"]
        cliente_documento = request.form["cliente_documento"]
        forma_pagamento = request.form["forma_pagamento"]
        produto_id = int(request.form["produto_id"])
        quantidade = int(request.form["quantidade"])
        usuario_id = session["usuario_id"]
        
        try:
            cursor.execute("BEGIN TRANSACTION;")
            
            cursor.execute("SELECT quantidade_estoque, preco_venda FROM Produto WHERE id_produto = ?", (produto_id,))
            prod = cursor.fetchone()
            
            if not prod or prod[0] < quantidade:
                raise Exception("Estoque insuficiente para concluir a venda!")
                
            estoque_atual = prod[0]
            preco_unitario = prod[1]
            subtotal = preco_unitario * quantidade
            
            numero_pedido = f"PED-2026-{abs(hash(cliente_documento)) % 10000:04d}"
            
            # Usando OUTPUT INSERTED para capturar o ID de forma 100% garantida
            cursor.execute("""
                INSERT INTO Vendas (numero_pedido, cliente_nome, cliente_documento, forma_pagamento, valor_total, status_venda, usuario_id)
                OUTPUT INSERTED.id_venda
                VALUES (?, ?, ?, ?, ?, 'CONCLUIDA', ?)
            """, (numero_pedido, cliente_nome, cliente_documento, forma_pagamento, subtotal, usuario_id))
            
            row_id = cursor.fetchone()
            if row_id and row_id[0] is not None:
                venda_id = int(row_id[0])
            else:
                raise Exception("Não foi possível recuperar o ID da venda gerada.")
            
            cursor.execute("""
                INSERT INTO Itens_Venda (venda_id, produto_id, quantidade_vendida, preco_unitario_praticado, subtotal_item)
                VALUES (?, ?, ?, ?, ?)
            """, (venda_id, produto_id, quantidade, preco_unitario, subtotal))
            
            novo_estoque = estoque_atual - quantidade
            cursor.execute("UPDATE Produto SET quantidade_estoque = ? WHERE id_produto = ?", (novo_estoque, produto_id))
            
            cursor.execute("""
                INSERT INTO Movimentacao (id_produto, tipo_operacao, quantidade, justificativa)
                VALUES (?, 'Saída', ?, ?)
            """, (produto_id, quantidade, f"Venda faturada - Pedido {numero_pedido}"))
            
            conn.commit()
            flash(f"Venda {numero_pedido} realizada com sucesso!", "success")
            return redirect(url_for("recibo", venda_id=venda_id))
            
        except Exception as e:
            conn.rollback()
            flash(f"Erro na transação (Operação Abortada): {str(e)}", "danger")
            return redirect(url_for("checkout"))
            
        finally:
            conn.close()
            
    cursor.execute("SELECT id_produto, nome_comercial, preco_venda, quantidade_estoque FROM Produto WHERE quantidade_estoque > 0")
    produtos = cursor.fetchall()
    conn.close()
    
    return render_template("checkout.html", produtos=produtos)

# ---------------------------------------------------------
# TELA DE RECIBO / COMPROVANTE
# ---------------------------------------------------------
@app.route("/venda/recibo/<int:venda_id>")
def recibo(venda_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT v.id_venda, v.numero_pedido, v.data_hora, v.cliente_nome, v.cliente_documento, 
               v.forma_pagamento, v.valor_total, u.nome_completo AS operador
        FROM Vendas v
        INNER JOIN Usuarios u ON v.usuario_id = u.id_usuario
        WHERE v.id_venda = ?
    """, (venda_id,))
    venda = cursor.fetchone()
    
    # Proteção vital: se a venda não existir, avisa e volta ao início em vez de crashar
    if not venda:
        conn.close()
        flash("Comprovante não encontrado. Faça uma nova venda para gerar o recibo.", "danger")
        return redirect(url_for("index"))
    
    cursor.execute("""
        SELECT p.nome_comercial, i.quantidade_vendida, i.preco_unitario_praticado, i.subtotal_item
        FROM Itens_Venda i
        INNER JOIN Produto p ON i.produto_id = p.id_produto
        WHERE i.venda_id = ?
    """, (venda_id,))
    itens = cursor.fetchall()
    
    conn.close()
    return render_template("recibo.html", venda=venda, itens=itens)

# ---------------------------------------------------------
# EXCLUSÃO DE ATIVO (COM SEGURANÇA RBAC E INTEGRIDADE)
# ---------------------------------------------------------
@app.route('/produto/excluir-selecionado', methods=['POST'])
def excluir_selecionado():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
        
    if session.get('perfil') != 'GERENTE':
        flash("Acesso negado. Apenas gerentes podem excluir ativos.", "danger")
        return redirect(url_for('index'))
        
    id_produto = request.form.get("id_produto")
    if not id_produto:
        flash("Nenhum produto selecionado.", "danger")
        return redirect(url_for('index'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION;")
        # Apaga os vínculos nas tabelas filhas para respeitar a chave estrangeira
        cursor.execute("DELETE FROM Itens_Venda WHERE produto_id = ?", (id_produto,))
        cursor.execute("DELETE FROM Movimentacao WHERE id_produto = ?", (id_produto,))
        # Apaga o produto
        cursor.execute("DELETE FROM Produto WHERE id_produto = ?", (id_produto,))
        conn.commit()
        flash("Ativo e seus registros vinculados foram excluídos com sucesso!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Erro ao excluir ativo: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)