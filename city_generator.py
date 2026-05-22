# city_generator.py - GENERADOR Y PERSISTENCIA DE CIUDADES

import json
import os
from models import Grafo
from config import FILAS, GRID_SIZE


DATA_DIR = "ciudades"


def crear_ciudad_20x20() -> Grafo:
    """Crea una cuadrícula de 20x20 con aristas ponderadas"""
    g = Grafo()
    
    # Agregar nodos en la cuadrícula
    for fi, f in enumerate(FILAS):
        for ci in range(GRID_SIZE):
            g.agregar_nodo(f"{f}{ci+1}", "interseccion", ci, fi)

    # Aristas horizontales
    for fi, f in enumerate(FILAS):
        for ci in range(GRID_SIZE - 1):
            p = 1.0 if f in ('A', 'F', 'K', 'P') else 2.0
            if f == 'D' and (ci + 1) % 3 == 0:
                p = 3.0
            g.agregar_arista(f"{f}{ci+1}", f"{f}{ci+2}", p)

    # Aristas verticales
    for ci in range(GRID_SIZE):
        for fi in range(GRID_SIZE - 1):
            p = 1.0 if ci in (0, 5, 10, 15) else 2.0
            if ci == 9 and fi % 4 == 0:
                p = 3.5
            g.agregar_arista(f"{FILAS[fi]}{ci+1}", f"{FILAS[fi+1]}{ci+1}", p)

    # Aristas diagonales
    for f in ('A', 'F', 'K', 'P'):
        for c in (1, 6, 11, 16):
            fi = FILAS.index(f)
            if c < GRID_SIZE and fi < GRID_SIZE - 1:
                try:
                    g.agregar_arista(f"{f}{c}", f"{FILAS[fi+1]}{c+1}", 1.2)
                except:
                    pass
                if c > 1:
                    try:
                        g.agregar_arista(f"{f}{c}", f"{FILAS[fi+1]}{c-1}", 1.2)
                    except:
                        pass
    return g


def cargar_ciudad_prueba(g: Grafo):
    """Carga una configuración de prueba con bases, empresas y zonas de tráfico"""
    # Bases militares
    bases = ["A1", "A10", "A20", "T1", "T10", "T20", "D5", "D15",
             "F1", "F20", "K1", "K20", "P1", "P20", "J10", "L10"]
    for b in bases:
        n = g.obtener_nodo(b)
        if n:
            n.tipo = "base"
    
    # Empresas
    empresas = ["B3", "C7", "D2", "E5", "B18", "C14", "D17", "E12",
                "R4", "S8", "Q3", "P5", "R18", "S15", "Q17", "P15",
                "G8", "H12", "I6", "J14", "M7", "N11", "O9", "L14",
                "C1", "C20", "R1", "R20", "F10", "K15"]
    for e in empresas:
        n = g.obtener_nodo(e)
        if n:
            n.tipo = "empresa"
    
    # Zonas de tráfico
    zonas = [("K10", "K11", 3.5), ("K10", "J10", 2.8), ("K10", "L10", 2.8),
             ("J10", "I10", 3.0), ("F10", "F11", 2.5), ("F9", "F10", 2.5),
             ("P10", "P11", 3.0), ("D15", "D16", 4.0), ("R4", "R5", 3.2)]
    for o, d, m in zonas:
        g.aplicar_trafico(o, d, m)


def guardar_ciudad(grafo: Grafo, nombre: str) -> bool:
    """Guarda una ciudad en formato JSON"""
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        # Preparar datos
        nodos_data = []
        for n in grafo.nodos():
            nodos_data.append({
                "nombre": n.nombre,
                "tipo": n.tipo,
                "x": n.x,
                "y": n.y
            })
        
        aristas_data = []
        seen = set()
        for a in grafo.todas_aristas():
            key = tuple(sorted([a.origen, a.destino]))
            if key not in seen:
                seen.add(key)
                aristas_data.append({
                    "origen": a.origen,
                    "destino": a.destino,
                    "peso_base": a.peso_base,
                    "trafico": a.trafico
                })
        
        data = {
            "nodos": nodos_data,
            "aristas": aristas_data
        }
        
        # Guardar JSON
        filepath = os.path.join(DATA_DIR, f"{nombre}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error al guardar: {e}")
        return False


def cargar_ciudad_json(filepath: str) -> Grafo:
    """Carga una ciudad desde un archivo JSON"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        g = Grafo()
        
        # Cargar nodos
        for n_data in data.get("nodos", []):
            g.agregar_nodo(n_data["nombre"], n_data.get("tipo", "interseccion"),
                          n_data.get("x"), n_data.get("y"))
        
        # Cargar aristas
        for a_data in data.get("aristas", []):
            g.agregar_arista(a_data["origen"], a_data["destino"],
                            a_data["peso_base"], bidireccional=False)
            # Restaurar tráfico si es diferente
            if a_data.get("trafico", 1.0) != 1.0:
                g.aplicar_trafico(a_data["origen"], a_data["destino"],
                                 a_data["trafico"], bidireccional=False)
        
        return g
    except Exception as e:
        print(f"Error al cargar: {e}")
        return None


def listar_ciudades() -> list:
    """Lista las ciudades guardadas"""
    ciudades = []
    try:
        if not os.path.exists(DATA_DIR):
            return ciudades
        
        for archivo in os.listdir(DATA_DIR):
            if archivo.endswith('.json'):
                filepath = os.path.join(DATA_DIR, archivo)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    ciudades.append({
                        "nombre": archivo[:-5],  # Sin .json
                        "archivo": filepath,
                        "nodos": len(data.get("nodos", [])),
                        "calles": len(data.get("aristas", []))
                    })
                except:
                    pass
    except Exception as e:
        print(f"Error al listar ciudades: {e}")
    
    return ciudades
