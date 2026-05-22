# models.py - MODELOS DE DATOS

from dataclasses import dataclass
from typing import Optional, List
import math

@dataclass
class Nodo:
    """Representa un nodo en el grafo (intersección, base o empresa)"""
    nombre: str
    tipo: str = "interseccion"
    x: Optional[int] = None
    y: Optional[int] = None

    def __repr__(self):
        return self.nombre


@dataclass
class Arista:
    """Representa una arista en el grafo con peso base y tráfico"""
    origen: str
    destino: str
    peso_base: float
    trafico: float = 1.0

    @property
    def peso_efectivo(self) -> float:
        """Calcula el peso considerando el tráfico"""
        return self.peso_base * self.trafico


class Grafo:
    """Estructura de grafo con nodos y aristas para la ciudad"""
    
    def __init__(self):
        self._nodos: dict[str, Nodo] = {}
        self._ady: dict[str, list[Arista]] = {}

    def agregar_nodo(self, nombre, tipo="interseccion", x=None, y=None) -> Nodo:
        """Agrega un nuevo nodo al grafo"""
        if nombre in self._nodos:
            raise ValueError(f"Nodo '{nombre}' ya existe")
        n = Nodo(nombre, tipo, x, y)
        self._nodos[nombre] = n
        self._ady[nombre] = []
        return n

    def obtener_nodo(self, nombre) -> Optional[Nodo]:
        """Obtiene un nodo por nombre"""
        return self._nodos.get(nombre)

    def nodos(self):
        """Retorna lista de todos los nodos"""
        return list(self._nodos.values())

    def __contains__(self, n):
        return n in self._nodos

    def __len__(self):
        return len(self._nodos)

    def agregar_arista(self, origen, destino, peso, bidireccional=True):
        """Agrega una arista entre dos nodos"""
        for n in (origen, destino):
            if n not in self._nodos:
                raise ValueError(f"Nodo '{n}' no existe")
        if peso <= 0:
            raise ValueError("Peso debe ser > 0")
        self._ady[origen].append(Arista(origen, destino, peso))
        if bidireccional:
            self._ady[destino].append(Arista(destino, origen, peso))

    def vecinos(self, nombre) -> List[Arista]:
        """Retorna las aristas adyacentes de un nodo"""
        return self._ady.get(nombre, [])

    def todas_aristas(self) -> List[Arista]:
        """Retorna todas las aristas del grafo"""
        r = []
        for lst in self._ady.values():
            r.extend(lst)
        return r

    def aplicar_trafico(self, origen, destino, mult, bidireccional=True) -> bool:
        """Modifica el tráfico de una arista"""
        ok = False
        for a in self._ady.get(origen, []):
            if a.destino == destino:
                a.trafico = mult
                ok = True
        if bidireccional:
            for a in self._ady.get(destino, []):
                if a.destino == origen:
                    a.trafico = mult
                    ok = True
        return ok

    def resetear_trafico(self):
        """Resetea el tráfico de todas las aristas"""
        for lst in self._ady.values():
            for a in lst:
                a.trafico = 1.0


@dataclass
class ResultadoRuta:
    """Resultado de una búsqueda de ruta"""
    origen: str
    destino: str
    camino: list
    coste: float
    detalle: list
    encontrada: bool = False
