"""
CONFIGURACIONES DE MEMORI GAME
"""

# CONSTANTES VISUALES 
WIDTH, HEIGHT = 1200, 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHTGRAY = (230, 230, 230)
RED = (220, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 120, 255)
LIGHTBLUE = (173, 216, 230)
YELLOW = (255, 225, 0)
PURPLE = (180, 0, 255)
ORANGE = (255, 165, 0)
CARD_COLOR = (255, 215, 0)  # Oro
CYAN = (0, 255, 255)
LIGHTGREEN = (144, 238, 144)
LIGHTRED = (255, 182, 193)
CARD_FLIPPED_COLOR = (255, 255, 224)  # Beige
CARD_MATCHED_COLOR = (50, 205, 50)  # Verde lima
BUTTON_COLOR = (70, 130, 180)  # Azul acero
BUTTON_HOVER_COLOR = (100, 149, 237)  # Azul real
BUTTON_ALT_COLOR = (244, 164, 96)  # Naranja arenoso
BUTTON_ALT_HOVER = (255, 165, 0)  # Naranja
BUTTON_TEXT_COLOR = WHITE
SCREEN_BG = (25, 25, 112)  # Azul marino
DIALOG_BG = (72, 61, 139)  # Púrpura oscuro
FONT_NAME = "Arial"
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 149, 237)
FONT_NAME = "Arial"

# CONSTANTES DE VALIDACIÓN 
CONNECTION_TIMEOUT = 300
MAX_NAME_LENGTH = 15
MAX_CARD_TEXT_LENGTH = 20
VALID_MODES = ["País-Capital", "Matemáticas", "Español-Inglés"]
VALID_DIFFICULTIES = ["Fácil", "Medio", "Difícil"]
VALID_TUTORIALS = ["País-Capital", "Matemáticas", "Español-Inglés", "Supervivencia", "Multijugador"] 
MIN_PORT = 1024
MAX_PORT = 65535
DEFAULT_PORT = 5555


#CONFIGURACIÓN DEL JUEGO 
DIFICULTAD_CONFIG = {
    "Fácil": {
        "total_cartas": 12,     # 6 pares
        "cols": 4,
        "rows": 3
    },
    "Medio": {
        "total_cartas": 16,    # 8 pares
        "cols": 4,
        "rows": 4
    },
    "Difícil": {
        "total_cartas": 36,    # 18 pares
        "cols": 6,
        "rows": 6
    }
}


# DATOS EDUCATIVOS 
PAISES_CAPITALES = {
    "Quito": "Ecuador", "Lima": "Perú", "Bogotá": "Colombia",
    "Santiago": "Chile", "Buenos Aires": "Argentina", "Brasilia": "Brasil",
    "Caracas": "Venezuela", "Montevideo": "Uruguay", "Asunción": "Paraguay",
    "La Paz": "Bolivia", "Ciudad de México": "México", "San José": "Costa Rica",
    "Panamá": "Panamá", "Havana": "Cuba", "Madrid": "España", "Lisboa": "Portugal",
    "París": "Francia", "Roma": "Italia", "Berlín": "Alemania", "Tokio": "Japán"
}

PALABRAS_ESPANOL_INGLES = {
    "Casa": "House", "Perro": "Dog", "Gato": "Cat", "Agua": "Water",
    "Sol": "Sun", "Luna": "Moon", "Cielo": "Sky", "Fuego": "Fire",
    "Libro": "Book", "Escuela": "School", "Amigo": "Friend",
    "Familia": "Family", "Comida": "Food", "Ciudad": "City",
    "País": "Country", "Música": "Music", "Auto": "Car", "Avión": "Plane"
}

# SISTEMA DE TUTORIAL 
TUTORIAL_DATA = {
    "País-Capital": {
        "titulo": "MODO PAÍS-CAPITAL",
        "descripcion": "Encuentra los pares de países con sus capitales correspondientes",
        "ejemplo": [
            {"carta1": "España", "carta2": "Madrid", "explicacion": "Madrid es la capital de España"},
            {"carta1": "Francia", "carta2": "París", "explicacion": "París es la capital de Francia"}
        ],
        "instrucciones": [
            "Encuentra el país que corresponde a cada capital",
            "Las cartas pueden mostrar países o capitales",
            "Haz clic en dos cartas para voltearlas",
            "Si forman un par correcto, permanecerán visibles"
        ]
    },
    "Matemáticas": {
        "titulo": "MODO MATEMÁTICAS", 
        "descripcion": "Resuelve operaciones matemáticas y encuentra sus resultados",
        "ejemplo": [
            {"carta1": "5 + 3", "carta2": "8", "explicacion": "5 + 3 = 8"},
            {"carta1": "10 x 4", "carta2": "40", "explicacion": "10 x 4 = 40"}
        ],
        "instrucciones": [
            "Encuentra la operación con su resultado correcto",
            "Pueden ser sumas, restas o multiplicaciones",
            "Haz coincidir cada operación con su solución",
            "¡Practica tu agilidad mental!"
        ]
    },
    "Español-Inglés": {
        "titulo": "MODO ESPAÑOL-INGLÉS",
        "descripcion": "Aprende vocabulario emparejando palabras en español con inglés",
        "ejemplo": [
            {"carta1": "Casa", "carta2": "House", "explicacion": "Casa en inglés es House"},
            {"carta1": "Perro", "carta2": "Dog", "explicacion": "Perro en inglés es Dog"}
        ],
        "instrucciones": [
            "Empareja cada palabra en español con su traducción en inglés",
            "Amplía tu vocabulario mientras juegas",
            "Las cartas pueden estar en cualquier idioma",
            "¡Aprende inglés de forma divertida!"
        ]
    },
     "Supervivencia": {
        "titulo": "MODO SUPERVIVENCIA",
        "descripcion": "¡Contra reloj! Encuentra pares antes de que se acabe el tiempo. Cada acierto te da tiempo extra, cada error te quita tiempo.",
        "ejemplo": [
            {
                "carta1": "Par encontrado", 
                "carta2": "+15 segundos", 
                "explicacion": "Cada par correcto te da tiempo extra según la dificultad"
            },
            {
                "carta1": "Error", 
                "carta2": "-5 segundos", 
                "explicacion": "Cada error reduce tu tiempo restante"
            }
        ],
        "instrucciones": [
            "Tienes tiempo limitado: 90s (Fácil), 75s (Medio), 60s (Difícil)",
            "Cada acierto suma tiempo: +15s (Fácil), +12s (Medio), +10s (Difícil)",
            "Cada error resta tiempo: -5s (Fácil), -7s (Medio), -10s (Difícil)",
            "El juego termina cuando el tiempo llegue a 0",
            "¡Encuentra todos los pares antes de que se agote el tiempo!",
            
        ]
    },
    "Multijugador": {
        "titulo": "MODO MULTIJUGADOR",
        "descripcion": "Juega contra amigos en tiempo real - Crea salas o únete a partidas existentes",
        "ejemplo": [
            {
                "carta1": "CREAR SALA",
                "carta2": "CÓDIGO: ABCD", 
                "explicacion": "Como ANFITRIÓN creas la sala y compartes el código"
            },
            {
                "carta1": "UNIRSE A SALA",
                "carta2": "INGRESAR CÓDIGO",
                "explicacion": "Como INVITADO usas el código para unirte a una sala"
            },
            {
                "carta1": "TURNO ANFITRIÓN", 
                "carta2": "TURNO INVITADO",
                "explicacion": "Los turnos se alternan automáticamente entre jugadores"
            }
        ],
        "instrucciones": [
            " El ANFITRIÓN elige el modo de juego y dificultad",
            " Ambos jugadores deben dar 'LISTO' para comenzar", 
            " Los turnos se alternan después de cada par incorrecto",
            " Encuentra pares para sumar puntos a tu marcador personal",
            " El juego termina cuando se encuentran todos los pares",
            " Gana el jugador con más puntos al final",
            " ¡Cuidado! Abandonar la sala significa derrota automática",
            " Usa auriculares para mejor experiencia con los sonidos"
        ]
    }

}

#  FUNCIONES DE VALIDACIÓN 
def validar_texto_carta(texto):
    if not texto:
        return " "
    texto = str(texto)
    if len(texto) > MAX_CARD_TEXT_LENGTH:
        return texto[:MAX_CARD_TEXT_LENGTH-3] + "..."
    return texto

def validar_modo(modo):
    return modo if modo in VALID_MODES else VALID_MODES[0]

def validar_dificultad(dificultad):
    return dificultad if dificultad in VALID_DIFFICULTIES else VALID_DIFFICULTIES[0]

#  MODO SUPERVIVENCIA 
MODOS_JUEGO = ["Normal", "Supervivencia"]

SUPERVIVENCIA_CONFIG = {
    "Fácil": {"tiempo_inicial": 90, "bonus_acierto": 15, "penalizacion_error": 5},
    "Medio": {"tiempo_inicial": 75, "bonus_acierto": 12, "penalizacion_error": 7},
    "Difícil": {"tiempo_inicial": 60, "bonus_acierto": 10, "penalizacion_error": 10}
}