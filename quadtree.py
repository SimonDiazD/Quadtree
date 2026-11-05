
class NodoQuadtree:
    def __init__(self, limites, capacidad=4):
        self.min_x, self.max_x, self.min_y, self.max_y = limites
        self.capacidad = capacidad
        self.puntos = []
        self.hijos = None

    def subdividir(self):
        mitad_x = (self.min_x + self.max_x) / 2
        mitad_y = (self.min_y + self.max_y) / 2

        def crear_hijo(limites):
            return NodoQuadtree(limites, self.capacidad)

        self.hijos = {
            "NO": crear_hijo((self.min_x, mitad_x, mitad_y, self.max_y)),
            "NE": crear_hijo((mitad_x, self.max_x, mitad_y, self.max_y)),
            "SO": crear_hijo((self.min_x, mitad_x, self.min_y, mitad_y)),
            "SE": crear_hijo((mitad_x, self.max_x, self.min_y, mitad_y))
        }

    def _insertar_en_hijo(self, punto):
        x, y = punto

        mitad_x = (self.min_x + self.max_x) / 2
        mitad_y = (self.min_y + self.max_y) / 2

        if x < mitad_x:
            hijo = self.hijos["SO"] if y < mitad_y else self.hijos["NO"]
        else:
            hijo = self.hijos["SE"] if y < mitad_y else self.hijos["NE"]

        return hijo.insertar(punto)

    def insertar(self, punto):
        x, y = punto

        # Comprobar si el punto pertenece a esta región
        if not (self.min_x <= x <= self.max_x and
                self.min_y <= y <= self.max_y):
            return False

        # Si todavía hay espacio, almacenar el punto
        if self.hijos is None:
            if len(self.puntos) < self.capacidad:
                self.puntos.append(punto)
                return True

            # Si se alcanzó la capacidad, subdividir
            self.subdividir()

            puntos_anteriores = self.puntos
            self.puntos = []

            # Redistribuir los puntos anteriores
            for p in puntos_anteriores:
                self._insertar_en_hijo(p)

        # Insertar en la región correspondiente
        return self._insertar_en_hijo(punto)

    
    def intersecta_radio(self, centro, radio):
        x, y = centro

        # Distancia mínima desde el centro hasta el rectángulo
        dx = max(self.min_x - x, 0, x - self.max_x)
        dy = max(self.min_y - y, 0, y - self.max_y)

        return dx**2 + dy**2 <= radio**2

    def buscar_radio(self, centro, radio):
        x, y = centro

        # Descartar regiones que no intersectan el círculo
        if not self.intersecta_radio(centro, radio):
            return []

        # Si es una hoja, revisar sus puntos
        if self.hijos is None:
            encontrados = []

            for px, py in self.puntos:
                distancia2 = (px - x)**2 + (py - y)**2

                if distancia2 <= radio**2:
                    encontrados.append((px, py))

            return encontrados

        # Si tiene hijos, buscar recursivamente
        encontrados = []

        for hijo in self.hijos.values():
            encontrados.extend(hijo.buscar_radio(centro, radio))

        return encontrados

    
    def distancia_minima2(self, centro):
        x, y = centro

        dx = max(self.min_x - x, 0, x - self.max_x)
        dy = max(self.min_y - y, 0, y - self.max_y)

        return dx**2 + dy**2

    def buscar_mas_cercano(self, centro, mejor_punto=None,
                           mejor_distancia2=float("inf")):

        # Descartar regiones que no pueden mejorar el resultado
        if self.distancia_minima2(centro) > mejor_distancia2:
            return mejor_punto, mejor_distancia2

        # Si es una hoja, revisar sus puntos
        if self.hijos is None:

            x, y = centro

            for px, py in self.puntos:
                distancia2 = (px - x)**2 + (py - y)**2

                if distancia2 < mejor_distancia2:
                    mejor_distancia2 = distancia2
                    mejor_punto = (px, py)

        else:
            # Revisar primero las regiones más cercanas
            hijos_ordenados = sorted(
                self.hijos.values(),
                key=lambda hijo: hijo.distancia_minima2(centro)
            )

            for hijo in hijos_ordenados:
                mejor_punto, mejor_distancia2 = hijo.buscar_mas_cercano(
                    centro, mejor_punto, mejor_distancia2
                )

        return mejor_punto, mejor_distancia2

    def contar_puntos(self):
        if self.hijos is None:
            return len(self.puntos)

        return sum(hijo.contar_puntos() for hijo in self.hijos.values())

class Quadtree:
    def __init__(self, limites, capacidad=4):
        self.raiz = NodoQuadtree(limites, capacidad)

    def insertar(self, punto):
        return self.raiz.insertar(punto)

    def insertar_puntos(self, puntos):
        for punto in puntos:
            if not self.insertar(punto):
                raise ValueError(f"Punto fuera de los límites: {punto}")

    def buscar_radio(self, centro, radio=500):
        return self.raiz.buscar_radio(centro, radio)

    def contar_puntos(self):
        return self.raiz.contar_puntos()

    def buscar_vecino_mas_cercano(self, centro):
        punto, distancia2 = self.raiz.buscar_mas_cercano(centro)

        if punto is None:
            return None

        distancia = distancia2**0.5

        return punto, distancia
