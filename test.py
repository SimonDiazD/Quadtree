# Esta libreria nos ayudara a generar los puntos.
import random
# Esta libreria es la que nos ayudar a crear los graficos.
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from quadtree import Quadtree

"""
SECCIÓN 1: GENERACIÓN DE PUNTOS Y DELIMITACIÓN DE LA ZONA.
"""
# Con esta semilla, cada vez que ejecutemos el código, obtendremos los mismos puntos.
SEMILLA = 42
CANTIDAD_PUNTOS = 10000
TAMANO_ZONA = 10000  # 10 km expresados en metros

# Generación reproducible
random.seed(SEMILLA)

puntos = []

for i in range(CANTIDAD_PUNTOS):
    x = random.uniform(0, TAMANO_ZONA)
    y = random.uniform(0, TAMANO_ZONA)

    puntos.append((x, y))
print(f"Cantidad de puntos: {len(puntos)}")


# Límites de la zona
min_x = min(p[0] for p in puntos)
max_x = max(p[0] for p in puntos)

min_y = min(p[1] for p in puntos)
max_y = max(p[1] for p in puntos)

print("\nLímites de la zona:")
print(f"X: {min_x:.2f} - {max_x:.2f}")
print(f"Y: {min_y:.2f} - {max_y:.2f}")


"""
SECCIÓN 2: CONSTRUCCIÓN DEL ÁRBOL QUADTREE.
"""
# Definir los límites de nuestra zona
limites = (min_x, max_x, min_y, max_y)

# Crear el árbol
arbol = Quadtree(limites, capacidad=4)

# Insertar los 10.000 puntos
arbol.insertar_puntos(puntos)

# Verificar
print("\nÁRBOL CONSTRUIDO. \nPuntos almacenados:", arbol.contar_puntos())


"""
SECCIÓN 3: BUSQUEDA POR RADIO.
"""

# Ubicación de consulta para la búsqueda por radio
centro_radio = puntos[5000]

# Radio de búsqueda: 500 metros
radio = 500

# Consultar el Quadtree
vecinos = arbol.buscar_radio(centro_radio, radio)

print("\nBUSQUEDA POR RADIO DE 500 METROS")
print("Ubicación consultada:", centro_radio)
print("Radio:", radio, "metros")
print("Puntos encontrados:", len(vecinos))
print("Primeros 5 puntos encontrados:")

for punto in vecinos[:5]:
    print(punto)


"""
SECCIÓN 4: BUSQUEDA DE VECINO MÁS CERCANO.
"""
# Ubicación de consulta para el vecino más cercano
centro_vecino = (2500, 5000)

# Buscar vecino más cercano
resultado = arbol.buscar_vecino_mas_cercano(centro_vecino)

if resultado is not None:
    vecino, distancia = resultado
    print("\nBUSQUEDA DE VECINO MAS CERCANO")
    print("Ubicación consultada:", centro_vecino)
    print("Vecino más cercano:", vecino)
    print(f"Distancia: {distancia:.2f} metros")
else:
    print("No hay puntos en el árbol.")


"""
SECCIÓN 5: VERIFICACIÓN VISUAL.
"""
resultado_vecino = arbol.buscar_vecino_mas_cercano(centro_vecino)

fig, (grafica_radio, grafica_vecino) = plt.subplots(1, 2, figsize=(14, 6))

grafica_radio.scatter(*zip(*puntos), s=4, color="lightgray", label="Puntos")
grafica_radio.scatter(
    *zip(*vecinos), s=12, color="red", label="Puntos encontrados"
)
grafica_radio.scatter(
    *centro_radio, s=60, color="blue", label="Centro de consulta"
)
grafica_radio.add_patch(
    Circle(centro_radio, radio, fill=False, color="blue", linewidth=2)
)
grafica_radio.set_title("Búsqueda en radio de 500 m")
grafica_radio.set_xlabel("X (m)")
grafica_radio.set_ylabel("Y (m)")
grafica_radio.legend()
grafica_radio.set_aspect("equal")

grafica_vecino.scatter(*zip(*puntos), s=4, color="lightgray", label="Puntos")
grafica_vecino.scatter(
    *centro_vecino, s=60, color="blue", label="Centro de consulta"
)
if resultado_vecino is not None:
    vecino, distancia = resultado_vecino
    grafica_vecino.scatter(
        *vecino, s=80, color="green", label="Vecino más cercano"
    )
    grafica_vecino.plot(
        [centro_vecino[0], vecino[0]],
        [centro_vecino[1], vecino[1]],
        color="green",
        linestyle="--",
        label=f"Distancia: {distancia:.2f} m",
    )
grafica_vecino.set_title("Verificación del vecino más cercano")
grafica_vecino.set_xlabel("X (m)")
grafica_vecino.set_ylabel("Y (m)")
grafica_vecino.legend()
grafica_vecino.set_aspect("equal")

plt.tight_layout()
plt.savefig("verificacion_visual_quadtree.png")
plt.show()
