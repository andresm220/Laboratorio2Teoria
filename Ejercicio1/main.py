class Estado:
    contador = 0
    
    def __init__(self):
        self.id = Estado.contador
        Estado.contador += 1
        self.es_final = False
        self.transiciones = {}
    
    def agregar_transicion(self, simbolo, estado_destino):
        if simbolo not in self.transiciones:
            self.transiciones[simbolo] = []
        self.transiciones[simbolo].append(estado_destino)
    
    def __str__(self):
        return f"q{self.id}"
    
    def __repr__(self):
        return f"q{self.id}"

class AFN:
    def __init__(self, estado_inicial, estado_final):
        self.estado_inicial = estado_inicial
        self.estado_final = estado_final
        self.estados = set()
        self.alfabeto = set()
        self._recopilar_estados()
    
    def _recopilar_estados(self):
        visitados = set()
        cola = [self.estado_inicial]
        
        while cola:
            estado = cola.pop(0)
            if estado in visitados:
                continue
            visitados.add(estado)
            self.estados.add(estado)
            
            for simbolo, destinos in estado.transiciones.items():
                if simbolo != 'ε':
                    self.alfabeto.add(simbolo)
                for destino in destinos:
                    if destino not in visitados:
                        cola.append(destino)
    
    def mostrar(self):
        print(f"Estado inicial: {self.estado_inicial}")
        print(f"Estado final: {self.estado_final}")
        print("Transiciones:")
        for estado in sorted(self.estados, key=lambda x: x.id):
            for simbolo, destinos in estado.transiciones.items():
                for destino in destinos:
                    print(f"  {estado} --{simbolo}--> {destino}")

class ConstructorThompson:
    def __init__(self):
        Estado.contador = 0
    
    def caracter(self, c):
        """Construye AFN para un caracter individual"""
        inicial = Estado()
        final = Estado()
        final.es_final = True
        inicial.agregar_transicion(c, final)
        return AFN(inicial, final)
    
    def clase_caracteres(self, caracteres):
        """Construye AFN para una clase de caracteres [abc]"""
        inicial = Estado()
        final = Estado()
        final.es_final = True
        
        for c in caracteres:
            inicial.agregar_transicion(c, final)
        
        return AFN(inicial, final)
    
    def cadena(self, texto):
        """Construye AFN para una cadena literal"""
        if not texto:
            return self.epsilon()
        
        afn_actual = self.caracter(texto[0])
        for i in range(1, len(texto)):
            afn_char = self.caracter(texto[i])
            afn_actual = self.concatenacion(afn_actual, afn_char)
        
        return afn_actual
    
    def epsilon(self):
        """Construye AFN para epsilon"""
        inicial = Estado()
        final = Estado()
        final.es_final = True
        inicial.agregar_transicion('ε', final)
        return AFN(inicial, final)
    
    def concatenacion(self, afn1, afn2):
        """Concatena dos AFN"""
        # Conectar el estado final de afn1 con el inicial de afn2 usando epsilon
        afn1.estado_final.es_final = False
        afn1.estado_final.agregar_transicion('ε', afn2.estado_inicial)
        
        # Crear nuevo AFN
        nuevo_afn = AFN(afn1.estado_inicial, afn2.estado_final)
        return nuevo_afn
    
    def union(self, afn1, afn2):
        """Une dos AFN con operador |"""
        inicial = Estado()
        final = Estado()
        final.es_final = True
        
        # Conectar nuevo inicial con los iniciales de ambos AFN
        inicial.agregar_transicion('ε', afn1.estado_inicial)
        inicial.agregar_transicion('ε', afn2.estado_inicial)
        
        # Conectar los finales de ambos AFN con el nuevo final
        afn1.estado_final.es_final = False
        afn2.estado_final.es_final = False
        afn1.estado_final.agregar_transicion('ε', final)
        afn2.estado_final.agregar_transicion('ε', final)
        
        return AFN(inicial, final)
    
    def estrella(self, afn):
        """Aplica operador * (estrella de Kleene)"""
        inicial = Estado()
        final = Estado()
        final.es_final = True
        
        # Conectar nuevo inicial con el inicial del AFN y con el final
        inicial.agregar_transicion('ε', afn.estado_inicial)
        inicial.agregar_transicion('ε', final)
        
        # Conectar el final del AFN con su inicial y con el nuevo final
        afn.estado_final.es_final = False
        afn.estado_final.agregar_transicion('ε', afn.estado_inicial)
        afn.estado_final.agregar_transicion('ε', final)
        
        return AFN(inicial, final)
    
    def mas(self, afn):
        """Aplica operador + (una o más veces)"""
        # a+ = aa*
        afn_estrella = self.estrella(afn)
        return self.concatenacion(afn, afn_estrella)
    
    def opcional(self, afn):
        """Aplica operador ? (opcional)"""
        inicial = Estado()
        final = Estado()
        final.es_final = True
        
        # Camino directo (epsilon)
        inicial.agregar_transicion('ε', final)
        
        # Camino a través del AFN
        inicial.agregar_transicion('ε', afn.estado_inicial)
        afn.estado_final.es_final = False
        afn.estado_final.agregar_transicion('ε', final)
        
        return AFN(inicial, final)

class ConversorAFD:
    def __init__(self, afn):
        self.afn = afn
        self.estados_afd = {}
        self.transiciones_afd = {}
        self.estado_inicial_afd = None
        self.estados_finales_afd = set()
    
    def epsilon_closure(self, estados):
        """Calcula la epsilon clausura de un conjunto de estados"""
        closure = set(estados)
        pila = list(estados)
        
        while pila:
            estado = pila.pop()
            if 'ε' in estado.transiciones:
                for siguiente in estado.transiciones['ε']:
                    if siguiente not in closure:
                        closure.add(siguiente)
                        pila.append(siguiente)
        
        return frozenset(closure)
    
    def move(self, estados, simbolo):
        """Calcula el conjunto de estados alcanzables con un símbolo"""
        resultado = set()
        for estado in estados:
            if simbolo in estado.transiciones:
                resultado.update(estado.transiciones[simbolo])
        return resultado
    
    def convertir(self):
        """Convierte AFN a AFD usando construcción de subconjuntos"""
        # Estado inicial del AFD es la epsilon clausura del inicial del AFN
        inicial_closure = self.epsilon_closure([self.afn.estado_inicial])
        self.estado_inicial_afd = inicial_closure
        
        estados_por_procesar = [inicial_closure]
        estados_procesados = set()
        
        # Mapeo de conjuntos de estados a nombres
        contador_estados = 0
        self.estados_afd[inicial_closure] = f"q{contador_estados}"
        contador_estados += 1
        
        while estados_por_procesar:
            conjunto_actual = estados_por_procesar.pop(0)
            
            if conjunto_actual in estados_procesados:
                continue
            
            estados_procesados.add(conjunto_actual)
            
            # Verificar si es estado final
            for estado in conjunto_actual:
                if estado.es_final or estado == self.afn.estado_final:
                    self.estados_finales_afd.add(conjunto_actual)
                    break
            
            # Para cada símbolo del alfabeto
            for simbolo in self.afn.alfabeto:
                siguiente_conjunto = self.move(conjunto_actual, simbolo)
                if siguiente_conjunto:
                    closure_siguiente = self.epsilon_closure(siguiente_conjunto)
                    
                    if closure_siguiente not in self.estados_afd:
                        self.estados_afd[closure_siguiente] = f"q{contador_estados}"
                        contador_estados += 1
                        estados_por_procesar.append(closure_siguiente)
                    
                    # Agregar transición
                    if conjunto_actual not in self.transiciones_afd:
                        self.transiciones_afd[conjunto_actual] = {}
                    self.transiciones_afd[conjunto_actual][simbolo] = closure_siguiente
    
    def mostrar_afd(self):
        print("\n=== AFD RESULTANTE ===")
        print(f"Estado inicial: {self.estados_afd[self.estado_inicial_afd]}")
        
        print("Estados finales:", end=" ")
        finales_nombres = [self.estados_afd[estado] for estado in self.estados_finales_afd]
        print(", ".join(finales_nombres))
        
        print("\nTabla de transiciones:")
        print("Estado\t", end="")
        if self.afn.alfabeto:
            for simbolo in sorted(self.afn.alfabeto):
                print(f"{simbolo}\t", end="")
        print()
        
        for conjunto_estado in sorted(self.estados_afd.keys(), key=lambda x: self.estados_afd[x]):
            nombre_estado = self.estados_afd[conjunto_estado]
            print(f"{nombre_estado}\t", end="")
            
            for simbolo in sorted(self.afn.alfabeto):
                if conjunto_estado in self.transiciones_afd and simbolo in self.transiciones_afd[conjunto_estado]:
                    destino = self.transiciones_afd[conjunto_estado][simbolo]
                    print(f"{self.estados_afd[destino]}\t", end="")
                else:
                    print("-\t", end="")
            print()

def procesar_expresion_simple(expresion, constructor):
    """Procesa expresiones regulares simples"""
    print(f"\n=== Procesando: {expresion} ===")
    
    if expresion == "(a|t)c":
        # Construir (a|t)
        afn_a = constructor.caracter('a')
        afn_t = constructor.caracter('t')
        afn_union = constructor.union(afn_a, afn_t)
        
        # Concatenar con c
        afn_c = constructor.caracter('c')
        afn_final = constructor.concatenacion(afn_union, afn_c)
        
    elif expresion == "(a|b)*":
        afn_a = constructor.caracter('a')
        afn_b = constructor.caracter('b')
        afn_union = constructor.union(afn_a, afn_b)
        afn_final = constructor.estrella(afn_union)
        
    elif expresion == "(a*|b*)*":
        afn_a = constructor.caracter('a')
        afn_a_star = constructor.estrella(afn_a)
        afn_b = constructor.caracter('b')
        afn_b_star = constructor.estrella(afn_b)
        afn_union = constructor.union(afn_a_star, afn_b_star)
        afn_final = constructor.estrella(afn_union)
        
    elif expresion == "((ε|a)|b*)*":
        afn_epsilon = constructor.epsilon()
        afn_a = constructor.caracter('a')
        afn_eps_a = constructor.union(afn_epsilon, afn_a)
        afn_b = constructor.caracter('b')
        afn_b_star = constructor.estrella(afn_b)
        afn_union = constructor.union(afn_eps_a, afn_b_star)
        afn_final = constructor.estrella(afn_union)
        
    elif expresion == "(a|b)*abb(a|b)*":
        # (a|b)*
        afn_a1 = constructor.caracter('a')
        afn_b1 = constructor.caracter('b')
        afn_union1 = constructor.union(afn_a1, afn_b1)
        afn_prefix = constructor.estrella(afn_union1)
        
        # abb
        afn_a2 = constructor.caracter('a')
        afn_b2 = constructor.caracter('b')
        afn_b3 = constructor.caracter('b')
        afn_ab = constructor.concatenacion(afn_a2, afn_b2)
        afn_abb = constructor.concatenacion(afn_ab, afn_b3)
        
        # (a|b)*
        afn_a3 = constructor.caracter('a')
        afn_b4 = constructor.caracter('b')
        afn_union2 = constructor.union(afn_a3, afn_b4)
        afn_suffix = constructor.estrella(afn_union2)
        
        # Concatenar todo
        afn_temp = constructor.concatenacion(afn_prefix, afn_abb)
        afn_final = constructor.concatenacion(afn_temp, afn_suffix)
        
    elif expresion == "0?(1?)?0*":
        # 0?
        afn_0_1 = constructor.caracter('0')
        afn_0_opt = constructor.opcional(afn_0_1)
        
        # 1?
        afn_1 = constructor.caracter('1')
        afn_1_opt = constructor.opcional(afn_1)
        
        # (1?)?
        afn_1_opt_opt = constructor.opcional(afn_1_opt)
        
        # 0*
        afn_0_2 = constructor.caracter('0')
        afn_0_star = constructor.estrella(afn_0_2)
        
        # Concatenar todo
        afn_temp = constructor.concatenacion(afn_0_opt, afn_1_opt_opt)
        afn_final = constructor.concatenacion(afn_temp, afn_0_star)
    
    else:
        print(f"Expresión {expresion} no implementada en este ejemplo")
        return None
    
    print("\n--- AFN construido con Thompson ---")
    afn_final.mostrar()
    
    print("\n--- Conversión a AFD ---")
    conversor = ConversorAFD(afn_final)
    conversor.convertir()
    conversor.mostrar_afd()
    
    return afn_final

def procesar_expresion_compleja_g(constructor):
    """
    Procesa: if\([ae]+\)\{[ei]+\}(\n(else\{[jl]+\}))?
    Interpretando \ como escape: if([ae]+){[ei]+}(\n(else{[jl]+}))?
    """
    print(f"\n=== Procesando expresión g: if([ae]+){{[ei]+}}(\\n(else{{[jl]+}}))? ===")
    
    # Parte 1: "if"
    afn_if = constructor.cadena("if")
    
    # Parte 2: "("
    afn_paren_izq = constructor.caracter('(')
    
    # Parte 3: [ae]+
    afn_ae_class = constructor.clase_caracteres(['a', 'e'])
    afn_ae_plus = constructor.mas(afn_ae_class)
    
    # Parte 4: ")"
    afn_paren_der = constructor.caracter(')')
    
    # Parte 5: "{"
    afn_llave_izq = constructor.caracter('{')
    
    # Parte 6: [ei]+
    afn_ei_class = constructor.clase_caracteres(['e', 'i'])
    afn_ei_plus = constructor.mas(afn_ei_class)
    
    # Parte 7: "}"
    afn_llave_der = constructor.caracter('}')
    
    # Concatenar la parte obligatoria
    afn_temp1 = constructor.concatenacion(afn_if, afn_paren_izq)
    afn_temp2 = constructor.concatenacion(afn_temp1, afn_ae_plus)
    afn_temp3 = constructor.concatenacion(afn_temp2, afn_paren_der)
    afn_temp4 = constructor.concatenacion(afn_temp3, afn_llave_izq)
    afn_temp5 = constructor.concatenacion(afn_temp4, afn_ei_plus)
    afn_parte_obligatoria = constructor.concatenacion(afn_temp5, afn_llave_der)
    
    # Parte opcional: (\n(else\{[jl]+\}))?
    # \n
    afn_newline = constructor.caracter('\n')
    
    # "else"
    afn_else = constructor.cadena("else")
    
    # "{"
    afn_llave_izq2 = constructor.caracter('{')
    
    # [jl]+
    afn_jl_class = constructor.clase_caracteres(['j', 'l'])
    afn_jl_plus = constructor.mas(afn_jl_class)
    
    # "}"
    afn_llave_der2 = constructor.caracter('}')
    
    # Concatenar la parte del else
    afn_else_temp1 = constructor.concatenacion(afn_else, afn_llave_izq2)
    afn_else_temp2 = constructor.concatenacion(afn_else_temp1, afn_jl_plus)
    afn_else_completo = constructor.concatenacion(afn_else_temp2, afn_llave_der2)
    
    # \n(else{[jl]+})
    afn_newline_else = constructor.concatenacion(afn_newline, afn_else_completo)
    
    # Hacer opcional toda la parte del else
    afn_parte_opcional = constructor.opcional(afn_newline_else)
    
    # Concatenar parte obligatoria con opcional
    afn_final = constructor.concatenacion(afn_parte_obligatoria, afn_parte_opcional)
    
    print("\n--- AFN construido con Thompson ---")
    afn_final.mostrar()
    
    print("\n--- Conversión a AFD ---")
    conversor = ConversorAFD(afn_final)
    conversor.convertir()
    conversor.mostrar_afd()
    
    return afn_final

def procesar_expresion_compleja_h(constructor):
    """
    Procesa: [ae03]+@[ae03]+.(com|net|org)(.(gt|cr|co))?
    """
    print(f"\n=== Procesando expresión h: [ae03]+@[ae03]+.(com|net|org)(.(gt|cr|co))? ===")
    
    # Parte 1: [ae03]+
    afn_usuario_class = constructor.clase_caracteres(['a', 'e', '0', '3'])
    afn_usuario = constructor.mas(afn_usuario_class)
    
    # Parte 2: "@"
    afn_arroba = constructor.caracter('@')
    
    # Parte 3: [ae03]+
    afn_dominio_class = constructor.clase_caracteres(['a', 'e', '0', '3'])
    afn_dominio = constructor.mas(afn_dominio_class)
    
    # Parte 4: "."
    afn_punto1 = constructor.caracter('.')
    
    # Parte 5: (com|net|org)
    afn_com = constructor.cadena("com")
    afn_net = constructor.cadena("net")
    afn_org = constructor.cadena("org")
    afn_temp_union1 = constructor.union(afn_com, afn_net)
    afn_tld_principal = constructor.union(afn_temp_union1, afn_org)
    
    # Concatenar las partes obligatorias
    afn_temp1 = constructor.concatenacion(afn_usuario, afn_arroba)
    afn_temp2 = constructor.concatenacion(afn_temp1, afn_dominio)
    afn_temp3 = constructor.concatenacion(afn_temp2, afn_punto1)
    afn_parte_obligatoria = constructor.concatenacion(afn_temp3, afn_tld_principal)
    
    # Parte opcional: (.(gt|cr|co))?
    # "."
    afn_punto2 = constructor.caracter('.')
    
    # (gt|cr|co)
    afn_gt = constructor.cadena("gt")
    afn_cr = constructor.cadena("cr")
    afn_co = constructor.cadena("co")
    afn_temp_union2 = constructor.union(afn_gt, afn_cr)
    afn_tld_pais = constructor.union(afn_temp_union2, afn_co)
    
    # .(gt|cr|co)
    afn_punto_pais = constructor.concatenacion(afn_punto2, afn_tld_pais)
    
    # Hacer opcional
    afn_parte_opcional = constructor.opcional(afn_punto_pais)
    
    # Concatenar todo
    afn_final = constructor.concatenacion(afn_parte_obligatoria, afn_parte_opcional)
    
    print("\n--- AFN construido con Thompson ---")
    afn_final.mostrar()
    
    print("\n--- Conversión a AFD ---")
    conversor = ConversorAFD(afn_final)
    conversor.convertir()
    conversor.mostrar_afd()
    
    return afn_final

# Función principal para probar las expresiones
def main():
    print("=== CONVERTIDOR DE EXPRESIONES REGULARES A AFN Y AFD ===")
    print("Usando algoritmo de Thompson para AFN y construcción de subconjuntos para AFD")
    
    # Expresiones simples (a-f)
    expresiones_simples = [
        "(a|t)c",           # a)
        "(a|b)*",           # b)
        "(a*|b*)*",         # c)
        "((ε|a)|b*)*",      # d)
        "(a|b)*abb(a|b)*",  # e)
        "0?(1?)?0*"         # f)
    ]
    
    print("\n" + "="*80)
    print("PROCESANDO EXPRESIONES SIMPLES (a-f)")
    print("="*80)
    
    for expresion in expresiones_simples:
        constructor = ConstructorThompson()
        procesar_expresion_simple(expresion, constructor)
        print("\n" + "="*60)
    
    # Expresiones complejas (g-h)
    print("\n" + "="*80)
    print("PROCESANDO EXPRESIONES COMPLEJAS (g-h)")
    print("="*80)
    
    # Expresión g
    constructor_g = ConstructorThompson()
    procesar_expresion_compleja_g(constructor_g)
    print("\n" + "="*60)
    
    # Expresión h
    constructor_h = ConstructorThompson()
    procesar_expresion_compleja_h(constructor_h)
    print("\n" + "="*60)
    
    # Resumen de todas las expresiones
    print("\n" + "="*80)
    print("RESUMEN DE TODAS LAS EXPRESIONES PROCESADAS")
    print("="*80)
    print("a) (𝑎|𝑡)𝑐")
    print("b) (𝑎|𝑏)*")
    print("c) (𝑎*|𝑏*)*") 
    print("d) ((𝜀|𝑎)|𝑏*)*")
    print("e) (𝑎|𝑏)*𝑎𝑏𝑏(𝑎|𝑏)*")
    print("f) 0?(1?)?0*")
    print("g) 𝑖𝑓\\([𝑎𝑒]+\\)\\{[𝑒𝑖]+\\}(\\𝑛(𝑒𝑙𝑠𝑒\\{[𝑗𝑙]+\\}))?")
    print("h) [𝑎𝑒03]+@[𝑎𝑒03]+.(𝑐𝑜𝑚|𝑛𝑒𝑡|𝑜𝑟𝑔)(.(𝑔𝑡|𝑐𝑟|𝑐𝑜))?")
    print("\nTodas fueron convertidas exitosamente a AFN (Thompson) y AFD (subconjuntos)")

if __name__ == "__main__":
    main()