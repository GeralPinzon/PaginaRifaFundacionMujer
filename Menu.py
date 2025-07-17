import json

# Cargar el archivo JSON o crearlo si no existe
def cargar_datos():
    try:
        with open('numeros.json', 'r') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        datos = {
            str(i): {"estado": 0, "nombre": "", "telefono": "", "correo": "", "pago": 0}
            for i in range(1, 1000)
        }
        with open('numeros.json', 'w') as archivo:
            json.dump(datos, archivo, indent=4)
        return datos

def anular_boletas(datos):
    entrada = input("Ingrese los números que desea anular (separados por comas): ")
    numeros = [str(int(num.strip())) for num in entrada.split(",") if num.strip().isdigit()]

    anulados = []
    no_vendidos = []
    no_existentes = []

    for numero in numeros:
        if numero in datos:
            if datos[numero]["estado"] == 1:
                datos[numero] = {
                    "estado": 0,
                    "nombre": "",
                    "telefono": "",
                    "correo": "",
                    "pago": 0
                }
                anulados.append(numero.zfill(3))
            else:
                no_vendidos.append(numero.zfill(3))
        else:
            no_existentes.append(numero)

    guardar_datos(datos)

    if anulados:
        print(f"\n✅ Boletas anuladas: {', '.join(anulados)}")
    if no_vendidos:
        print(f"⚠️ Estos números no estaban vendidos: {', '.join(no_vendidos)}")
    if no_existentes:
        print(f"❌ Números inválidos: {', '.join(no_existentes)}")

def venta_por_lista(datos):
    entrada = input("Ingrese los números que desea vender (separados por comas): ")
    numeros_crudos = entrada.split(",")

    # Procesar cada número: quitar espacios, ceros innecesarios y validar que sea un número válido
    numeros = []
    for num in numeros_crudos:
        num_limpio = num.strip()
        if num_limpio.isdigit():
            numero_formateado = str(int(num_limpio))  # convierte "090" en "90"
            if 1 <= int(numero_formateado) <= 999:
                numeros.append(numero_formateado)
            else:
                print(f"Número {num} está fuera de rango (1-999).")
        else:
            print(f"Número {num} no es válido.")


    nombre = input("Ingrese el nombre del comprador: ")
    telefono = input("Ingrese el número telefónico: ")
    correo = input("Ingrese el correo electrónico: ")
    pago = input("¿Los números están pagados? (1 = Sí, 0 = No): ")

    vendidos = []
    ya_vendidos = []
    no_existentes = []

    for numero in numeros:
        if numero in datos:
            if datos[numero]["estado"] == 0:
                datos[numero]["estado"] = 1
                datos[numero]["nombre"] = nombre
                datos[numero]["telefono"] = telefono
                datos[numero]["correo"] = correo
                datos[numero]["pago"] = int(pago)
                vendidos.append(numero)
            else:
                ya_vendidos.append(numero)
        else:
            no_existentes.append(numero)

    guardar_datos(datos)

    print(f"\n✅ Se vendieron {len(vendidos)} números a {nombre}: {', '.join(vendidos)}")
    if ya_vendidos:
        print(f"⚠️ Ya estaban vendidos: {', '.join(ya_vendidos)}")
    if no_existentes:
        print(f"❌ No encontrados en el sistema: {', '.join(no_existentes)}")
    
# Guardar los cambios en el archivo JSON
def guardar_datos(datos):
    with open('numeros.json', 'w') as archivo:
        json.dump(datos, archivo, indent=4)

# Mostrar el menú
def mostrar_menu():
    print("\n=== MENÚ ===")
    print("1. Ver números disponibles")
    print("2. Vender un número")
    print("3. Ver números vendidos")
    print("4. Marcar un número como pagado")
    print("5. Ver números no pagados")
    print("6. Salir")
    print("7. Consultar información de un número")
    print("8. Venta masiva de números")
    print("9. Anular boletas por número")


# Mostrar números disponibles
def ver_disponibles(datos):
    disponibles = [int(num) for num, info in datos.items() if info["estado"] == 0]
    disponibles.sort()

    if disponibles:
        print(f"\n=== Números disponibles ({len(disponibles)}) ===\n")

        # Mostrar los números en filas de 10
        fila = ""
        for i, num in enumerate(disponibles, 1):
            fila += f"{num}, "
            if i % 10 == 0:
                print(fila.rstrip(", "))
                fila = ""
        if fila:  # Imprimir los que quedaron al final
            print(fila.rstrip(", "))

        print("\nPuedes copiar y pegar esta lista para enviar por WhatsApp.")
    else:
        print("\nNo hay números disponibles.")


# Mostrar números vendidos
def ver_vendidos(datos):
    vendidos = {num: info for num, info in datos.items() if info["estado"] == 1}
    if vendidos:
        print("\n=== Números vendidos ===")
        for num, info in vendidos.items():
            estado_pago = "Pagado" if info["pago"] == 1 else "No pagado"
            print(f"Número {num}: {info['nombre']} - {info['telefono']} - {info['correo']} - {estado_pago}")
    else:
        print("\nAún no hay números vendidos.")

# Vender un número
def vender_numero(datos):
    numero = input("Ingrese el número que desea vender: ")
    if numero in datos:
        if datos[numero]["estado"] == 0:
            nombre = input("Ingrese el nombre del comprador: ")
            telefono = input("Ingrese el número telefónico: ")
            correo = input("Ingrese el correo electrónico: ")
            pago = input("Ingrese si el numero es cancelado o no: ")
            
            datos[numero]["estado"] = 1
            datos[numero]["nombre"] = nombre
            datos[numero]["telefono"] = telefono
            datos[numero]["correo"] = correo
            datos[numero]["pago"] = pago  # Por defecto no pagado

            guardar_datos(datos)
            print(f"Número {numero} vendido exitosamente a {nombre}.")
        else:
            print(f"El número {numero} ya está vendido.")
    else:
        print("Número inválido.")

# Marcar un número como pagado
def marcar_como_pagado(datos):
    numero = input("Ingrese el número que desea marcar como pagado: ")
    if numero in datos:
        if datos[numero]["estado"] == 1:
            if datos[numero]["pago"] == 0:
                datos[numero]["pago"] = 1
                guardar_datos(datos)
                print(f"Número {numero} marcado como pagado.")
            else:
                print(f"El número {numero} ya está pagado.")
        else:
            print("El número no está vendido aún.")
    else:
        print("Número inválido.")

# Mostrar números no pagados
def ver_no_pagados(datos):
    no_pagados = {num: info for num, info in datos.items() if info["estado"] == 1 and info["pago"] == 0}
    if no_pagados:
        print("\n=== Números no pagados ===")
        for num, info in no_pagados.items():
            print(f"Número {num}: {info['nombre']} - {info['telefono']} - {info['correo']}")
    else:
        print("\nTodos los números vendidos están pagados.")

# Consultar información de un número específico
def consultar_numero(datos):
    numero = input("Ingrese el número que desea consultar: ")
    if numero in datos:
        info = datos[numero]
        if info["estado"] == 0:
            print(f"El número {numero} está disponible.")
        else:
            estado_pago = "Pagado" if info["pago"] == 1 else "No pagado"
            print(f"Número {numero}:")
            print(f"Nombre: {info['nombre']}")
            print(f"Teléfono: {info['telefono']}")
            print(f"Correo: {info['correo']}")
            print(f"Estado de pago: {estado_pago}")
    else:
        print("Número inválido.")

# Programa principal
def main():
    datos = cargar_datos()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            ver_disponibles(datos)
        elif opcion == '2':
            vender_numero(datos)
        elif opcion == '3':
            ver_vendidos(datos)
        elif opcion == '4':
            marcar_como_pagado(datos)
        elif opcion == '5':
            ver_no_pagados(datos)
        elif opcion == '6':
            print("Saliendo del programa.")
            break
        elif opcion == '7':
            consultar_numero(datos)
        elif opcion == '8':
            venta_por_lista(datos)
        elif opcion == '9':
            anular_boletas(datos)
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()
