
"""
MEMORI GAME 
"""
import pygame
import sys
from game_core import Client

def main():
    """Función principal del juego"""
    try:
        print("Iniciando Memori Game...")
        client = Client()
        client.main_loop()
    except Exception as e:
        print(f"Error crítico: {e}")
        import traceback
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
    