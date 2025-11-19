"""
SISTEMA DE LOGROS PARA MEMORI GAME
"""
import json
import os
import time
from datetime import datetime

# CATEGORÍAS DE LOGROS
ACHIEVEMENT_CATEGORIES = {
    "PRIMEROS_PASOS": "Primeros Pasos",
    "MAESTRO_MEMORIA": "Maestro de la Memoria", 
    "VELOCIDAD": "Velocidad y Reflexes",
    "MODOS_JUEGO": "Especialista en Modos",
    "DIFICULTAD": "Retos de Dificultad",
    "MULTIJUGADOR": "Competitivo",
    "SUPERVIVENCIA": "Supervivencia Extrema",
    "COLECCIONISTA": "Coleccionista",
    "SECRETOS": "Logros Secretos"
}

# SISTEMA DE LOGROS 
ACHIEVEMENTS = {
    # PRIMEROS PASOS 
    "PRIMER_JUEGO": {
        "id": "PRIMER_JUEGO",
        "nombre": "¡Primer Juego!",
        "descripcion": "Completa tu primera partida",
        "categoria": "PRIMEROS_PASOS",
        "tipo": "contador_partidas",
        "meta": 1,
        "puntos": 10,
        "icono": "",
        "rareza": "común"
    },
    
    "PRIMER_PAR": {
        "id": "PRIMER_PAR", 
        "nombre": "Primer Par Encontrado",
        "descripcion": "Encuentra tu primer par de cartas",
        "categoria": "PRIMEROS_PASOS",
        "tipo": "contador_pares",
        "meta": 1,
        "puntos": 5,
        "icono": "",
        "rareza": "común"
    },

    "TUTORIAL_COMPLETO": {
        "id": "TUTORIAL_COMPLETO",
        "nombre": "Aprendiz Aprobado",
        "descripcion": "Completa todos los tutoriales",
        "categoria": "PRIMEROS_PASOS", 
        "tipo": "contador_tutoriales",
        "meta": 4,
        "puntos": 20,
        "icono": "",
        "rareza": "raro"
    },

    # === MAESTRO DE MEMORIA ===
    "MEMORIA_PERFECTA": {
        "id": "MEMORIA_PERFECTA",
        "nombre": "Memoria Perfecta",
        "descripcion": "Completa un juego sin errores",
        "categoria": "MAESTRO_MEMORIA",
        "tipo": "sin_errores",
        "meta": 1,
        "puntos": 50,
        "icono": "",
        "rareza": "épico"
    },

    "CADENA_ACIERTOS": {
        "id": "CADENA_ACIERTOS",
        "nombre": "Racha de Aciertos",
        "descripcion": "Encuentra 5 pares consecutivos sin errores",
        "categoria": "MAESTRO_MEMORIA",
        "tipo": "racha_pares",
        "meta": 5,
        "puntos": 30,
        "icono": "",
        "rareza": "raro"
    },

    "EFICIENCIA_MAXIMA": {
        "id": "EFICIENCIA_MAXIMA",
        "nombre": "Eficiencia Máxima",
        "descripcion": "Completa un juego con 100% de eficiencia",
        "categoria": "MAESTRO_MEMORIA",
        "tipo": "eficiencia_100",
        "meta": 100,
        "puntos": 75,
        "icono": "",
        "rareza": "legendario"
    },

    # === VELOCIDAD ===
    "VELOCIDAD_RELOJ": {
        "id": "VELOCIDAD_RELOJ",
        "nombre": "Velocidad Relámpago",
        "descripcion": "Completa un juego en modo Difícil en menos de 60 segundos",
        "categoria": "VELOCIDAD", 
        "tipo": "tiempo_dificil",
        "meta": 60,
        "puntos": 40,
        "icono": "",
        "rareza": "raro"
    },

    # === MODOS DE JUEGO ===
    "MAESTRO_PAISES": {
        "id": "MAESTRO_PAISES",
        "nombre": "Geógrafo Experto",
        "descripcion": "Gana 10 partidas en modo País-Capital",
        "categoria": "MODOS_JUEGO",
        "tipo": "victorias_pais_capital",
        "meta": 10,
        "puntos": 30,
        "icono": "",
        "rareza": "raro"
    },

    "GENIO_MATEMATICO": {
        "id": "GENIO_MATEMATICO", 
        "nombre": "Genio Matemático",
        "descripcion": "Gana 10 partidas en modo Matemáticas",
        "categoria": "MODOS_JUEGO",
        "tipo": "victorias_matematicas", 
        "meta": 10,
        "puntos": 30,
        "icono": "",
        "rareza": "raro"
    },

    "POLIGLOTA": {
        "id": "POLIGLOTA",
        "nombre": "Políglota",
        "descripcion": "Gana 10 partidas en modo Español-Inglés", 
        "categoria": "MODOS_JUEGO",
        "tipo": "victorias_espanol_ingles",
        "meta": 10,
        "puntos": 30,
        "icono": "",
        "rareza": "raro"
    },

    "EXPLORADOR_MODOS": {
        "id": "EXPLORADOR_MODOS",
        "nombre": "Explorador de Modos",
        "descripcion": "Juega al menos una partida en cada modo",
        "categoria": "MODOS_JUEGO",
        "tipo": "modos_jugados",
        "meta": 3,
        "puntos": 25,
        "icono": "",
        "rareza": "común"
    },

    # === DIFICULTAD ===
    "INICIADO_FACIL": {
        "id": "INICIADO_FACIL",
        "nombre": "Iniciado",
        "descripcion": "Completa 5 partidas en dificultad Fácil",
        "categoria": "DIFICULTAD",
        "tipo": "partidas_facil",
        "meta": 5,
        "puntos": 15,
        "icono": "",
        "rareza": "común"
    },

    "EXPERTO_MEDIO": {
        "id": "EXPERTO_MEDIO",
        "nombre": "Experto",
        "descripcion": "Completa 10 partidas en dificultad Medio", 
        "categoria": "DIFICULTAD",
        "tipo": "partidas_medio",
        "meta": 10,
        "puntos": 30,
        "icono": "",
        "rareza": "raro"
    },

    "MAESTRO_DIFICIL": {
        "id": "MAESTRO_DIFICIL",
        "nombre": "Maestro",
        "descripcion": "Completa 15 partidas en dificultad Difícil",
        "categoria": "DIFICULTAD",
        "tipo": "partidas_dificil",
        "meta": 15,
        "puntos": 50,
        "icono": "",
        "rareza": "épico"
    },

    "TRIPLE_CORONA": {
        "id": "TRIPLE_CORONA",
        "nombre": "Triple Corona",
        "descripcion": "Establece récords en las 3 dificultades de un modo",
        "categoria": "DIFICULTAD",
        "tipo": "records_todas_dificultades",
        "meta": 1,
        "puntos": 100,
        "icono": "",
        "rareza": "legendario"
    },

    # === MULTIJUGADOR ===
    "PRIMERA_VICTORIA_MULTI": {
        "id": "PRIMERA_VICTORIA_MULTI",
        "nombre": "Primera Victoria Multijugador",
        "descripcion": "Gana tu primera partida multijugador",
        "categoria": "MULTIJUGADOR", 
        "tipo": "victorias_multijugador",
        "meta": 1,
        "puntos": 20,
        "icono": "",
        "rareza": "común"
    },

    "INVICTO_MULTI": {
        "id": "INVICTO_MULTI",
        "nombre": "Invicto",
        "descripcion": "Gana 5 partidas multijugador consecutivas",
        "categoria": "MULTIJUGADOR",
        "tipo": "racha_victorias_multi",
        "meta": 5,
        "puntos": 60,
        "icono": "",
        "rareza": "épico"
    },

    "ANFITRION_EXPERTO": {
        "id": "ANFITRION_EXPERTO",
        "nombre": "Anfitrión Experto",
        "descripcion": "Crea 10 salas diferentes",
        "categoria": "MULTIJUGADOR",
        "tipo": "salas_creadas",
        "meta": 10,
        "puntos": 25,
        "icono": "",
        "rareza": "raro"
    },

    "INVITADO_FRECUENTE": {
        "id": "INVITADO_FRECUENTE", 
        "nombre": "Invitado Frecuente",
        "descripcion": "Únete a 10 salas diferentes",
        "categoria": "MULTIJUGADOR",
        "tipo": "salas_unidas",
        "meta": 10,
        "puntos": 25,
        "icono": "",
        "rareza": "raro"
    },

    # === SUPERVIVENCIA ===
    "CADENA_SUPERVIVENCIA": {
        "id": "CADENA_SUPERVIVENCIA",
        "nombre": "Cadena de Supervivencia",
        "descripcion": "Encuentra 10 pares consecutivos en Supervivencia",
        "categoria": "SUPERVIVENCIA",
        "tipo": "racha_supervivencia",
        "meta": 10,
        "puntos": 40,
        "icono": "",
        "rareza": "épico"
    },

    # === COLECCIONISTA ===
    "JUGADOR_ASIDUO": {
        "id": "JUGADOR_ASIDUO",
        "nombre": "Jugador Asiduo",
        "descripcion": "Juega 50 partidas en total",
        "categoria": "COLECCIONISTA",
        "tipo": "total_partidas",
        "meta": 50,
        "puntos": 30,
        "icono": "",
        "rareza": "raro"
    },

    "ADICTO_MEMORI": {
        "id": "ADICTO_MEMORI",
        "nombre": "Adicto a Memori",
        "descripcion": "Juega 100 partidas en total", 
        "categoria": "COLECCIONISTA",
        "tipo": "total_partidas",
        "meta": 100,
        "puntos": 60,
        "icono": "",
        "rareza": "épico"
    },

    "LEYENDA_VIVIENTE": {
        "id": "LEYENDA_VIVIENTE",
        "nombre": "Leyenda Viviente",
        "descripcion": "Juega 200 partidas en total",
        "categoria": "COLECCIONISTA",
        "tipo": "total_partidas",
        "meta": 200,
        "puntos": 100,
        "icono": "",
        "rareza": "legendario"
    },

    "COLECCIONISTA_LOGROS": {
        "id": "COLECCIONISTA_LOGROS",
        "nombre": "Coleccionista de Logros",
        "descripcion": "Desbloquea 25 logros diferentes",
        "categoria": "COLECCIONISTA",
        "tipo": "logros_desbloqueados",
        "meta": 25,
        "puntos": 75,
        "icono": "",
        "rareza": "épico"
    },

    "MAESTRO_ABSOLUTO": {
        "id": "MAESTRO_ABSOLUTO",
        "nombre": "Maestro Absoluto",
        "descripcion": "Desbloquea todos los logros del juego",
        "categoria": "COLECCIONISTA", 
        "tipo": "logros_desbloqueados",
        "meta": 35,
        "puntos": 200,
        "icono": "",
        "rareza": "legendario"
    },

    # === LOGROS SECRETOS ===
    "PERFECCIONISTA": {
        "id": "PERFECCIONISTA",
        "nombre": "Perfeccionista",
        "descripcion": "Completa un juego sin voltear cartas incorrectas",
        "categoria": "SECRETOS", 
        "tipo": "sin_errores",
        "meta": 1,
        "puntos": 45,
        "icono": "",
        "rareza": "épico",
        "secreto": True
    },

    "RAPIDO_Y_PRECISO": {
        "id": "RAPIDO_Y_PRECISO",
        "nombre": "Rápido y Preciso",
        "descripcion": "Completa un juego en menos de 30 segundos sin errores",
        "categoria": "SECRETOS",
        "tipo": "tiempo_sin_errores",
        "meta": 30,
        "puntos": 80,
        "icono": "",
        "rareza": "legendario", 
        "secreto": True
    },

    "ULTIMO_SEGUNDO": {
        "id": "ULTIMO_SEGUNDO",
        "nombre": "Último Segundo",
        "descripcion": "Gana una partida de Supervivencia con menos de 3 segundos restante",
        "categoria": "SECRETOS",
        "tipo": "supervivencia_ultimo_segundo",
        "meta": 3,
        "puntos": 35,
        "icono": "",
        "rareza": "épico",
        "secreto": True
    },

    "INVENCIBLE": {
        "id": "INVENCIBLE",
        "nombre": "Invencible",
        "descripcion": "Gana 10 partidas multijugador sin perder ninguna",
        "categoria": "SECRETOS",
        "tipo": "racha_victorias_multi",
        "meta": 10,
        "puntos": 90,
        "icono": "",
        "rareza": "legendario",
        "secreto": True
    }
}

# CLASE GESTOR DE LOGROS
class AchievementManager:
    def __init__(self):
        self.achievements_data = {}
        self.estadisticas_partida_actual = {
            "pares_consecutivos": 0,
            "errores_partida": 0,
            "tiempo_partida": 0,
            "modo_actual": "",
            "dificultad_actual": "",
            "es_supervivencia": False,
            "es_multijugador": False
        }
        self.client_reference = None  # Referencia al cliente para notificaciones
        self.load_achievements()
        
    def set_client_reference(self, client):
        """Establecer referencia al cliente para notificaciones"""
        self.client_reference = client
        
    def load_achievements(self):
        """Cargar progreso de logros desde archivo"""
        try:
            if os.path.exists("achievements.json"):
                with open("achievements.json", "r", encoding='utf-8') as f:
                    self.achievements_data = json.load(f)
            else:
                self.achievements_data = self.get_estructura_inicial()
                self.save_achievements()
        except Exception as e:
            print(f"Error cargando logros: {e}")
            self.achievements_data = self.get_estructura_inicial()
            
    def save_achievements(self):
        """Guardar progreso de logros"""
        try:
            with open("achievements.json", "w", encoding='utf-8') as f:
                json.dump(self.achievements_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando logros: {e}")
            
    def get_estructura_inicial(self):
        """Estructura inicial de logros"""
        return {
            "logros_desbloqueados": {},
            "estadisticas": {
                "total_partidas": 0,
                "partidas_ganadas": 0,
                "total_pares_encontrados": 0,
                "total_errores": 0,
                "tiempo_total_jugado": 0,
                "partidas_por_modo": {
                    "País-Capital": 0,
                    "Matemáticas": 0,
                    "Español-Inglés": 0,
                    "Supervivencia": 0
                },
                "partidas_por_dificultad": {
                    "Fácil": 0,
                    "Medio": 0,
                    "Difícil": 0
                },
                "victorias_multijugador": 0,
                "racha_actual_victorias": 0,
                "mejor_racha_victorias": 0,
                "salas_creadas": 0,
                "salas_unidas": 0,
                "mejor_tiempo_supervivencia": 0,
                "tutoriales_completados": 0,
                "modos_jugados": [],
                "records_establecidos": []
            },
            "progreso_logros": {},
            "puntos_totales": 0,
            "nivel": 1
        }
    
    def iniciar_partida(self, modo, dificultad, es_supervivencia=False, es_multijugador=False):
        """Inicializar estadísticas para una nueva partida """
        self.estadisticas_partida_actual = {
            "pares_consecutivos": 0,
            "errores_partida": 0,
            "tiempo_partida": 0,
            "modo_actual": modo,
            "dificultad_actual": dificultad,
            "es_supervivencia": es_supervivencia,
            "es_multijugador": es_multijugador,
            "pares_encontrados": 0 
        }
        print(f" Logros: Partida iniciada - Modo: {modo}, Multijugador: {es_multijugador}")
            
    def registrar_par_encontrado(self):
        """Registrar que se encontró un par correctamente """
        try:
            # SE INICIALIZA SI NO EXISTE
            if "pares_encontrados" not in self.estadisticas_partida_actual:
                self.estadisticas_partida_actual["pares_encontrados"] = 0
                
            self.estadisticas_partida_actual["pares_consecutivos"] += 1
            self.estadisticas_partida_actual["pares_encontrados"] += 1
            
            # Actualizar estadística global
            self.actualizar_estadistica("total_pares_encontrados", 1)
            
            # Verificar logro de cadena de aciertos
            if self.estadisticas_partida_actual["pares_consecutivos"] >= 5:
                self.actualizar_progreso_logro("CADENA_ACIERTOS", 1)
                
            # Verificar logro de cadena en supervivencia
            if (self.estadisticas_partida_actual["es_supervivencia"] and 
                self.estadisticas_partida_actual["pares_consecutivos"] >= 10):
                self.actualizar_progreso_logro("CADENA_SUPERVIVENCIA", 1)
                
        except Exception as e:
            print(f" Error en registrar_par_encontrado: {e}")
            # Reinicializar en caso de error
            self.estadisticas_partida_actual["pares_encontrados"] = 1
            self.estadisticas_partida_actual["pares_consecutivos"] = 1

    def registrar_error(self):
        """Registrar un error (par incorrecto)"""
        self.estadisticas_partida_actual["pares_consecutivos"] = 0
        self.estadisticas_partida_actual["errores_partida"] += 1
        self.actualizar_estadistica("total_errores", 1)
    
    def finalizar_partida(self, tiempo, victoria=False):
        """Finalizar partida y verificar logros"""
        self.estadisticas_partida_actual["tiempo_partida"] = tiempo
        
        # Actualizar estadísticas generales
        self.actualizar_estadistica("total_partidas", 1)
        self.actualizar_estadistica("tiempo_total_jugado", tiempo)
        
        modo = self.estadisticas_partida_actual["modo_actual"]
        dificultad = self.estadisticas_partida_actual["dificultad_actual"]
        
        # Actualizar estadísticas por modo y dificultad
        self.actualizar_estadistica("", 0, modo, dificultad)
        
        if victoria:
            self.actualizar_estadistica("partidas_ganadas", 1)
            
            # Verificar logros específicos por modo
            if modo == "País-Capital":
                self.actualizar_progreso_logro("MAESTRO_PAISES", self.achievements_data["estadisticas"]["partidas_por_modo"]["País-Capital"])
            elif modo == "Matemáticas":
                self.actualizar_progreso_logro("GENIO_MATEMATICO", self.achievements_data["estadisticas"]["partidas_por_modo"]["Matemáticas"])
            elif modo == "Español-Inglés":
                self.actualizar_progreso_logro("POLIGLOTA", self.achievements_data["estadisticas"]["partidas_por_modo"]["Español-Inglés"])
                
            # Verificar logros de velocidad
            if dificultad == "Difícil" and tiempo <= 60:
                self.actualizar_progreso_logro("VELOCIDAD_RELOJ", 1)
                
            # Verificar logros de perfección
            if self.estadisticas_partida_actual["errores_partida"] == 0:
                self.actualizar_progreso_logro("MEMORIA_PERFECTA", 1)
                self.actualizar_progreso_logro("PERFECCIONISTA", 1)
                
                # Verificar rapidez y precisión
                if tiempo <= 30:
                    self.actualizar_progreso_logro("RAPIDO_Y_PRECISO", 1)
            
            # Verificar eficiencia máxima
            total_pares = self.estadisticas_partida_actual["pares_encontrados"]
            total_intentos = total_pares + self.estadisticas_partida_actual["errores_partida"]
            if total_intentos > 0:
                eficiencia = (total_pares / total_intentos) * 100
                if eficiencia == 100:
                    self.actualizar_progreso_logro("EFICIENCIA_MAXIMA", 1)
        
        # Verificar multijugador
        if self.estadisticas_partida_actual["es_multijugador"] and victoria:
            self.actualizar_estadistica("victorias_multijugador", 1)
            self.actualizar_estadistica("racha_actual_victorias", 1)
            
            # Actualizar mejor racha
            racha_actual = self.achievements_data["estadisticas"]["racha_actual_victorias"]
            mejor_racha = self.achievements_data["estadisticas"]["mejor_racha_victorias"]
            if racha_actual > mejor_racha:
                self.achievements_data["estadisticas"]["mejor_racha_victorias"] = racha_actual
            
            # Verificar logros de multijugador
            self.actualizar_progreso_logro("PRIMERA_VICTORIA_MULTI", self.achievements_data["estadisticas"]["victorias_multijugador"])
            self.actualizar_progreso_logro("INVICTO_MULTI", self.achievements_data["estadisticas"]["mejor_racha_victorias"])
            self.actualizar_progreso_logro("INVENCIBLE", self.achievements_data["estadisticas"]["mejor_racha_victorias"])
        elif self.estadisticas_partida_actual["es_multijugador"] and not victoria:
            self.actualizar_estadistica("racha_actual_victorias", 0)
        
        # Verificar supervivencia
        if self.estadisticas_partida_actual["es_supervivencia"] and victoria:
            if tiempo <= 3:  # Menos de 3 segundos restantes
                self.actualizar_progreso_logro("ULTIMO_SEGUNDO", 1)
            
            # Actualizar mejor tiempo de supervivencia
            mejor_tiempo = self.achievements_data["estadisticas"]["mejor_tiempo_supervivencia"]
            if tiempo > mejor_tiempo:
                self.achievements_data["estadisticas"]["mejor_tiempo_supervivencia"] = tiempo
        
        self.verificar_logros()
        self.save_achievements()
        
    def actualizar_estadistica(self, clave, valor=1, modo=None, dificultad=None):
        """Actualizar una estadística del jugador"""
        if clave and clave in self.achievements_data["estadisticas"]:
            if isinstance(self.achievements_data["estadisticas"][clave], (int, float)):
                self.achievements_data["estadisticas"][clave] += valor
                
        if modo and modo in self.achievements_data["estadisticas"]["partidas_por_modo"]:
            self.achievements_data["estadisticas"]["partidas_por_modo"][modo] += valor
            
            # Actualizar modos jugados únicos
            if modo not in self.achievements_data["estadisticas"]["modos_jugados"]:
                self.achievements_data["estadisticas"]["modos_jugados"].append(modo)
                self.actualizar_progreso_logro("EXPLORADOR_MODOS", len(self.achievements_data["estadisticas"]["modos_jugados"]))
            
        if dificultad and dificultad in self.achievements_data["estadisticas"]["partidas_por_dificultad"]:
            self.achievements_data["estadisticas"]["partidas_por_dificultad"][dificultad] += valor
            
            # Verificar logros por dificultad
            if dificultad == "Fácil":
                self.actualizar_progreso_logro("INICIADO_FACIL", self.achievements_data["estadisticas"]["partidas_por_dificultad"]["Fácil"])
            elif dificultad == "Medio":
                self.actualizar_progreso_logro("EXPERTO_MEDIO", self.achievements_data["estadisticas"]["partidas_por_dificultad"]["Medio"])
            elif dificultad == "Difícil":
                self.actualizar_progreso_logro("MAESTRO_DIFICIL", self.achievements_data["estadisticas"]["partidas_por_dificultad"]["Difícil"])
        
    def actualizar_progreso_logro(self, achievement_id, progreso):
        """Actualizar progreso específico de un logro"""
        if achievement_id not in self.achievements_data["progreso_logros"]:
            self.achievements_data["progreso_logros"][achievement_id] = 0
            
        self.achievements_data["progreso_logros"][achievement_id] = max(
            self.achievements_data["progreso_logros"][achievement_id], progreso
        )
        
    def verificar_logros(self):
        """Verificar y desbloquear logros basados en estadísticas actuales"""
        stats = self.achievements_data["estadisticas"]
        
        for achievement_id, achievement in ACHIEVEMENTS.items():
            if achievement_id in self.achievements_data["logros_desbloqueados"]:
                continue
                
            progreso_actual = self.calcular_progreso(achievement, stats)
            
            if progreso_actual >= achievement["meta"]:
                self.desbloquear_logro(achievement_id)


    def verificar_estado_partida_actual(self):
        """Verificar y corregir el estado de la partida actual"""
        claves_requeridas = [
            "pares_consecutivos", "errores_partida", "tiempo_partida",
            "modo_actual", "dificultad_actual", "es_supervivencia",
            "es_multijugador", "pares_encontrados"
        ]
        
        for clave in claves_requeridas:
            if clave not in self.estadisticas_partida_actual:
                if clave == "pares_encontrados":
                    self.estadisticas_partida_actual[clave] = 0
                elif clave in ["pares_consecutivos", "errores_partida"]:
                    self.estadisticas_partida_actual[clave] = 0
                elif clave == "tiempo_partida":
                    self.estadisticas_partida_actual[clave] = 0
                elif clave == "modo_actual":
                    self.estadisticas_partida_actual[clave] = "País-Capital"
                elif clave == "dificultad_actual":
                    self.estadisticas_partida_actual[clave] = "Fácil"
                elif clave in ["es_supervivencia", "es_multijugador"]:
                    self.estadisticas_partida_actual[clave] = False
                
    def calcular_progreso(self, achievement, stats):
        """Calcular progreso actual para un logro"""
        tipo = achievement["tipo"]
        
        if tipo == "total_partidas":
            return stats["total_partidas"]
        elif tipo == "contador_pares":
            return min(stats["total_pares_encontrados"], achievement["meta"])
        elif tipo == "victorias_pais_capital":
            return stats["partidas_por_modo"]["País-Capital"]
        elif tipo == "victorias_matematicas":
            return stats["partidas_por_modo"]["Matemáticas"]
        elif tipo == "victorias_espanol_ingles":
            return stats["partidas_por_modo"]["Español-Inglés"]
        elif tipo == "partidas_facil":
            return stats["partidas_por_dificultad"]["Fácil"]
        elif tipo == "partidas_medio":
            return stats["partidas_por_dificultad"]["Medio"]
        elif tipo == "partidas_dificil":
            return stats["partidas_por_dificultad"]["Difícil"]
        elif tipo == "victorias_multijugador":
            return stats["victorias_multijugador"]
        elif tipo == "racha_victorias_multi":
            return stats["mejor_racha_victorias"]
        elif tipo == "salas_creadas":
            return stats["salas_creadas"]
        elif tipo == "salas_unidas":
            return stats["salas_unidas"]
        elif tipo == "logros_desbloqueados":
            return len(self.achievements_data["logros_desbloqueados"])
        elif tipo == "modos_jugados":
            return len(stats["modos_jugados"])
        elif tipo == "contador_tutoriales":
            return stats["tutoriales_completados"]
        elif tipo in ["sin_errores", "eficiencia_100", "tiempo_dificil", "tiempo_sin_errores", 
                     "supervivencia_ultimo_segundo", "records_todas_dificultades"]:
            # Para logros booleanos, usar el progreso guardado
            return self.achievements_data["progreso_logros"].get(achievement["id"], 0)
        elif tipo in ["racha_pares", "racha_supervivencia"]:
            return self.achievements_data["progreso_logros"].get(achievement["id"], 0)
        
        return 0
        
    def desbloquear_logro(self, achievement_id):
        """Desbloquear un logro"""
        if achievement_id not in self.achievements_data["logros_desbloqueados"]:
            achievement = ACHIEVEMENTS.get(achievement_id)
            if not achievement:
                print(f"Error: Logro {achievement_id} no encontrado")
                return False
                
            timestamp = datetime.now().isoformat()
            
            self.achievements_data["logros_desbloqueados"][achievement_id] = {
                "fecha": timestamp,
                "puntos": achievement["puntos"],
                "nombre": achievement["nombre"],
                "icono": achievement["icono"]
            }
            
            self.achievements_data["puntos_totales"] += achievement["puntos"]
            self.actualizar_nivel()
            
            # ENVIAR NOTIFICACIÓN AL CLIENTE DE QUE DESBLOQUEO UN LOGRO
            if self.client_reference:
                self.client_reference.achievement_notification = {
                    "nombre": achievement["nombre"],
                    "icono": achievement["icono"],
                    "puntos": achievement["puntos"]
                }
                self.client_reference.achievement_notification_time = time.time()
            
            print(f" ¡Logro desbloqueado: {achievement['nombre']}!")
            self.save_achievements()
            return True
            
        return False
        
    def actualizar_nivel(self):
        """Actualizar nivel basado en puntos totales"""
        puntos = self.achievements_data["puntos_totales"]
        self.achievements_data["nivel"] = min(100, 1 + (puntos // 50))
        
    def get_logros_por_categoria(self):
        """Obtener logros organizados por categoría"""
        logros_por_categoria = {}
        
        for categoria in ACHIEVEMENT_CATEGORIES.values():
            logros_por_categoria[categoria] = []
            
        for achievement_id, achievement in ACHIEVEMENTS.items():
            categoria_nombre = ACHIEVEMENT_CATEGORIES[achievement["categoria"]]
            desbloqueado = achievement_id in self.achievements_data["logros_desbloqueados"]
            
            # Para logros secretos no desbloqueados, mostrar información limitada
            if achievement.get("secreto", False) and not desbloqueado:
                logro_info = {
                    "id": achievement_id,
                    "nombre": "???",
                    "descripcion": "Logro secreto - ¡Sigue jugando para descubrirlo!",
                    "icono": "",
                    "puntos": "?",
                    "rareza": "secreto",
                    "desbloqueado": False,
                    "progreso": 0,
                    "meta": 0,
                    "secreto": True
                }
            else:
                progreso_actual = self.calcular_progreso(achievement, self.achievements_data["estadisticas"])
                logro_info = {
                    "id": achievement_id,
                    "nombre": achievement["nombre"],
                    "descripcion": achievement["descripcion"],
                    "icono": achievement["icono"],
                    "puntos": achievement["puntos"],
                    "rareza": achievement["rareza"],
                    "desbloqueado": desbloqueado,
                    "progreso": progreso_actual,
                    "meta": achievement["meta"],
                    "secreto": achievement.get("secreto", False)
                }
            
            logros_por_categoria[categoria_nombre].append(logro_info)
            
        return logros_por_categoria
    
    def registrar_tutorial_completado(self):
        """Registrar que se completó un tutorial"""
        self.actualizar_estadistica("tutoriales_completados", 1)
        self.actualizar_progreso_logro("TUTORIAL_COMPLETO", self.achievements_data["estadisticas"]["tutoriales_completados"])
        self.verificar_logros()
        self.save_achievements()
    
    def registrar_sala_creada(self):
        """Registrar que se creó una sala"""
        self.actualizar_estadistica("salas_creadas", 1)
        self.actualizar_progreso_logro("ANFITRION_EXPERTO", self.achievements_data["estadisticas"]["salas_creadas"])
        self.verificar_logros()
        self.save_achievements()
    
    def registrar_sala_unida(self):
        """Registrar que se unió a una sala"""
        self.actualizar_estadistica("salas_unidas", 1)
        self.actualizar_progreso_logro("INVITADO_FRECUENTE", self.achievements_data["estadisticas"]["salas_unidas"])
        self.verificar_logros()
        self.save_achievements()
    
    def get_estadisticas(self):
        """Obtener estadísticas del jugador"""
        return self.achievements_data["estadisticas"]
    
    def get_puntos_totales(self):
        """Obtener puntos totales"""
        return self.achievements_data["puntos_totales"]
    
    def get_nivel(self):
        """Obtener nivel actual"""
        return self.achievements_data["nivel"]
    
    def get_logros_desbloqueados(self):
        """Obtener lista de logros desbloqueados"""
        return self.achievements_data["logros_desbloqueados"]

# Instancia global del gestor de logros
achievement_manager = AchievementManager()