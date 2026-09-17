from flask import Flask, jsonify, render_template, request
import sqlite3
import os

app = Flask(__name__)
app.config['DATABASE'] = os.environ.get('DATABASE_PATH', 'database.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mysecretkey')

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

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
        c.execute('SELECT valor FROM valores WHERE numero = ?', (numero,))
        fila = c.fetchone()
    finally:
        conn.close()
    if fila:
        return {'valor': fila[0]}
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