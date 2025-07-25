import psycopg2
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'chave_secreta_segura' 

# Conexão com o banco de dados
def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "clube_filmes"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "senha"),
        port=os.environ.get("DB_PORT", "5432")
    )

# Rora de manutenção
@app.route('/manutencao')
def manutencao():
    return render_template('manutencao.html')

# Rota para lista de filmes
@app.route('/', endpoint='home')
def home():
    conn = get_connection()
    cur = conn.cursor()

    # Busca o ID do filme da semana a partir da tabela config
    cur.execute("SELECT genero_da_semana FROM config LIMIT 1")
    resultado = cur.fetchone()
    genero_da_semana = resultado[0] if resultado else 1  # fallback para 1 caso não haja resultado
    print(genero_da_semana)
    # Busca os dados do filme da semana
    cur.execute("SELECT id, titulo, imagem_url FROM filmes WHERE genero = %s ORDER BY ordem ASC" , (genero_da_semana,))
    filmes_genero = cur.fetchall()
    print(filmes_genero)
    # Busca a lista de todos os filmes de Animação
    cur.execute("SELECT id, titulo, imagem_url, genero, indicacao FROM filmes WHERE genero = 'Animação' ORDER BY ordem ASC")
    filmes_animacao = cur.fetchall()
    print(filmes_animacao)
    # Busca a lista de todos os filmes de Terror
    cur.execute("SELECT id, titulo, imagem_url, genero, indicacao FROM filmes WHERE genero = 'Terror' ORDER BY ordem ASC")
    filmes_terror = cur.fetchall()

    # Busca a lista de todos os filmes de Aventura
    cur.execute("SELECT id, titulo, imagem_url, genero, indicacao FROM filmes WHERE genero = 'Aventura' ORDER BY ordem ASC")
    filmes_aventura = cur.fetchall()

    # Busca a lista de todos os filmes de Drama
    cur.execute("SELECT id, titulo, imagem_url, genero, indicacao FROM filmes WHERE genero = 'Drama' ORDER BY ordem ASC")
    filmes_drama = cur.fetchall()

    # Busca a lista de todos os filmes de Ficção Científica
    cur.execute("SELECT id, titulo, imagem_url, genero, indicacao FROM filmes WHERE genero = 'Ficção Científica' ORDER BY ordem ASC")
    filmes_scifi = cur.fetchall()

    cur.close()
    conn.close()
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
    cur.execute("SELECT id, titulo, imagem_url FROM filmes WHERE genero = 'real'")
    filmes = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('real.html', filmes=filmes, filme=filme)

# Rota da pagina de configurações
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

    # Dados do filme
    cur.execute("SELECT titulo, imagem_url FROM filmes WHERE id = %s", (filme_id,))
    filme = cur.fetchone()

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

            # Verifica notas
            for campo in ['roteiro', 'atuacao', 'direcao', 'fotografia', 'trilha', 'montagem', 'impacto']:
                dados[campo] = int(dados[campo])
                if dados[campo] < 1 or dados[campo] > 5:
                    raise ValueError(f"A nota de {campo} deve ser entre 1 e 5.")

            dados['total'] = int(dados['total'])
            if dados['total'] < 1 or dados['total'] > 10:
                raise ValueError("A nota total deve ser entre 1 e 10.")

            cur.execute("""
                INSERT INTO avaliacoes 
                (nome, roteiro, atuacao, direcao, fotografia, trilha, montagem, impacto, critica, total, filme_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                dados['nome'], dados['roteiro'], dados['atuacao'], dados['direcao'],
                dados['fotografia'], dados['trilha'], dados['montagem'], dados['impacto'],
                dados['critica'], dados['total'], filme_id
            ))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('avaliacoes', filme_id=filme_id))

        except Exception as e:
            erro = str(e)

    cur.close()
    conn.close()
    return render_template('avaliar.html', filme=filme, filme_id=filme_id, erro=erro, dados=dados)

# Rota da pagina de avaliações
@app.route('/avaliacoes/<int:filme_id>')
def avaliacoes(filme_id):
    conn = get_connection()
    cur = conn.cursor()

    # Busca os dados para o poster
    cur.execute("SELECT titulo, imagem_url FROM filmes WHERE id = %s", (filme_id,))
    filme = cur.fetchone()

    # Busca os dados de avaliações do filme
    cur.execute("SELECT * FROM avaliacoes WHERE filme_id = %s ORDER BY data DESC", (filme_id,))
    avaliacoes = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('avaliacoes.html', filme=filme, avaliacoes=avaliacoes, filme_id=filme_id)

# Rota para o botão de excluir avaliação
@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM avaliacoes WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(request.referrer or '/')

# Iniciar aplicação
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
