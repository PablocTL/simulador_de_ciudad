# drawing_utils.py - UTILIDADES DE DIBUJO

import pygame
from config import BG


def draw_text(surface, text, font, color, x, y, center=False):
    """Dibuja texto en la pantalla"""
    txt = font.render(str(text), True, color)
    rect = txt.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(txt, rect)


def glow_line(surface, color, p1, p2, w=2, glow=3):
    """Dibuja una línea con efecto glow"""
    # Glow oscuro base
    dark_color = tuple(max(0, c // 3) for c in color)
    for offset in range(glow, 0, -1):
        alpha = 255 // (glow + 1) * (glow - offset + 1)
        s = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        pygame.draw.line(s, (*dark_color, alpha), p1, p2, w + offset * 2)
        surface.blit(s, (0, 0))
    
    # Línea principal
    pygame.draw.line(surface, color, p1, p2, w)


def glow_circle(surface, color, x, y, r, glow=4):
    """Dibuja un círculo con efecto glow"""
    # Glow oscuro base
    dark_color = tuple(max(0, c // 3) for c in color)
    for offset in range(glow, 0, -1):
        alpha = 255 // (glow + 1) * (glow - offset + 1)
        s = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        pygame.draw.circle(s, (*dark_color, alpha), (x, y), r + offset)
        surface.blit(s, (0, 0))
    
    # Círculo principal
    pygame.draw.circle(surface, color, (x, y), r)


def draw_button(surface, rect, text, font, color_bg, color_text, hover=False):
    """Dibuja un botón con efecto hover"""
    if hover:
        color_bg = tuple(min(255, c + 40) for c in color_bg)
    
    pygame.draw.rect(surface, color_bg, rect, border_radius=5)
    pygame.draw.rect(surface, color_text, rect, 1, border_radius=5)
    
    txt = font.render(text, True, color_text)
    txt_rect = txt.get_rect(center=rect.center)
    surface.blit(txt, txt_rect)


def draw_panel(surface, rect, color_bg, color_border=None, title=None, font=None):
    """Dibuja un panel/ventana"""
    pygame.draw.rect(surface, color_bg, rect, border_radius=8)
    if color_border:
        pygame.draw.rect(surface, color_border, rect, 1, border_radius=8)
    
    if title and font:
        txt = font.render(title, True, (255, 255, 255))
        surface.blit(txt, (rect.x + 10, rect.y + 8))
