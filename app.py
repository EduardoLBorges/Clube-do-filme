from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        port=os.environ['DB_PORT']
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
    app.run()
