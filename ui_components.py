# ui_components.py - COMPONENTES DE INTERFAZ

import pygame
from config import PANEL, BORDER, TEXT, MUTED, ACCENT3


class TextInput:
    """Campo de entrada de texto"""
    
    def __init__(self, x, y, w, h, font, placeholder=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.value = ""
        self.placeholder = placeholder
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def handle_event(self, event):
        """Maneja eventos de entrada"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.key == pygame.K_RETURN:
                return self.value
            elif len(self.value) < 30:
                self.value += event.unicode
        return None
    
    def update(self, dt):
        """Actualiza la visibilidad del cursor"""
        self.cursor_timer += dt
        if self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, surface):
        """Dibuja el campo de entrada"""
        # Fondo
        pygame.draw.rect(surface, PANEL, self.rect, border_radius=4)
        pygame.draw.rect(surface, BORDER, self.rect, 1, border_radius=4)
        
        # Texto
        display_text = self.value if self.value else self.placeholder
        color = TEXT if self.value else MUTED
        txt = self.font.render(display_text, True, color)
        surface.blit(txt, (self.rect.x + 8, self.rect.y + 6))
        
        # Cursor
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 8 + txt.get_width()
            pygame.draw.line(surface, ACCENT3, (cursor_x, self.rect.y + 4),
                           (cursor_x, self.rect.y + self.rect.h - 4), 2)


class Button:
    """Botón interactivo"""
    
    def __init__(self, x, y, w, h, text, font, color_bg, color_text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.color_bg = color_bg
        self.color_text = color_text
        self.hovered = False
    
    def handle_event(self, event):
        """Retorna True si fue clickeado"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.rect.collidepoint(event.pos)
        return False
    
    def update(self, mouse_pos):
        """Actualiza estado de hover"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface):
        """Dibuja el botón"""
        color = tuple(min(255, c + 40) for c in self.color_bg) if self.hovered else self.color_bg
        
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, self.color_text, self.rect, 1, border_radius=5)
        
        txt = self.font.render(self.text, True, self.color_text)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)
