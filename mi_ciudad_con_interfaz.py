
#SIMULADOR DE CIUDAD – GRAFOS


import heapq
import math
import json
import os
import sys
import pygame
from dataclasses import dataclass, field
from typing import Optional, Tuple


# PALETA DE COLORES  (estética oscura/neon)

BG          = (13,  15,  20)
SURFACE     = (20,  24,  34)
PANEL       = (26,  31,  46)
BORDER      = (37,  45,  61)
ACCENT      = (0,   229, 255)   # cian
ACCENT2     = (255, 107, 53)    # naranja
ACCENT3     = (57,  255, 20)    # verde neón
RED         = (255, 59,  92)
BLUE        = (74,  158, 255)
YELLOW      = (255, 210, 63)
MUTED       = (107, 122, 153)
TEXT        = (224, 230, 240)
WHITE       = (255, 255, 255)

NODE_BASE      = RED
NODE_EMPRESA   = BLUE
NODE_INTER     = (42,  54,  80)
NODE_INTER_LIT = (55,  70, 100)
EDGE_FAST      = ACCENT3
EDGE_NORMAL    = (37,  48,  70)
EDGE_TRAFFIC   = ACCENT2
EDGE_ROUTE     = ACCENT


# MODELOS DE DATOS
# 
@dataclass
class Nodo:
    nombre: str
    tipo: str = "interseccion"
    x: Optional[int] = None
    y: Optional[int] = None

    def __repr__(self): return self.nombre

@dataclass
class Arista:
    origen: str
    destino: str
    peso_base: float
    trafico: float = 1.0

    @property
    def peso_efectivo(self) -> float:
        return self.peso_base * self.trafico

class Grafo:
    def __init__(self):
        self._nodos: dict[str, Nodo] = {}
        self._ady:   dict[str, list[Arista]] = {}

    def agregar_nodo(self, nombre, tipo="interseccion", x=None, y=None):
        if nombre in self._nodos:
            raise ValueError(f"Nodo '{nombre}' ya existe")
        n = Nodo(nombre, tipo, x, y)
        self._nodos[nombre] = n
        self._ady[nombre] = []
        return n

    def obtener_nodo(self, nombre) -> Optional[Nodo]:
        return self._nodos.get(nombre)

    def nodos(self): return list(self._nodos.values())
    def __contains__(self, n): return n in self._nodos
    def __len__(self): return len(self._nodos)

    def agregar_arista(self, origen, destino, peso, bidireccional=True):
        for n in (origen, destino):
            if n not in self._nodos:
                raise ValueError(f"Nodo '{n}' no existe")
        if peso <= 0: raise ValueError("Peso debe ser > 0")
        self._ady[origen].append(Arista(origen, destino, peso))
        if bidireccional:
            self._ady[destino].append(Arista(destino, origen, peso))

    def vecinos(self, nombre): return self._ady.get(nombre, [])

    def todas_aristas(self):
        r = []
        for lst in self._ady.values(): r.extend(lst)
        return r

    def aplicar_trafico(self, origen, destino, mult, bidireccional=True):
        ok = False
        for a in self._ady.get(origen, []):
            if a.destino == destino: a.trafico = mult; ok = True
        if bidireccional:
            for a in self._ady.get(destino, []):
                if a.destino == origen: a.trafico = mult; ok = True
        return ok

    def resetear_trafico(self):
        for lst in self._ady.values():
            for a in lst: a.trafico = 1.0


# DIJKSTRA

@dataclass
class ResultadoRuta:
    origen: str
    destino: str
    camino: list
    coste: float
    detalle: list
    encontrada: bool = False

def dijkstra(grafo: Grafo, origen: str, destino: str) -> ResultadoRuta:
    dist    = {n.nombre: math.inf for n in grafo.nodos()}
    previo  = {n.nombre: None     for n in grafo.nodos()}
    arista_u= {n.nombre: None     for n in grafo.nodos()}
    dist[origen] = 0.0
    heap = [(0.0, origen)]
    vis  = set()

    while heap:
        cost, cur = heapq.heappop(heap)
        if cur in vis: continue
        vis.add(cur)
        if cur == destino: break
        for a in grafo.vecinos(cur):
            nc = cost + a.peso_efectivo
            if nc < dist[a.destino]:
                dist[a.destino] = nc
                previo[a.destino] = cur
                arista_u[a.destino] = a
                heapq.heappush(heap, (nc, a.destino))

    if dist[destino] == math.inf:
        return ResultadoRuta(origen, destino, [], math.inf, [], False)

    camino, cur = [], destino
    while cur: camino.append(cur); cur = previo[cur]
    camino.reverse()

    detalle = []
    for i in range(len(camino)-1):
        a = arista_u[camino[i+1]]
        detalle.append((camino[i], camino[i+1], a.peso_efectivo if a else 0))

    return ResultadoRuta(origen, destino, camino, dist[destino], detalle, True)


# GENERADOR CIUDAD 20×20

FILAS = list('ABCDEFGHIJKLMNOPQRST')

def crear_ciudad_20x20() -> Grafo:
    g = Grafo()
    for fi, f in enumerate(FILAS):
        for ci in range(20):
            g.agregar_nodo(f"{f}{ci+1}", "interseccion", ci, fi)

    for fi, f in enumerate(FILAS):
        for ci in range(19):
            p = 1.0 if f in ('A','F','K','P') else 2.0
            if f == 'D' and (ci+1) % 3 == 0: p = 3.0
            g.agregar_arista(f"{f}{ci+1}", f"{f}{ci+2}", p)

    for ci in range(20):
        for fi in range(19):
            p = 1.0 if ci in (0,5,10,15) else 2.0
            if ci == 9 and fi % 4 == 0: p = 3.5
            g.agregar_arista(f"{FILAS[fi]}{ci+1}", f"{FILAS[fi+1]}{ci+1}", p)

    for f in ('A','F','K','P'):
        for c in (1,6,11,16):
            fi = FILAS.index(f)
            if c < 20 and fi < 19:
                try: g.agregar_arista(f"{f}{c}", f"{FILAS[fi+1]}{c+1}", 1.2)
                except: pass
                if c > 1:
                    try: g.agregar_arista(f"{f}{c}", f"{FILAS[fi+1]}{c-1}", 1.2)
                    except: pass
    return g

def cargar_ciudad_prueba(g: Grafo):
    bases = ["A1","A10","A20","T1","T10","T20","D5","D15",
            "F1","F20","K1","K20","P1","P20","J10","L10"]
    for b in bases:
        n = g.obtener_nodo(b)
        if n: n.tipo = "base"
    empresas = ["B3","C7","D2","E5","B18","C14","D17","E12",
                "R4","S8","Q3","P5","R18","S15","Q17","P15",
                "G8","H12","I6","J14","M7","N11","O9","L14",
                "C1","C20","R1","R20","F10","K15"]
    for e in empresas:
        n = g.obtener_nodo(e)
        if n: n.tipo = "empresa"
    zonas = [("K10","K11",3.5),("K10","J10",2.8),("K10","L10",2.8),
            ("J10","I10",3.0),("F10","F11",2.5),("F9","F10",2.5),
            ("P10","P11",3.0),("D15","D16",4.0),("R4","R5",3.2)]
    for o,d,m in zonas:
        g.aplicar_trafico(o,d,m)


# HELPERS DE DIBUJO

def draw_rect_rounded(surf, color, rect, r=6, alpha=255):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0,0,rect[2],rect[3]), border_radius=r)
    surf.blit(s, (rect[0], rect[1]))

def draw_text(surf, text, font, color, x, y, center=False, right=False):
    img = font.render(str(text), True, color)
    if center: x -= img.get_width() // 2
    if right:  x -= img.get_width()
    surf.blit(img, (x, y))
    return img.get_width(), img.get_height()

def glow_circle(surf, color, cx, cy, r, glow=8):
    for i in range(glow, 0, -1):
        alpha = int(60 * (i / glow))
        s = pygame.Surface((r*2+glow*2, r*2+glow*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, alpha), (r+glow, r+glow), r+i)
        surf.blit(s, (cx-r-glow, cy-r-glow))
    pygame.draw.circle(surf, color, (cx, cy), r)

def glow_line(surf, color, p1, p2, w=2, glow=4):
    for i in range(glow, 0, -1):
        alpha = int(80 * (i / glow))
        s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.line(s, (*color, alpha), p1, p2, w + i*2)
        surf.blit(s, (0,0))
    pygame.draw.line(surf, color, p1, p2, w)


# INPUT BOX

class InputBox:
    def __init__(self, x, y, w, h, font, placeholder="", value=""):
        self.rect   = pygame.Rect(x, y, w, h)
        self.font   = font
        self.placeholder = placeholder
        self.value  = value
        self.active = False
        self.cursor_timer = 0

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(e.pos)
        if e.type == pygame.KEYDOWN and self.active:
            if e.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif e.key in (pygame.K_RETURN, pygame.K_TAB):
                self.active = False
            else:
                if len(self.value) < 15: # Aumentado el límite de caracteres
                    self.value += e.unicode.upper()

    def update(self, dt):
        self.cursor_timer += dt

    def draw(self, surf):
        bc = ACCENT if self.active else BORDER
        pygame.draw.rect(surf, PANEL, self.rect, border_radius=4)
        pygame.draw.rect(surf, bc,    self.rect, 1, border_radius=4)
        txt = self.value if self.value else self.placeholder
        col = TEXT if self.value else MUTED
        tw, _ = draw_text(surf, txt, self.font, col,
                          self.rect.x+8, self.rect.y+self.rect.h//2-8)
        if self.active and (self.cursor_timer//500) % 2 == 0:
            cx = self.rect.x + 8 + tw + 2
            pygame.draw.line(surf, ACCENT,
                             (cx, self.rect.y+5), (cx, self.rect.bottom-5), 1)


# BUTTON

class Button:
    def __init__(self, x, y, w, h, label, font, color=ACCENT, text_color=(0,0,0)):
        self.rect   = pygame.Rect(x, y, w, h)
        self.label  = label
        self.font   = font
        self.color  = color
        self.tc     = text_color
        self.hovered= False

    def handle_event(self, e):
        if e.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(e.pos)
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            return self.rect.collidepoint(e.pos)
        return False

    def draw(self, surf):
        c = tuple(min(255,v+30) for v in self.color) if self.hovered else self.color
        pygame.draw.rect(surf, c, self.rect, border_radius=4)
        draw_text(surf, self.label, self.font, self.tc,
                  self.rect.centerx, self.rect.centery-7, center=True)


# SLIDER

class Slider:
    def __init__(self, x, y, w, mn, mx, val, font):
        self.rect  = pygame.Rect(x, y, w, 6)
        self.mn, self.mx = mn, mx
        self.val   = val
        self.font  = font
        self.dragging = False
        self.knob_r = 8

    @property
    def norm(self): return (self.val - self.mn) / (self.mx - self.mn)

    def knob_pos(self):
        return (self.rect.x + int(self.norm * self.rect.w), self.rect.centery)

    def handle_event(self, e):
        kx, ky = self.knob_pos()
        knob = pygame.Rect(kx-self.knob_r, ky-self.knob_r, self.knob_r*2, self.knob_r*2)
        if e.type == pygame.MOUSEBUTTONDOWN and e.button==1:
            if knob.collidepoint(e.pos) or self.rect.collidepoint(e.pos):
                self.dragging = True
        if e.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        if e.type == pygame.MOUSEMOTION and self.dragging:
            t = (e.pos[0] - self.rect.x) / self.rect.w
            self.val = self.mn + max(0, min(1, t)) * (self.mx - self.mn)

    def draw(self, surf):
        pygame.draw.rect(surf, BORDER, self.rect, border_radius=3)
        filled = pygame.Rect(self.rect.x, self.rect.y,
                             int(self.norm * self.rect.w), self.rect.h)
        pygame.draw.rect(surf, ACCENT2, filled, border_radius=3)
        kx, ky = self.knob_pos()
        pygame.draw.circle(surf, ACCENT2, (kx, ky), self.knob_r)
        pygame.draw.circle(surf, WHITE,   (kx, ky), self.knob_r, 2)
        draw_text(surf, f"×{self.val:.1f}", self.font, ACCENT2,
                  self.rect.right + 8, ky-8)


# APP PRINCIPAL

CARPETA_GUARDADOS = "ciudades_guardadas"

def _asegurar_carpeta():
    if not os.path.exists(CARPETA_GUARDADOS):
        os.makedirs(CARPETA_GUARDADOS)

def listar_ciudades() -> list[dict]:
    """Devuelve lista de dicts con info de cada ciudad guardada, ordenada por fecha."""
    _asegurar_carpeta()
    resultado = []
    for f in os.listdir(CARPETA_GUARDADOS):
        if not f.endswith(".json"):
            continue
        ruta = os.path.join(CARPETA_GUARDADOS, f)
        try:
            mtime = os.path.getmtime(ruta)
            with open(ruta, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            meta = data.get("meta", {})
            resultado.append({
                "nombre":  meta.get("nombre", f[:-5]),
                "archivo": ruta,
                "nodos":   meta.get("nodos", 0),
                "calles":  meta.get("calles", 0),
                "fecha":   meta.get("fecha", ""),
                "mtime":   mtime,
            })
        except Exception:
            continue
    resultado.sort(key=lambda x: x["mtime"], reverse=True)
    return resultado

def guardar_ciudad(grafo: Grafo, nombre: str) -> bool:
    """Serializa el grafo a JSON en la carpeta de guardados."""
    import time as _time
    _asegurar_carpeta()
    nombre_limpio = "".join(c for c in nombre if c.isalnum() or c in " _-").strip()
    if not nombre_limpio:
        return False
    archivo = os.path.join(CARPETA_GUARDADOS, f"{nombre_limpio}.json")

    aristas_unicas = []
    seen = set()
    for a in grafo.todas_aristas():
        key = tuple(sorted([a.origen, a.destino]))
        if key in seen:
            continue
        seen.add(key)
        aristas_unicas.append({
            "origen":     a.origen,
            "destino":    a.destino,
            "peso_base":  a.peso_base,
            "trafico":    a.trafico,
        })

    datos = {
        "meta": {
            "nombre": nombre_limpio,
            "fecha":  _time.strftime("%d/%m/%Y %H:%M"),
            "nodos":  len(grafo),
            "calles": len(aristas_unicas),
        },
        "nodos": [
            {"nombre": n.nombre, "tipo": n.tipo, "x": n.x, "y": n.y}
            for n in grafo.nodos()
        ],
        "aristas": aristas_unicas,
    }
    try:
        with open(archivo, "w", encoding="utf-8") as fh:
            json.dump(datos, fh, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def cargar_ciudad_json(archivo: str) -> Optional[Grafo]:
    """Carga un Grafo desde un archivo JSON guardado."""
    try:
        with open(archivo, "r", encoding="utf-8") as fh:
            datos = json.load(fh)
    except Exception:
        return None
    g = Grafo()
    for nd in datos.get("nodos", []):
        try:
            g.agregar_nodo(nd["nombre"], nd.get("tipo","interseccion"),
                           nd.get("x"), nd.get("y"))
        except Exception:
            pass
    for ar in datos.get("aristas", []):
        try:
            g.agregar_arista(ar["origen"], ar["destino"],
                             ar["peso_base"], bidireccional=True)
            # restaurar tráfico en ambas direcciones
            for a in g.vecinos(ar["origen"]):
                if a.destino == ar["destino"]:
                    a.trafico = ar.get("trafico", 1.0)
            for a in g.vecinos(ar["destino"]):
                if a.destino == ar["origen"]:
                    a.trafico = ar.get("trafico", 1.0)
        except Exception:
            pass
    return g

def eliminar_ciudad(archivo: str) -> bool:
    try:
        os.remove(archivo)
        return True
    except Exception:
        return False


class App:
    SIDEBAR_W = 310
    TAB_H     = 38
    TABS      = ["RUTA", "TRÁFICO", "EDITAR", "CIUDADES", "LOG"]

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Simulador de Ciudad – Grafos")
        info = pygame.display.Info()
        self.W = min(1400, info.current_w - 40)
        self.H = min(860,  info.current_h - 60)
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        self.clock  = pygame.time.Clock()

        # Fuentes
        self.fnt_big   = pygame.font.SysFont("consolas", 20, bold=True)
        self.fnt_med   = pygame.font.SysFont("consolas", 13, bold=True)
        self.fnt_small = pygame.font.SysFont("consolas", 11)
        self.fnt_tiny  = pygame.font.SysFont("consolas", 10)

        # Grafo
        self.grafo = crear_ciudad_20x20()

        # Vista mapa (offset + escala)
        self.map_offset = [self.SIDEBAR_W + 20, 20]
        self.cell_size  = 0
        self._fit_map()

        # Estado
        self.tab          = 0
        self.ruta         = None
        self.click_step   = 0   # 0=origen 1=destino
        self.click_origen = None
        self.selected_node= None
        self.hover_node   = None
        self.log_lines    = []
        self.show_labels  = False

        # Widgets tab RUTA
        sx = 10
        self.inp_orig = InputBox(sx, 90, self.SIDEBAR_W-20, 28, self.fnt_small, "Origen (ej: A1)")
        self.inp_dest = InputBox(sx, 140, self.SIDEBAR_W-20, 28, self.fnt_small, "Destino (ej: T20)")
        self.btn_calc = Button(sx, 178, self.SIDEBAR_W-20, 28, "▶ CALCULAR RUTA", self.fnt_small, ACCENT, (0,0,0))
        self.btn_clear= Button(sx, 212, self.SIDEBAR_W-20, 28, "✕ LIMPIAR", self.fnt_small, PANEL, TEXT)
        self.btn_prueba=Button(sx, 248, self.SIDEBAR_W-20, 28, "🏙 CIUDAD DE PRUEBA", self.fnt_small, (40,60,30), ACCENT3)

        # Widgets tab TRÁFICO
        self.inp_traf_o = InputBox(sx, 90, self.SIDEBAR_W-20, 28, self.fnt_small, "Desde")
        self.inp_traf_d = InputBox(sx, 140, self.SIDEBAR_W-20, 28, self.fnt_small, "Hasta")
        self.slider_mult= Slider(sx, 195, self.SIDEBAR_W-60, 1.0, 10.0, 2.5, self.fnt_small)
        self.btn_traf   = Button(sx, 220, self.SIDEBAR_W-20, 28, "⚠ APLICAR TRÁFICO", self.fnt_small, ACCENT2, (0,0,0))
        self.btn_reset  = Button(sx, 254, self.SIDEBAR_W-20, 28, "↺ RESET TRÁFICO", self.fnt_small, PANEL, TEXT)

        # Widgets tab EDITAR
        self.inp_calle_o= InputBox(sx, 150, self.SIDEBAR_W-20, 28, self.fnt_small, "Desde")
        self.inp_calle_d= InputBox(sx, 200, self.SIDEBAR_W-20, 28, self.fnt_small, "Hasta")
        self.inp_calle_p= InputBox(sx, 250, self.SIDEBAR_W-20, 28, self.fnt_small, "Peso", "1.0")
        self.btn_add_calle= Button(sx, 285, self.SIDEBAR_W-20, 28, "+ AGREGAR CALLE", self.fnt_small, ACCENT3, (0,0,0))
        self.btn_tipo_base  = Button(sx,  90, (self.SIDEBAR_W-20)//3-2, 26, "BASE", self.fnt_small, (60,20,30), RED)
        self.btn_tipo_emp   = Button(sx+(self.SIDEBAR_W-20)//3+2, 90, (self.SIDEBAR_W-20)//3-2, 26, "EMPRESA", self.fnt_small, (20,30,60), BLUE)
        self.btn_tipo_inter = Button(sx+2*((self.SIDEBAR_W-20)//3+2), 90, (self.SIDEBAR_W-20)//3-2, 26, "INTER.", self.fnt_small, PANEL, TEXT)

        # Widgets tab CIUDADES
        self.inp_nombre_ciudad = InputBox(sx, 90, self.SIDEBAR_W-20, 28,
                                          self.fnt_small, "Nombre de la ciudad...")
        self.btn_guardar   = Button(sx, 126, self.SIDEBAR_W-20, 28,
                                    "GUARDAR CIUDAD ACTUAL", self.fnt_small,
                                    (20,50,40), ACCENT3)
        # Estado de la lista de ciudades
        self._ciudades_cache: list[dict] = []
        self._ciudades_scroll = 0
        self._ciudad_seleccionada: Optional[dict] = None
        self._confirm_delete: Optional[dict] = None
        self._feedback_msg  = ("", "ok", 0)

        # Pan drag con botón izquierdo (arrastrar mapa)
        self._drag_active = False
        self._drag_start_pos = (0, 0)
        self._drag_start_offset = (0, 0)
        self._drag_threshold = 5  # píxeles para distinguir clic de arrastre

        self._log("Ciudad 20×20 cargada – 400 nodos", "ok")
        self._log("Arrastra con el botón izquierdo para mover el mapa", "info")

    #  MAPA: FIT & COORD 
    def _fit_map(self):
        map_w = self.W - self.SIDEBAR_W - 30
        map_h = self.H - 30
        self.cell_size = min(map_w, map_h) // 21
        self.map_offset = [self.SIDEBAR_W + 15, 15]

    def _node_screen_pos(self, nodo: Nodo):
        cs = self.cell_size
        ox, oy = self.map_offset
        return (ox + int((nodo.x + 0.5) * cs),
                oy + int((nodo.y + 0.5) * cs))

    def _screen_to_node(self, sx, sy):
        cs = self.cell_size
        ox, oy = self.map_offset
        gx = (sx - ox) / cs - 0.5
        gy = (sy - oy) / cs - 0.5
        best, best_d = None, cs * 0.45
        for n in self.grafo.nodos():
            d = math.hypot(n.x - gx, n.y - gy)
            if d < best_d:
                best_d = d; best = n.nombre
        return best

    #  LOGGING 
    def _log(self, msg, kind="info"):
        import time
        t = time.strftime("%H:%M:%S")
        self.log_lines.append((t, msg, kind))
        if len(self.log_lines) > 120:
            self.log_lines.pop(0)

    #  EVENT HANDLING 
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.VIDEORESIZE:
                self.W, self.H = e.w, e.h
                self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
                self._fit_map()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self._clear_route()
                if e.key == pygame.K_l:
                    self.show_labels = not self.show_labels
                if e.key == pygame.K_RETURN:
                    if self.tab == 0: self._calcular()
                    if self.tab == 1: self._aplicar_trafico()
                if e.key == pygame.K_t:
                    self.grafo.resetear_trafico()
                    self._log("Tráfico reseteado", "info")

            # Scroll zoom
            if e.type == pygame.MOUSEWHEEL:
                factor = 0.9 if e.y > 0 else 1.1
                mx, my = pygame.mouse.get_pos()
                if mx > self.SIDEBAR_W:
                    self._zoom(factor, mx, my)

            # Botón izquierdo: inicio de posible arrastre
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                if mx > self.SIDEBAR_W:  # dentro del área del mapa
                    self._drag_active = True
                    self._drag_start_pos = (mx, my)
                    self._drag_start_offset = tuple(self.map_offset)
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

            # Movimiento con botón izquierdo presionado
            if e.type == pygame.MOUSEMOTION and self._drag_active:
                mx, my = e.pos
                dx = mx - self._drag_start_pos[0]
                dy = my - self._drag_start_pos[1]
                # Actualizar el offset del mapa si hemos movido lo suficiente
                # (pero no esperamos al umbral para mover, solo para decidir el clic final)
                self.map_offset = [self._drag_start_offset[0] + dx,
                                   self._drag_start_offset[1] + dy]

            # Soltar botón izquierdo: final de arrastre o clic
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                if self._drag_active:
                    mx, my = e.pos
                    dx = mx - self._drag_start_pos[0]
                    dy = my - self._drag_start_pos[1]
                    dist = math.hypot(dx, dy)
                    # Solo considerar clic si el ratón no se movió más del umbral
                    if dist < self._drag_threshold:
                        # Fue un clic → seleccionar nodo
                        clicked = self._screen_to_node(mx, my)
                        if clicked:
                            self._on_node_click(clicked)
                    # Restaurar cursor
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    self._drag_active = False

            # El resto de eventos de interfaz (botones, inputs) se manejan según la pestaña
            # Tab 0 widgets
            if self.tab == 0:
                self.inp_orig.handle_event(e)
                self.inp_dest.handle_event(e)
                if self.btn_calc.handle_event(e):  self._calcular()
                if self.btn_clear.handle_event(e): self._clear_route()
                if self.btn_prueba.handle_event(e):self._load_test()

            # Tab 1 widgets
            elif self.tab == 1:
                self.inp_traf_o.handle_event(e)
                self.inp_traf_d.handle_event(e)
                self.slider_mult.handle_event(e)
                if self.btn_traf.handle_event(e):  self._aplicar_trafico()
                if self.btn_reset.handle_event(e):
                    self.grafo.resetear_trafico()
                    self._log("Tráfico reseteado en toda la ciudad", "info")

            # Tab 2 widgets
            elif self.tab == 2:
                self.inp_calle_o.handle_event(e)
                self.inp_calle_d.handle_event(e)
                self.inp_calle_p.handle_event(e)
                if self.btn_add_calle.handle_event(e): self._agregar_calle()
                if self.btn_tipo_base.handle_event(e):  self._set_tipo("base")
                if self.btn_tipo_emp.handle_event(e):   self._set_tipo("empresa")
                if self.btn_tipo_inter.handle_event(e): self._set_tipo("interseccion")

            # Tab 3 – CIUDADES
            elif self.tab == 3:
                self.inp_nombre_ciudad.handle_event(e)
                if self.btn_guardar.handle_event(e):
                    self._accion_guardar()
                # Scroll en la lista
                if e.type == pygame.MOUSEWHEEL:
                    mx2, _ = pygame.mouse.get_pos()
                    if mx2 < self.SIDEBAR_W:
                        self._ciudades_scroll = max(
                            0, min(self._ciudades_scroll - e.y,
                                max(0, len(self._ciudades_cache) - 5)))
                # Clic en un slot de ciudad
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx2, my2 = e.pos
                    if mx2 < self.SIDEBAR_W:
                        self._handle_ciudad_list_click(mx2, my2)
                        
            # Clic en las pestañas
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                if 0 <= mx <= self.SIDEBAR_W and 50 <= my <= 50 + self.TAB_H:
                    tw = self.SIDEBAR_W // len(self.TABS)
                    nueva_tab = mx // tw
                    if 0 <= nueva_tab < len(self.TABS):
                        self.tab = nueva_tab

        return True

    #  ACTIONS 
    def _on_node_click(self, nombre):
        self.selected_node = nombre
        if self.click_step == 0:
            self.click_origen = nombre
            self.inp_orig.value = nombre
            self.click_step = 1
            self._log(f"Origen seleccionado: {nombre}", "info")
        elif self.click_step == 1:
            self.inp_dest.value = nombre
            self.click_step = 2
            self._log(f"Destino seleccionado: {nombre}", "info")
            self._calcular()
        else:
            self.click_step = 0
            self.click_origen = None
            self.inp_orig.value = nombre
            self.click_step = 1

    def _calcular(self):
        o = self.inp_orig.value.strip().upper()
        d = self.inp_dest.value.strip().upper()
        if not o or not d: return
        if o not in self.grafo:
            self._log(f"Nodo '{o}' no existe", "err"); return
        if d not in self.grafo:
            self._log(f"Nodo '{d}' no existe", "err"); return
        self.ruta = dijkstra(self.grafo, o, d)
        if self.ruta.encontrada:
            self._log(f"Ruta {o}→{d}: {len(self.ruta.camino)-1} pasos, coste={self.ruta.coste:.2f}", "ok")
        else:
            self._log(f"Sin ruta entre {o} y {d}", "err")

    def _clear_route(self):
        self.ruta = None
        self.click_step = 0
        self.click_origen = None
        self.selected_node = None
        self.inp_orig.value = ""
        self.inp_dest.value = ""

    def _load_test(self):
        self.grafo = crear_ciudad_20x20()
        cargar_ciudad_prueba(self.grafo)
        self.ruta = None
        self._log("Ciudad de prueba cargada", "ok")

    def _aplicar_trafico(self):
        o = self.inp_traf_o.value.strip().upper()
        d = self.inp_traf_d.value.strip().upper()
        m = self.slider_mult.val
        if not o or not d: return
        ok = self.grafo.aplicar_trafico(o, d, m)
        if ok: self._log(f"Tráfico ×{m:.1f} en {o}↔{d}", "warn")
        else:  self._log(f"No existe calle entre {o} y {d}", "err")

    def _agregar_calle(self):
        o = self.inp_calle_o.value.strip().upper()
        d = self.inp_calle_d.value.strip().upper()
        try:
            p = float(self.inp_calle_p.value or "1.0")
        except ValueError:
            p = 1.0
        if not o or not d: return
        try:
            self.grafo.agregar_arista(o, d, p)
            self._log(f"Calle {o}↔{d} añadida (peso {p:.2f})", "ok")
        except Exception as ex:
            self._log(str(ex), "err")

    def _set_tipo(self, tipo):
        if not self.selected_node: return
        n = self.grafo.obtener_nodo(self.selected_node)
        if n:
            n.tipo = tipo
            self._log(f"{self.selected_node} → {tipo}", "ok")

    def _zoom(self, factor, cx, cy):
        # Adjust offset so zoom is centered on cursor
        ox, oy = self.map_offset
        self.cell_size = max(8, min(60, int(self.cell_size * factor)))
        # Keep the point under cursor fixed
        new_ox = cx - (cx - ox) * factor
        new_oy = cy - (cy - oy) * factor
        self.map_offset = [new_ox, new_oy]

    #  DRAW 
    def draw(self):
        self.screen.fill(BG)
        self._draw_map()
        self._draw_sidebar()
        self._draw_header()
        pygame.display.flip()

    def _draw_header(self):
        # Logo bar
        pygame.draw.rect(self.screen, SURFACE, (0, 0, self.W, 46))
        pygame.draw.line(self.screen, BORDER, (0, 46), (self.W, 46))
        draw_text(self.screen, "CIUDAD·GRAFO", self.fnt_big, ACCENT, 12, 13)
        # Stats
        nn = len(self.grafo)
        ae = set()
        for a in self.grafo.todas_aristas(): ae.add(tuple(sorted([a.origen,a.destino])))
        nt = sum(1 for a in self.grafo.todas_aristas() if a.trafico > 1.0) // 2
        stats = [
            (f"{nn} nodos", TEXT),
            (f"{len(ae)} calles", TEXT),
            (f"{nt} tráfico", ACCENT2 if nt else MUTED),
        ]
        rx = self.W - 10
        for txt, col in reversed(stats):
            w, _ = draw_text(self.screen, txt, self.fnt_small, col, rx, 16, right=True)
            rx -= w + 24
        # Shortcut hints
        hints = "[L] etiquetas  [Scroll] zoom  [Izquierdo] arrastrar  [Esc] limpiar"
        draw_text(self.screen, hints, self.fnt_tiny, MUTED, self.SIDEBAR_W + 10, self.H - 18)

    def _draw_sidebar(self):
        pygame.draw.rect(self.screen, SURFACE, (0, 46, self.SIDEBAR_W, self.H - 46))
        pygame.draw.line(self.screen, BORDER, (self.SIDEBAR_W, 46), (self.SIDEBAR_W, self.H))

        # Tabs
        tw = self.SIDEBAR_W // len(self.TABS)
        for i, t in enumerate(self.TABS):
            active = i == self.tab
            bx = i * tw
            pygame.draw.rect(self.screen, PANEL if active else SURFACE,
                             (bx, 50, tw, self.TAB_H))
            col = ACCENT if active else MUTED
            draw_text(self.screen, t, self.fnt_small, col,
                      bx + tw//2, 58, center=True)
            if active:
                pygame.draw.line(self.screen, ACCENT, (bx+2, 50+self.TAB_H-2),
                                 (bx+tw-2, 50+self.TAB_H-2), 2)
        pygame.draw.line(self.screen, BORDER,
                         (0, 50+self.TAB_H), (self.SIDEBAR_W, 50+self.TAB_H))

        # Content
        content_y = 50 + self.TAB_H + 8
        if self.tab == 0: self._draw_tab_ruta(content_y)
        elif self.tab == 1: self._draw_tab_trafico(content_y)
        elif self.tab == 2: self._draw_tab_editar(content_y)
        elif self.tab == 3: self._draw_tab_ciudades(content_y)
        elif self.tab == 4: self._draw_tab_log(content_y)

    def _draw_tab_ruta(self, y0):
        sx = 10
        draw_text(self.screen, "─ CALCULAR RUTA ─", self.fnt_small, ACCENT, sx, y0)

        # Click mode hint
        if self.click_step == 0:
            hint = "▶ Haz clic en el mapa: ORIGEN"
            col = MUTED
        elif self.click_step == 1:
            hint = f"▶ Origen: {self.click_origen} — elige DESTINO"
            col = YELLOW
        else:
            hint = "✓ Listo — pulsa CALCULAR"
            col = ACCENT3
        draw_text(self.screen, hint, self.fnt_tiny, col, sx, y0+18)

        # Reposition widgets
        self.inp_orig.rect.y = y0 + 38
        self.inp_dest.rect.y = y0 + 80
        self.btn_calc.rect.y = y0 + 114
        self.btn_clear.rect.y= y0 + 148
        self.btn_prueba.rect.y=y0 + 182

        draw_text(self.screen, "Origen", self.fnt_tiny, MUTED, sx, y0+26)
        self.inp_orig.update(self.clock.get_time())
        self.inp_orig.draw(self.screen)
        draw_text(self.screen, "Destino", self.fnt_tiny, MUTED, sx, y0+68)
        self.inp_dest.update(self.clock.get_time())
        self.inp_dest.draw(self.screen)
        self.btn_calc.draw(self.screen)
        self.btn_clear.draw(self.screen)
        self.btn_prueba.draw(self.screen)

        # Result
        ry = y0 + 218
        if self.ruta:
            if self.ruta.encontrada:
                pygame.draw.rect(self.screen, (0,30,35),
                                 (sx, ry, self.SIDEBAR_W-20, 200), border_radius=4)
                pygame.draw.rect(self.screen, ACCENT,
                                 (sx, ry, self.SIDEBAR_W-20, 200), 1, border_radius=4)
                draw_text(self.screen, "RUTA ÓPTIMA", self.fnt_small, ACCENT, sx+8, ry+8)
                # Cost
                draw_text(self.screen, f"Coste:", self.fnt_small, MUTED, sx+8, ry+28)
                draw_text(self.screen, f"{self.ruta.coste:.2f}", self.fnt_big, ACCENT,
                          sx+60, ry+24)
                draw_text(self.screen, f"{len(self.ruta.camino)-1} pasos",
                          self.fnt_small, MUTED, sx+8, ry+52)
                # Route nodes (compact)
                route_str = " → ".join(self.ruta.camino)
                words = []
                line, lw = "", 0
                for tok in route_str.split():
                    tw = self.fnt_tiny.size(tok+" ")[0]
                    if lw + tw > self.SIDEBAR_W - 28:
                        words.append(line); line = tok+" "; lw = tw
                    else:
                        line += tok+" "; lw += tw
                if line: words.append(line)
                for li, w in enumerate(words[:4]):
                    draw_text(self.screen, w.strip(), self.fnt_tiny, TEXT, sx+8, ry+68+li*14)
                # Detalle (last few steps)
                dy = ry + 130
                draw_text(self.screen, "Últimos pasos:", self.fnt_tiny, MUTED, sx+8, dy)
                for desde, hasta, peso in self.ruta.detalle[-4:]:
                    dy += 13
                    col = ACCENT2 if peso != round(peso) else MUTED
                    draw_text(self.screen, f"{desde}→{hasta}", self.fnt_tiny, TEXT, sx+8, dy)
                    draw_text(self.screen, f"+{peso:.2f}", self.fnt_tiny, col,
                              self.SIDEBAR_W-28, dy, right=True)
            else:
                pygame.draw.rect(self.screen, (35,10,15),
                                 (sx, ry, self.SIDEBAR_W-20, 50), border_radius=4)
                pygame.draw.rect(self.screen, RED,
                                 (sx, ry, self.SIDEBAR_W-20, 50), 1, border_radius=4)
                draw_text(self.screen, "SIN RUTA ENCONTRADA", self.fnt_small, RED, sx+8, ry+10)
                draw_text(self.screen, f"{self.ruta.origen} → {self.ruta.destino}",
                          self.fnt_tiny, MUTED, sx+8, ry+28)

        # Legend
        ly = self.H - 140
        pygame.draw.line(self.screen, BORDER, (sx, ly), (self.SIDEBAR_W-10, ly))
        draw_text(self.screen, "LEYENDA", self.fnt_tiny, MUTED, sx, ly+6)
        legend = [
            ("●", NODE_BASE,     "Base"),
            ("●", NODE_EMPRESA,  "Empresa"),
            ("●", NODE_INTER_LIT,"Intersección"),
            ("─", EDGE_ROUTE,    "Ruta óptima"),
            ("─", EDGE_TRAFFIC,  "Tráfico"),
            ("─", EDGE_FAST,     "Rápida (≤1.2)"),
        ]
        for i, (sym, col, txt) in enumerate(legend):
            lx = sx + (i%2) * 140
            lly = ly + 22 + (i//2) * 16
            draw_text(self.screen, sym, self.fnt_small, col, lx, lly)
            draw_text(self.screen, txt, self.fnt_tiny, MUTED, lx+14, lly+1)

    def _draw_tab_trafico(self, y0):
        sx = 10
        draw_text(self.screen, "─ MODO TRÁFICO ─", self.fnt_small, ACCENT2, sx, y0)
        draw_text(self.screen, "Calle Desde", self.fnt_tiny, MUTED, sx, y0+18)
        self.inp_traf_o.rect.y = y0 + 30
        self.inp_traf_o.update(self.clock.get_time())
        self.inp_traf_o.draw(self.screen)
        draw_text(self.screen, "Calle Hasta", self.fnt_tiny, MUTED, sx, y0+64)
        self.inp_traf_d.rect.y = y0 + 76
        self.inp_traf_d.update(self.clock.get_time())
        self.inp_traf_d.draw(self.screen)
        draw_text(self.screen, "Multiplicador", self.fnt_tiny, MUTED, sx, y0+110)
        self.slider_mult.rect.y = y0 + 126
        self.slider_mult.draw(self.screen)
        self.btn_traf.rect.y   = y0 + 148
        self.btn_reset.rect.y  = y0 + 182
        self.btn_traf.draw(self.screen)
        self.btn_reset.draw(self.screen)

        # Calles con tráfico
        draw_text(self.screen, "─ TRÁFICO ACTIVO ─", self.fnt_tiny, MUTED, sx, y0+220)
        seen = set(); ty = y0+236
        for a in self.grafo.todas_aristas():
            if a.trafico == 1.0: continue
            key = tuple(sorted([a.origen, a.destino]))
            if key in seen: continue
            seen.add(key)
            draw_text(self.screen, f"{a.origen} ↔ {a.destino}", self.fnt_tiny, TEXT, sx, ty)
            draw_text(self.screen, f"×{a.trafico:.1f}", self.fnt_tiny, ACCENT2,
                      self.SIDEBAR_W-28, ty, right=True)
            ty += 14
            if ty > self.H - 60: break
        if not seen:
            draw_text(self.screen, "Sin tráfico activo", self.fnt_tiny, MUTED, sx, ty)

    def _draw_tab_editar(self, y0):
        sx = 10
        draw_text(self.screen, "─ NODO SELECCIONADO ─", self.fnt_small, ACCENT, sx, y0)
        if self.selected_node:
            n = self.grafo.obtener_nodo(self.selected_node)
            draw_text(self.screen, self.selected_node, self.fnt_big, ACCENT, sx, y0+16)
            draw_text(self.screen, f"Tipo: {n.tipo}  Pos:({n.x},{n.y})",
                      self.fnt_tiny, MUTED, sx, y0+40)
            draw_text(self.screen, f"Conexiones: {len(self.grafo.vecinos(self.selected_node))}",
                      self.fnt_tiny, MUTED, sx, y0+54)
            draw_text(self.screen, "Cambiar tipo:", self.fnt_tiny, MUTED, sx, y0+72)
            self.btn_tipo_base.rect.y = y0 + 86
            self.btn_tipo_emp.rect.y  = y0 + 86
            self.btn_tipo_inter.rect.y= y0 + 86
            self.btn_tipo_base.draw(self.screen)
            self.btn_tipo_emp.draw(self.screen)
            self.btn_tipo_inter.draw(self.screen)
        else:
            draw_text(self.screen, "Haz clic en un nodo del mapa",
                      self.fnt_tiny, MUTED, sx, y0+18)

        draw_text(self.screen, "─ AGREGAR CALLE ─", self.fnt_small, ACCENT3, sx, y0+125)
        draw_text(self.screen, "Desde", self.fnt_tiny, MUTED, sx, y0+143)
        self.inp_calle_o.rect.y = y0+155
        self.inp_calle_o.update(self.clock.get_time())
        self.inp_calle_o.draw(self.screen)
        draw_text(self.screen, "Hasta", self.fnt_tiny, MUTED, sx, y0+187)
        self.inp_calle_d.rect.y = y0+199
        self.inp_calle_d.update(self.clock.get_time())
        self.inp_calle_d.draw(self.screen)
        draw_text(self.screen, "Peso", self.fnt_tiny, MUTED, sx, y0+231)
        self.inp_calle_p.rect.y = y0+243
        self.inp_calle_p.update(self.clock.get_time())
        self.inp_calle_p.draw(self.screen)
        self.btn_add_calle.rect.y = y0+277
        self.btn_add_calle.draw(self.screen)

        # List special nodes
        draw_text(self.screen, "─ NODOS ESPECIALES ─", self.fnt_tiny, MUTED, sx, y0+315)
        ny = y0+331
        for n in self.grafo.nodos():
            if n.tipo == "interseccion": continue
            icon = "⚑" if n.tipo=="base" else "⚬"
            col  = RED if n.tipo=="base" else BLUE
            draw_text(self.screen, f"{icon} {n.nombre}", self.fnt_tiny, col, sx, ny)
            ny += 13
            if ny > self.H - 30: break

    #  TAB 3: CIUDADES Y PERSISTENCIA 
    def _accion_guardar(self):
        nombre = self.inp_nombre_ciudad.value.strip()
        if not nombre:
            self._log("Escribe un nombre válido para guardar", "err")
            return
            
        if guardar_ciudad(self.grafo, nombre):
            self._log(f"Ciudad '{nombre}' guardada con éxito", "ok")
            self.inp_nombre_ciudad.value = ""
            # Forzamos la actualización de la lista
            self._ciudades_cache = listar_ciudades() 
        else:
            self._log("Error al intentar guardar la ciudad", "err")

    def _handle_ciudad_list_click(self, mx, my):
        # Comprobamos si el clic ha dado en algún botón de "CARGAR"
        for c in self._ciudades_cache:
            if "rect_cargar" in c and c["rect_cargar"].collidepoint(mx, my):
                nuevo_grafo = cargar_ciudad_json(c["archivo"])
                if nuevo_grafo:
                    self.grafo = nuevo_grafo
                    self._clear_route()
                    self._log(f"Ciudad '{c['nombre']}' cargada correctamente", "ok")
                else:
                    self._log(f"Error al cargar la ciudad '{c['nombre']}'", "err")
                break

    def _draw_tab_ciudades(self, y0):
        sx = 10
        draw_text(self.screen, "─ GUARDAR CIUDAD ACTUAL ─", self.fnt_small, ACCENT, sx, y0)
        draw_text(self.screen, "Nombre del archivo:", self.fnt_tiny, MUTED, sx, y0+22)
        
        self.inp_nombre_ciudad.rect.y = y0 + 38
        self.inp_nombre_ciudad.update(self.clock.get_time())
        self.inp_nombre_ciudad.draw(self.screen)
        
        self.btn_guardar.rect.y = y0 + 74
        self.btn_guardar.draw(self.screen)

        draw_text(self.screen, "─ MIS CIUDADES GUARDADAS ─", self.fnt_small, ACCENT3, sx, y0+130)

        # Cargar la lista solo si está vacía
        if not self._ciudades_cache:
            self._ciudades_cache = listar_ciudades()

        cy = y0 + 155
        ciudades_visibles = self._ciudades_cache[self._ciudades_scroll:]
        
        if not ciudades_visibles:
            draw_text(self.screen, "No hay ciudades guardadas aún.", self.fnt_tiny, MUTED, sx, cy)
            return

        for c in ciudades_visibles:
            if cy > self.H - 50: 
                break # Evitar que dibuje fuera de la pantalla

            # Fondo de la tarjeta de la ciudad
            rect_bg = pygame.Rect(sx, cy, self.SIDEBAR_W - 20, 50)
            pygame.draw.rect(self.screen, PANEL, rect_bg, border_radius=5)
            pygame.draw.rect(self.screen, BORDER, rect_bg, 1, border_radius=5)

            # Textos
            draw_text(self.screen, c["nombre"].upper(), self.fnt_med, TEXT, sx+10, cy+8)
            info_grafos = f"{c.get('nodos', 0)} nodos | {c.get('calles', 0)} calles"
            draw_text(self.screen, info_grafos, self.fnt_tiny, MUTED, sx+10, cy+28)

            # Botón visual de Cargar
            btn_cargar = pygame.Rect(self.SIDEBAR_W - 85, cy + 12, 70, 26)
            c["rect_cargar"] = btn_cargar # Guardamos el rectángulo para detectar el clic
            
            # Efecto hover manual para el botón de la lista
            mx, my = pygame.mouse.get_pos()
            color_btn = (100, 255, 100) if btn_cargar.collidepoint(mx, my) else (57, 255, 20)
            
            pygame.draw.rect(self.screen, color_btn, btn_cargar, border_radius=3)
            draw_text(self.screen, "CARGAR", self.fnt_tiny, (0,0,0), btn_cargar.centerx, btn_cargar.centery-6, center=True)

            cy += 60

    def _draw_tab_log(self, y0):
        sx = 10
        draw_text(self.screen, "─ REGISTRO DE EVENTOS ─", self.fnt_small, MUTED, sx, y0)
        colors = {"ok": ACCENT3, "err": RED, "warn": ACCENT2, "info": ACCENT}
        for i, (t, msg, kind) in enumerate(reversed(self.log_lines)):
            ly = y0 + 20 + i * 15
            if ly > self.H - 20: break
            draw_text(self.screen, t, self.fnt_tiny, MUTED, sx, ly)
            draw_text(self.screen, msg, self.fnt_tiny, colors.get(kind, TEXT), sx+55, ly)

    #  MAP DRAW 
    def _draw_map(self):
        cs = self.cell_size
        ox, oy = int(self.map_offset[0]), int(self.map_offset[1])
        map_rect = pygame.Rect(self.SIDEBAR_W, 46, self.W-self.SIDEBAR_W, self.H-46)
        self.screen.set_clip(map_rect)

        # Subtle grid
        for i in range(21):
            x = ox + i*cs
            y = oy + i*cs
            pygame.draw.line(self.screen, (20,25,38), (x, oy), (x, oy+20*cs), 1)
            pygame.draw.line(self.screen, (20,25,38), (ox, y), (ox+20*cs, y), 1)

        route_set = set()
        if self.ruta and self.ruta.encontrada:
            for i in range(len(self.ruta.camino)-1):
                a, b = self.ruta.camino[i], self.ruta.camino[i+1]
                route_set.add((a,b)); route_set.add((b,a))

        # Edges
        seen_edges = set()
        for a in self.grafo.todas_aristas():
            key = tuple(sorted([a.origen, a.destino]))
            if key in seen_edges: continue
            seen_edges.add(key)
            n1 = self.grafo.obtener_nodo(a.origen)
            n2 = self.grafo.obtener_nodo(a.destino)
            if not n1 or not n2: continue
            p1 = (ox + int((n1.x+0.5)*cs), oy + int((n1.y+0.5)*cs))
            p2 = (ox + int((n2.x+0.5)*cs), oy + int((n2.y+0.5)*cs))
            in_route = (a.origen,a.destino) in route_set
            if in_route:
                glow_line(self.screen, EDGE_ROUTE, p1, p2, w=3, glow=5)
            elif a.trafico > 1.0:
                pygame.draw.line(self.screen, EDGE_TRAFFIC, p1, p2, max(1,cs//12))
            elif a.peso_efectivo <= 1.2:
                pygame.draw.line(self.screen, EDGE_FAST, p1, p2, max(1,cs//18))
            else:
                pygame.draw.line(self.screen, EDGE_NORMAL, p1, p2, max(1,cs//20))

        # Nodes
        hover = self._screen_to_node(*pygame.mouse.get_pos()) if pygame.mouse.get_pos()[0] > self.SIDEBAR_W else None
        for n in self.grafo.nodos():
            px, py = ox + int((n.x+0.5)*cs), oy + int((n.y+0.5)*cs)
            in_route = self.ruta and self.ruta.encontrada and n.nombre in self.ruta.camino
            is_sel   = n.nombre == self.selected_node
            is_orig  = n.nombre == self.click_origen
            is_hover = n.nombre == hover

            if n.tipo == "base":
                r = max(5, cs//5)
                glow_circle(self.screen, NODE_BASE, px, py, r, glow=8)
                draw_text(self.screen, "⚑", self.fnt_tiny, WHITE, px-4, py-5)
            elif n.tipo == "empresa":
                r = max(4, cs//6)
                glow_circle(self.screen, NODE_EMPRESA, px, py, r, glow=6)
                draw_text(self.screen, "⚬", self.fnt_tiny, WHITE, px-4, py-5)
            else:
                r = max(2, cs//14)
                if in_route:
                    pygame.draw.circle(self.screen, EDGE_ROUTE, (px,py), max(3,cs//8))
                    pygame.draw.circle(self.screen, BG, (px,py), max(1,cs//12))
                elif is_hover:
                    pygame.draw.circle(self.screen, YELLOW, (px,py), max(3,cs//9))
                else:
                    pygame.draw.circle(self.screen, NODE_INTER, (px,py), r)

            # Selection ring
            if is_sel or is_orig:
                col = YELLOW if is_orig else ACCENT
                ring_r = max(5, cs//5 + 3)
                pygame.draw.circle(self.screen, col, (px,py), ring_r, 2)

            # Labels
            if self.show_labels or n.tipo != "interseccion" or in_route or is_hover:
                col_lbl = (RED if n.tipo=="base" else
                           BLUE if n.tipo=="empresa" else
                           (ACCENT if in_route else YELLOW if is_hover else MUTED))
                draw_text(self.screen, n.nombre, self.fnt_tiny, col_lbl,
                          px, py + max(4, cs//5 + 2), center=True)

        # Row/col axis labels (when zoomed in enough)
        if cs >= 20:
            for i in range(20):
                draw_text(self.screen, FILAS[i], self.fnt_tiny, MUTED,
                          ox - 14, oy + i*cs + cs//2 - 5, center=True)
                draw_text(self.screen, str(i+1), self.fnt_tiny, MUTED,
                          ox + i*cs + cs//2, oy - 14, center=True)

        self.screen.set_clip(None)

    #  MAIN LOOP 
    def run(self):
        while True:
            dt = self.clock.tick(60)
            if not self.handle_events():
                break
            self.draw()
        pygame.quit()
        sys.exit()


# ENTRY POINT


if __name__ == "__main__":
    try:
        import pygame
    except ImportError:
        print("Pygame no está instalado. Ejecuta:  pip install pygame")
        sys.exit(1)
    App().run()