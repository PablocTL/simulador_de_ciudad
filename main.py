# main.py - APLICACIÓN PRINCIPAL

import pygame
import sys
import json
from models import Grafo
from config import *
from algorithm import dijkstra
from city_generator import (crear_ciudad_20x20, cargar_ciudad_prueba,
                            guardar_ciudad, cargar_ciudad_json, listar_ciudades)
from drawing_utils import draw_text, glow_line, glow_circle
from ui_components import TextInput, Button


class App:
    """Aplicación principal del simulador de ciudad"""
    
    def __init__(self):
        pygame.init()
        
        self.W, self.H = 1400, 900
        self.SIDEBAR_W = 250
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("SIMULADOR DE CIUDAD – GRAFOS")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fuentes
        self.fnt_tiny = pygame.font.SysFont("monospace", 10)
        self.fnt_med = pygame.font.SysFont("monospace", 12)
        self.fnt_small = pygame.font.SysFont("monospace", 13)
        self.fnt_big = pygame.font.SysFont("monospace", 16)
        
        # Estado del grafo y rutas
        self.grafo = crear_ciudad_20x20()
        cargar_ciudad_prueba(self.grafo)
        self.ruta = None
        self.click_origen = None
        self.selected_node = None
        self.show_labels = False
        
        # Cámara
        self.cell_size = 32
        self.map_offset = [100, 100]
        
        # Interfaz
        self.current_tab = 0
        self.log_lines = []
        self._ciudades_cache = []
        self._ciudades_scroll = 0
        
        # Componentes UI
        self.inp_nombre_ciudad = TextInput(20, 300, 210, 28, self.fnt_tiny, "nombre_ciudad")
        self.btn_guardar = Button(20, 330, 210, 28, "GUARDAR", self.fnt_tiny,
                                 ACCENT3, (0, 0, 0))
        
        self._log("Aplicación iniciada", "ok")
    
    def _log(self, msg, kind="info"):
        """Agrega un mensaje al log"""
        import time
        t = time.strftime("%H:%M:%S")
        self.log_lines.append((t, msg, kind))
        if len(self.log_lines) > 50:
            self.log_lines.pop(0)
    
    def handle_events(self) -> bool:
        """Maneja eventos. Retorna False si debe cerrarse"""
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.show_labels = not self.show_labels
                elif event.key == pygame.K_r:
                    self._clear_route()
                elif event.key == pygame.K_UP:
                    self.cell_size = min(100, self.cell_size + 5)
                elif event.key == pygame.K_DOWN:
                    self.cell_size = max(10, self.cell_size - 5)
                elif event.key == pygame.K_LEFT:
                    self.map_offset[0] += 20
                elif event.key == pygame.K_RIGHT:
                    self.map_offset[0] -= 20
                elif event.key == pygame.K_w:
                    self.map_offset[1] += 20
                elif event.key == pygame.K_s:
                    self.map_offset[1] -= 20
                elif event.key == pygame.K_1:
                    self.current_tab = 0
                elif event.key == pygame.K_2:
                    self.current_tab = 1
                elif event.key == pygame.K_3:
                    self.current_tab = 2
                elif event.key == pygame.K_4:
                    self.current_tab = 3
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mx > self.SIDEBAR_W:
                    # Clic en el mapa
                    node = self._screen_to_node(mx, my)
                    if node:
                        if event.button == 1:  # Click izquierdo
                            if self.click_origen is None:
                                self.click_origen = node
                                self._log(f"Origen: {node}", "info")
                            else:
                                self._calcular_ruta(self.click_origen, node)
                                self.click_origen = None
                        elif event.button == 3:  # Click derecho
                            self.selected_node = node
                else:
                    # Clic en sidebar
                    if self.current_tab == 2:
                        self._handle_ciudad_list_click(mx, my)
            
            # Componentes UI
            if self.current_tab == 2:
                self.inp_nombre_ciudad.handle_event(event)
                if self.btn_guardar.handle_event(event):
                    self._accion_guardar()
        
        # Actualizar hover de botón
        self.btn_guardar.update((mx, my))
        
        return True
    
    def _screen_to_node(self, sx, sy):
        """Convierte coordenadas de pantalla a nodo"""
        cs = self.cell_size
        ox, oy = self.map_offset
        
        gx = (sx - self.SIDEBAR_W - ox) / cs
        gy = (sy - 46 - oy) / cs
        
        gx, gy = int(round(gx)), int(round(gy))
        
        if 0 <= gx < 20 and 0 <= gy < 20:
            node_name = f"{FILAS[gy]}{gx+1}"
            if node_name in self.grafo:
                return node_name
        return None
    
    def _clear_route(self):
        """Limpia la ruta actual"""
        self.ruta = None
        self.click_origen = None
        self._log("Ruta limpiada", "info")
    
    def _calcular_ruta(self, origen, destino):
        """Calcula ruta entre dos nodos"""
        if origen == destino:
            self._log("El origen y destino son iguales", "warn")
            return
        
        self.ruta = dijkstra(self.grafo, origen, destino)
        if self.ruta.encontrada:
            self._log(f"Ruta encontrada: coste {self.ruta.coste:.2f}", "ok")
        else:
            self._log(f"No hay ruta entre {origen} y {destino}", "err")
    
    def _accion_guardar(self):
        """Guarda la ciudad actual"""
        nombre = self.inp_nombre_ciudad.value.strip()
        if not nombre:
            self._log("Escribe un nombre válido para guardar", "err")
            return
        
        if guardar_ciudad(self.grafo, nombre):
            self._log(f"Ciudad '{nombre}' guardada con éxito", "ok")
            self.inp_nombre_ciudad.value = ""
            self._ciudades_cache = listar_ciudades()
        else:
            self._log("Error al intentar guardar la ciudad", "err")
    
    def _handle_ciudad_list_click(self, mx, my):
        """Maneja click en lista de ciudades"""
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
    
    def draw(self):
        """Dibuja la interfaz completa"""
        self.screen.fill(BG)
        
        # Dibujar mapa
        self._draw_map()
        
        # Dibujar sidebar
        pygame.draw.rect(self.screen, SURFACE, (0, 0, self.SIDEBAR_W, self.H))
        pygame.draw.line(self.screen, BORDER, (self.SIDEBAR_W, 0),
                        (self.SIDEBAR_W, self.H), 1)
        
        # Pestañas
        self._draw_tabs()
        
        # Contenido de pestaña actual
        if self.current_tab == 0:
            self._draw_tab_info(55)
        elif self.current_tab == 1:
            self._draw_tab_nodos(55)
        elif self.current_tab == 2:
            self._draw_tab_ciudades(55)
        elif self.current_tab == 3:
            self._draw_tab_log(55)
        
        pygame.display.flip()
    
    def _draw_tabs(self):
        """Dibuja las pestañas superior"""
        tabs = ["INFO", "NODOS", "CIUDADES", "LOG"]
        tab_w = self.SIDEBAR_W // 4
        
        for i, tab in enumerate(tabs):
            x = i * tab_w
            active = i == self.current_tab
            color = ACCENT if active else MUTED
            
            pygame.draw.rect(self.screen, PANEL if active else SURFACE,
                           (x, 0, tab_w, 46))
            if active:
                pygame.draw.line(self.screen, ACCENT, (x, 46),
                               (x + tab_w, 46), 2)
            
            draw_text(self.screen, tab, self.fnt_tiny, color, x + tab_w//2 - 15, 16)
    
    def _draw_tab_info(self, y0):
        """Dibuja pestaña de info"""
        sx = 10
        draw_text(self.screen, "─ CONTROLES ─", self.fnt_small, ACCENT, sx, y0)
        controles = [
            "ESPACIO: Etiquetas",
            "FLECHAS: Mover",
            "↑↓: Zoom",
            "1-4: Pestañas",
            "R: Limpiar ruta",
            "ESC: Salir"
        ]
        y = y0 + 22
        for ctrl in controles:
            draw_text(self.screen, ctrl, self.fnt_tiny, TEXT, sx, y)
            y += 16
        
        draw_text(self.screen, "─ DATOS GRAFO ─", self.fnt_small, ACCENT3, sx, y0 + 130)
        draw_text(self.screen, f"Nodos: {len(self.grafo)}", self.fnt_tiny, TEXT, sx, y0 + 152)
        draw_text(self.screen, f"Aristas: {len(self.grafo.todas_aristas())//2}", self.fnt_tiny, TEXT, sx, y0 + 170)
        
        if self.ruta and self.ruta.encontrada:
            draw_text(self.screen, "─ RUTA ACTIVA ─", self.fnt_small, ACCENT, sx, y0 + 210)
            draw_text(self.screen, f"Coste: {self.ruta.coste:.2f}", self.fnt_tiny, TEXT, sx, y0 + 232)
            draw_text(self.screen, f"Pasos: {len(self.ruta.camino)}", self.fnt_tiny, TEXT, sx, y0 + 250)
    
    def _draw_tab_nodos(self, y0):
        """Dibuja pestaña de nodos"""
        sx = 10
        draw_text(self.screen, "─ NODOS ESPECIALES ─", self.fnt_tiny, MUTED, sx, y0+315)
        ny = y0+331
        for n in self.grafo.nodos():
            if n.tipo == "interseccion":
                continue
            icon = "⚑" if n.tipo == "base" else "⚬"
            col = RED if n.tipo == "base" else BLUE
            draw_text(self.screen, f"{icon} {n.nombre}", self.fnt_tiny, col, sx, ny)
            ny += 13
            if ny > self.H - 30:
                break
    
    def _draw_tab_ciudades(self, y0):
        """Dibuja pestaña de ciudades"""
        sx = 10
        draw_text(self.screen, "─ GUARDAR CIUDAD ACTUAL ─", self.fnt_small, ACCENT, sx, y0)
        draw_text(self.screen, "Nombre del archivo:", self.fnt_tiny, MUTED, sx, y0+22)
        
        self.inp_nombre_ciudad.rect.y = y0 + 38
        self.inp_nombre_ciudad.update(self.clock.get_time())
        self.inp_nombre_ciudad.draw(self.screen)
        
        self.btn_guardar.rect.y = y0 + 74
        self.btn_guardar.draw(self.screen)
        
        draw_text(self.screen, "─ MIS CIUDADES GUARDADAS ─", self.fnt_small, ACCENT3, sx, y0+130)
        
        if not self._ciudades_cache:
            self._ciudades_cache = listar_ciudades()
        
        cy = y0 + 155
        ciudades_visibles = self._ciudades_cache[self._ciudades_scroll:]
        
        if not ciudades_visibles:
            draw_text(self.screen, "No hay ciudades guardadas aún.", self.fnt_tiny, MUTED, sx, cy)
            return
        
        for c in ciudades_visibles:
            if cy > self.H - 50:
                break
            
            rect_bg = pygame.Rect(sx, cy, self.SIDEBAR_W - 20, 50)
            pygame.draw.rect(self.screen, PANEL, rect_bg, border_radius=5)
            pygame.draw.rect(self.screen, BORDER, rect_bg, 1, border_radius=5)
            
            draw_text(self.screen, c["nombre"].upper(), self.fnt_med, TEXT, sx+10, cy+8)
            info_grafos = f"{c.get('nodos', 0)} nodos | {c.get('calles', 0)} calles"
            draw_text(self.screen, info_grafos, self.fnt_tiny, MUTED, sx+10, cy+28)
            
            btn_cargar = pygame.Rect(self.SIDEBAR_W - 85, cy + 12, 70, 26)
            c["rect_cargar"] = btn_cargar
            
            mx, my = pygame.mouse.get_pos()
            color_btn = (100, 255, 100) if btn_cargar.collidepoint(mx, my) else (57, 255, 20)
            
            pygame.draw.rect(self.screen, color_btn, btn_cargar, border_radius=3)
            draw_text(self.screen, "CARGAR", self.fnt_tiny, (0,0,0),
                     btn_cargar.centerx, btn_cargar.centery-6, center=True)
            
            cy += 60
    
    def _draw_tab_log(self, y0):
        """Dibuja pestaña de log"""
        sx = 10
        draw_text(self.screen, "─ REGISTRO DE EVENTOS ─", self.fnt_small, MUTED, sx, y0)
        colors = {"ok": ACCENT3, "err": RED, "warn": ACCENT2, "info": ACCENT}
        for i, (t, msg, kind) in enumerate(reversed(self.log_lines)):
            ly = y0 + 20 + i * 15
            if ly > self.H - 20:
                break
            draw_text(self.screen, t, self.fnt_tiny, MUTED, sx, ly)
            draw_text(self.screen, msg, self.fnt_tiny, colors.get(kind, TEXT), sx+55, ly)
    
    def _draw_map(self):
        """Dibuja el mapa de la ciudad"""
        cs = self.cell_size
        ox, oy = int(self.map_offset[0]), int(self.map_offset[1])
        map_rect = pygame.Rect(self.SIDEBAR_W, 46, self.W-self.SIDEBAR_W, self.H-46)
        self.screen.set_clip(map_rect)
        
        # Grilla
        for i in range(21):
            x = ox + i*cs
            y = oy + i*cs
            pygame.draw.line(self.screen, (20,25,38), (x, oy), (x, oy+20*cs), 1)
            pygame.draw.line(self.screen, (20,25,38), (ox, y), (ox+20*cs, y), 1)
        
        # Aristas
        route_set = set()
        if self.ruta and self.ruta.encontrada:
            for i in range(len(self.ruta.camino)-1):
                a, b = self.ruta.camino[i], self.ruta.camino[i+1]
                route_set.add((a,b))
                route_set.add((b,a))
        
        seen_edges = set()
        for a in self.grafo.todas_aristas():
            key = tuple(sorted([a.origen, a.destino]))
            if key in seen_edges:
                continue
            seen_edges.add(key)
            n1 = self.grafo.obtener_nodo(a.origen)
            n2 = self.grafo.obtener_nodo(a.destino)
            if not n1 or not n2:
                continue
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
        
        # Nodos
        hover = self._screen_to_node(*pygame.mouse.get_pos()) if pygame.mouse.get_pos()[0] > self.SIDEBAR_W else None
        for n in self.grafo.nodos():
            px, py = ox + int((n.x+0.5)*cs), oy + int((n.y+0.5)*cs)
            in_route = self.ruta and self.ruta.encontrada and n.nombre in self.ruta.camino
            is_sel = n.nombre == self.selected_node
            is_orig = n.nombre == self.click_origen
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
            
            if is_sel or is_orig:
                col = YELLOW if is_orig else ACCENT
                ring_r = max(5, cs//5 + 3)
                pygame.draw.circle(self.screen, col, (px,py), ring_r, 2)
            
            if self.show_labels or n.tipo != "interseccion" or in_route or is_hover:
                col_lbl = (RED if n.tipo=="base" else
                          BLUE if n.tipo=="empresa" else
                          (ACCENT if in_route else YELLOW if is_hover else MUTED))
                draw_text(self.screen, n.nombre, self.fnt_tiny, col_lbl,
                         px, py + max(4, cs//5 + 2), center=True)
        
        # Labels de eje
        if cs >= 20:
            for i in range(20):
                draw_text(self.screen, FILAS[i], self.fnt_tiny, MUTED,
                         ox - 14, oy + i*cs + cs//2 - 5, center=True)
                draw_text(self.screen, str(i+1), self.fnt_tiny, MUTED,
                         ox + i*cs + cs//2, oy - 14, center=True)
        
        self.screen.set_clip(None)
    
    def run(self):
        """Loop principal de la aplicación"""
        while True:
            dt = self.clock.tick(60)
            if not self.handle_events():
                break
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    try:
        import pygame
    except ImportError:
        print("Pygame no está instalado. Ejecuta:  pip install pygame")
        sys.exit(1)
    
    App().run()
