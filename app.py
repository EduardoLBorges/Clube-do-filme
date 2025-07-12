from flask import Flask, render_template, request, redirect
import psycopg2
import os
import datetime
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do .env

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "clube_filmes"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "senha"),
        port=os.environ.get("DB_PORT", "5432")
    )

@app.route('/', methods=['GET', 'POST'])
def index():
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
            request.form['critica']
        )
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO avaliacoes (nome, roteiro, atuacao, direcao, fotografia, trilha, montagem, impacto, critica)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, dados)
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/')

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM avaliacoes ORDER BY data DESC")
    avaliacoes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', avaliacoes=avaliacoes)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
