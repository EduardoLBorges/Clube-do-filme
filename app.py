import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import db

app = Flask(__name__)
app.secret_key = 'chave_secreta_segura'

# Rora de manutenção
@app.route('/manutencao')
def manutencao():
    return render_template('manutencao.html')

# Rota para lista de filmes
@app.route('/', endpoint='home')
def home():
    genero_da_semana = db.get_genero_da_semana()
    filmes_genero = db.get_filmes_por_genero(genero_da_semana)
    filmes_animacao = db.get_filmes_por_categoria('Animação')
    filmes_terror = db.get_filmes_por_categoria('Terror')
    filmes_aventura = db.get_filmes_por_categoria('Aventura')
    filmes_drama = db.get_filmes_por_categoria('Drama')
    filmes_scifi = db.get_filmes_por_categoria('Ficção Científica')

    return render_template('home.html',
                           filmes_animacao=filmes_animacao,
                           filmes_terror=filmes_terror,
                           filmes_aventura=filmes_aventura,
                           filmes_drama=filmes_drama,
                           filmes_scifi=filmes_scifi,
                           filmes_genero=filmes_genero,
                           genero_da_semana=genero_da_semana)

# Rota para lista real
@app.route('/real')
def real():
    filme_id = db.get_filme_da_semana_id()
    filme = db.get_filme_por_id(filme_id)
    filmes = db.get_filmes_real()
    return render_template('real.html', filmes=filmes, filme=filme)

# Rota da pagina de configurações
@app.route('/config', methods=['GET', 'POST'])
def config():
    if not session.get('autenticado'):
        if request.method == 'POST' and 'senha' in request.form:
            senha_digitada = request.form['senha']
            senha_correta = db.get_senha_config()

            if senha_digitada == senha_correta:
                session['autenticado'] = True
                return redirect(url_for('config'))
            else:
                flash("Senha incorreta.", "erro")

        return render_template('login_config.html')

    if request.method == 'POST':
        if 'titulo' in request.form and 'imagem_url' in request.form:
            titulo = request.form['titulo']
            imagem_url = request.form['imagem_url']
            db.inserir_filme(titulo, imagem_url)

        if 'filme_da_semana_id' in request.form:
            novo_id = int(request.form['filme_da_semana_id'])
            db.update_filme_da_semana(novo_id)

    filmes = db.get_todos_filmes_ordenados()
    filme_atual = db.get_filme_atual_id()
    return render_template('config.html', filmes=filmes, filme_atual=filme_atual)

@app.route('/avaliar/<int:filme_id>', methods=['GET', 'POST'])
def avaliar(filme_id):
    filme = db.get_dados_filme(filme_id)
    erro = None
    dados = {}

    if request.method == 'POST':
        campos = ['nome', 'roteiro', 'atuacao', 'direcao', 'fotografia', 'trilha', 'montagem', 'impacto', 'critica', 'total']
        try:
            for campo in campos:
                valor = request.form.get(campo, "").strip()
                if not valor:
                    raise ValueError(f"Campo '{campo}' obrigatório.")
                dados[campo] = valor

            for campo in ['roteiro', 'atuacao', 'direcao', 'fotografia', 'trilha', 'montagem', 'impacto']:
                dados[campo] = int(dados[campo])
                if dados[campo] < 1 or dados[campo] > 5:
                    raise ValueError(f"A nota de {campo} deve ser entre 1 e 5.")

            dados['total'] = int(dados['total'])
            if dados['total'] < 1 or dados['total'] > 10:
                raise ValueError("A nota total deve ser entre 1 e 10.")

            db.inserir_avaliacao(dados, filme_id)
            return redirect(url_for('avaliacoes', filme_id=filme_id))

        except Exception as e:
            erro = str(e)

    return render_template('avaliar.html', filme=filme, filme_id=filme_id, erro=erro, dados=dados)

# Rota da pagina de avaliações
@app.route('/avaliacoes/<int:filme_id>')
def avaliacoes(filme_id):
    filme = db.get_dados_filme(filme_id)
    avaliacoes = db.get_avaliacoes_por_filme(filme_id)
    return render_template('avaliacoes.html', filme=filme, avaliacoes=avaliacoes, filme_id=filme_id)

# Rota para o botão de excluir avaliação
@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    db.excluir_avaliacao(id)
    return redirect(request.referrer or '/')

# Rota da pagina de apresentação
@app.route('/apresentacao/<int:filme_id>')
def apresentacao(filme_id):
    filme = db.get_dados_apresentacao_filme(filme_id)
    avaliacoes = db.get_avaliacoes_por_filme_ordenado_por_nome(filme_id)
    genero = filme[3]
    filmes_genero = db.get_filmes_por_genero_ordenado_por_ordem(genero)
    return render_template('apresentacao.html', filme=filme, avaliacoes=avaliacoes, filme_id=filme_id, filmes_genero=filmes_genero)

# Iniciar aplicação
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
