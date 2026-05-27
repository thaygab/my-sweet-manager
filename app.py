from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Produto, Pedido

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vendas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'segredo-simples'

db.init_app(app)

with app.app_context():
    db.create_all()


# =========================
# PAINEL
# =========================
@app.route('/')
def index():

    produtos = Produto.query.all()
    pedidos = Pedido.query.all()

    total_produtos = len(produtos)
    total_pedidos = len(pedidos)

    total_vendido = sum(
        p.preco_venda * p.quantidade
        for p in pedidos
    )

    total_lucro = sum(
        (p.preco_venda - p.preco_custo) * p.quantidade
        for p in pedidos
    )

    estoque_baixo = len([
        p for p in produtos
        if p.estoque <= 5
    ])

    return render_template(
        'index.html',
        total_produtos=total_produtos,
        total_pedidos=total_pedidos,
        total_vendido=total_vendido,
        total_lucro=total_lucro,
        estoque_baixo=estoque_baixo
    )


# =========================
# LISTAR PRODUTOS + BUSCA
# =========================
@app.route('/produtos')
def listar_produtos():

    busca = request.args.get('busca')

    if busca:

        produtos = Produto.query.filter(
            Produto.nome.contains(busca)
        ).all()

    else:

        produtos = Produto.query.all()

    return render_template(
        'produtos.html',
        produtos=produtos,
        busca=busca
    )


# =========================
# NOVO PRODUTO
# =========================
@app.route('/produtos/novo', methods=['GET', 'POST'])
def novo_produto():

    if request.method == 'POST':

        nome = request.form['nome']
        preco_custo = float(request.form['preco_custo'])
        preco_venda = float(request.form['preco_venda'])
        estoque = int(request.form['estoque'])

        produto = Produto(
            nome=nome,
            preco_custo=preco_custo,
            preco_venda=preco_venda,
            estoque=estoque
        )

        db.session.add(produto)
        db.session.commit()

        flash('Produto cadastrado com sucesso!')

        return redirect(
            url_for('listar_produtos')
        )

    return render_template('novo_produto.html')


# =========================
# EDITAR PRODUTO
# =========================
@app.route('/produtos/editar/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):

    produto = Produto.query.get_or_404(id)

    if request.method == 'POST':

        produto.nome = request.form['nome']
        produto.preco_custo = float(
            request.form['preco_custo']
        )

        produto.preco_venda = float(
            request.form['preco_venda']
        )

        produto.estoque = int(
            request.form['estoque']
        )

        db.session.commit()

        flash('Produto atualizado com sucesso!')

        return redirect(
            url_for('listar_produtos')
        )

    return render_template(
        'editar_produto.html',
        produto=produto
    )


# =========================
# EXCLUIR PRODUTO
# =========================
@app.route('/produtos/excluir/<int:id>', methods=['POST'])
def excluir_produto(id):

    produto = Produto.query.get_or_404(id)

    db.session.delete(produto)
    db.session.commit()

    flash('Produto excluído com sucesso!')

    return redirect(
        url_for('listar_produtos')
    )


# =========================
# LISTAR PEDIDOS
# =========================
@app.route('/pedidos')
def listar_pedidos():

    pedidos = Pedido.query.all()

    total_vendido = sum(
        p.preco_venda * p.quantidade
        for p in pedidos
    )

    total_lucro = sum(
        (p.preco_venda - p.preco_custo) * p.quantidade
        for p in pedidos
    )

    return render_template(
        'pedidos.html',
        pedidos=pedidos,
        total_vendido=total_vendido,
        total_lucro=total_lucro
    )


# =========================
# NOVO PEDIDO
# =========================
@app.route('/pedidos/novo', methods=['GET', 'POST'])
def novo_pedido():

    produtos = Produto.query.all()

    if request.method == 'POST':

        produto_id = int(
            request.form['produto_id']
        )

        quantidade = int(
            request.form['quantidade']
        )

        produto = Produto.query.get(produto_id)

        if not produto:

            flash('Produto não encontrado.')

            return redirect(
                url_for('novo_pedido')
            )

        if quantidade <= 0:

            flash('A quantidade deve ser maior que zero.')

            return redirect(
                url_for('novo_pedido')
            )

        if quantidade > produto.estoque:

            flash('Estoque insuficiente para essa venda.')

            return redirect(
                url_for('novo_pedido')
            )

        pedido = Pedido(
            produto_nome=produto.nome,
            quantidade=quantidade,
            preco_custo=produto.preco_custo,
            preco_venda=produto.preco_venda
        )

        produto.estoque -= quantidade

        db.session.add(pedido)
        db.session.commit()

        flash('Venda registrada com sucesso!')

        return redirect(
            url_for('listar_pedidos')
        )

    return render_template(
        'novo_pedido.html',
        produtos=produtos
    )


# =========================
# RODAR APP
# =========================
if __name__ == '__main__':
    app.run()