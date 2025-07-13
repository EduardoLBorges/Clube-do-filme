import psycopg2
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'chave_secreta_segura' 


def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "clube_filmes"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "senha"),
        port=os.environ.get("DB_PORT", "5432")
    )

@app.route('/')
def home():
    conn = get_connection()
    cur = conn.cursor()

    # Busca o ID do filme da semana a partir da tabela config
    cur.execute("SELECT filme_da_semana_id FROM config LIMIT 1")
    resultado = cur.fetchone()
    filme_id = resultado[0] if resultado else 1  # fallback para 1 caso não haja resultado

    # Busca os dados do filme da semana
    cur.execute("SELECT id, titulo, imagem_url FROM filmes WHERE id = %s", (filme_id,))
    filme = cur.fetchone()

    # Busca a lista de todos os filmes
    cur.execute("SELECT id, titulo, imagem_url FROM filmes")
    filmes = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('home.html', filmes=filmes, filme=filme)

@app.route('/config', methods=['GET', 'POST'])
def config():
    conn = get_connection()
    cur = conn.cursor()

    # Verifica se usuário já está autenticado
    if not session.get('autenticado'):
        if request.method == 'POST' and 'senha' in request.form:
            senha_digitada = request.form['senha']
            cur.execute("SELECT senha_config FROM config LIMIT 1")
            resultado = cur.fetchone()
            senha_correta = resultado[0] if resultado else None

            if senha_digitada == senha_correta:
                session['autenticado'] = True
                return redirect(url_for('config'))
            else:
                flash("Senha incorreta.", "erro")

        cur.close()
        conn.close()
        return render_template('login_config.html')

    # Processa formulários após login
    if request.method == 'POST':
        # Inserir novo filme
        if 'titulo' in request.form and 'imagem_url' in request.form:
            titulo = request.form['titulo']
            imagem_url = request.form['imagem_url']
            cur.execute("INSERT INTO filmes (titulo, imagem_url) VALUES (%s, %s)", (titulo, imagem_url))
            conn.commit()

        # Atualizar o filme da semana
        if 'filme_da_semana_id' in request.form:
            novo_id = int(request.form['filme_da_semana_id'])
            cur.execute("UPDATE config SET filme_da_semana_id = %s", (novo_id,))
            conn.commit()

    # Busca dados para o formulário
    cur.execute("SELECT id, titulo FROM filmes ORDER BY id DESC")
    filmes = cur.fetchall()
    cur.execute("SELECT filme_da_semana_id FROM config LIMIT 1")
    resultado = cur.fetchone()
    filme_atual = resultado[0] if resultado else None

    cur.close()
    conn.close()
    return render_template('config.html', filmes=filmes, filme_atual=filme_atual)


@app.route('/avaliar/<int:filme_id>', methods=['GET', 'POST'])
def avaliar(filme_id):
    conn = get_connection()
    cur = conn.cursor()

    # Busca dados do filme
    cur.execute("SELECT titulo, imagem_url FROM filmes WHERE id = %s", (filme_id,))
    filme = cur.fetchone()

    if request.method == 'POST':
        dados = (
            request.form['nome'],
            int(request.form['roteiro']),
            int(request.form['atuacao']),
            int(request.form['direcao']),
            int(request.form['fotografia']),
            int(request.form['trilha']),
            int(request.form['montagem']),
            int(request.form['impacto']),
            request.form['critica'],
            int(request.form['total']),
            filme_id
        )
        cur.execute("""
            INSERT INTO avaliacoes (nome, roteiro, atuacao, direcao, fotografia, trilha, montagem, impacto, critica, total, filme_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, dados)
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('avaliacoes', filme_id=filme_id))

    cur.close()
    conn.close()
    return render_template('avaliar.html', filme=filme, filme_id=filme_id)

@app.route('/avaliacoes/<int:filme_id>')
def avaliacoes(filme_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT titulo, imagem_url FROM filmes WHERE id = %s", (filme_id,))
    filme = cur.fetchone()

    cur.execute("SELECT * FROM avaliacoes WHERE filme_id = %s ORDER BY data DESC", (filme_id,))
    avaliacoes = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('avaliacoes.html', filme=filme, avaliacoes=avaliacoes, filme_id=filme_id)

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM avaliacoes WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(request.referrer or '/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
