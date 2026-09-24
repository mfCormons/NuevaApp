from flask import Flask, jsonify, render_template, request
import psycopg
from psycopg.rows import dict_row
import os

app = Flask(__name__)
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'postgresql://nuevaapp:nuevaapp_dev@127.0.0.1:5432/nuevaapp')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mysecretkey')

def get_db():
    return psycopg.connect(app.config['DATABASE_URL'], row_factory=dict_row)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/consultar')
def consultar():
    numero=request.args.get('numero', type=int)
    if numero is None:
        return jsonify({'error': 'Número no proporcionado'}), 400
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute('SELECT valor FROM valores WHERE numero = %s', (numero,))
        fila = c.fetchone()
    finally:
        conn.close()
    if fila:
        return {'valor': fila['valor']}
    return jsonify({'error': 'Número no encontrado'}), 404

@app.route('/health')
def health():
    try:
        conn = get_db()
        conn.execute('SELECT 1')
        conn.close()
        return jsonify({'status': 'ok'})
    except Exception:
        return jsonify({'status': 'error'}), 500

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1')
