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

@app.route('/api/valores', methods=['POST'])
def crear_valores():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Body JSON no proporcionado'}), 400

    registros = data if isinstance(data, list) else [data]
    if not registros:
        return jsonify({'error': 'Lista vacía'}), 400

    errores = []
    filas = []
    for i, reg in enumerate(registros):
        if not isinstance(reg, dict):
            errores.append(f'registro {i}: debe ser un objeto JSON')
            continue
        numero = reg.get('numero')
        valor = reg.get('valor')
        if not isinstance(numero, int) or isinstance(numero, bool):
            errores.append(f'registro {i}: "numero" debe ser entero')
        elif not isinstance(valor, str) or not valor.strip():
            errores.append(f'registro {i}: "valor" debe ser texto no vacío')
        else:
            filas.append((numero, valor))

    if errores:
        return jsonify({'errores': errores}), 400

    conn = get_db()
    try:
        c = conn.cursor()
        c.executemany(
            'INSERT INTO valores (numero, valor) VALUES (%s, %s) '
            'ON CONFLICT (numero) DO UPDATE SET valor = EXCLUDED.valor',
            filas,
        )
        conn.commit()
    finally:
        conn.close()
    return jsonify({'insertados': len(filas)}), 201

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
