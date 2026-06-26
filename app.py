from flask import Flask, render_template, request, redirect, flash
import sqlite3, re

app = Flask(__name__)
app.secret_key = "mujerlindacats"

def obtener_conexion():
    
    conexion = sqlite3.connect('rifa.db')

    conexion.row_factory = sqlite3.Row

    return conexion    

@app.route('/')
def inicio():

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM numeros
        WHERE estado = 1
    """)
    vendidos = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM numeros
        WHERE estado = 0
    """)
    disponibles = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM numeros
        WHERE pago = 1
    """)
    pagados = cursor.fetchone()[0]

    conexion.close()

    pendientes = vendidos - pagados

    VALOR_BOLETA = 10000

    recaudado = pagados * VALOR_BOLETA
    pendiente_cobro = pendientes * VALOR_BOLETA

    porcentaje = round((vendidos / 999) * 100, 1)

    return render_template(
        'index.html',
        vendidos=vendidos,
        disponibles=disponibles,
        pagados=pagados,
        pendientes=pendientes,
        recaudado=recaudado,
        pendiente_cobro=pendiente_cobro,
        porcentaje=porcentaje
    )

@app.route('/vender', methods=['GET', 'POST'])
def vender():

    if request.method == 'POST':

        numero = request.form['numero'].strip()
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form['correo']
        pago = int(request.form['pago'])

        try:
            numero = int(numero)
        except:
            flash(
                '❌ Número inválido.',
                'danger'
            )
            return redirect('/vender')

        conexion = obtener_conexion()

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT estado
            FROM numeros
            WHERE numero = ?
        """, (numero,))

        registro = cursor.fetchone()

        if registro and registro["estado"] == 0:

            cursor.execute("""
                UPDATE numeros
                SET
                    estado = 1,
                    nombre = ?,
                    telefono = ?,
                    correo = ?,
                    pago = ?
                WHERE numero = ?
            """, (
                nombre,
                telefono,
                correo,
                pago,
                numero
            ))

            conexion.commit()
            conexion.close()

            flash(
                f'✅ Boleta {str(numero).zfill(3)} vendida correctamente a {nombre}.',
                'success'
            )

            return redirect('/vender')

        conexion.close()

        flash(
            f'❌ La boleta {str(numero).zfill(3)} ya fue vendida o no existe.',
            'danger'
        )

    return render_template('vender.html')

@app.route('/venta_multiple', methods=['GET', 'POST'])
def venta_multiple():

    if request.method == 'POST':

        numeros = request.form['numeros']
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form['correo']
        pago = int(request.form['pago'])

        lista_numeros = re.split(r'[\n,]+', numeros)

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        vendidos = []
        no_vendidos = []

        for numero in lista_numeros:

            numero = numero.strip()

            try:
                numero_int = int(numero)
            except:
                no_vendidos.append(numero)
                continue

            cursor.execute("""
                SELECT estado
                FROM numeros
                WHERE numero = ?
            """, (numero_int,))

            registro = cursor.fetchone()
            if registro and registro["estado"] == 0:
                
                cursor.execute("""
                    UPDATE numeros
                    SET
                        estado = 1,
                        nombre = ?,
                        telefono = ?,
                        correo = ?,
                        pago = ?
                    WHERE numero = ?
                """, (
                    nombre,
                    telefono,
                    correo,
                    pago,
                    numero_int
                ))

                vendidos.append(str(numero_int).zfill(3))

            else:

                no_vendidos.append(str(numero_int).zfill(3))

        conexion.commit()
        conexion.close()

        if vendidos:

            flash(
                f'✅ Se vendieron {len(vendidos)} boletas correctamente.',
                'success'
            )

        if no_vendidos:

            flash(
                f'⚠️ No se pudieron vender: {", ".join(no_vendidos)}',
                'warning'
            )

        return redirect('/venta_multiple')

    return render_template('venta_multiple.html')

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():

    resultados = []

    if request.method == 'POST':

        nombre_buscado = request.form['nombre'].strip().lower()

        conexion = obtener_conexion()

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT *
            FROM numeros
            WHERE estado = 1
            AND LOWER(nombre) LIKE ?
        """, (f'%{nombre_buscado}%',))

        registros = cursor.fetchall()

        conexion.close()

        for registro in registros:

            resultados.append({
                "numero": str(registro["numero"]).zfill(3),
                "nombre": registro["nombre"],
                "telefono": registro["telefono"],
                "correo": registro["correo"],
                "pago": "Sí" if registro["pago"] == 1 else "No"
            })

    return render_template(
        'buscar.html',
        resultados=resultados,
        busqueda_realizada=request.method == 'POST'
    )

@app.route('/anular', methods=['GET', 'POST'])
def anular():

    anuladas = []

    if request.method == 'POST':

        numeros = request.form['numeros']

        lista_numeros = numeros.split(',')

        conexion = obtener_conexion()

        cursor = conexion.cursor()

        for numero in lista_numeros:

            numero = numero.strip()

            try:
                numero = int(numero)
            except:
                continue

            cursor.execute("""
                SELECT estado
                FROM numeros
                WHERE numero = ?
            """, (numero,))

            registro = cursor.fetchone()

            if registro and registro["estado"] == 1:

                cursor.execute("""
                    UPDATE numeros
                    SET
                        estado = 0,
                        nombre = '',
                        telefono = '',
                        correo = '',
                        pago = 0
                    WHERE numero = ?
                """, (numero,))

                anuladas.append(
                    str(numero).zfill(3)
                )

        conexion.commit()
        conexion.close()

        if len(anuladas) > 0:

            flash(
                f'✅ Se anularon {len(anuladas)} boletas correctamente.',
                'success'
            )

        else:

            flash(
                '⚠️ No se anuló ninguna boleta.',
                'warning'
            )

    return render_template(
        'anular.html',
        anuladas=anuladas
    )

@app.route('/pendientes')
def pendientes():

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT numero, nombre, telefono, correo
        FROM numeros
        WHERE estado = 1
        AND pago = 0
        ORDER BY numero
    """)

    registros = cursor.fetchall()

    conexion.close()

    lista_pendientes = []

    for registro in registros:

        lista_pendientes.append({
            "numero": str(registro["numero"]).zfill(3),
            "nombre": registro["nombre"],
            "telefono": registro["telefono"],
            "correo": registro["correo"]
        })

    return render_template(
        'pendientes.html',
        pendientes=lista_pendientes
    )

@app.route('/disponibles')
def disponibles():

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT numero
        FROM numeros
        WHERE estado = 0
        ORDER BY numero
    """)

    registros = cursor.fetchall()

    conexion.close()

    lista_disponibles = []

    for registro in registros:

        lista_disponibles.append(
            str(registro["numero"]).zfill(3)
        )

    lineas = []

    for i in range(0, len(lista_disponibles), 10):

        linea = " - ".join(
            lista_disponibles[i:i+10]
        )

        lineas.append(linea)

    texto_disponibles = "\n".join(lineas)

    return render_template(
        'disponibles.html',
        disponibles=lista_disponibles,
        texto_disponibles=texto_disponibles
    )

@app.route('/marcar_pagado', methods=['GET', 'POST'])
def marcar_pagado():

    mensaje = ""

    if request.method == 'POST':

        numero = request.form['numero'].strip()

        try:
            numero = int(numero)
        except:
            mensaje = "❌ Número inválido."

            return render_template(
                'marcar_pagado.html',
                mensaje=mensaje
            )

        conexion = obtener_conexion()

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT estado, pago
            FROM numeros
            WHERE numero = ?
        """, (numero,))

        registro = cursor.fetchone()

        if registro:

            if registro["estado"] == 1:

                if registro["pago"] == 0:

                    cursor.execute("""
                        UPDATE numeros
                        SET pago = 1
                        WHERE numero = ?
                    """, (numero,))

                    conexion.commit()

                    mensaje = (
                        f"✅ La boleta {str(numero).zfill(3)} "
                        "fue marcada como pagada."
                    )

                else:

                    mensaje = (
                        f"⚠️ La boleta {str(numero).zfill(3)} "
                        "ya estaba pagada."
                    )

            else:

                mensaje = "❌ La boleta no está vendida."

        else:

            mensaje = "❌ La boleta no existe."

        conexion.close()

    return render_template(
        'marcar_pagado.html',
        mensaje=mensaje
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0')