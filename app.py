from flask import Flask, render_template, request, redirect, url_for, flash
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

@app.route("/")
def index():
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

@app.route("/produto/novo", methods=["GET", "POST"])
def novo_produto():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        sku = request.form["sku"].strip()
        nome_comercial = request.form["nome_comercial"].strip()
        fabricante = request.form["fabricante"].strip()
        especificacao_tecnica = request.form.get("especificacao_tecnica", "")
        modalidade_licenciamento = request.form.get("modalidade_licenciamento", "N/A")
        preco_venda = float(request.form["preco_venda"])
        quantidade_estoque = int(request.form["quantidade_estoque"])
        localizacao = request.form["localizacao"].strip()
        id_categoria = int(request.form["id_categoria"])
        id_fornecedor = int(request.form["id_fornecedor"])

        try:
            cursor.execute("""
                INSERT INTO Produto (sku, nome_comercial, fabricante, especificacao_tecnica,
                                     modalidade_licenciamento, preco_venda, quantidade_estoque,
                                     localizacao, id_categoria, id_fornecedor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sku, nome_comercial, fabricante, especificacao_tecnica,
                  modalidade_licenciamento, preco_venda, quantidade_estoque,
                  localizacao, id_categoria, id_fornecedor))
            conn.commit()
            flash("Ativo cadastrado com sucesso!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            conn.rollback()
            flash(f"Erro ao cadastrar ativo: {e}", "danger")
        finally:
            conn.close()

    cursor.execute("SELECT id_categoria, nome FROM Categoria ORDER BY nome")
    categorias = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_fornecedor, razao_social FROM Fornecedor ORDER BY razao_social")
    fornecedores = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    return render_template("form_produto.html", categorias=categorias, fornecedores=fornecedores)

@app.route('/movimentacao', methods=['GET', 'POST'])
def movimentacao():
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

if __name__ == '__main__':
    app.run(debug=True)