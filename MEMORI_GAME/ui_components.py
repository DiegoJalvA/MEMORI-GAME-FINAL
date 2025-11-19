
#COMPONENTES DE INTERFAZ DE USUARIO

import pygame
import config

def draw_text(screen, text, size, color, x, y, align="center", max_width=None):
    """Dibujar texto en la pantalla con soporte para max_width"""
    font = pygame.font.SysFont(config.FONT_NAME, size)
    
    # Si hay max_width, dividir el texto en múltiples líneas
    if max_width and max_width > 0:
        lines = []
        words = text.split(' ')
        current_line = []
        
        for word in words:
            # Probar si la palabra cabe en la línea actual
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                # Nueva línea
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        # Agregar a la última línea
        if current_line:
            lines.append(' '.join(current_line))
        
        # Dibujar cada línea
        total_height = len(lines) * (size + 2)  # Espacio entre líneas
        start_y = y - (total_height // 2)
        
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            line_rect = line_surface.get_rect()
            
            if align == "center":
                line_rect.center = (x, start_y + i * (size + 2))
            elif align == "left":
                line_rect.midleft = (x, start_y + i * (size + 2))
            elif align == "right":
                line_rect.midright = (x, start_y + i * (size + 2))
            
            screen.blit(line_surface, line_rect)
        
        # Devolver el rectángulo que contiene todo el texto
        if lines:
            first_line = font.render(lines[0], True, color)
            last_line = font.render(lines[-1], True, color)
            return pygame.Rect(x - max_width//2, start_y, max_width, total_height)
        return pygame.Rect(x, y, 0, 0)
    
    else:
        # Comportamiento sin max_width
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        if align == "center":
            text_rect.center = (x, y)
        elif align == "left":
            text_rect.midleft = (x, y)
        elif align == "right":
            text_rect.midright = (x, y)
        
        screen.blit(text_surface, text_rect)
        return text_rect

def draw_button(screen, text, x, y, width, height, color=config.BUTTON_COLOR, 
                hover_color=config.BUTTON_HOVER_COLOR, text_color=config.BUTTON_TEXT_COLOR):
    # Se Dibuja un botón 
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, width, height)
    
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, button_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 215, 0), button_rect, 3, border_radius=15)
    else:
        pygame.draw.rect(screen, color, button_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 0), button_rect, 2, border_radius=15)
    
    # Ajustar tamaño de fuente según el ancho del botón y longitud del texto
    font_size = 24
    font = pygame.font.SysFont(config.FONT_NAME, font_size)
    text_surf = font.render(text, True, text_color)
    
    # Si el texto es demasiado ancho para el botón, se reduce el tamaño de la fuente
    while text_surf.get_width() > width - 20 and font_size > 12:
        font_size -= 1
        font = pygame.font.SysFont(config.FONT_NAME, font_size)
        text_surf = font.render(text, True, text_color)
    
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)
    return button_rect

def draw_card(screen, card, x, y, width, height):
    # Dibuja una carta en la posición especificada
    if card["matched"]:
        pygame.draw.rect(screen, config.CARD_MATCHED_COLOR, (x, y, width, height), border_radius=15)
        pygame.draw.rect(screen, (0, 255, 0), (x, y, width, height), 4, border_radius=15)
    elif card["flipped"]:
        pygame.draw.rect(screen, config.CARD_FLIPPED_COLOR, (x, y, width, height), border_radius=15)
        pygame.draw.rect(screen, (255, 215, 0), (x, y, width, height), 3, border_radius=15)
    else:
        pygame.draw.rect(screen, config.CARD_COLOR, (x, y, width, height), border_radius=15)
        pygame.draw.rect(screen, (0, 0, 0), (x, y, width, height), 3, border_radius=15)
    
    if card["flipped"] or card["matched"]:
        font_size = 20 if len(str(card["front"])) < 10 else 16
        font = pygame.font.SysFont(config.FONT_NAME, font_size)
        text = font.render(str(card["front"]), True, config.BLACK)
        text_rect = text.get_rect(center=(x + width//2, y + height//2))
        screen.blit(text, text_rect)

def draw_background(screen, num_stars=100):
    #  Dibuja el fondo estrellado
    screen.fill(config.SCREEN_BG)
    for i in range(num_stars):
        x = (i * 73) % config.WIDTH
        y = (i * 57) % config.HEIGHT
        pygame.draw.circle(screen, (255, 255, 200), (x, y), 1)