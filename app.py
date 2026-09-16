from flask import Flask, jsonify, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/consultar')
def consultar():
    numero=request.args.get('numero', type=int)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT valor FROM valores WHERE numero = ?', (numero,))
    fila = c.fetchone()
    conn.close()    
    if fila:
        return {'valor': fila[0]}
    return jsonify({'error': 'Número no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)