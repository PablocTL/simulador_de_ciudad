# algorithm.py - ALGORITMO DE DIJKSTRA

import heapq
import math
from models import Grafo, ResultadoRuta


def dijkstra(grafo: Grafo, origen: str, destino: str) -> ResultadoRuta:
    """
    Implementa el algoritmo de Dijkstra para encontrar el camino más corto.
    
    Args:
        grafo: El grafo de la ciudad
        origen: Nombre del nodo origen
        destino: Nombre del nodo destino
    
    Returns:
        ResultadoRuta con el camino encontrado, coste y detalles
    """
    # Inicializar distancias y previos
    dist = {n.nombre: math.inf for n in grafo.nodos()}
    previo = {n.nombre: None for n in grafo.nodos()}
    arista_u = {n.nombre: None for n in grafo.nodos()}
    dist[origen] = 0.0
    
    # Usar heap para procesar nodos en orden de distancia
    heap = [(0.0, origen)]
    vis = set()

    while heap:
        cost, cur = heapq.heappop(heap)
        
        # Saltar si ya visitamos este nodo
        if cur in vis:
            continue
        vis.add(cur)
        
        # Terminar si llegamos al destino
        if cur == destino:
            break
        
        # Procesar vecinos
        for a in grafo.vecinos(cur):
            nc = cost + a.peso_efectivo
            if nc < dist[a.destino]:
                dist[a.destino] = nc
                previo[a.destino] = cur
                arista_u[a.destino] = a
                heapq.heappush(heap, (nc, a.destino))

    # Verificar si se encontró ruta
    if dist[destino] == math.inf:
        return ResultadoRuta(origen, destino, [], math.inf, [], False)

    # Reconstruir el camino
    camino, cur = [], destino
    while cur:
        camino.append(cur)
        cur = previo[cur]
    camino.reverse()

    # Crear detalle de la ruta
    detalle = []
    for i in range(len(camino) - 1):
        a = arista_u[camino[i + 1]]
        detalle.append((camino[i], camino[i + 1], a.peso_efectivo if a else 0))

    return ResultadoRuta(origen, destino, camino, dist[destino], detalle, True)
