import re

# Precedencia y asociatividad
precedence = {
    '*': 3,
    '+': 3,
    '?': 3,
    '.': 2,
    '|': 1
}

right_associative = {'*', '+', '?'}

# Inserta concatenaciones explícitas con '.'
def insert_concatenation(exp):
    output = ""
    for i in range(len(exp)):
        c1 = exp[i]
        output += c1
        if i + 1 < len(exp):
            c2 = exp[i + 1]
            if (
                (c1 not in '(|' and c2 not in '|)*+?)') or
                (c1 in ')*+?' and c2 not in '|)*+?)')
            ):
                output += '.'
    return output

# Verifica si un carácter es un operador
def is_operator(c):
    return c in precedence

# Algoritmo de Shunting Yard para regex
def shunting_yard(regex):
    output = []
    stack = []
    steps = []
    i = 0
    while i < len(regex):
        c = regex[i]
        if c == '\\':  # caracter escapado
            i += 1
            if i < len(regex):
                output.append('\\' + regex[i])
                steps.append(f"Añadir carácter escapado: \\{regex[i]}")
        elif c == '(':
            stack.append(c)
            steps.append("Apilar paréntesis abierto: (")
        elif c == ')':
            while stack and stack[-1] != '(':
                op = stack.pop()
                output.append(op)
                steps.append(f"Desapilar y añadir operador: {op}")
            if stack and stack[-1] == '(':
                stack.pop()
                steps.append("Eliminar paréntesis abierto")
        elif is_operator(c):
            while (
                stack and stack[-1] != '(' and
                (
                    (c not in right_associative and precedence[c] <= precedence[stack[-1]]) or
                    (c in right_associative and precedence[c] < precedence[stack[-1]])
                )
            ):
                op = stack.pop()
                output.append(op)
                steps.append(f"Desapilar y añadir operador: {op}")
            stack.append(c)
            steps.append(f"Apilar operador: {c}")
        else:
            output.append(c)
            steps.append(f"Añadir operando: {c}")
        i += 1

    while stack:
        op = stack.pop()
        output.append(op)
        steps.append(f"Desapilar y añadir al final: {op}")

    return ''.join(output), steps

# Procesar archivo
def procesar_archivo(nombre_archivo):
    with open(nombre_archivo, 'r') as archivo:
        lineas = archivo.readlines()
        for idx, linea in enumerate(lineas, 1):
            expresion = linea.strip()
            print(f"\nExpresión {idx}: {expresion}")
            expresion_mod = insert_concatenation(expresion)
            print(f"Expresión con concatenación explícita: {expresion_mod}")
            postfix, pasos = shunting_yard(expresion_mod)
            print("Postfix:", postfix)
            print("Pasos del algoritmo:")
            for paso in pasos:
                print("  -", paso)

# Ejecutar con ejemplo
if __name__ == "__main__":
    archivo = "expresiones.txt"  
    procesar_archivo(archivo)
