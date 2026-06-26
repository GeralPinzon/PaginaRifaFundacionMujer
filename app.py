from flask import Flask, render_template, request, redirect, flash
import json

app = Flask(__name__)
app.secret_key = "mujerlindacats"

def cargar_datos():
    with open('numeros.json', 'r', encoding='utf-8') as archivo:
        return json.load(archivo)
    
def guardar_datos(datos):
    with open('numeros.json', 'w', encoding='utf-8') as archivo:
        json.dump(datos, archivo, indent=4)

@app.route('/')
def inicio():

    datos = cargar_datos()

    vendidos = sum(1 for info in datos.values() if info["estado"] == 1)
    disponibles = sum(1 for info in datos.values() if info["estado"] == 0)
    pagados = sum(1 for info in datos.values() if info["pago"] == 1)
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

        numero = request.form['numero']
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form['correo']
        pago = int(request.form['pago'])

        datos = cargar_datos()

        if numero in datos and datos[numero]["estado"] == 0:

            datos[numero]["estado"] = 1
            datos[numero]["nombre"] = nombre
            datos[numero]["telefono"] = telefono
            datos[numero]["correo"] = correo
            datos[numero]["pago"] = pago

            guardar_datos(datos)

            flash(
                f'✅ Boleta {numero} vendida correctamente a {nombre}.',
                'success'
            )

            return redirect('/vender')

        flash(
            f'❌ La boleta {numero} ya fue vendida o no existe.',
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

        datos = cargar_datos()

        lista_numeros = numeros.split(',')

        vendidos = []
        no_vendidos = []

        for numero in lista_numeros:

            numero = numero.strip()

            try:
                numero = str(int(numero))
            except:
                no_vendidos.append(numero)
                continue

            if numero in datos and datos[numero]["estado"] == 0:

                datos[numero]["estado"] = 1
                datos[numero]["nombre"] = nombre
                datos[numero]["telefono"] = telefono
                datos[numero]["correo"] = correo
                datos[numero]["pago"] = pago

                vendidos.append(numero.zfill(3))

            else:

                no_vendidos.append(numero.zfill(3))

        guardar_datos(datos)

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

        datos = cargar_datos()

        for numero, info in datos.items():

            if (
                info["estado"] == 1
                and nombre_buscado in info["nombre"].lower()
            ):

                resultados.append({
                    "numero": numero.zfill(3),
                    "nombre": info["nombre"],
                    "telefono": info["telefono"],
                    "correo": info["correo"],
                    "pago": "Sí" if info["pago"] == 1 else "No"
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

        datos = cargar_datos()

        lista_numeros = numeros.split(',')

        for numero in lista_numeros:

            numero = numero.strip()

            try:
                numero = str(int(numero))
            except:
                continue

            if numero in datos and datos[numero]["estado"] == 1:

                datos[numero] = {
                    "estado": 0,
                    "nombre": "",
                    "telefono": "",
                    "correo": "",
                    "pago": 0
                }

                anuladas.append(numero.zfill(3))

        guardar_datos(datos)

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

    datos = cargar_datos()

    lista_pendientes = []

    for numero, info in datos.items():

        if info["estado"] == 1 and info["pago"] == 0:

            lista_pendientes.append({
                "numero": numero.zfill(3),
                "nombre": info["nombre"],
                "telefono": info["telefono"],
                "correo": info["correo"]
            })

    return render_template(
        'pendientes.html',
        pendientes=lista_pendientes
    )

@app.route('/disponibles')
def disponibles():

    datos = cargar_datos()

    lista_disponibles = []

    for numero, info in datos.items():

        if info["estado"] == 0:

            lista_disponibles.append(numero.zfill(3))

    lista_disponibles.sort()

    lineas = []

    for i in range(0, len(lista_disponibles), 10):
        linea = " - ".join(lista_disponibles[i:i+10])
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
            numero = str(int(numero))
        except:
            mensaje = "Número inválido."
            return render_template(
                'marcar_pagado.html',
                mensaje=mensaje
            )

        datos = cargar_datos()

        if numero in datos:

            if datos[numero]["estado"] == 1:
                
                if datos[numero]["pago"] == 0:

                    datos[numero]["pago"] = 1

                    guardar_datos(datos)

                    mensaje = (
                        f"✅ La boleta {numero.zfill(3)} "
                        "fue marcada como pagada."
                    )

                else:

                    mensaje = (
                        f"⚠️ La boleta {numero.zfill(3)} "
                        "ya estaba pagada."
                    )

        else:

            mensaje = "❌ La boleta no existe."

    return render_template(
        'marcar_pagado.html',
        mensaje=mensaje
    )

if __name__ == '__main__':
    ##app.run(debug=True)
    app.run()