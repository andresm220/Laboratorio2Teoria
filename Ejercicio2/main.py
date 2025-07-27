def balancear(expresion):
    stack = []
    pares = {')': '(', ']': '[', '}': '{'}
    apertura = set(pares.values())
    cierre = set(pares.keys())
    balanceado = True

    print(f"Expresión: {expresion}")
    for i, caracter in enumerate(expresion):
        if caracter in apertura:
            stack.append(caracter)
            print(f"  Paso {i}: push '{caracter}' → {stack}")
        elif caracter in cierre:
            if not stack:
                print(f"  Paso {i}: ERROR – se encontró '{caracter}' pero la pila está vacía ")
                balanceado = False
                break
            tope = stack.pop()
            print(f"  Paso {i}: pop '{tope}' porque se encontró '{caracter}' → {stack}")
            if pares[caracter] != tope:
                print(f"  Paso {i}: ERROR – se esperaba '{pares[caracter]}', pero se encontró '{tope}' ")
                balanceado = False
                break

    if stack:
        print(f"  Al final, la pila no está vacía: {stack} ")
        balanceado = False
    if balanceado:
        print("  Resultado:  La expresión está bien balanceada.")
    else:
        print("  Resultado:  La expresión NO está balanceada.")
    print("-" * 60)

# Leer expresiones desde archivo
try:
    with open("expresiones.txt", "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()
        for linea in lineas:
            expresion = linea.strip()
            if expresion:
                balancear(expresion)
except FileNotFoundError:
    print("No se encontró el archivo 'expresiones.txt'. Asegúrate de que esté en la misma carpeta que este script.")
