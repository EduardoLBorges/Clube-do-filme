import psycopg2
import os

def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "clube_filmes"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "senha"),
        port=os.environ.get("DB_PORT", "5432")
    )

def get_genero_da_semana():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT genero_da_semana FROM config LIMIT 1")
            resultado = cur.fetchone()
            return resultado[0] if resultado else 1

def get_filmes_por_genero(genero):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT f.id, f.titulo, f.imagem_url, COUNT(av.filme_id) AS total_avaliacoes, STRING_AGG(av.nome, ', ') AS nomes_avaliadores 
                FROM filmes AS f 
                FULL JOIN avaliacoes AS av ON av.filme_id = f.id 
                WHERE genero = %s 
                GROUP BY f.id, f.titulo, f.imagem_url 
                ORDER BY f.id
            """, (genero,))
            return cur.fetchall()

def get_filmes_por_categoria(categoria):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, titulo, imagem_url, genero, indicacao FROM filmes WHERE genero = %s ORDER BY ordem ASC", (categoria,))
            return cur.fetchall()

def get_filme_da_semana_id():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT filme_da_semana_id FROM config LIMIT 1")
            resultado = cur.fetchone()
            return resultado[0] if resultado else 1

def get_filme_por_id(filme_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, titulo, imagem_url FROM filmes WHERE id = %s", (filme_id,))
            return cur.fetchone()

def get_filmes_real():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, titulo, imagem_url FROM filmes WHERE genero = 'real'")
            return cur.fetchall()

def get_senha_config():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT senha_config FROM config LIMIT 1")
            resultado = cur.fetchone()
            return resultado[0] if resultado else None

def inserir_filme(titulo, imagem_url):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO filmes (titulo, imagem_url) VALUES (%s, %s)", (titulo, imagem_url))
            conn.commit()

def update_filme_da_semana(novo_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE config SET filme_da_semana_id = %s", (novo_id,))
            conn.commit()

def get_todos_filmes_ordenados():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, titulo FROM filmes ORDER BY id DESC")
            return cur.fetchall()

def get_filme_atual_id():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT filme_da_semana_id FROM config LIMIT 1")
            resultado = cur.fetchone()
            return resultado[0] if resultado else None

def get_dados_filme(filme_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT titulo, imagem_url FROM filmes WHERE id = %s", (filme_id,))
            return cur.fetchone()

def inserir_avaliacao(dados, filme_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
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

def get_avaliacoes_por_filme(filme_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM avaliacoes WHERE filme_id = %s ORDER BY data DESC", (filme_id,))
            return cur.fetchall()

def excluir_avaliacao(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM avaliacoes WHERE id = %s", (id,))
            conn.commit()

def get_dados_apresentacao_filme(filme_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, titulo, imagem_url, genero, ordem FROM filmes WHERE id = %s", (filme_id,))
            return cur.fetchone()

def get_avaliacoes_por_filme_ordenado_por_nome(filme_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM avaliacoes WHERE filme_id = %s ORDER BY nome ASC", (filme_id,))
            return cur.fetchall()

def get_filmes_por_genero_ordenado_por_ordem(genero):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, titulo, imagem_url FROM filmes WHERE genero = %s ORDER BY ordem ASC", (genero,))
            return cur.fetchall()
