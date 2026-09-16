import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS valores (
                numero INTEGER PRIMARY KEY,
                valor TEXT NOT NULL
            )''')

datos = [
    (1, 'Valor 1'),
    (2, 'Valor 2'),
    (3, 'Valor 3'),
    (4, 'Valor 4'),
    (5, 'Valor 5')
]
c.execute("DELETE FROM valores")
c.executemany('INSERT INTO valores (numero, valor) VALUES (?, ?)', datos)

conn.commit()
conn.close()
