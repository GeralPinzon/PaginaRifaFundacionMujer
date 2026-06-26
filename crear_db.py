import sqlite3

conexion = sqlite3.connect('rifa.db')

cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS numeros (
    numero INTEGER PRIMARY KEY,
    estado INTEGER DEFAULT 0,
    nombre TEXT DEFAULT '',
    telefono TEXT DEFAULT '',
    correo TEXT DEFAULT '',
    pago INTEGER DEFAULT 0
)
""")

for numero in range(1, 1000):

    cursor.execute("""
    INSERT OR IGNORE INTO numeros
    (numero, estado, nombre, telefono, correo, pago)
    VALUES (?, 0, '', '', '', 0)
    """, (numero,))

conexion.commit()
conexion.close()

print("Base de datos creada correctamente.")