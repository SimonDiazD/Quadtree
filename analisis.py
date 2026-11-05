import random
import time
 
import matplotlib.pyplot as plt
 
from quadtree import Quadtree
 
"""
SECCIÓN 1: PARÁMETROS Y DATOS.
"""
SEMILLA = 42
TAMANO_ZONA = 10000          # 10 km expresados en metros
RADIO = 500                  # metros
NUM_CONSULTAS = 100          # ubicaciones consultadas en cada medición
REPETICIONES = 3             # veces que se repite cada medición (se promedia)
 
# Cantidades de puntos que vamos a probar
TAMANOS = [1000, 2500, 5000, 10000, 25000, 50000, 75000, 100000]
 
random.seed(SEMILLA)
 
# Se generan los puntos una sola vez; cada prueba usa los primeros N
todos_los_puntos = [
    (random.uniform(0, TAMANO_ZONA), random.uniform(0, TAMANO_ZONA))
    for _ in range(max(TAMANOS))
]
 
# Ubicaciones donde se hacen las consultas (las mismas para todos los métodos)
consultas = [
    (random.uniform(0, TAMANO_ZONA), random.uniform(0, TAMANO_ZONA))
    for _ in range(NUM_CONSULTAS)
]
 
 
"""
SECCIÓN 2: FUERZA BRUTA (recorrer la lista completa).
"""
def distancia2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
 
 
def vecino_mas_cercano_lista(lista, centro):
    # Revisa todos los puntos y se queda con el más cercano
    return min(lista, key=lambda p: distancia2(p, centro))
 
 
def buscar_radio_lista(lista, centro, radio):
    # Revisa todos los puntos y se queda con los que están a <= radio
    return [p for p in lista if distancia2(p, centro) <= radio ** 2]
 
 
"""
SECCIÓN 3: MEDICIÓN DE TIEMPO.
"""
def medir(operacion):
    # Ejecuta la operación para las 100 consultas, REPETICIONES veces,
    # y devuelve el tiempo promedio de una pasada completa (en segundos).
    tiempos = []
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        for centro in consultas:
            operacion(centro)
        tiempos.append(time.perf_counter() - inicio)
    return sum(tiempos) / len(tiempos)
 
 
"""
SECCIÓN 4: EXPERIMENTO.
"""
limites = (0, TAMANO_ZONA, 0, TAMANO_ZONA)
 
# Aquí se guardan los resultados, un valor por cada tamaño probado
vecino_lista, vecino_arbol = [], []
radio_lista, radio_arbol = [], []
 
print(f"{'N':>7} | {'Vecino: lista':>14} {'Vecino: árbol':>14} | "
      f"{'Radio: lista':>13} {'Radio: árbol':>13}   (segundos por {NUM_CONSULTAS} consultas)")
 
for n in TAMANOS:
    # La lista y el árbol contienen exactamente los mismos N puntos
    lista = todos_los_puntos[:n]
    arbol = Quadtree(limites, capacidad=4)
    arbol.insertar_puntos(lista)
 
    # Comprobación rápida: ambos métodos deben dar el mismo resultado
    centro = consultas[0]
    assert arbol.buscar_vecino_mas_cercano(centro)[0] == vecino_mas_cercano_lista(lista, centro)
    assert sorted(arbol.buscar_radio(centro, RADIO)) == sorted(buscar_radio_lista(lista, centro, RADIO))
 
    # Tiempos del vecino más cercano
    vecino_lista.append(medir(lambda c: vecino_mas_cercano_lista(lista, c)))
    vecino_arbol.append(medir(lambda c: arbol.buscar_vecino_mas_cercano(c)))
 
    # Tiempos de la búsqueda por radio
    radio_lista.append(medir(lambda c: buscar_radio_lista(lista, c, RADIO)))
    radio_arbol.append(medir(lambda c: arbol.buscar_radio(c, RADIO)))
 
    print(f"{n:>7} | {vecino_lista[-1]:>14.5f} {vecino_arbol[-1]:>14.5f} | "
          f"{radio_lista[-1]:>13.5f} {radio_arbol[-1]:>13.5f}")
 
 
"""
SECCIÓN 5: RESULTADO
"""
def mediciontiempos(tiempos_lista, tiempos_arbol):
    for n, t_lista, t_arbol in zip(TAMANOS, tiempos_lista, tiempos_arbol):
        if t_arbol < t_lista:
            return n
    return None
 
 
for nombre, t_lista, t_arbol in [
    ("vecino más cercano", vecino_lista, vecino_arbol),
    ("búsqueda en radio", radio_lista, radio_arbol),
]:
    n = mediciontiempos(t_lista, t_arbol)
    if n is None:
        print(f"\n{nombre}: el árbol no fue más rápido en los tamaños probados.")
    else:
        print(f"\n{nombre}: el árbol es más rápido desde N = {n} puntos.")
 
 
"""
SECCIÓN 6: GRÁFICAS.
"""
fig, (grafica_vecino, grafica_radio) = plt.subplots(1, 2, figsize=(14, 6))
 
for grafica, t_lista, t_arbol, titulo in [
    (grafica_vecino, vecino_lista, vecino_arbol, "Vecino más cercano"),
    (grafica_radio, radio_lista, radio_arbol, f"Búsqueda en radio de {RADIO} m"),
]:
    grafica.plot(TAMANOS, t_lista, marker="o", label="Lista (fuerza bruta)")
    grafica.plot(TAMANOS, t_arbol, marker="o", label="Quadtree")
    grafica.set_xscale("log")
    grafica.set_yscale("log")
    grafica.set_xticks(TAMANOS)
    grafica.set_xticklabels([f"{n:,}" for n in TAMANOS], rotation=45)
    grafica.minorticks_off()
    grafica.set_title(titulo)
    grafica.set_xlabel("Cantidad de puntos (N)")
    grafica.set_ylabel(f"Tiempo de {NUM_CONSULTAS} consultas (s)")
    grafica.grid(True, alpha=0.3)
    grafica.legend()
 
plt.tight_layout()
plt.savefig("comparacion_quadtree_vs_lista.png", dpi=150)
plt.show()