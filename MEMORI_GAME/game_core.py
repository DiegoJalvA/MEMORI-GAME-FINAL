
#CLIENTE PRINCIPAL DEL JUEGO MEMORI

import pygame 
import sys
import random
import socket
import threading
import pickle
import time
import string
import os
import json
from pygame import mixer
from achievements import achievement_manager

import config
import ui_components


#  FUNCIONES AUXILIARES 
def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

#Tranforma los dos ultimos ocetos de la ip a codigo
def ip_a_codigo(ip):
    try:
        partes = ip.split('.')
        if len(partes) != 4:
            raise ValueError("IP inválida")
        ultimo_octeto = int(partes[3])
        penultimo_octeto = int(partes[2])
        num = penultimo_octeto * 256 + ultimo_octeto
        caracteres = string.ascii_uppercase + string.digits
        codigo = ''
        #Codigo de 4 digitos, numeros y letras
        for _ in range(4):
            num, resto = divmod(num, len(caracteres))
            codigo = caracteres[resto] + codigo
        return codigo.ljust(4, 'A')[:4]
    except Exception:
        return "AAAA"

#El codigo lo tranforma a ip
def codigo_a_ip(codigo, network_prefix="192.168"):
    try:
        caracteres = string.ascii_uppercase + string.digits
        num = 0
        for char in codigo:
            num = num * len(caracteres) + caracteres.index(char)
        b = num % 256
        a = (num // 256) % 256
        a = max(0, min(255, a))
        b = max(0, min(255, b))
        return f"{network_prefix}.{a}.{b}"
    except Exception:
        return "127.0.0.1"

def validar_nombre(nombre):
    if not nombre or not nombre.strip():
        return "Jugador"
    nombre = ''.join(c for c in nombre if c.isalnum() or c in " _-")
    return nombre.strip()[:config.MAX_NAME_LENGTH]

def generar_cartas(modo, dificultad):
    cartas = []
    total = config.DIFICULTAD_CONFIG[dificultad]["total_cartas"]
    total_pares = total // 2
    
    if modo == "País-Capital":
        items = random.sample(list(config.PAISES_CAPITALES.items()), total_pares)
        for p, c in items:
            cartas.append({"front": p, "back": c, "flipped": False, "matched": False})
            cartas.append({"front": c, "back": p, "flipped": False, "matched": False})
    elif modo == "Matemáticas":
        operaciones = []
        for _ in range(total_pares):
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            op = random.choice(["+", "-", "*"])
            if op == "+": res = a + b
            elif op == "-":
                res = a - b
                if res < 0: a, b = b, a; res = a - b
            elif op == "*": res = a * b
            operaciones.append((f"{a} {op} {b}", str(res)))
        for op, res in operaciones:
            cartas.append({"front": op, "back": res, "flipped": False, "matched": False})
            cartas.append({"front": res, "back": op, "flipped": False, "matched": False})
    elif modo == "Español-Inglés":
        items = random.sample(list(config.PALABRAS_ESPANOL_INGLES.items()), total_pares)
        for e, i in items:
            cartas.append({"front": e, "back": i, "flipped": False, "matched": False})
            cartas.append({"front": i, "back": e, "flipped": False, "matched": False})
    random.shuffle(cartas)
    return cartas


def load_highscores():
    try:
        if os.path.exists("highscores.json"):
            with open("highscores.json", "r", encoding='utf-8') as f:
                data = json.load(f)
                #  Crear copia para evitar referencias compartidas
                return migrar_estructura_records(data)
    except:
        pass
    
    return {
        "País-Capital": {
            "Fácil": {"puntos": 0, "tiempo": float('inf')},
            "Medio": {"puntos": 0, "tiempo": float('inf')},
            "Difícil": {"puntos": 0, "tiempo": float('inf')}
        },
        "Matemáticas": {
            "Fácil": {"puntos": 0, "tiempo": float('inf')},
            "Medio": {"puntos": 0, "tiempo": float('inf')},
            "Difícil": {"puntos": 0, "tiempo": float('inf')}
        },
        "Español-Inglés": {
            "Fácil": {"puntos": 0, "tiempo": float('inf')},
            "Medio": {"puntos": 0, "tiempo": float('inf')},
            "Difícil": {"puntos": 0, "tiempo": float('inf')}
        }
    }

def migrar_estructura_records(data):
    print(" Migrando estructura de records...")
    
    # Si es la estructura antigua (solo números)
    if isinstance(data.get("País-Capital"), int):
        print(" Detectada estructura antigua (números)")
        nuevo_data = {}
        for modo in ["País-Capital", "Matemáticas", "Español-Inglés"]:
            puntos_viejos = data.get(modo, 0)
            puntos_facil = min(puntos_viejos, 6)
            puntos_medio = min(puntos_viejos, 8)
            puntos_dificil = min(puntos_viejos, 18)
            #  CREAR ESTRUCTURAS INDEPENDIENTES
            nuevo_data[modo] = {
                "Fácil": {"puntos": puntos_facil, "tiempo": float('inf')},
                "Medio": {"puntos": puntos_medio, "tiempo": float('inf')},
                "Difícil": {"puntos": puntos_dificil, "tiempo": float('inf')}
            }
        print(" Migración completada: estructura antigua -> nueva")
        return nuevo_data
    
    # Si es estructura con modos Supervivencia, filtrarlos
    modos_normales = ["País-Capital", "Matemáticas", "Español-Inglés"]
    modos_supervivencia = [f"{modo} - Supervivencia" for modo in modos_normales]
    
    # Verificar si hay modos Supervivencia en los datos
    tiene_supervivencia = any(modo in data for modo in modos_supervivencia)
    
    if tiene_supervivencia:
        print(" Detectados modos Supervivencia, filtrando...")
        data_filtrado = {}
        
        for modo in modos_normales:
            if modo in data:
                #  CREAR COPIA para evitar referencias compartidas
                data_filtrado[modo] = {
                    "Fácil": {
                        "puntos": min(data[modo]["Fácil"]["puntos"], 6),
                        "tiempo": data[modo]["Fácil"]["tiempo"]
                    },
                    "Medio": {
                        "puntos": min(data[modo]["Medio"]["puntos"], 8),
                        "tiempo": data[modo]["Medio"]["tiempo"]
                    },
                    "Difícil": {
                        "puntos": min(data[modo]["Difícil"]["puntos"], 18),
                        "tiempo": data[modo]["Difícil"]["tiempo"]
                    }
                }
            else:
                # Si no existe, crear estructura vacía 
                data_filtrado[modo] = {
                    "Fácil": {"puntos": 0, "tiempo": float('inf')},
                    "Medio": {"puntos": 0, "tiempo": float('inf')},
                    "Difícil": {"puntos": 0, "tiempo": float('inf')}
                }
        
        print(" Filtrado completado: modos Supervivencia eliminados")
        return data_filtrado
    
    # Si la estructura es correcta, crear copia para evitar referencias
    print(" Estructura ya está actualizada, creando copia...")
    data_copia = {}
    for modo in modos_normales:
        if modo in data:
            data_copia[modo] = {
                "Fácil": dict(data[modo]["Fácil"]),  
                "Medio": dict(data[modo]["Medio"]),
                "Difícil": dict(data[modo]["Difícil"])
            }
        else:
            data_copia[modo] = {
                "Fácil": {"puntos": 0, "tiempo": float('inf')},
                "Medio": {"puntos": 0, "tiempo": float('inf')},
                "Difícil": {"puntos": 0, "tiempo": float('inf')}
            }
    return data_copia
#Records
def save_highscore(mode, difficulty, score, game_time):
    highscores = load_highscores()
    
    nuevo_record_puntos = False
    nuevo_record_tiempo = False
    
    modos_permitidos = ["País-Capital", "Matemáticas", "Español-Inglés"]
    if mode not in modos_permitidos:
        print(f" Modo '{mode}' no permitido para guardar records")
        return False, False
    
    if mode not in highscores:
        print(f" Modo '{mode}' no encontrado en highscores, creando...")
        highscores[mode] = {
            "Fácil": {"puntos": 0, "tiempo": float('inf')},
            "Medio": {"puntos": 0, "tiempo": float('inf')},
            "Difícil": {"puntos": 0, "tiempo": float('inf')}
        }
    
    # Verificar puntuación actual
    current_score = highscores[mode][difficulty]["puntos"]
    current_time = highscores[mode][difficulty]["tiempo"]
    
    print(f" Comparando records - Modo: {mode}, Dificultad: {difficulty}")
    print(f"   Puntos actuales: {current_score}, Nuevos puntos: {score}")
    print(f"   Tiempo actual: {current_time}, Nuevo tiempo: {game_time}")
    
    # Permitir igualdad para actualizar tiempo
    if score >= current_score:  # Cambiado de > a >=
        if score > current_score:  # mensaje de nuevo record si es mayor
            highscores[mode][difficulty]["puntos"] = score
            nuevo_record_puntos = True
            print(f" NUEVO RÉCORD de puntos en {mode} - {difficulty}: {score}")
        else:
            # Mismo puntaje, pero se actualiza el tiempo
            print(f" Mismo puntaje ({score}), verificando tiempo...")
    
    # Solo guardar tiempo si se completaron todos los pares
    total_pares = config.DIFICULTAD_CONFIG[difficulty]["total_cartas"] // 2
    if score == total_pares and game_time < current_time:
        highscores[mode][difficulty]["tiempo"] = game_time
        nuevo_record_tiempo = True
        print(f" NUEVO RÉCORD de tiempo en {mode} - {difficulty}: {game_time:.1f}s")
    
    if nuevo_record_puntos or nuevo_record_tiempo:
        try:
            #  VERIFICAR QUÉ SE VA A GUARDAR
            print(f" Guardando highscores: {list(highscores.keys())}")
            with open("highscores.json", "w", encoding='utf-8') as f:
                json.dump(highscores, f, ensure_ascii=False, indent=2)
            print(f" Récords guardados exitosamente para {mode}")
        except Exception as e:
            print(f" Error al guardar récords: {e}")
    else:
        print(" No hay nuevos records para guardar")
    
    return nuevo_record_puntos, nuevo_record_tiempo

def play_sound(self, sound):
    """Reproducir efecto de sonido"""
    if not self.sfx_enabled:
        return
        
    if sound:
        try:
            #volumen configurado
            sound.set_volume(self.sfx_volume)
            sound.play()
            print(f" Sonido reproducido (vol: {self.sfx_volume})")
        except Exception as e:
            print(f" Error reproduciendo sonido: {e}")


# =================== SERVER THREAD ===================
class ServerThread(threading.Thread):
    def __init__(self, host='0.0.0.0', port=5555):
        super().__init__()
        self.host = host
        self.port = port
        self.server = None
        self.clients = []
        self.clients_lock = threading.Lock()
        self.running = True
        self.reset_state()
        self.iniciar_servidor()
        self.state["tutorial_completado"] = [False, False] 

        # Temporizador de turno en el SERVIDOR
        self.tiempo_turno_actual = 0
        self.tiempo_limite_turno = 15  # 15 segundos por turno
        self.temporizador_turno_activo = False
        self.last_update_time = time.time()

    def iniciar_servidor(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(2)
            print(f"Servidor iniciado en {self.host}:{self.port}")
        except Exception as e:
            print(f"Error al iniciar servidor: {e}")
            raise

    def reset_state(self):
            self.state = {
                "ready": [False, False],
                "cartas": [],
                "turno": 0,
                "scores": [0, 0],
                "abandon": -1,      # Índice del jugador que abandonó
                "abandon_nombre": "",   
                "abandon_voluntario": False,  # voluntario o desconexión
                "nombres": ["Jugador 1", "Jugador 2"],
                "juego_iniciado": False,
                "game_over": False,
                "winner": -1,
                "modo": "País-Capital",
                "dificultad": "Fácil",
                # Estado del temporizador para sincronizar con clientes
                "tiempo_turno_actual": 0,
                "temporizador_activo": False
            }
            print(" Estado del servidor reseteado")

    def run(self):
        accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
        accept_thread.start()
        
        self.last_print_time = 0
        self.print_interval = 2.0
        self.last_update_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - self.last_update_time
            self.last_update_time = current_time
            
            #ACTUALIZAR TEMPORIZADOR DE TURNO EN SERVIDOR
            if self.state["juego_iniciado"] and not self.state["game_over"] and self.state["temporizador_activo"]:
                self.state["tiempo_turno_actual"] -= dt
                
                if self.state["tiempo_turno_actual"] <= 0:
                    print(" SERV: Tiempo de turno agotado - Pasando turno...")
                    self.state["tiempo_turno_actual"] = 0
                    self.state["temporizador_activo"] = False
                    
                    # Voltear cartas no emparejadas
                    cartas_volteadas = []
                    for i, carta in enumerate(self.state["cartas"]):
                        if carta.get("flipped", False) and not carta.get("matched", False):
                            cartas_volteadas.append(i)
                            carta["flipped"] = False
                    
                    if cartas_volteadas:
                        print(f" SERV: Volteando {len(cartas_volteadas)} carta(s) no emparejadas")
                    
                    self.state["turno"] = 1 - self.state["turno"]
                    self.state["tiempo_turno_actual"] = self.tiempo_limite_turno
                    self.state["temporizador_activo"] = True
                    print(f" SERV: Turno cambiado a jugador {self.state['turno']}")

            with self.clients_lock:
                num_clients = len(self.clients)
                
            if num_clients == 0 and not self.running:
                print(" Servidor deteniéndose (sin clientes)...")
                break
                
            if num_clients >= 1:
                try:
                    #DETECCIÓN DE FIN DE JUEGO
                    juego_terminado = False
                    
                    if self.state["juego_iniciado"] and self.state["cartas"]:
                        # VERIFICACIÓN PARA TODAS LAS DIFICULTADES
                        total_cartas = len(self.state["cartas"])
                        cartas_emparejadas = 0
                        
                        # Contar cartas emparejadas de forma explícita
                        for card in self.state["cartas"]:
                            if card.get("matched", False):
                                cartas_emparejadas += 1
                        
                        #  DEBUG ESPECÍFICO PARA DIFICULTAD DIFÍCIL
                        if self.state["dificultad"] == "Difícil" and cartas_emparejadas >= total_cartas - 2:
                            print(f" SERV [DIFÍCIL]: Progreso {cartas_emparejadas}/{total_cartas} cartas emparejadas")
                        
                        all_matched = (cartas_emparejadas == total_cartas)
                        
                        if all_matched and not self.state["game_over"]:
                            print(f" SERV: ¡JUEGO TERMINADO! {cartas_emparejadas}/{total_cartas} cartas emparejadas")
                            print(f" SERV: Dificultad: {self.state['dificultad']} - Modo: {self.state['modo']}")
                            
                            self.state["game_over"] = True
                            self.state["temporizador_activo"] = False
                            juego_terminado = True
                            
                            #  CÁLCULO CONSISTENTE DEL GANADOR
                            print(f" SERV: Calculando ganador - Puntos: {self.state['scores']}")
                            
                            if self.state["scores"][0] > self.state["scores"][1]:
                                self.state["winner"] = 0
                                print(f" SERV: Ganador = Jugador 1 ({self.state['nombres'][0]})")
                            elif self.state["scores"][1] > self.state["scores"][0]:
                                self.state["winner"] = 1
                                print(f" SERV: Ganador = Jugador 2 ({self.state['nombres'][1]})")
                            else:
                                self.state["winner"] = 2
                                print(" SERV: Empate")
                    
                    #  SINCRONIZAR TEMPORIZADOR
                    if self.state["temporizador_activo"]:
                        self.state["tiempo_turno_actual"] = max(0, self.state["tiempo_turno_actual"])
                    
                    data = pickle.dumps(self.state)
                    clients_to_remove = []
                    
                    with self.clients_lock:
                        clients_snapshot = list(self.clients)

                    #  ENVIAR A TODOS LOS JUGADORES
                    clientes_exitosos = 0
                    for c in clients_snapshot:
                        try:
                            # Verificar conexión
                            try:
                                c.getpeername()
                            except:
                                print(f" SERV: Cliente desconectado, removiendo...")
                                clients_to_remove.append(c)
                                continue
                                
                            # Enviar datos
                            c.sendall(data)
                            clientes_exitosos += 1
                            
                            #  LOG ESPECIAL CUANDO EL JUEGO TERMINA
                            if juego_terminado:
                                print(f" SERV: ¡ESTADO FINAL ENVIADO A CLIENTE {clientes_exitosos}! Winner: {self.state['winner']}")
                                
                        except Exception as e:
                            print(f" SERV: Error enviando a cliente: {e}")
                            clients_to_remove.append(c)
                    
                    #  LOG CRÍTICO SI NO SE PUDO ENVIAR A ALGÚN CLIENTE
                    if juego_terminado:
                        if clientes_exitosos < len(clients_snapshot):
                            print(f" SERV: ¡ADVERTENCIA! Solo {clientes_exitosos}/{len(clients_snapshot)} clientes recibieron estado final")
                        else:
                            print(f" SERV: ¡ÉXITO! Estado final enviado a {clientes_exitosos}/{len(clients_snapshot)} clientes")
                    
                    # Manejar clientes desconectados
                    for c in clients_to_remove:
                        self.manejar_cliente_desconectado(c)
                    
                    #  LOGS MEJORADOS CON INFORMACIÓN DE DIFICULTAD
                    if current_time - self.last_print_time > self.print_interval:
                        if self.state["juego_iniciado"]:
                            if self.state["game_over"]:
                                print(f" SERV: [DIFICULTAD: {self.state['dificultad']}] JUEGO TERMINADO")
                                print(f" SERV: Winner: {self.state['winner']}, Puntos: {self.state['scores']}")
                                print(f" SERV: Clientes conectados: {len(clients_snapshot)}")
                            else:
                                cartas_emparejadas = sum(1 for card in self.state["cartas"] if card.get("matched", False))
                                total_cartas = len(self.state["cartas"])
                                tiempo_restante = int(self.state["tiempo_turno_actual"]) if self.state["temporizador_activo"] else "Inactivo"
                                print(f" SERV: [DIFICULTAD: {self.state['dificultad']}] En juego")
                                print(f" SERV: Progreso: {cartas_emparejadas}/{total_cartas}, Turno: {self.state['turno']}, Tiempo: {tiempo_restante}s")
                        else:
                            print(f" SERV: En sala - Ready: {self.state['ready']}, Dificultad: {self.state['dificultad']}")
                        
                        self.last_print_time = current_time
                        
                except Exception as e:
                    current_time = time.time()
                    if current_time - self.last_print_time > self.print_interval:
                        print(f" Error en servidor: {e}")
                        import traceback
                        traceback.print_exc()
                        self.last_print_time = current_time
            
            time.sleep(0.05)
        
        self.close_all()
        print(" Servidor detenido")

    def manejar_cliente_desconectado(self, cliente):
        with self.clients_lock:
            if cliente in self.clients:
                idx = self.clients.index(cliente)
                
                print(f" Cliente {idx} ({self.state['nombres'][idx]}) desconectado")
                
                # Si el jugador que se desconecta tenía cartas volteadas, se voltean de nuevo
                if self.state["juego_iniciado"] and not self.state["game_over"]:
                    if self.state["abandon"] == -1:  # Solo se marca el primer abandono
                        # Voltear cartas del jugador desconectado
                        cartas_volteadas = []
                        for i, carta in enumerate(self.state["cartas"]):
                            if carta.get("flipped", False) and not carta.get("matched", False):
                                cartas_volteadas.append(i)
                                carta["flipped"] = False
                        
                        if cartas_volteadas:
                            print(f" SERV: Jugador {idx} desconectado - Volteando {len(cartas_volteadas)} carta(s)")
                        
                        self.state["abandon"] = idx
                        self.state["abandon_nombre"] = self.state["nombres"][idx]
                        self.state["abandon_voluntario"] = False
                        
                        #  Si era el turno del jugador desconectado se pasa el turno al otro jugador
                        if self.state["turno"] == idx:
                            self.state["turno"] = 1 - idx
                            self.state["tiempo_turno_actual"] = self.tiempo_limite_turno
                            self.state["temporizador_activo"] = True
                        
                        print(f" Abandono registrado para jugador {idx}")
                
                # Remover cliente
                self.clients.remove(cliente)
                try:
                    cliente.close()
                except:
                    pass
                
                print(f" Clientes restantes: {len(self.clients)}")
                
                # Si no quedan clientes, CERRAR el servidor
                if len(self.clients) == 0:
                    print(" Sala vacía - CERRANDO servidor...")
                    self.running = False
                else:
                    print(" Sala sigue activa con jugadores restantes")


    def accept_clients(self):
        while self.running:
            try:
                self.server.settimeout(1.0)
                conn, addr = self.server.accept()
                if not self.running:
                    conn.close()
                    break
                conn.settimeout(config.CONNECTION_TIMEOUT)
                
                with self.clients_lock:
                    #   Permitir hasta 2 clientes, pero aceptar reconexiones
                    if len(self.clients) < 2:
                        print(f" Nuevo cliente conectado: {addr}")
                        self.clients.append(conn)
                        client_thread = threading.Thread(target=self.handle_client, args=(conn, len(self.clients)-1), daemon=True)
                        client_thread.start()
                    else:
                        print(" Sala llena, rechazando conexión")
                        conn.close()
                        
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error aceptando cliente: {e}")
                    time.sleep(0.1)
                continue


    def handle_client(self, conn, idx):
        
        #Maneja la comunicación con un cliente específico
        
        client_name = f"Jugador {idx+1}"
        print(f" Iniciando manejo de {client_name}")

        try:
            # Recibir identificación inicial
            data = conn.recv(8192)
            if not data:
                print(f" {client_name} se desconectó durante identificación")
                self.manejar_cliente_desconectado(conn)
                return
            
            try:
                msg = pickle.loads(data)
            except Exception as e:
                print(f"Error decodificando mensaje del cliente {idx}: {e}")
                self.manejar_cliente_desconectado(conn)
                return
            
            if "nombre" in msg:
                nombre = validar_nombre(msg["nombre"])
                
                if self.state["abandon"] == idx:
                    print(f" {client_name} se reconectó - LIMPIANDO estado de abandono")
                    self.state["abandon"] = -1
                    self.state["abandon_nombre"] = ""
                    self.state["abandon_voluntario"] = False
                
                self.state["nombres"][idx] = nombre
                client_name = nombre
                
                conn.settimeout(None)
                print(f"Cliente {idx} se identifica como: {nombre}")
            else:
                print(f"Cliente {idx} no envió nombre válido")
                self.manejar_cliente_desconectado(conn)
                return

        except socket.timeout:
            print(f"Timeout recibiendo nombre del cliente {idx}")
            self.manejar_cliente_desconectado(conn)
            return
        except Exception as e:
            print(f"Error recibiendo nombre del cliente {idx}: {e}")
            self.manejar_cliente_desconectado(conn)
            return
        
        # Bucle principal de comunicación
        while self.running:
            try:
                data = conn.recv(8192)
                if not data:
                    # Cliente desconectado
                    if self.state["juego_iniciado"] and not self.state["game_over"]:
                        if self.state["abandon"] == -1:
                            self.state["abandon"] = idx
                            self.state["abandon_nombre"] = self.state["nombres"][idx]
                            self.state["abandon_voluntario"] = False
                            print(f" Abandono registrado para {client_name}")
                    break
                
                try:
                    msg = pickle.loads(data)
                except Exception as e:
                    print(f"Error decodificando mensaje del cliente {idx}: {e}")
                    continue
                
                if isinstance(msg, dict):
                    # LIMPIAR ABANDONO EN CUALQUIER MENSAJE
                    if self.state["abandon"] == idx:
                        print(f" {client_name} envió mensaje - LIMPIANDO abandono")
                        self.state["abandon"] = -1
                        self.state["abandon_nombre"] = ""
                        self.state["abandon_voluntario"] = False
                    
                    if "ready" in msg:
                        self.state["ready"][idx] = bool(msg["ready"])
                        print(f"Cliente {idx} ready: {msg['ready']}")
                    
                    elif "iniciar_juego" in msg and msg["iniciar_juego"]:
                        if isinstance(msg["cartas"], list):
                            self.state["cartas"] = [card.copy() for card in msg["cartas"]]
                            self.state["turno"] = msg["turno"]
                            self.state["scores"] = msg["scores"]
                            self.state["juego_iniciado"] = True
                            self.state["game_over"] = False
                            # INICIAR TEMPORIZADOR EN EL SERVIDOR AL COMENZAR JUEGO
                            self.state["tiempo_turno_actual"] = self.tiempo_limite_turno
                            self.state["temporizador_activo"] = True
                            # Limpiar estado de abandono al iniciar juego
                            self.state["abandon"] = -1
                            self.state["abandon_nombre"] = ""
                            self.state["abandon_voluntario"] = False
                           
                    
                    elif "flipped" in msg and "cartas" in msg:
                        if isinstance(msg["cartas"], list):
                            self.state["cartas"] = [card.copy() for card in msg["cartas"]]
                            self.state["turno"] = int(msg["turno"])
                            self.state["scores"] = [int(s) for s in msg["scores"]]
                            #  REINICIAR TEMPORIZADOR EN SERVIDOR AL VOLTEAR CARTA
                            self.state["tiempo_turno_actual"] = self.tiempo_limite_turno
                            self.state["temporizador_activo"] = True
                            
                    
                    #  ACEPTAR ESTADO game_over DE LOS CLIENTES
                    elif "game_over" in msg and msg["game_over"]:
                        if not self.state["game_over"]:
                            print(f" Cliente {idx} reporta fin de juego - Sincronizando...")
                            self.state["game_over"] = True
                            self.state["temporizador_activo"] = False
                            self.state["winner"] = msg.get("winner", -1)
                            print(f" Servidor acepta game_over del cliente - Winner: {self.state['winner']}")
                    
                    elif "cambio_turno" in msg:
                        #  MANEJAR CAMBIO DE TURNO (por tiempo agotado desde cliente)
                        self.state["turno"] = msg["turno"]
                        self.state["tiempo_turno_actual"] = self.tiempo_limite_turno
                        self.state["temporizador_activo"] = True
                        
                        # VOLTEAR CARTAS NO EMPAREJADAS SI HAY ALGUNA VOLTEADA
                        cartas_volteadas = []
                        for i, carta in enumerate(self.state["cartas"]):
                            if carta.get("flipped", False) and not carta.get("matched", False):
                                cartas_volteadas.append(i)
                                carta["flipped"] = False
                        
                        if cartas_volteadas:
                            print(f" SERV: Cambio de turno - Volteando {len(cartas_volteadas)} carta(s) no emparejadas")
                        
                        print(f" Turno cambiado a jugador {msg['turno']} - Temporizador reiniciado")
                    
                    elif "nombre" in msg:
                        nombre = validar_nombre(msg["nombre"])
                        self.state["nombres"][idx] = nombre
                    
                    elif "abandon" in msg:
                        if self.state["juego_iniciado"] and not self.state["game_over"]:
                            if self.state["abandon"] == -1:
                                nombre_abandono = msg.get("nombre", self.state["nombres"][idx])
                                self.state["abandon"] = idx
                                self.state["abandon_nombre"] = nombre_abandono
                                self.state["abandon_voluntario"] = True
                                print(f"🚪 Jugador {idx} ({nombre_abandono}) abandonó voluntariamente")
                        break
            
            except socket.timeout:
                continue
            except (ConnectionResetError, ConnectionAbortedError):
                print(f"Cliente {idx} perdió conexión")
                if self.state["juego_iniciado"] and not self.state["game_over"]:
                    if self.state["abandon"] == -1:
                        self.state["abandon"] = idx
                        self.state["abandon_nombre"] = self.state["nombres"][idx]
                        self.state["abandon_voluntario"] = False
                        print(f" Abandono por desconexión registrado para {client_name}")
                break
            except Exception as e:
                print(f"Error con cliente {idx}: {e}")
                break
        
        self.manejar_cliente_desconectado(conn)



    def stop(self):
        self.running = False
        with self.clients_lock:
            for client in self.clients[:]:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()
        if self.server:
            try:
                self.server.close()
            except:
                pass
   #CERRAR Y LIMPIAR FUNCIONES
    def close_all(self):
        with self.clients_lock:
            for c in self.clients[:]:
                try:
                    c.close()
                except:
                    pass
            self.clients.clear()
        if self.server:
            try:
                self.server.close()
            except:
                pass

#  CLIENTE PRINCIPAL 
class Client:

    def __init__(self):
        self.running = True
        self.state = "inicio"
        self.name = "Jugador"
        self.modo = "País-Capital"
        self.dificultad = "Fácil"
        self.solo = True
        self.input_text = ""
        self.input_active = False
        self.ready = False
        self.other_ready = False
        self.server_thread = None
        self.codigo_sala = ""
        self.cartas = []
        self.flipped = []
        self.turno = 0
        self.scores = [0, 0]
        self.nombres = ["Jugador 1", "Jugador 2"]
        self.highscores = load_highscores()
        self.timer = 0
        self.timer_active = False
        self.game_over = False
        self.winner = -1
        self.editing_name = False
        self.show_modes_dialog = False
        self.show_difficulty_dialog = False
        self.show_records_dialog = False
        self.show_join_dialog = False
        self.connection_error = False
        self.last_connection_attempt = 0
        self.reconnection_delay = 3
        self.es_anfitrion = False
        self.ip_servidor = None
        self.sock = None
        self.client_thread = None
        self.juego_iniciado = False
        self.mostrar_resultado_final = False
        self.tiempo_resultado = 0
        self.last_state_update = 0
        self.esperando_volteo = False
        self.temporizador_volteo = 0
        self.tiempo_espera_volteo = 0.8
        self.nuevo_record_puntos = False
        self.nuevo_record_tiempo = False

        # CONTROL DE AUDIO 
        self.music_volume = 0.9  # Volumen inicial de música 
        self.sfx_volume = 1.0    # Volumen inicial de efectos
        self.music_enabled = True  # Música activada por defecto
        self.sfx_enabled = True    # Efectos activados por defecto
        self.show_audio_dialog = False  # Diálogo de configuración de audio
        self.audio_buttons = None  
        self.audio_dialog_elements = None  
        # Inicializar Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption("MEMORI GAME")
        self.clock = pygame.time.Clock()

        # Cargar audio
        self.load_audio()
        
        self.music_enabled = True
        self.sfx_enabled = True

        # Sistema de tutorial
        self.tutorial_completado = self.load_tutorial_progress()
        self.mostrar_tutorial = False
        self.tutorial_modo_actual = ""

        # Modo Supervivencia 
        self.modo_juego = "Normal"  
        self.tiempo_restante = 0
        self.tiempo_maximo = 300  # 5 minutos máximo

        # Sistema de logros
        self.achievement_manager = achievement_manager
        self.achievement_manager.set_client_reference(self)
        self.show_achievements_dialog = False
        self.achievement_notification = None
        self.achievement_notification_time = 0

        # Sistema de scroll
        self.achievements_scroll_y = 0
        self.achievements_scroll_max = 0
        self.scroll_dragging = False
        self.scroll_start_y = 0

        # Estado de tutorial para multijugador
        self.other_tutorial_completado = False  # Estado del otro jugador
        self.accion_multijugador_pendiente = None  # Para tutorial multijugador
        self.codigo_sala_temporal = ""  # Para guardar código durante tutorial

        # Variables para control de frecuencia de prints
        self.last_print_time = 0
        self.print_interval = 2.0  # imprimir cada 2 segundos

        # guardar último estado del servidor
        self.last_server_state = {}

        self.tiempo_turno_actual = 0
        self.tiempo_limite_turno = 15  # 15 segundos por turno
        self.temporizador_turno_activo = False

        # Para guardar último estado del servidor
        self.last_server_state = {}
        self.last_game_over_state = False  # detectar cambios
        self.last_abandon_state = -1  # detectar cambios en abandono
        
 
    def iniciar_supervivencia(self):
        """Iniciar modo supervivenci"""
        # Iniciar juego despues de tutorial
        if self.mostrar_tutorial:
            self.mostrar_tutorial = False
            self.modo_juego = "Supervivencia"
            config_supervivencia = config.SUPERVIVENCIA_CONFIG[self.dificultad]
            self.tiempo_restante = config_supervivencia["tiempo_inicial"]
            self.timer_active = True
            self.game_over = False
            self.juego_iniciado = True
            self.flipped = []
            self.mostrar_resultado_final = False
            self.cartas = generar_cartas(self.modo, self.dificultad)
            self.turno = 0
            self.scores = [0, 0]
            self.state = "juego"
            self.timer = 0
            print(f" Modo Supervivencia iniciado - Tiempo: {self.tiempo_restante}s")
        else:
            #  Primera vez, verificar si hay que mostrar tutorial
            if self.check_mostrar_tutorial("Supervivencia"):
                self.mostrar_tutorial = True
                if self.button_click_sound:
                    self.play_sound(self.button_click_sound)
            else:
                # No hay tutorial, iniciar directamente
                self.modo_juego = "Supervivencia"
                config_supervivencia = config.SUPERVIVENCIA_CONFIG[self.dificultad]
                self.tiempo_restante = config_supervivencia["tiempo_inicial"]
                self.timer_active = True
                self.game_over = False
                self.juego_iniciado = True
                self.flipped = []
                self.mostrar_resultado_final = False
                self.cartas = generar_cartas(self.modo, self.dificultad)
                self.turno = 0
                self.scores = [0, 0]
                self.state = "juego"
                self.timer = 0


                 #  INICIAR SEGUIMIENTO DE LOGROS PARA SUPERVIVENCIA 
                self.achievement_manager.iniciar_partida(
                    modo=self.modo,
                    dificultad=self.dificultad,
                    es_supervivencia=True,
                    es_multijugador=False
                )
                print(f" Modo Supervivencia iniciado - Tiempo: {self.tiempo_restante}s")

                
    def update_supervivencia(self, dt):
        """Actualizar lógica del modo supervivencia"""
        if self.timer_active and self.tiempo_restante > 0:
            self.tiempo_restante -= dt 
         
        # Verificar si se acabó el tiempo 
            if self.tiempo_restante <= 0 and not self.game_over:
                self.tiempo_restante = 0  # Asegurar que no sea negativo
                self.game_over = True
                self.timer_active = False
                self.mostrar_resultado_final = True
                self.tiempo_resultado = time.time()
                if self.game_over_sound:
                     self.play_sound(self.game_over_sound)
                print(" Tiempo agotado - Juego terminado")

    def aplicar_bonus_supervivencia(self, acierto):
        """Aplicar bonus/penalización en modo supervivencia"""
        config_supervivencia = config.SUPERVIVENCIA_CONFIG[self.dificultad]
    
        if acierto:
            # Acierto: + tiempo extra
            bonus = config_supervivencia["bonus_acierto"]
            nuevo_tiempo = self.tiempo_restante + bonus
            self.tiempo_restante = min(nuevo_tiempo, self.tiempo_maximo)
            print(f" +{bonus}s - Tiempo: {self.tiempo_restante:.1f}s")
        else:
            # Error: - tiempo
            penalizacion = config_supervivencia["penalizacion_error"]
            self.tiempo_restante = max(0, self.tiempo_restante - penalizacion)
            print(f" -{penalizacion}s - Tiempo: {self.tiempo_restante:.1f}s")

        # VERIFICAR INMEDIATAMENTE SI SE AGOTÓ EL TIEMPO
        if self.tiempo_restante <= 0 and not self.game_over:
            self.game_over = True
            self.timer_active = False
            self.mostrar_resultado_final = True
            self.tiempo_resultado = time.time()
            if self.game_over_sound:
                 self.play_sound(self.game_over_sound)
            print(" Tiempo agotado - Juego terminado")

   #Sonidos
    def load_sounds(self):
        """Cargar sonidos del juego"""
        try:
            mixer.init()
            if os.path.exists("flip.wav"):
                self.flip_sound = mixer.Sound("flip.wav")
            if os.path.exists("match.wav"):
                self.match_sound = mixer.Sound("match.wav")
            if os.path.exists("win.wav"):
                self.win_sound = mixer.Sound("win.wav")
            if os.path.exists("click.wav"):
                self.click_sound = mixer.Sound("click.wav")
            if os.path.exists("lose.wav"):
                self.lose_sound = mixer.Sound("lose.wav")
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar los sonidos: {e}")

    def reset_highscores(self):
        """Borra todos los récords guardados"""
        confirm = self.confirm_dialog("¿Borrar TODOS los récords?\nEsta acción no se puede deshacer.")
        if confirm:
            try:
                if os.path.exists("highscores.json"):
                    os.remove("highscores.json")
                    self.highscores = load_highscores()
                    self.alerta(" Récords borrados exitosamente")
                    print("Récords borrados y reiniciados")
                else:
                    self.alerta(" No hay récords guardados para borrar")
            except Exception as e:
                self.alerta(f" Error borrando récords: {e}")

    def limpiar_estado_conexion(self):
        #Limpiar estado de conexión pero mantener servidor
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        self.connection_error = False
        self.ready = False
        self.other_ready = False
        self.juego_iniciado = False
        self.codigo_sala = ""
        self.ip_servidor = None
        # NO se limpia server_thread para permitir reconexión del anfitrión

    def connect_to_server(self, host, port):
        current_time = time.time()
        if current_time - self.last_connection_attempt < self.reconnection_delay:
            return False
        self.last_connection_attempt = current_time
        print(f"Intentando conectar a {host}:{port}")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((host, port))
            self.sock.settimeout(None)
            self.client_thread = threading.Thread(target=self.receive_server, daemon=True)
            self.client_thread.start()
            time.sleep(0.5)
            success = self.send_to_server({
                "nombre": self.name,
                "modo": self.modo,
                "dificultad": self.dificultad
            })
            if success:
                print("Conexión exitosa y nombre/envío de modo+dificultad enviado")
                self.connection_error = False
                return True
            else:
                print("Error enviando nombre/envío de modo+dificultad después de conexión")
                self.connection_error = True
                return False
        except socket.timeout:
            print("Timeout en conexión - servidor no responde")
            self.connection_error = True
            return False
        except ConnectionRefusedError:
            print("Conexión rechazada - servidor no disponible")
            self.connection_error = True
            return False
        except Exception as e:
            print(f"Error de conexión: {e}")
            self.connection_error = True
            return False

    def receive_server(self):
        buffer = b""
        while self.running and not self.connection_error:
            try:
                data = self.sock.recv(8192)
                if not data:
                    print("Servidor cerró la conexión")
                    self.connection_error = True
                    break
                buffer += data
                try:
                    state_server = pickle.loads(buffer)
                    buffer = b""
                    self.actualizar_estado_desde_servidor(state_server)
                except pickle.UnpicklingError:
                    if len(buffer) > 100000:
                        buffer = b""
                    continue
                except Exception as e:
                    print(f"Error procesando datos del servidor: {e}")
                    buffer = b""
                    continue
            except socket.timeout:
                continue
            except ConnectionResetError:
                print("Conexión resetada por el servidor")
                self.connection_error = True
                break
            except Exception as e:
                print(f"Error en receive_server: {e}")
                self.connection_error = True
                break
        if self.connection_error and self.state != "inicio":
            print("Volviendo al inicio por error de conexión")
            self.volver_al_inicio()

    def actualizar_estado_desde_servidor(self, estado_servidor):
        """
        Actualiza el estado del cliente desde el servidor - CON TEMPORIZADOR MANEJADO POR SERVIDOR
        """
        try:
            # ✅ SOLUCIÓN: Guardar estado anterior para detectar cambios
            abandon_anterior = getattr(self, 'last_abandon_state', -1)
            game_over_anterior = getattr(self, 'last_game_over_state', False)
            
            self.last_server_state = estado_servidor.copy()
            
            # Detectar cambios importantes
            abandon_actual = estado_servidor.get("abandon", -1)
            game_over_actual = estado_servidor.get("game_over", False)
            
            # ✅ DEBUG: Mostrar cambios importantes
            if game_over_anterior != game_over_actual:
                print(f"🔄 {self.name}: Cambio game_over {game_over_anterior} -> {game_over_actual}")
            
            self.last_abandon_state = abandon_actual
            self.last_game_over_state = game_over_actual
            
            # ✅ SINCRONIZAR TODO DESDE EL SERVIDOR (incluyendo temporizador)
            if "modo" in estado_servidor:
                self.modo = estado_servidor["modo"]
            if "dificultad" in estado_servidor:
                self.dificultad = estado_servidor["dificultad"]

            if isinstance(estado_servidor.get("ready"), list) and len(estado_servidor["ready"]) == 2:
                if self.es_anfitrion:
                    self.ready = estado_servidor["ready"][0]
                    self.other_ready = estado_servidor["ready"][1]
                else:
                    self.ready = estado_servidor["ready"][1]
                    self.other_ready = estado_servidor["ready"][0]

            if estado_servidor.get("juego_iniciado") and isinstance(estado_servidor.get("cartas"), list) and len(estado_servidor["cartas"]) > 0:
                # ✅ IMPORTANTE: Sincronizar TODAS las cartas desde el servidor
                self.cartas = [card.copy() for card in estado_servidor["cartas"]]
                self.juego_iniciado = True
                
                if self.state != "juego":
                    self.state = "juego"
                    self.timer = 0
                    self.timer_active = True
                    self.game_over = False

            if isinstance(estado_servidor.get("turno"), int) and 0 <= estado_servidor["turno"] <= 1:
                self.turno = estado_servidor["turno"]

            if isinstance(estado_servidor.get("scores"), list) and len(estado_servidor["scores"]) == 2:
                self.scores = estado_servidor["scores"]

            if isinstance(estado_servidor.get("nombres"), list) and len(estado_servidor["nombres"]) == 2:
                self.nombres = estado_servidor["nombres"]

            # ✅ SINCRONIZAR TEMPORIZADOR DESDE EL SERVIDOR
            if "tiempo_turno_actual" in estado_servidor:
                self.tiempo_turno_actual = estado_servidor["tiempo_turno_actual"]
            
            if "temporizador_activo" in estado_servidor:
                self.temporizador_turno_activo = estado_servidor["temporizador_activo"]

            # Manejar reconexión durante el juego
            if estado_servidor.get("juego_iniciado") and not self.juego_iniciado and self.state == "juego":
                self.juego_iniciado = True
                self.timer_active = True

            # ✅ CORRECCIÓN CRÍTICA: Manejar fin de juego sincronizado - FORZAR ACTUALIZACIÓN
            if estado_servidor.get("game_over") and not self.game_over:
                print(f"🎯 {self.name}: RECIBIENDO game_over del servidor - Winner: {estado_servidor.get('winner', -1)}")
                self.game_over = True
                self.timer_active = False
                self.temporizador_turno_activo = False
                self.winner = estado_servidor.get("winner", -1)
                self.mostrar_resultado_final = True
                self.tiempo_resultado = time.time()
                
                print(f"🎯 {self.name}: Juego terminado - Ganador: {self.winner} - Puntos: {self.scores}")
                print(f"🎯 {self.name}: Es anfitrión: {self.es_anfitrion} - Nombres: {self.nombres}")
                
                # ✅ REGISTRAR LOGRO TAMBIÉN CUANDO SE RECIBE DEL SERVIDOR
                if not self.solo:
                    tiempo_final = self.timer
                    victoria = (self.winner == 0 and self.es_anfitrion) or (self.winner == 1 and not self.es_anfitrion)
                    self.achievement_manager.finalizar_partida(tiempo_final, victoria)
                    
                    # ✅ REPRODUCIR SONIDO APROPIADO
                    if victoria:
                        if self.victory_sound:
                            self.victory_sound.play()
                        print(f"🎉 {self.name}: Sonido de VICTORIA reproducido")
                    else:
                        if self.game_over_sound:
                            self.game_over_sound.play()
                        print(f"💥 {self.name}: Sonido de DERROTA reproducido")
            
            # ✅ CORRECCIÓN: También manejar si el servidor envía game_over pero nosotros ya lo tenemos
            elif estado_servidor.get("game_over") and self.game_over and self.winner != estado_servidor.get("winner", -1):
                print(f"🔄 {self.name}: Sincronizando winner - Antes: {self.winner}, Ahora: {estado_servidor.get('winner', -1)}")
                self.winner = estado_servidor.get("winner", -1)

            # ✅ CORREGIDO: Si el servidor dice que el juego NO está iniciado, sincronizar
            if not estado_servidor.get("juego_iniciado", False) and self.juego_iniciado:
                self.juego_iniciado = False
                self.timer_active = False
                if self.state == "juego":
                    self.state = "sala"

        except Exception as e:
            print(f"❌ Error en actualizar_estado_desde_servidor: {e}")
            import traceback
            traceback.print_exc()

    def send_to_server(self, msg):
        if not hasattr(self, 'sock') or self.connection_error or not self.sock:
            print("No hay conexión activa para enviar mensaje")
            return False
        try:
            try:
                self.sock.getpeername()
            except:
                print("Socket desconectado, no se puede enviar")
                self.connection_error = True
                return False
            data = pickle.dumps(msg)
            self.sock.sendall(data)
            return True
        except Exception as e:
            print(f"Error enviando mensaje al servidor: {e}")
            self.connection_error = True
            return False
        

    def enviar_estado_tutorial(self, completado):
        """Enviar estado de tutorial al servidor - VERSIÓN COMPLETA"""
        if not self.solo and hasattr(self, 'sock') and self.sock and not self.connection_error:
            try:
                success = self.send_to_server({
                    "tutorial_completado": completado
                })
                if success:
                    print(f" {self.name}: Estado tutorial enviado - Completado: {completado}")
                else:
                    print(f" {self.name}: Error enviando estado tutorial")
            except Exception as e:
                print(f"Error enviando estado de tutorial: {e}")
        else:
            print(f" {self.name}: No se pudo enviar estado tutorial - Conexión no disponible")


        #  SISTEMA DE TUTORIAL 
    def load_tutorial_progress(self):
        """Cargar progreso de tutorial desde archivo"""
        try:
            if os.path.exists("tutorial_progress.json"):
                with open("tutorial_progress.json", "r", encoding='utf-8') as f:
                    progress = json.load(f)
                    #  Asegurar que existen todas las claves necesarias
                    claves_requeridas = ["País-Capital", "Matemáticas", "Español-Inglés", "Supervivencia", "Multijugador"]
                    for clave in claves_requeridas:
                        if clave not in progress:
                            progress[clave] = False
                    return progress
        except:
            pass
        # Por defecto, ningún tutorial completado
        return {
            "País-Capital": False,
            "Matemáticas": False, 
            "Español-Inglés": False,
            "Supervivencia": False,
            "Multijugador": False 
        }
            
    
    def save_tutorial_progress(self):
        """Guardar progreso de tutorial"""
        try:
            with open("tutorial_progress.json", "w", encoding='utf-8') as f:
                json.dump(self.tutorial_completado, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def check_mostrar_tutorial(self, modo):
        """Verificar si debe mostrarse el tutorial para este modo - VERSIÓN MODIFICADA"""
        
       # Mostrar SOLO el tutorial multijugador
        if not self.solo:  
            if modo == "Multijugador":
                if not self.tutorial_completado.get("Multijugador", False):
                    self.mostrar_tutorial = True
                    self.tutorial_modo_actual = "Multijugador"
                    return True
                return False
            else:
                # NO mostrar tutoriales de modos específicos
                print(f" Multijugador: Saltando tutorial del modo {modo}")
                return False
        
        #  Para Supervivencia 
        elif modo == "Supervivencia":
            if not self.tutorial_completado.get("Supervivencia", False):
                self.mostrar_tutorial = True
                self.tutorial_modo_actual = "Supervivencia"
                return True
            return False
        
        else:
            #  Para modos normales en individual
            if not self.tutorial_completado.get(modo, False):
                self.mostrar_tutorial = True
                self.tutorial_modo_actual = modo
                return True
            return False
      
    def completar_tutorial(self):
        """Marcar tutorial como completado"""
        self.tutorial_completado[self.tutorial_modo_actual] = True
        self.save_tutorial_progress()
        self.mostrar_tutorial = False
        
        # REGISTRAR TUTORIAL COMPLETADO PARA LOGROS
        self.achievement_manager.registrar_tutorial_completado()
        
        print(f"Tutorial completado para: {self.tutorial_modo_actual}")
    
    def draw_tutorial(self):
        """Dibujar pantalla de tutorial"""
        # Fondo semitransparente
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Obtener datos del tutorial actual
        tutorial_data = config.TUTORIAL_DATA.get(self.tutorial_modo_actual, {})
        
        # Panel principal del tutorial
        panel_rect = pygame.Rect(config.WIDTH//2 - 350, config.HEIGHT//2 - 280, 700, 520)
        pygame.draw.rect(self.screen, config.DIALOG_BG, panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 215, 0), panel_rect, 4, border_radius=20)
        
        # Título
        ui_components.draw_text(self.screen, tutorial_data.get("titulo", "TUTORIAL"), 
                            42, (255, 255, 0), config.WIDTH//2, config.HEIGHT//2 - 250, "center")
        
        # Descripción
        descripcion_rect = ui_components.draw_text(self.screen, tutorial_data.get("descripcion", ""), 
                            22, config.WHITE, config.WIDTH//2, config.HEIGHT//2 - 200, "center")
        
        # Línea separadora
        pygame.draw.line(self.screen, (255, 215, 0), 
                        (config.WIDTH//2 - 300, config.HEIGHT//2 - 170),
                        (config.WIDTH//2 + 300, config.HEIGHT//2 - 170), 2)
        
        # Ejemplos 
        ejemplos = tutorial_data.get("ejemplo", [])
        y_pos = config.HEIGHT//2 - 140
        
        for i, ejemplo in enumerate(ejemplos[:2]):  # Mostrar máximo 2 ejemplos
            # Cartas de ejemplo 
            carta1_rect = pygame.Rect(config.WIDTH//2 - 180, y_pos, 120, 60)
            carta2_rect = pygame.Rect(config.WIDTH//2 + 60, y_pos, 120, 60)
            
            # Dibujar cartas
            pygame.draw.rect(self.screen, config.CARD_FLIPPED_COLOR, carta1_rect, border_radius=8)
            pygame.draw.rect(self.screen, config.CARD_COLOR, carta1_rect, 2, border_radius=8)
            pygame.draw.rect(self.screen, config.CARD_FLIPPED_COLOR, carta2_rect, border_radius=8)
            pygame.draw.rect(self.screen, config.CARD_COLOR, carta2_rect, 2, border_radius=8)
            
            # Texto de las cartas
            ui_components.draw_text(self.screen, ejemplo["carta1"], 16, config.BLACK, 
                                config.WIDTH//2 - 120, y_pos + 30, "center")
            ui_components.draw_text(self.screen, ejemplo["carta2"], 16, config.BLACK, 
                                config.WIDTH//2 + 120, y_pos + 30, "center")
            
            # Flecha de conexión
            pygame.draw.line(self.screen, config.GREEN, 
                        (config.WIDTH//2 - 60, y_pos + 30), 
                        (config.WIDTH//2 + 60, y_pos + 30), 3)
            
            # Flecha en medio
            pygame.draw.polygon(self.screen, config.GREEN, [
                (config.WIDTH//2 - 10, y_pos + 25),
                (config.WIDTH//2, y_pos + 30),
                (config.WIDTH//2 - 10, y_pos + 35)
            ])
            pygame.draw.polygon(self.screen, config.GREEN, [
                (config.WIDTH//2 + 10, y_pos + 25),
                (config.WIDTH//2, y_pos + 30),
                (config.WIDTH//2 + 10, y_pos + 35)
            ])
            
            # Explicación
            explicacion_rect = ui_components.draw_text(self.screen, ejemplo["explicacion"], 16, config.LIGHTGRAY, 
                                config.WIDTH//2, y_pos + 85, "center")
            
            y_pos += 120
        
        # Línea separadora antes de instrucciones
        pygame.draw.line(self.screen, (255, 215, 0), 
                        (config.WIDTH//2 - 300, y_pos + 10),
                        (config.WIDTH//2 + 300, y_pos + 10), 2)
        
        # Instrucciones - ESPACIO LIMITADO
        instrucciones = tutorial_data.get("instrucciones", [])
        
        # Título de instrucciones
        instrucciones_title_rect = ui_components.draw_text(self.screen, "Cómo jugar:", 
                                20, (255, 255, 0), config.WIDTH//2 - 280, y_pos + 30, "left")
        
        y_pos += 60
        
        # Mostrar instrucciones
        instrucciones_mostrar = instrucciones[:4]  # Máximo 4 instrucciones
        
        for instruccion in instrucciones_mostrar:
            instruccion_rect = ui_components.draw_text(self.screen, f"• {instruccion}", 16, config.LIGHTBLUE, 
                                config.WIDTH//2 - 280, y_pos, "left", max_width=550)
            y_pos += 28
        
        # MOSTRAR ESTADO DEL OTRO JUGADOR (solo en multijugador)
        estado_oponente_y = y_pos + 20
        
        if not self.solo and hasattr(self, 'other_tutorial_completado'):
            # Determinar nombre del oponente
            if self.es_anfitrion:
                nombre_oponente = self.nombres[1] if len(self.nombres) > 1 else "Invitado"
            else:
                nombre_oponente = self.nombres[0] if len(self.nombres) > 0 else "Anfitrión"
            
            # Determinar estado y color
            if self.other_tutorial_completado:
                estado_texto = f"{nombre_oponente}:  LISTO"
                color_estado = config.GREEN
            else:
                estado_texto = f"{nombre_oponente}:  VIENDO TUTORIAL"
                color_estado = config.YELLOW
            
            # Dibujar estado del oponente
            estado_rect = ui_components.draw_text(self.screen, estado_texto, 18, color_estado, 
                                config.WIDTH//2, estado_oponente_y, "center")
            
            boton_y = estado_oponente_y + 40
        else:
            # Posición normal del botón si no es multijugador
            boton_y = y_pos + 30
        
        # Botón para continuar
        continuar_btn = ui_components.draw_button(self.screen, "ENTENDIDO", 
                                                config.WIDTH//2 - 80, boton_y, 
                                                160, 40, config.GREEN)
        
        # Instrucción adicional para multijugador
        if not self.solo:
            ui_components.draw_text(self.screen, "Presiona ENTENDIDO cuando estés listo", 
                                14, config.LIGHTGRAY, config.WIDTH//2, boton_y + 50, "center")
        
        # GUARDAR la posición para que handle_tutorial_click la use
        self.tutorial_boton_y = boton_y
        
        return continuar_btn
    
    def handle_tutorial_click(self, pos):
        """Manejar clics en el tutorial"""
        boton_x = config.WIDTH//2 - 80
        boton_y = self.tutorial_boton_y
        boton_ancho = 160
        boton_alto = 40
        
        continuar_btn = pygame.Rect(boton_x, boton_y, boton_ancho, boton_alto)
        
        if continuar_btn.collidepoint(pos):
            modo_del_tutorial = self.tutorial_modo_actual
            
            self.completar_tutorial()
            # Audio de botón
            if self.button_click_sound:
                self.button_click_sound.play()
            
            #  NOTIFICAR AL SERVIDOR QUE COMPLETÓ EL TUTORIAL
            if not self.solo:
                self.enviar_estado_tutorial(True)
                print(f" {self.name}: Tutorial completado - Notificado al servidor")
            
            #  EJECUTAR ACCIÓN SEGÚN EL TUTORIAL
            if modo_del_tutorial == "Supervivencia":
                self.iniciar_supervivencia()
            elif modo_del_tutorial == "Multijugador":
                if hasattr(self, 'accion_multijugador_pendiente'):
                    if self.accion_multijugador_pendiente == "crear_sala":
                        self._crear_sala_despues_tutorial()
                    elif self.accion_multijugador_pendiente == "unirse_sala":
                        self._unirse_sala_despues_tutorial()
                    del self.accion_multijugador_pendiente
            else:
                # TUTORIALES DE MODO EN MULTIJUGADOR
                if not self.solo:
                    if self.es_anfitrion:
                        # Anfitrión: iniciar juego después del tutorial
                        print(" Anfitrión: Tutorial completado - Iniciando juego...")
                        self._iniciar_juego_multijugador()
                    else:
                        # Invitado: unirse al juego después del tutorial
                        print(" Invitado: Tutorial completado - Uniéndose al juego...")
                        self.iniciar_juego_como_invitado()
                else:
                    # Modo individual
                    self.start_game()
            
            return True
        return False



    def crear_sala(self):
        if not self.name or self.name.strip() == "":
            self.alerta("Debes ingresar un nombre antes de crear una sala")
            return
        
        #Verificar si ya hay servidor activo y reconectar
        if self.server_thread and self.server_thread.running:
            # Mostrar alerta de reconexión
            confirm = self.confirm_dialog("Ya tienes una sala activa.\n\n¿Deseas reconectar como anfitrión?")
            if confirm:
                print(" Reconectando a sala existente como anfitrión...")
                self._reconectar_como_anfitrion()
            else:
                print(" Usuario canceló reconexión")
            return
        
        # VERIFICAR TUTORIAL MULTIJUGADOR
        if self.check_mostrar_tutorial("Multijugador"):
            self.mostrar_tutorial = True
            self.accion_multijugador_pendiente = "crear_sala"
            if self.button_click_sound:
                    self.play_sound(self.button_click_sound)
            return
        
        # Si no hay tutorial, crear sala nueva
        self._crear_sala_despues_tutorial()

    def _reconectar_como_anfitrion(self):
        """Reconectar a sala existente como anfitrión"""
        print(" Reconectando como anfitrión...")
        
        self.limpiar_estado_conexion()
        
        # Configurar estado
        self.state = "sala"
        ip_anfitrion = obtener_ip_local()
        self.codigo_sala = ip_a_codigo(ip_anfitrion)
        self.ready = False
        self.other_ready = False
        self.es_anfitrion = True
        self.juego_iniciado = False
        self.ip_servidor = ip_anfitrion
        
        print(f" Reconectando a sala: {self.codigo_sala}")
        
        # Conectar al servidor local
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect(("127.0.0.1", config.DEFAULT_PORT))
            self.sock.settimeout(None)
            self.client_thread = threading.Thread(target=self.receive_server, daemon=True)
            self.client_thread.start()
            time.sleep(0.5)
            
            #Enviar datos normales
            success = self.send_to_server({
                "nombre": self.name,
                "modo": self.modo,
                "dificultad": self.dificultad
            })
            
            if success:
                print(" Reconexión como anfitrión exitosa")
                self.connection_error = False
            else:
                raise ConnectionError("No se pudo enviar datos al servidor")
                
        except Exception as e:
            print(f" Error reconectando: {e}")
            self.alerta("Error al reconectar con el servidor local.\nLa sala pudo haber sido cerrada.")
            self.state = "inicio"
            if self.server_thread:
                self.server_thread = None

    def _crear_sala_despues_tutorial(self):
        """Crear sala NUEVA después del tutorial multijugador"""
        print(" Creando sala NUEVA...")
        
        self.limpiar_estado_conexion()
        
        #  Asegurar que no hay servidor previo
        if self.server_thread:
            print(" Cerrando servidor anterior...")
            self.server_thread.stop()
            time.sleep(1)
            self.server_thread = None
        
        try:
            # Crear nuevo servidor
            self.server_thread = ServerThread(host='0.0.0.0', port=config.DEFAULT_PORT)
            self.server_thread.state["nombres"][0] = self.name
            self.server_thread.state["modo"] = self.modo
            self.server_thread.state["dificultad"] = self.dificultad
            self.server_thread.daemon = True
            self.server_thread.start()
            time.sleep(2)
            print(" Servidor NUEVO iniciado")
        except Exception as e:
            self.alerta(f"Error al crear servidor: {str(e)}")
            self.state = "inicio"
            return
        
        # Configurar estado
        self.state = "sala"
        ip_anfitrion = obtener_ip_local()
        self.codigo_sala = ip_a_codigo(ip_anfitrion)
        self.ready = False
        self.other_ready = False
        self.es_anfitrion = True
        self.juego_iniciado = False
        self.ip_servidor = ip_anfitrion
        
        print(f" Sala NUEVA creada con código: {self.codigo_sala}")
        
        self.achievement_manager.registrar_sala_creada()
        
        # Conectar al servidor local
        if not self.connect_to_server("127.0.0.1", config.DEFAULT_PORT):
            self.alerta("Error al conectar con el servidor local")
            self.state = "inicio"
            if self.server_thread:
                self.server_thread.stop()
                self.server_thread = None
        else:
            print(" Sala NUEVA creada exitosamente")

    def unirse_sala_con_codigo(self, codigo):
        if not self.name or self.name.strip() == "":
            self.alerta("Debes ingresar un nombre antes de unirte a una sala")
            return
        
        #Verificar si es el anfitrión reconectándose a su propia sala
        ip_anfitrion = codigo_a_ip(codigo)
        ip_local = obtener_ip_local()
        
        if ip_anfitrion == ip_local and self.server_thread and self.server_thread.running:
            print(" Anfitrión detectado reconectándose a su propia sala")
            # Mostrar confirmación
            confirm = self.confirm_dialog("Estás intentando unirte a tu propia sala.\n\n¿Reconectar como anfitrión?")
            if confirm:
                self._reconectar_como_anfitrion()
            else:
                print(" Usuario canceló reconexión como anfitrión")
            return
        
        #  VERIFICAR TUTORIAL MULTIJUGADOR  
        if self.check_mostrar_tutorial("Multijugador"):
            self.mostrar_tutorial = True
            self.accion_multijugador_pendiente = "unirse_sala"
            self.codigo_sala_temporal = codigo
            if self.button_click_sound:
                    self.play_sound(self.button_click_sound)
            return
            
        # Si no hay tutorial, unirse normalmente como invitado
        self._unirse_sala_despues_tutorial(codigo)


    def _unirse_sala_despues_tutorial(self, codigo=None):
        """Unirse a sala como INVITADO después del tutorial multijugador"""
        if codigo is None and hasattr(self, 'codigo_sala_temporal'):
            codigo = self.codigo_sala_temporal
        
        if not codigo or len(codigo) != 4:
            self.alerta("Código de sala inválido.")
            return
            
        print(f" Uniéndose como INVITADO a sala: {codigo}")
        
        self.limpiar_estado_conexion()
        self.codigo_sala = codigo
        self.es_anfitrion = False 
        self.juego_iniciado = False
        
        ip_anfitrion = codigo_a_ip(codigo)
        self.ip_servidor = ip_anfitrion
        
        print(f" Conectando como INVITADO a: {ip_anfitrion}")
        
        self.achievement_manager.registrar_sala_unida()
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((ip_anfitrion, config.DEFAULT_PORT))
            self.sock.settimeout(None)
            self.client_thread = threading.Thread(target=self.receive_server, daemon=True)
            self.client_thread.start()
            time.sleep(0.5)
            if not self.send_to_server({
                "nombre": self.name,
                "modo": self.modo,
                "dificultad": self.dificultad
            }):
                raise ConnectionError("No se pudo enviar datos al servidor")
            self.ready = False
            self.other_ready = False
            self.state = "sala"
            self.connection_error = False
            print(" Unido exitosamente como INVITADO")
        except Exception as e:
            self.limpiar_estado_conexion()
            self.alerta(f"Error de conexión: {str(e)}")
            self.state = "inicio"
            self.connection_error = True


    def dar_listo(self):
        if not hasattr(self, 'sock') or self.connection_error or not self.sock:
            self.alerta("Error de conexión. No se puede cambiar el estado.")
            return
        self.ready = not self.ready
        if not self.send_to_server({"ready": self.ready}):
            self.ready = not self.ready
            self.alerta("Error al enviar estado al servidor.")

    def start_game(self):
        """Iniciar juego, mostrando tutorial si es necesario"""
        
        #  Si es Supervivencia, usar la función específica
        if hasattr(self, 'modo_juego') and self.modo_juego == "Supervivencia":
            self.iniciar_supervivencia()
            return
        
        #  PARA MULTIJUGADOR: Anfitrión inicia el juego
        if not self.solo and self.es_anfitrion:
            # EN MULTIJUGADOR solo verificar tutorial multijugador, NO tutoriales de los modos
            if self.check_mostrar_tutorial("Multijugador"):
                # Mostrar tutorial multijugador en lugar de iniciar inmediatamente
                self.mostrar_tutorial = True
                if self.button_click_sound:
                    self.play_sound(self.button_click_sound)
                print(f" Anfitrión: Mostrando tutorial MULTIJUGADOR")
                return
            self._iniciar_juego_multijugador()
            
        # PARA MODO INDIVIDUAL (SOLO)
        elif self.solo:
            # Verificar si debemos mostrar tutorial
            if self.check_mostrar_tutorial(self.modo):
                # Mostrar tutorial en lugar de iniciar juego inmediatamente
                self.mostrar_tutorial = True
                self.tutorial_modo_actual = self.modo
                if self.button_click_sound:
                    self.play_sound(self.button_click_sound)
                return
            
            # INICIAR SEGUIMIENTO DE LOGROS PARA MODO INDIVIDUAL
            es_supervivencia = hasattr(self, 'modo_juego') and self.modo_juego == "Supervivencia"
            es_multijugador = not self.solo
            
            self.achievement_manager.iniciar_partida(
                modo=self.modo,
                dificultad=self.dificultad,
                es_supervivencia=es_supervivencia,
                es_multijugador=es_multijugador
            )
            
            # SOLO código para modo individual
            self.modo_juego = "Normal"
            self.state = "juego"
            self.timer = 0
            self.timer_active = True
            self.game_over = False
            self.winner = -1
            self.juego_iniciado = True
            self.flipped = []
            self.mostrar_resultado_final = False
            self.nuevo_record_puntos = False
            self.nuevo_record_tiempo = False
            self.tiempo_restante = 0
            
            #Solo generar cartas para individual
            self.cartas = generar_cartas(self.modo, self.dificultad)
            self.turno = 0
            self.scores = [0, 0]
            
            print(f" Modo Individual iniciado - Cartas: {len(self.cartas)}")
            if self.button_click_sound:
                    self.play_sound(self.button_click_sound)
        
        # PARA INVITADO EN MULTIJUGADOR 
        elif not self.solo and not self.es_anfitrion:
            print(" Invitado listo - Esperando que anfitrión inicie el juego")

    def _iniciar_juego_multijugador(self):
        """Iniciar juego multijugador después de que el anfitrión complete tutorial """
        print(f" Anfitrión: Iniciando juego multijugador - Modo: {self.modo}, Dificultad: {self.dificultad}")
        
        #  EN MULTIJUGADOR: Saltar directamente al juego sin ver tutorial del modo
        self.modo_juego = "Normal"
        self.state = "juego"
        self.timer = 0
        self.timer_active = True
        self.game_over = False
        self.winner = -1
        self.juego_iniciado = True
        self.flipped = []
        self.mostrar_resultado_final = False
        self.nuevo_record_puntos = False
        self.nuevo_record_tiempo = False
        self.tiempo_restante = 0
        
        # Generar cartas ANTES de enviar al servidor
        self.cartas = generar_cartas(self.modo, self.dificultad)
        self.turno = 0
        self.scores = [0, 0]
        
        print(f" Cartas generadas: {len(self.cartas)} para modo {self.modo}")
        
        #  INICIAR LOGROS PARA MULTIJUGADOR
        self.achievement_manager.iniciar_partida(
            modo=self.modo,
            dificultad=self.dificultad,
            es_supervivencia=False,
            es_multijugador=True
        )
        print(f" Sistema de logros iniciado para multijugador")
        
        #Enviar estado inicial a todos los clientes
        success = self.send_to_server({
            "iniciar_juego": True,
            "cartas": [card.copy() for card in self.cartas],
            "turno": self.turno,
            "scores": self.scores
        })
        
        if success:
            print(f" Juego multijugador iniciado exitosamente - Cartas: {len(self.cartas)}")
            if self.button_click_sound:
                    self.play_sound(self.button_click_sound)
        else:
            print(" Error al enviar inicio de juego al servidor")
            # Revertir estado en caso de error
            self.state = "sala"
            self.juego_iniciado = False
            self.timer_active = False

    def iniciar_juego_como_invitado(self):
        # Método para que el invitado inicie el juego después del tutorial del modo 
        if not self.solo and not self.es_anfitrion and self.juego_iniciado:
            # Solo cambiar el estado a juego 
            self.state = "juego"
            self.timer = 0
            self.timer_active = True
            self.game_over = False
            self.mostrar_resultado_final = False
            
            #  VERIFICAR que las cartas estén cargadas correctamente
            if self.cartas and len(self.cartas) > 0:
                print(f" Invitado: {len(self.cartas)} cartas cargadas correctamente")
            else:
                print(" Invitado: No hay cartas cargadas")
            
            if self.button_click_sound:
                    self.play_sound(self.button_click_sound)
        else:
            print(f" Invitado: No se pudo unir al juego - "
                f"Juego iniciado: {self.juego_iniciado}, "
                f"Es anfitrión: {self.es_anfitrion}, "
                f"Solo: {self.solo}")

    def puede_voltear_carta(self, index):
        if not self.cartas or index < 0 or index >= len(self.cartas):
            return False
        if self.game_over or not self.juego_iniciado:
            return False
        carta = self.cartas[index]
        if carta["matched"] or carta["flipped"] or len(self.flipped) >= 2 or self.esperando_volteo:
            return False
        if not self.solo:
            jugador_actual = 0 if self.es_anfitrion else 1
            if self.turno != jugador_actual:
                return False
        return True

    def click_juego(self, pos):
        if not self.cartas or not self.juego_iniciado or self.game_over or self.esperando_volteo:
            return
        
        if not self.solo:
            jugador_actual = 0 if self.es_anfitrion else 1
            if self.turno != jugador_actual:
                return
        
        config_juego = config.DIFICULTAD_CONFIG[self.dificultad]
        cols = config_juego["cols"]
        rows = config_juego["rows"]
        size = min(config.WIDTH // cols, (config.HEIGHT - 100) // rows)
        grid_width = cols * size
        grid_height = rows * size
        start_x = (config.WIDTH - grid_width) // 2
        start_y = (config.HEIGHT - grid_height) // 2 + 25
        mx, my = pos
        
        for i, card in enumerate(self.cartas):
            row = i // cols
            col = i % cols
            cx = start_x + col * size
            cy = start_y + row * size
            if cx <= mx <= cx + size and cy <= my <= cy + size:
                if self.puede_voltear_carta(i):
                    # EL SERVIDOR SE ENCARGA DE REINICIAR EL TEMPORIZADOR Y MANEJAR LAS CARTAS
                    card["flipped"] = True
                    self.flipped.append(i)
                    # sistema de audio
                    if self.card_flip_sound:
                        self.card_flip_sound.play()
                    
                    #  Enviar el estado completo al servidor
                    if not self.solo:
                        self.send_to_server({
                            "flipped": True,
                            "cartas": [card.copy() for card in self.cartas],  # Enviar TODAS las cartas
                            "turno": self.turno,
                            "scores": self.scores
                        })
                    
                    if len(self.flipped) == 2:
                        self.esperando_volteo = True
                        self.temporizador_volteo = 0
                    break



    def update(self, dt):

        # verificar resultado final del juego
        if self.mostrar_resultado_final:
            tiempo_transcurrido_resultado = time.time() - self.tiempo_resultado
            if tiempo_transcurrido_resultado > 5:
                self.volver_al_inicio()
                return

        # ACTUALIZACIONES DEL JUEGO
        if self.modo_juego == "Supervivencia" and self.juego_iniciado and not self.game_over:
            self.update_supervivencia(dt)
        elif self.timer_active and self.state == "juego" and not self.game_over and self.modo_juego == "Normal":
            self.timer += dt

        # Actualizar notificación de logro
        if self.achievement_notification and time.time() - self.achievement_notification_time > 3:
            self.achievement_notification = None

        # LÓGICA DE VOLTEO
        if self.esperando_volteo:
            self.temporizador_volteo += dt
            if self.temporizador_volteo >= self.tiempo_espera_volteo:
                a, b = self.flipped
                if a < 0 or a >= len(self.cartas) or b < 0 or b >= len(self.cartas):
                    self.flipped = []
                    self.esperando_volteo = False
                    return
                
                emparejadas = False
                if (self.cartas[a]["back"] == self.cartas[b]["front"] or
                    self.cartas[a]["front"] == self.cartas[b]["back"]):
                    emparejadas = True
                    self.cartas[a]["matched"] = True
                    self.cartas[b]["matched"] = True
                    self.scores[self.turno] += 1
                    
                    if self.card_match_sound:
                        self.card_match_sound.play()
                    
                    self.achievement_manager.registrar_par_encontrado()
                    
                    if self.modo_juego == "Supervivencia":
                        self.aplicar_bonus_supervivencia(True)
                else:
                    self.cartas[a]["flipped"] = False
                    self.cartas[b]["flipped"] = False
                    
                    self.achievement_manager.registrar_error()
                    
                    if self.modo_juego == "Supervivencia":
                        self.aplicar_bonus_supervivencia(False)
                    
                    # SOLO cambiar turno en multijugador
                    if not self.solo:
                        self.turno = 1 - self.turno
                
                self.flipped = []
                self.esperando_volteo = False
                
                # DETECCIÓN DE FIN DE JUEGO PARA TODAS LAS DIFICULTADES
                all_matched = True
                cartas_emparejadas = 0
                total_cartas = len(self.cartas)
                
                for card in self.cartas:
                    if not card.get("matched", False):
                        all_matched = False
                    else:
                        cartas_emparejadas += 1
                
                # DEBUG MEJORADO PARA TODAS LAS DIFICULTADES
                if cartas_emparejadas >= total_cartas - 2:
                    print(f" {self.name} [{self.dificultad}]: Progreso {cartas_emparejadas}/{total_cartas} cartas emparejadas")
                
                #  MANEJO DE FIN DE JUEGO PARA TODOS LOS MODOS
                if all_matched and not self.game_over:
                    print(f" {self.name}: ¡JUEGO TERMINADO! {cartas_emparejadas}/{total_cartas} cartas emparejadas")
                    print(f" Modo: {self.modo}, Dificultad: {self.dificultad}, Juego: {self.modo_juego}")
                    
                    if self.solo:
                        #  MODO INDIVIDUAL: Manejar fin de juego directamente
                        self.game_over = True
                        self.timer_active = False
                        self.temporizador_turno_activo = False
                        self.mostrar_resultado_final = True
                        self.tiempo_resultado = time.time()
                        
                        #  CALCULAR TIEMPO FINAL SEGÚN MODO
                        if self.modo_juego == "Normal":
                            tiempo_final = self.timer
                            #  GUARDAR RECORDS SOLO EN MODO NORMAL
                            self.nuevo_record_puntos, self.nuevo_record_tiempo = save_highscore(
                                self.modo, self.dificultad, self.scores[0], self.timer
                            )
                        else:  # Supervivencia
                            tiempo_final = self.tiempo_restante
                        
                        victoria = True
                        self.achievement_manager.finalizar_partida(tiempo_final, victoria)
                        
                        if self.victory_sound:
                            self.victory_sound.play()
                        print(f" {self.name}: ¡VICTORIA en modo individual!")
                    
                    else:
                        #  MODO MULTIJUGADOR: Enviar estado actualizado
                        print(f" {self.name}: Estado final enviado al servidor - Esperando sincronización...")
                
                #  SINCRONIZACIÓN EN MULTIJUGADOR DESPUÉS DE CADA ACCIÓN
                if not self.solo:
                    success = self.send_to_server({
                        "flipped": True,
                        "cartas": [card.copy() for card in self.cartas],
                        "turno": self.turno,
                        "scores": self.scores
                    })
                    
                    if success:
                        print(f" {self.name}: Estado sincronizado - Turno: {self.turno}, Puntos: {self.scores}")
                    else:
                        print(" Error sincronizando estado con servidor")

        #  VERIFICACIÓN DE CONEXIÓN SOLO EN MULTIJUGADOR
        if not self.solo:
            self.check_connection()

    def check_connection(self):
        current_time = time.time()
        if (self.connection_error and
            current_time - self.last_connection_attempt > self.reconnection_delay and
            not self.solo and self.state != "inicio"):
            
            print(f" Intentando reconexión...")
            
            if self.es_anfitrion:
                success = self.connect_to_server("127.0.0.1", config.DEFAULT_PORT)
            else:
                success = self.connect_to_server(self.ip_servidor, config.DEFAULT_PORT)
            
            if success:
                print(" Reconexión exitosa")
                # Intentar re-sincronizar el estado del juego
                if self.state == "juego":
                    # Enviar ping para verificar estado actual
                    self.send_to_server({"ping": True})
                
                # Resetear contador de reconexiones fallidas
                if hasattr(self, 'reconexiones_fallidas'):
                    self.reconexiones_fallidas = 0
            else:
                #  SI LA RECONEXIÓN FALLA MUCHAS VECES, VOLVER AL INICIO
                if not hasattr(self, 'reconexiones_fallidas'):
                    self.reconexiones_fallidas = 0
                self.reconexiones_fallidas += 1
                
                if self.reconexiones_fallidas >= 3:  # Después de 3 intentos fallidos
                    print(" Múltiples reconexiones fallidas - Volviendo al inicio")
                    self.volver_al_inicio()

    def volver_al_inicio(self):
        self.state = "inicio"
        self.juego_iniciado = False
        self.timer_active = False
        self.game_over = False
        self.mostrar_resultado_final = False
        self.ready = False
        self.other_ready = False
        self.cartas = []
        self.flipped = []
        self.codigo_sala = ""
        
        # Resetear el modo de juego a Normal
        self.modo_juego = "Normal"  
        
        # Solo cerrar el socket del cliente 
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        
        self.es_anfitrion = False
        self.solo = True
        self.connection_error = False
        self.highscores = load_highscores()
        
        # Resetear contador de reconexiones
        if hasattr(self, 'reconexiones_fallidas'):
            self.reconexiones_fallidas = 0


    def abandonar(self):
        confirm = self.confirm_dialog("¿Seguro que desea abandonar la sala?")
        if confirm:
            if self.sock and not self.connection_error:
                try:
                    # Enviar nombre al abandonar
                    self.send_to_server({
                        "abandon": True,
                        "nombre": self.name  
                    })
                    print(f" {self.name} está abandonando la sala...")
                except Exception as e:
                    print(f"Error enviando mensaje de abandono: {e}")
            
            #  Solo limpiar estado del cliente 
            self.state = "inicio"
            self.juego_iniciado = False
            self.timer_active = False
            self.game_over = False
            self.mostrar_resultado_final = False
            self.ready = False
            self.other_ready = False
            self.cartas = []
            self.flipped = []
            self.codigo_sala = ""
            self.modo_juego = "Normal"  
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
                self.sock = None
            
            # El servidor se cierra si no hay jugadores 
            self.es_anfitrion = False
            self.solo = True
            self.connection_error = False


    def confirmar_salida(self):
        confirm = self.confirm_dialog("¿Seguro que desea salir del juego?")
        if confirm:
            self.volver_al_inicio()

    def alerta(self, mensaje):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        alert_rect = pygame.Rect(config.WIDTH//2 - 200, config.HEIGHT//2 - 50, 400, 100)
        pygame.draw.rect(self.screen, (255, 215, 0), alert_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 0, 0), alert_rect, 3, border_radius=15)
        ui_components.draw_text(self.screen, mensaje, 28, config.BLACK, config.WIDTH//2, config.HEIGHT//2 - 15, "center")
        ui_components.draw_text(self.screen, "Clic para continuar", 20, config.GRAY, config.WIDTH//2, config.HEIGHT//2 + 15, "center")
        pygame.display.flip()
        waiting = True
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

    def confirm_dialog(self, mensaje):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        dialog_rect = pygame.Rect(config.WIDTH//2 - 200, config.HEIGHT//2 - 100, 400, 200)
        pygame.draw.rect(self.screen, (255, 255, 0), dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 165, 0), dialog_rect, 3, border_radius=15)
        
        ui_components.draw_text(self.screen, mensaje, 28, config.BLACK, config.WIDTH//2, config.HEIGHT//2 - 50, "center")
        ui_components.draw_text(self.screen, "Selecciona una opción:", 20, config.GRAY, config.WIDTH//2, config.HEIGHT//2 - 10, "center")
        
        # Dibujar botones Sí/No
        si_button = ui_components.draw_button(self.screen, "SÍ", config.WIDTH//2 - 120, config.HEIGHT//2 + 20, 100, 40, config.GREEN)
        no_button = ui_components.draw_button(self.screen, "NO", config.WIDTH//2 + 20, config.HEIGHT//2 + 20, 100, 40, config.RED)
        
        pygame.display.flip()
        
        waiting = True
        result = False
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                    return False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if si_button.collidepoint(event.pos):
                        result = True
                        waiting = False
                        if self.button_click_sound:
                            self.play_sound(self.button_click_sound)
                    elif no_button.collidepoint(event.pos):
                        result = False
                        waiting = False
                        if self.button_click_sound:
                            self.play_sound(self.button_click_sound)
                        
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        result = True
                        waiting = False
                        if self.button_click_sound:
                            self.play_sound(self.button_click_sound)
                    elif event.key == pygame.K_ESCAPE:
                        result = False
                        waiting = False
                        if self.button_click_sound:
                             self.play_sound(self.button_click_sound)
        
        return result

    def draw(self):
        ui_components.draw_background(self.screen)
        
        # MOSTRAR TUTORIAL SI ESTÁ ACTIVO
        if self.mostrar_tutorial:
            self.draw_tutorial()
        elif self.state == "inicio":
            self.draw_inicio()
        elif self.state == "sala":
            self.draw_sala()
        elif self.state == "juego":
            self.draw_juego()
        
        # Dibujar diálogos
        if self.show_audio_dialog:  
            music_btn, music_slider, sfx_btn, sfx_slider, test_btn, close_btn = self.draw_audio_dialog()
            self.audio_dialog_elements = (music_btn, music_slider, sfx_btn, sfx_slider, test_btn, close_btn)
        
        if self.show_records_dialog:
            self.draw_records_dialog()
        if self.show_modes_dialog:
            self.draw_modes_dialog()
        if self.show_difficulty_dialog:
            self.draw_difficulty_dialog()
        if self.show_join_dialog:
            self.draw_join_dialog()
        if self.editing_name:
            self.draw_name_dialog()
        if self.show_achievements_dialog:
            self.draw_achievements_dialog()
                
        # Dibujar notificación de logro
        if self.achievement_notification:
            self.draw_achievement_notification()

        pygame.display.flip()


    def draw_inicio(self):
        ui_components.draw_text(self.screen, "MEMORI GAME", 48, (255, 215, 0), config.WIDTH//2, 50, "center")
        ui_components.draw_text(self.screen, "MEMORI GAME", 48, (255, 0, 0), config.WIDTH//2 + 2, 52, "center")
        
        #  BOTONES DE AUDIO
        music_btn, sfx_btn = self.draw_audio_buttons()
        self.audio_buttons = (music_btn, sfx_btn)  # Guardar para manejar clicks
        
        # Botones normales
        ui_components.draw_button(self.screen, "Nombre: " + self.name, config.WIDTH//2 - 150, 150, 300, 50, config.BUTTON_ALT_COLOR, config.BUTTON_ALT_HOVER)
        ui_components.draw_button(self.screen, "Modo: " + self.modo, config.WIDTH//2 - 150, 220, 300, 50, config.BUTTON_ALT_COLOR, config.BUTTON_ALT_HOVER)
        ui_components.draw_button(self.screen, "Dificultad: " + self.dificultad, config.WIDTH//2 - 150, 290, 300, 50, config.BUTTON_ALT_COLOR, config.BUTTON_ALT_HOVER)
        ui_components.draw_button(self.screen, "Jugar Solo", config.WIDTH//2 - 150, 360, 300, 50)
        ui_components.draw_button(self.screen, "Modo Supervivencia", config.WIDTH//2 - 150, 430, 300, 50, config.RED)
        ui_components.draw_button(self.screen, "Crear Sala", config.WIDTH//2 - 150, 500, 300, 50, config.BUTTON_ALT_COLOR, config.BUTTON_ALT_HOVER)
        ui_components.draw_button(self.screen, "Unirse a Sala", config.WIDTH//2 - 150, 570, 300, 50, config.BUTTON_ALT_COLOR, config.BUTTON_ALT_HOVER)
        ui_components.draw_button(self.screen, "Ver Records", config.WIDTH//2 - 150, 640, 300, 50, config.PURPLE)
        ui_components.draw_button(self.screen, "Logros", config.WIDTH//2 - 150, 710, 300, 50, config.ORANGE)


    def draw_modes_dialog(self):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        dialog_rect = pygame.Rect(config.WIDTH//2 - 200, config.HEIGHT//2 - 150, 400, 300)
        pygame.draw.rect(self.screen, config.DIALOG_BG, dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 215, 0), dialog_rect, 3, border_radius=15)
        ui_components.draw_text(self.screen, "SELECCIONAR MODO", 32, (255, 255, 0), config.WIDTH//2, config.HEIGHT//2 - 120, "center")
        ui_components.draw_button(self.screen, "País-Capital", config.WIDTH//2 - 150, config.HEIGHT//2 - 100, 300, 50,
                   (0, 255, 255) if self.modo == "País-Capital" else config.BUTTON_ALT_COLOR)
        ui_components.draw_button(self.screen, "Matemáticas", config.WIDTH//2 - 150, config.HEIGHT//2 - 30, 300, 50,
                   (0, 255, 255) if self.modo == "Matemáticas" else config.BUTTON_ALT_COLOR)
        ui_components.draw_button(self.screen, "Español-Inglés", config.WIDTH//2 - 150, config.HEIGHT//2 + 40, 300, 50,
                   (0, 255, 255) if self.modo == "Español-Inglés" else config.BUTTON_ALT_COLOR)
        ui_components.draw_button(self.screen, "Cerrar", config.WIDTH//2 - 50, config.HEIGHT//2 + 110, 100, 40, config.RED)

    def draw_difficulty_dialog(self):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        dialog_rect = pygame.Rect(config.WIDTH//2 - 200, config.HEIGHT//2 - 150, 400, 300)
        pygame.draw.rect(self.screen, config.DIALOG_BG, dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 215, 0), dialog_rect, 3, border_radius=15)
        ui_components.draw_text(self.screen, "SELECCIONAR DIFICULTAD", 32, (255, 255, 0), config.WIDTH//2, config.HEIGHT//2 - 120, "center")
        ui_components.draw_button(self.screen, "Fácil", config.WIDTH//2 - 150, config.HEIGHT//2 - 100, 300, 50,
                   (0, 255, 255) if self.dificultad == "Fácil" else config.BUTTON_ALT_COLOR)
        ui_components.draw_button(self.screen, "Medio", config.WIDTH//2 - 150, config.HEIGHT//2 - 30, 300, 50,
                   (0, 255, 255) if self.dificultad == "Medio" else config.BUTTON_ALT_COLOR)
        ui_components.draw_button(self.screen, "Difícil", config.WIDTH//2 - 150, config.HEIGHT//2 + 40, 300, 50,
                   (0, 255, 255) if self.dificultad == "Difícil" else config.BUTTON_ALT_COLOR)
        ui_components.draw_button(self.screen, "Cerrar", config.WIDTH//2 - 50, config.HEIGHT//2 + 110, 100, 40, config.RED)

    def draw_records_dialog(self):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Diálogo compacto
        dialog_rect = pygame.Rect(config.WIDTH//2 - 300, config.HEIGHT//2 - 200, 600, 450)
        pygame.draw.rect(self.screen, config.DIALOG_BG, dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 215, 0), dialog_rect, 3, border_radius=15)
        
        ui_components.draw_text(self.screen, "RÉCORDS - MODO NORMAL", 32, (255, 255, 0), config.WIDTH//2, config.HEIGHT//2 - 170, "center")
        
        # Encabezados
        ui_components.draw_text(self.screen, "Modo", 24, (255, 215, 0), config.WIDTH//2 - 250, config.HEIGHT//2 - 90)
        ui_components.draw_text(self.screen, "Fácil", 24, (173, 216, 230), config.WIDTH//2 - 100, config.HEIGHT//2 - 90, "center")
        ui_components.draw_text(self.screen, "Medio", 24, (255, 255, 0), config.WIDTH//2 + 50, config.HEIGHT//2 - 90, "center")
        ui_components.draw_text(self.screen, "Difícil", 24, (255, 165, 0), config.WIDTH//2 + 200, config.HEIGHT//2 - 90, "center")
        
        y_pos = config.HEIGHT//2 - 50
        
        # Solo modos normales
        modos_normales = ["País-Capital", "Matemáticas", "Español-Inglés"]
        
        for modo in modos_normales:
            ui_components.draw_text(self.screen, modo, 18, (200, 255, 200), config.WIDTH//2 - 250, y_pos)
            
            if modo in self.highscores and isinstance(self.highscores[modo], dict):
                facil = self.highscores[modo]["Fácil"]
                medio = self.highscores[modo]["Medio"]
                dificil = self.highscores[modo]["Difícil"]
                
                # Puntos y tiempo para Fácil
                tiempo_facil = f"({facil['tiempo']:.1f}s)" if facil['tiempo'] != float('inf') else ""
                ui_components.draw_text(self.screen, f"{facil['puntos']} {tiempo_facil}", 18, (173, 216, 230), config.WIDTH//2 - 100, y_pos, "center")
                
                # Puntos y tiempo para Medio
                tiempo_medio = f"({medio['tiempo']:.1f}s)" if medio['tiempo'] != float('inf') else ""
                ui_components.draw_text(self.screen, f"{medio['puntos']} {tiempo_medio}", 18, (255, 255, 0), config.WIDTH//2 + 50, y_pos, "center")
                
                # Puntos y tiempo para Difícil
                tiempo_dificil = f"({dificil['tiempo']:.1f}s)" if dificil['tiempo'] != float('inf') else ""
                ui_components.draw_text(self.screen, f"{dificil['puntos']} {tiempo_dificil}", 18, (255, 165, 0), config.WIDTH//2 + 200, y_pos, "center")
            
            y_pos += 35
        
        # Leyenda
        ui_components.draw_text(self.screen, "Formato: Puntos (Tiempo más rápido)", 16, (200, 200, 255), config.WIDTH//2, y_pos + 20, "center")
        
        #  Posición fija para los botones
        botones_y = config.HEIGHT//2 + 150  
        
        # Dibujar botones y guardar sus rectángulos
        self.cerrar_btn = ui_components.draw_button(self.screen, "Cerrar", config.WIDTH//2 - 120, botones_y, 100, 40, config.BUTTON_COLOR)
        self.borrar_btn = ui_components.draw_button(self.screen, "Borrar Récords", config.WIDTH//2 + 20, botones_y, 200, 40, config.RED)
        
        # Devolver los rectángulos para el manejo de clicks
        return self.cerrar_btn, self.borrar_btn
    
    def draw_achievements_dialog(self):

        # Overlay más opaco para bloquecer clicks
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        
        # Panel principal
        dialog_rect = pygame.Rect(50, 50, config.WIDTH - 100, config.HEIGHT - 100)
        pygame.draw.rect(self.screen, config.DIALOG_BG, dialog_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 215, 0), dialog_rect, 4, border_radius=20)
        
        # Título y estadísticas 
        ui_components.draw_text(self.screen, "LOGROS Y ESTADÍSTICAS", 36, (255, 255, 0), config.WIDTH//2, 70, "center")
        
        nivel = self.achievement_manager.get_nivel()
        puntos = self.achievement_manager.get_puntos_totales()
        stats = self.achievement_manager.get_estadisticas()
        
        ui_components.draw_text(self.screen, f"Nivel: {nivel} | Puntos: {puntos}", 24, (173, 216, 230), config.WIDTH//2, 110, "center")
        ui_components.draw_text(self.screen, f"Partidas: {stats['total_partidas']} | Victorias: {stats['partidas_ganadas']}", 20, config.WHITE, config.WIDTH//2, 140, "center")
        
        # Área de contenido scroll
        content_rect = pygame.Rect(90, 170, config.WIDTH - 180, config.HEIGHT - 250)
        pygame.draw.rect(self.screen, (40, 40, 60), content_rect, border_radius=10)
        
        # Calcular altura total del contenido PARA EL SCROLL
        logros_por_categoria = self.achievement_manager.get_logros_por_categoria()
        contenido_altura = 0
        
        for categoria, logros in logros_por_categoria.items():
            contenido_altura += 35  # Título de categoría
            for logro in logros:
                if logro["secreto"] and not logro["desbloqueado"]:
                    contenido_altura += 35  # Logro secreto
                else:
                    contenido_altura += 55  # Logro normal
            contenido_altura += 10  # Espacio entre categorías
        
        # Configurar scroll 
        self.achievements_scroll_max = max(0, contenido_altura - content_rect.height)
        self.achievements_scroll_y = max(0, min(self.achievements_scroll_y, self.achievements_scroll_max))
        
        # DIBUJAR CONTENIDO CON SCROLL 
        y_pos = 170 - self.achievements_scroll_y
        
        for categoria, logros in logros_por_categoria.items():
            if y_pos + 30 >= content_rect.y and y_pos <= content_rect.y + content_rect.height:
                ui_components.draw_text(self.screen, categoria, 24, (255, 215, 0), 230, y_pos)  
            y_pos += 35
            
            for logro in logros:
                if y_pos >= content_rect.y and y_pos <= content_rect.y + content_rect.height:
                    color = config.GREEN if logro["desbloqueado"] else config.LIGHTGRAY
                    
                    if logro["desbloqueado"]:
                        texto = f"{logro['icono']} {logro['nombre']} (+{logro['puntos']} pts)"
                        ui_components.draw_text(self.screen, texto, 18, color, 250, y_pos) 
                    else:
                        if logro["secreto"]:
                            texto = f"{logro['icono']} ???"
                        else:
                            progreso = min(logro["progreso"], logro["meta"])
                            texto = f"{logro['icono']} {logro['nombre']} [{progreso}/{logro['meta']}]"
                        ui_components.draw_text(self.screen, texto, 18, color, 250, y_pos)  
                    # Descripción solo para logros visibles
                    if (not logro["secreto"] or logro["desbloqueado"]) and y_pos + 25 <= content_rect.y + content_rect.height:
                        ui_components.draw_text(self.screen, logro["descripcion"], 14, config.LIGHTGRAY, 270, y_pos + 25) 
                        y_pos += 55
                    else:
                        y_pos += 35
                else:
                    # Avanzar posición aunque no se dibuje
                    y_pos += 55 if (not logro.get("secreto", False) or logro["desbloqueado"]) else 35
                
            y_pos += 10
        
        # Dibujar barra de scroll si es necesario
        if contenido_altura > content_rect.height and self.achievements_scroll_max > 0:
            scrollbar_width = 15
            scrollbar_rect = pygame.Rect(
                content_rect.right - scrollbar_width - 3,
                content_rect.y,
                scrollbar_width,
                content_rect.height
            )
            
            # Thumb más visible
            thumb_height = max(50, content_rect.height * (content_rect.height / contenido_altura))
            scroll_ratio = self.achievements_scroll_y / self.achievements_scroll_max
            thumb_y = content_rect.y + (content_rect.height - thumb_height) * scroll_ratio
            
            thumb_rect = pygame.Rect(
                scrollbar_rect.x,
                thumb_y,
                scrollbar_rect.width,
                thumb_height
            )
            
            # Color de la barra si está siendo arrastrada
            thumb_color = (200, 200, 255) if self.scroll_dragging else (180, 180, 200)
            
            pygame.draw.rect(self.screen, (80, 80, 100), scrollbar_rect, border_radius=6)
            pygame.draw.rect(self.screen, thumb_color, thumb_rect, border_radius=6)
        
        # Instrucciones de controles
        controls_text = "Controles: ↑/W=Arriba  ↓/S=Abajo  PgUp/PgDn=Rápido  Home/Inicio=Inicio  End/Fin=Final"
        ui_components.draw_text(self.screen, controls_text, 14, (200, 200, 255), config.WIDTH//2, config.HEIGHT - 75, "center")
        
        # Botón cerrar
        cerrar_btn = ui_components.draw_button(self.screen, "Cerrar", config.WIDTH//2 - 50, config.HEIGHT - 60, 100, 40, config.RED)
        
        return cerrar_btn, content_rect

    def draw_join_dialog(self):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        dialog_rect = pygame.Rect(config.WIDTH//2 - 200, config.HEIGHT//2 - 120, 400, 240)
        pygame.draw.rect(self.screen, config.DIALOG_BG, dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 215, 0), dialog_rect, 3, border_radius=15)
        
        ui_components.draw_text(self.screen, "UNIRSE A SALA", 32, (255, 255, 0), config.WIDTH//2, config.HEIGHT//2 - 90, "center")
        ui_components.draw_text(self.screen, "Ingresa el código de la sala :", 24, (255, 255, 0), config.WIDTH//2, config.HEIGHT//2 - 50, "center")
        
        input_rect = pygame.Rect(config.WIDTH//2 - 100, config.HEIGHT//2 - 10, 200, 40)
        pygame.draw.rect(self.screen, (255, 255, 224), input_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 215, 0), input_rect, 2, border_radius=10)
        ui_components.draw_text(self.screen, self.input_text, 28, config.BLACK, config.WIDTH//2, config.HEIGHT//2, "center")
        
        # Dibujar botones y guardar sus rectángulos para el manejo de clics
        confirmar_button = ui_components.draw_button(self.screen, "CONFIRMAR", config.WIDTH//2 - 120, config.HEIGHT//2 + 50, 110, 40, config.GREEN)
        cancelar_button = ui_components.draw_button(self.screen, "CANCELAR", config.WIDTH//2 + 10, config.HEIGHT//2 + 50, 110, 40, config.RED)
        
        ui_components.draw_text(self.screen, "Presiona ENTER para confirmar", 16, (173, 216, 230), config.WIDTH//2, config.HEIGHT//2 + 100, "center")
        ui_components.draw_text(self.screen, "ESC para cancelar", 16, (173, 216, 230), config.WIDTH//2, config.HEIGHT//2 + 120, "center")
        
        return confirmar_button, cancelar_button, input_rect
    
    def draw_name_dialog(self):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        dialog_rect = pygame.Rect(config.WIDTH//2 - 200, config.HEIGHT//2 - 100, 400, 200)
        pygame.draw.rect(self.screen, config.DIALOG_BG, dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 215, 0), dialog_rect, 3, border_radius=15)
        ui_components.draw_text(self.screen, "NOMBRE DE JUGADOR", 32, (255, 255, 0), config.WIDTH//2, config.HEIGHT//2 - 70, "center")
        input_rect = pygame.Rect(config.WIDTH//2 - 150, config.HEIGHT//2 - 20, 300, 40)
        pygame.draw.rect(self.screen, (255, 255, 224), input_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 215, 0), input_rect, 2, border_radius=10)
        ui_components.draw_text(self.screen, self.input_text, 28, config.BLACK, config.WIDTH//2, config.HEIGHT//2 - 15, "center")
        ui_components.draw_text(self.screen, "Presiona ENTER para confirmar", 18, (173, 216, 230), config.WIDTH//2, config.HEIGHT//2 + 30, "center")
        ui_components.draw_text(self.screen, "ESC para cancelar", 18, (173, 216, 230), config.WIDTH//2, config.HEIGHT//2 + 55, "center")

    def draw_achievement_notification(self):
        # Dibujar notificación de logro desbloqueado 
        if not self.achievement_notification:
            return
            
        notification_rect = pygame.Rect(config.WIDTH//2 - 200, 50, 400, 80)
        pygame.draw.rect(self.screen, (50, 50, 50, 200), notification_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 215, 0), notification_rect, 3, border_radius=15)
        
        logro = self.achievement_notification
        ui_components.draw_text(self.screen, " ¡Logro Desbloqueado!", 24, (255, 255, 0), config.WIDTH//2, 70, "center")
        ui_components.draw_text(self.screen, f"{logro['icono']} {logro['nombre']}", 20, config.WHITE, config.WIDTH//2, 100, "center")
        ui_components.draw_text(self.screen, f"+{logro['puntos']} puntos", 18, (173, 216, 230), config.WIDTH//2, 120, "center")

    def handle_achievements_dialog_click(self, pos):
        # Manejar clics en el diálogo de logros 
        x, y = pos
        # Botón cerrar
        if config.WIDTH//2 - 50 <= x <= config.WIDTH//2 + 50 and config.HEIGHT - 60 <= y <= config.HEIGHT - 20:
            self.show_achievements_dialog = False
            # Audio de botón
            if self.button_click_sound:
                self.button_click_sound.play()
            return True
        return False



    def handle_achievements_dialog_scroll(self, event):
        # Manejar scroll del mouse en logros 
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.achievements_scroll_y = max(0, self.achievements_scroll_y - 50)
            elif event.button == 5:  # Scroll down
                self.achievements_scroll_y = min(self.achievements_scroll_max, self.achievements_scroll_y + 50)

    def draw_sala(self):
    #  Fondo estrellado 
        for i in range(50):
            x = (i * 89) % config.WIDTH
            y = (i * 101) % config.HEIGHT
            pygame.draw.circle(self.screen, (255, 255, 100), (x, y), 1)
        

        ui_components.draw_text(self.screen, "SALA DE JUEGO", 40, (255, 215, 0), config.WIDTH//2, 50, "center")
        ui_components.draw_text(self.screen, f"Código de Sala: {self.codigo_sala}", 32, (255, 255, 0), config.WIDTH//2, 100, "center")
        ui_components.draw_text(self.screen, f"Jugador: {self.name}", 28, (255, 255, 0), config.WIDTH//2, 160, "center")
        ui_components.draw_text(self.screen, f"Modo: {self.modo}", 28, (255, 255, 0), config.WIDTH//2, 200, "center")
        ui_components.draw_text(self.screen, f"Dificultad: {self.dificultad}", 28, (255, 255, 0), config.WIDTH//2, 240, "center")
        
        if self.es_anfitrion:
            ui_components.draw_text(self.screen, f"{self.nombres[0]} (Tú): {'LISTO' if self.ready else 'NO LISTO'}",
                    28, config.GREEN if self.ready else config.RED, config.WIDTH//2, 300, "center")
            ui_components.draw_text(self.screen, f"{self.nombres[1]}: {'LISTO' if self.other_ready else 'ESPERANDO...'}",
                    28, config.GREEN if self.other_ready else config.RED, config.WIDTH//2, 340, "center")
        else:
            ui_components.draw_text(self.screen, f"{self.nombres[0]}: {'LISTO' if self.other_ready else 'ESPERANDO...'}",
                    28, config.GREEN if self.other_ready else config.RED, config.WIDTH//2, 300, "center")
            ui_components.draw_text(self.screen, f"{self.nombres[1]} (Tú): {'LISTO' if self.ready else 'NO LISTO'}",
                    28, config.GREEN if self.ready else config.RED, config.WIDTH//2, 340, "center")
        
        ui_components.draw_button(self.screen, "Dar Listo", config.WIDTH//2 - 100, 400, 200, 40)
        if self.es_anfitrion and self.ready and self.other_ready:
            ui_components.draw_button(self.screen, "Iniciar Juego", config.WIDTH//2 - 100, 470, 200, 40, config.GREEN)
        else:
            ui_components.draw_button(self.screen, "Iniciar Juego", config.WIDTH//2 - 100, 470, 200, 40, config.GRAY)
        ui_components.draw_button(self.screen, "Salir", config.WIDTH//2 - 100, 540, 200, 40, config.RED)


    def draw_juego(self):
        # Fondo estrellado
        for i in range(50):
            x = (i * 89) % config.WIDTH
            y = (i * 101) % config.HEIGHT
            pygame.draw.circle(self.screen, (255, 255, 100), (x, y), 1)
        
        # Mostrar modo de juego
        if self.modo_juego == "Supervivencia":
            ui_components.draw_text(self.screen, f"SUPERVIVENCIA: {self.modo} - {self.dificultad}", 24, (255, 100, 100), 20, 20, "left")
        else:
            ui_components.draw_text(self.screen, f"Modo: {self.modo} - {self.dificultad}", 24, (255, 215, 0), 20, 20, "left")

        if self.solo:
            ui_components.draw_text(self.screen, f"Puntos: {self.scores[0]}", 24, (0, 255, 255), config.WIDTH//2, 20, "center")
            
            if self.modo_juego == "Supervivencia":
                minutos = int(self.tiempo_restante) // 60
                segundos = int(self.tiempo_restante) % 60
                tiempo_formateado = f"{minutos:02d}:{segundos:02d}"
                color_tiempo = config.GREEN if self.tiempo_restante > 30 else config.YELLOW if self.tiempo_restante > 10 else config.RED
                ui_components.draw_text(self.screen, f" {tiempo_formateado}", 24, color_tiempo, config.WIDTH-20, 20, "right")
            else:
                #  Mostrar tiempo en individual
                minutos = int(self.timer) // 60
                segundos = int(self.timer) % 60
                tiempo_formateado = f"{minutos:02d}:{segundos:02d}"
                ui_components.draw_text(self.screen, f"Tiempo: {tiempo_formateado}", 24, (255, 215, 0), config.WIDTH-20, 20, "right")

        else:
           #  MULTIJUGADOR: solo puntos y turno CON TEMPORIZADOR
            ui_components.draw_text(self.screen, f"Tus Puntos: {self.scores[0] if self.es_anfitrion else self.scores[1]}", 20, (0, 255, 255), 20, 50, "left")
            ui_components.draw_text(self.screen, f"Oponente: {self.scores[1] if self.es_anfitrion else self.scores[0]}", 18, (255, 165, 0), 20, 75, "left")
            #  TEMPORIZADOR DE TURNO VISIBLE SOLO AL JUGADOR CON TURNO ACTUAL
            if self.temporizador_turno_activo:
                # Determinar si es el turno del jugador actual
                jugador_actual = 0 if self.es_anfitrion else 1
                if self.turno == jugador_actual:
                    tiempo_restante = max(0, int(self.tiempo_turno_actual))
                    # Color según el tiempo restante
                    if tiempo_restante > 10:
                        color_tiempo = config.GREEN
                    elif tiempo_restante > 5:
                        color_tiempo = config.YELLOW
                    else:
                        color_tiempo = config.RED
                    
                    ui_components.draw_text(self.screen, f"⏳ {tiempo_restante}s", 22, color_tiempo, config.WIDTH-20, 20, "right")

            # Indicador de turno
            if self.es_anfitrion:
                if self.turno == 0:
                    ui_components.draw_text(self.screen, "¡TU TURNO!", 26, config.GREEN, config.WIDTH//2, 20, "center")
                    
                else:
                    ui_components.draw_text(self.screen, "Turno del Oponente", 22, config.RED, config.WIDTH//2, 20, "center")
            else:
                if self.turno == 1:
                    ui_components.draw_text(self.screen, "¡TU TURNO!", 26, config.GREEN, config.WIDTH//2, 20, "center")
                    
                else:
                    ui_components.draw_text(self.screen, "Turno del Oponente", 22, config.RED, config.WIDTH//2, 20, "center")

        # Dibujar cartas
        config_juego = config.DIFICULTAD_CONFIG[self.dificultad]
        cols = config_juego["cols"]
        rows = config_juego["rows"]
        size = min(config.WIDTH // cols, (config.HEIGHT - 100) // rows)
        grid_width = cols * size
        grid_height = rows * size
        start_x = (config.WIDTH - grid_width) // 2
        start_y = (config.HEIGHT - grid_height) // 2 + 25
        
        for i, card in enumerate(self.cartas):
            row = i // cols
            col = i % cols
            cx = start_x + col * size
            cy = start_y + row * size
            ui_components.draw_card(self.screen, card, cx, cy, size - 5, size - 5)
        
        # Botón salir
        ui_components.draw_button(self.screen, "Salir",  18, 720, 100, 40, color=config.RED)
        
        # Mostrar resultado final si el juego terminó
        if self.game_over and self.mostrar_resultado_final:
            self.draw_final_results()

    def draw_final_results(self):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 215, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        if self.solo:
            ui_components.draw_text(self.screen, "¡VICTORIA!", 48, (255, 0, 0), config.WIDTH//2, config.HEIGHT//2 - 50, "center")
            ui_components.draw_text(self.screen, "¡VICTORIA!", 48, (255, 255, 0), config.WIDTH//2 + 2, config.HEIGHT//2 - 48, "center")
            ui_components.draw_text(self.screen, f"Puntos: {self.scores[0]}", 36, (0, 255, 0), config.WIDTH//2, config.HEIGHT//2, "center")
            ui_components.draw_text(self.screen, f"Puntos: {self.scores[0]}", 36, (0, 0, 0), config.WIDTH//2 + 2, config.HEIGHT//2 + 2, "center")
            
            # TIEMPO - DIFERENTE SEGÚN EL MODO
            if self.modo_juego == "Supervivencia":
                if self.tiempo_restante <= 0:
                    ui_components.draw_text(self.screen, " Te quedaste sin tiempo!", 36, (255, 50, 50), config.WIDTH//2, config.HEIGHT//2 + 40, "center")
                    ui_components.draw_text(self.screen, " Te quedaste sin tiempo!", 36, (255, 0, 0), config.WIDTH//2 + 2, config.HEIGHT//2 + 42, "center")
                else:
                    tiempo_formateado = f"Tiempo restante: {int(self.tiempo_restante)}s"
                    ui_components.draw_text(self.screen, tiempo_formateado, 36, (0, 255, 255), config.WIDTH//2, config.HEIGHT//2 + 40, "center")
                    ui_components.draw_text(self.screen, tiempo_formateado, 36, (0, 0, 255), config.WIDTH//2 + 2, config.HEIGHT//2 + 42, "center")
            else:
                minutos = int(self.timer) // 60
                segundos = int(self.timer) % 60
                tiempo_formateado = f"{minutos:02d}:{segundos:02d}"
                ui_components.draw_text(self.screen, f"Tiempo: {tiempo_formateado}", 36, (0, 255, 255), config.WIDTH//2, config.HEIGHT//2 + 40, "center")
                ui_components.draw_text(self.screen, f"Tiempo: {tiempo_formateado}", 36, (0, 0, 255), config.WIDTH//2 + 2, config.HEIGHT//2 + 42, "center")

            if self.nuevo_record_puntos and self.nuevo_record_tiempo:
                ui_components.draw_text(self.screen, "¡DOBLE RÉCORD! Puntos y Tiempo", 32, (255, 215, 0), config.WIDTH//2, config.HEIGHT//2 + 80, "center")
                ui_components.draw_text(self.screen, "¡DOBLE RÉCORD! Puntos y Tiempo", 32, (255, 0, 0), config.WIDTH//2 + 2, config.HEIGHT//2 + 82, "center")
            elif self.nuevo_record_puntos:
                ui_components.draw_text(self.screen, "¡Nuevo Récord de Puntos!", 32, (255, 215, 0), config.WIDTH//2, config.HEIGHT//2 + 80, "center")
                ui_components.draw_text(self.screen, "¡Nuevo Récord de Puntos!", 32, (255, 0, 0), config.WIDTH//2 + 2, config.HEIGHT//2 + 82, "center")
            elif self.nuevo_record_tiempo:
                ui_components.draw_text(self.screen, "¡Nuevo Récord de Tiempo!", 32, (255, 215, 0), config.WIDTH//2, config.HEIGHT//2 + 80, "center")
                ui_components.draw_text(self.screen, "¡Nuevo Récord de Tiempo!", 32, (255, 0, 0), config.WIDTH//2 + 2, config.HEIGHT//2 + 82, "center")
                
        else:
            #   LÓGICA CONSISTENTE PARA MULTIJUGADOR
            ui_components.draw_text(self.screen, "¡Partida Terminada!", 48, (255, 0, 0), config.WIDTH//2, config.HEIGHT//2 - 50, "center")
            ui_components.draw_text(self.screen, "¡Partida Terminada!", 48, (255, 255, 0), config.WIDTH//2 + 2, config.HEIGHT//2 - 48, "center")
            
            #  USAR LA MISMA LÓGICA QUE EL SEGUNDO CÓDIGO
            if self.winner == 0:
                if self.es_anfitrion:
                    ui_components.draw_text(self.screen, "¡VICTORIA!", 42, config.GREEN, config.WIDTH//2, config.HEIGHT//2 - 30, "center")
                    ui_components.draw_text(self.screen, f"¡Has ganado contra {self.nombres[1]}!", 32, config.WHITE, config.WIDTH//2, config.HEIGHT//2 + 10, "center")
                else:
                    ui_components.draw_text(self.screen, "¡DERROTA!", 42, config.RED, config.WIDTH//2, config.HEIGHT//2 - 30, "center")
                    ui_components.draw_text(self.screen, f"{self.nombres[0]} ha ganado contra ti.", 32, config.WHITE, config.WIDTH//2, config.HEIGHT//2 + 10, "center")
            elif self.winner == 1:
                if self.es_anfitrion:
                    ui_components.draw_text(self.screen, "¡DERROTA!", 42, config.RED, config.WIDTH//2, config.HEIGHT//2 - 30, "center")
                    ui_components.draw_text(self.screen, f"{self.nombres[1]} ha ganado contra ti.", 32, config.WHITE, config.WIDTH//2, config.HEIGHT//2 + 10, "center")
                else:
                    ui_components.draw_text(self.screen, "¡VICTORIA!", 42, config.GREEN, config.WIDTH//2, config.HEIGHT//2 - 30, "center")
                    ui_components.draw_text(self.screen, f"¡Has ganado contra {self.nombres[0]}!", 32, config.WHITE, config.WIDTH//2, config.HEIGHT//2 + 10, "center")
            else:
                ui_components.draw_text(self.screen, "¡EMPATE!", 42, config.ORANGE, config.WIDTH//2, config.HEIGHT//2 - 30, "center")
                ui_components.draw_text(self.screen, "¡Ningún jugador gana!", 32, config.WHITE, config.WIDTH//2, config.HEIGHT//2 + 10, "center")
            
            ui_components.draw_text(self.screen, f"Marcador: {self.nombres[0]} ({self.scores[0]}) - ({self.scores[1]}) {self.nombres[1]}", 36, config.WHITE, config.WIDTH//2, config.HEIGHT//2 + 50, "center")
        
        tiempo_restante = 5 - (time.time() - self.tiempo_resultado)
        if tiempo_restante > 0:
            ui_components.draw_text(self.screen, f"Volviendo al menú en {int(tiempo_restante)}...", 24, (173, 216, 230), config.WIDTH//2, config.HEIGHT//2 + 100, "center")


    def handle_click(self, pos):
        try:
            # Si hay algún diálogo abierto, manejar solo ese diálogo
            if self.show_audio_dialog and hasattr(self, 'audio_dialog_elements'):  
                if self.handle_audio_dialog_click(pos, *self.audio_dialog_elements):
                    return
            
            if self.show_achievements_dialog:
                if self.handle_achievements_dialog_click(pos):
                    return
            
            if self.show_records_dialog:
                if self.handle_records_dialog_click(pos):
                    return
                    
            if self.show_modes_dialog:
                if self.handle_modes_dialog_click(pos):
                    return
                        
            if self.show_difficulty_dialog:
                if self.handle_difficulty_dialog_click(pos):
                    return
                        
            if self.show_join_dialog:
                if self.handle_join_dialog_click(pos):
                    return
            
            # MANEJAR CLICS EN TUTORIAL
            if self.mostrar_tutorial:
                if self.handle_tutorial_click(pos):
                    return
                        
            x, y = pos
            if self.state == "inicio":
                self.handle_inicio_click(pos)
            elif self.state == "sala":
                self.handle_sala_click(pos)
            elif self.state == "juego":
                self.handle_juego_click(pos)
        except Exception:
            pass


    def handle_inicio_click(self, pos):
        # Manejar botones de audio primero
        if hasattr(self, 'audio_buttons'):
            music_btn, sfx_btn = self.audio_buttons
            
            if music_btn.collidepoint(pos):
                self.toggle_music()
                return
                
            if sfx_btn.collidepoint(pos):
                self.toggle_sfx()
                return
        
        # Manejar diálogos abiertos
        if self.show_audio_dialog and hasattr(self, 'audio_dialog_elements'):
            if self.handle_audio_dialog_click(pos, *self.audio_dialog_elements):
                return
                
        if self.show_modes_dialog:
            self.handle_modes_dialog_click(pos)
            return
        elif self.show_difficulty_dialog:
            self.handle_difficulty_dialog_click(pos)
            return
        elif self.show_records_dialog:
            self.handle_records_dialog_click(pos)
            return
        elif self.show_join_dialog:
            self.handle_join_dialog_click(pos)
            return
        elif self.show_achievements_dialog:
            if self.handle_achievements_dialog_click(pos):
                return
                
        # Manejar edición de nombre
        if self.editing_name:
            dialog_rect = pygame.Rect(config.WIDTH//2 - 200, config.HEIGHT//2 - 100, 400, 200)
            input_rect = pygame.Rect(config.WIDTH//2 - 150, config.HEIGHT//2 - 20, 300, 40)
            if input_rect.collidepoint(pos):
                pass
            else:
                self.editing_name = False
                self.input_text = ""
            return

        # Manejar botones principales
        x, y = pos
        if config.WIDTH//2 - 150 <= x <= config.WIDTH//2 + 150:
            if 150 <= y <= 200:
                self.editing_name = True
                self.input_text = self.name
                if self.button_click_sound and self.sfx_enabled:
                    self.button_click_sound.play()
            elif 220 <= y <= 270:
                self.show_modes_dialog = True
                if self.button_click_sound and self.sfx_enabled:
                    self.button_click_sound.play()
            elif 290 <= y <= 340:
                self.show_difficulty_dialog = True
                if self.button_click_sound and self.sfx_enabled:
                    self.button_click_sound.play()
            elif 360 <= y <= 410:
                self.solo = True
                self.start_game()
                if self.button_click_sound and self.sfx_enabled:
                    self.button_click_sound.play()
            elif 430 <= y <= 480:
                self.solo = True
                self.iniciar_supervivencia()
                if self.button_click_sound and self.sfx_enabled:
                    self.button_click_sound.play()
            elif 500 <= y <= 550:
                self.solo = False
                self.crear_sala()
                if self.button_click_sound and self.sfx_enabled:
                    self.button_click_sound.play()
            elif 570 <= y <= 620:
                self.solo = False
                self.show_join_dialog = True
                self.input_text = ""
                if self.button_click_sound and self.sfx_enabled:
                    self.button_click_sound.play()
            elif 640 <= y <= 690:
                self.show_records_dialog = True
                if self.button_click_sound and self.sfx_enabled:
                    self.button_click_sound.play()
            elif 710 <= y <= 760:
                self.show_achievements_dialog = True
                if self.button_click_sound and self.sfx_enabled:
                    self.button_click_sound.play()



    def handle_join_dialog_click(self, pos):
        # Manejar clics en el diálogo de unirse a sala 
        x, y = pos
        
        # Área del diálogo
        dialog_rect = pygame.Rect(config.WIDTH//2 - 200, config.HEIGHT//2 - 120, 400, 240)
        
        # Si el clic está fuera, ignorar
        if not dialog_rect.collidepoint(pos):
            return False
        
        # Verificar clic en botón CONFIRMAR
        confirmar_rect = pygame.Rect(config.WIDTH//2 - 120, config.HEIGHT//2 + 50, 110, 40)
        if confirmar_rect.collidepoint(pos):
            if self.input_text.strip() != "" and len(self.input_text) == 4:
                self.show_join_dialog = False
                codigo = self.input_text
                self.input_text = ""
                self.unirse_sala_con_codigo(codigo)
            else:
                self.alerta("Código inválido. Debe tener 4 caracteres.")
            #  Audio de botón
            if self.button_click_sound:
                self.button_click_sound.play()
            return True
        
        # Verificar clic en botón CANCELAR
        cancelar_rect = pygame.Rect(config.WIDTH//2 + 10, config.HEIGHT//2 + 50, 110, 40)
        if cancelar_rect.collidepoint(pos):
            self.show_join_dialog = False
            self.input_text = ""
            # Audio de botón
            if self.button_click_sound:
                self.button_click_sound.play()
            return True
        
        # Verificar clic en el campo de texto 
        input_rect = pygame.Rect(config.WIDTH//2 - 100, config.HEIGHT//2 - 10, 200, 40)
        if input_rect.collidepoint(pos):
            return True
        
        # Clic en cualquier parte dentro del diálogo = bloquear
        return True
   
    def handle_achievements_dialog_click(self, pos):
        # Manejar clics en el diálogo de logros 
        x, y = pos
        # Botón cerrar
        if config.WIDTH//2 - 50 <= x <= config.WIDTH//2 + 50 and config.HEIGHT - 60 <= y <= config.HEIGHT - 20:
            self.show_achievements_dialog = False
            if self.button_click_sound:
                    self.play_sound(self.button_click_sound)
            return True
        return False

    def handle_sala_click(self, pos):
        x, y = pos
        if config.WIDTH//2 - 100 <= x <= config.WIDTH//2 + 100:
            if 400 <= y <= 440:
                self.dar_listo()
                #  Audio de botón
                if self.button_click_sound:
                    self.button_click_sound.play()
            elif 470 <= y <= 510 and self.es_anfitrion and self.ready and self.other_ready:
                self.start_game()
                #  Audio de botón
                if self.button_click_sound:
                    self.button_click_sound.play()
            elif 540 <= y <= 580:
                self.abandonar()
                #  Audio de botón
                if self.button_click_sound:
                    self.button_click_sound.play()


    def handle_juego_click(self, pos):
        x, y = pos
        # Verificar clic en botón Salir 
        if 18 <= x <= 118 and 720 <= y <= 760:
            self.confirmar_salida()
            #  Audio de botón
            if self.button_click_sound:
                self.button_click_sound.play()
        elif not self.game_over:
            self.click_juego(pos)



    def handle_records_dialog_click(self, pos):
        # Manejar clics en records 
        x, y = pos
        
        # Área del diálogo
        dialog_rect = pygame.Rect(config.WIDTH//2 - 300, config.HEIGHT//2 - 200, 600, 450)
        
        # Si el clic está fuera, ignorar
        if not dialog_rect.collidepoint(pos):
            return False
        
        botones_y = config.HEIGHT//2 + 150
        
        # Verificar clic en botón "Cerrar"
        if config.WIDTH//2 - 120 <= x <= config.WIDTH//2 - 20 and botones_y <= y <= botones_y + 40:
            self.show_records_dialog = False
            if self.button_click_sound:
                self.button_click_sound.play()
            return True
        
        # Verificar clic en botón "Borrar Récords"  
        elif config.WIDTH//2 + 20 <= x <= config.WIDTH//2 + 220 and botones_y <= y <= botones_y + 40:
            self.reset_highscores()
        
            if self.button_click_sound:
                self.button_click_sound.play()
            return True
        
        # Clic en cualquier parte dentro del diálogo = bloquear
        return True

    def handle_modes_dialog_click(self, pos):
        # Manejar clics en modos
        x, y = pos
        
        # Área del diálogo
        dialog_rect = pygame.Rect(config.WIDTH//2 - 200, config.HEIGHT//2 - 150, 400, 300)
        
        if not dialog_rect.collidepoint(pos):
            return False
            
        if config.WIDTH//2 - 150 <= x <= config.WIDTH//2 + 150:
            if config.HEIGHT//2 - 100 <= y <= config.HEIGHT//2 - 50:
                self.modo = "País-Capital"
                self.show_modes_dialog = False
        
                if self.button_click_sound:
                    self.button_click_sound.play()
                return True
            elif config.HEIGHT//2 - 30 <= y <= config.HEIGHT//2 + 20:
                self.modo = "Matemáticas"
                self.show_modes_dialog = False

                if self.button_click_sound:
                    self.button_click_sound.play()
                return True
            elif config.HEIGHT//2 + 40 <= y <= config.HEIGHT//2 + 90:
                self.modo = "Español-Inglés"
                self.show_modes_dialog = False
               
                if self.button_click_sound:
                    self.button_click_sound.play()
                return True
        
        if config.WIDTH//2 - 50 <= x <= config.WIDTH//2 + 50 and config.HEIGHT//2 + 110 <= y <= config.HEIGHT//2 + 150:
            self.show_modes_dialog = False
           
            if self.button_click_sound:
                self.button_click_sound.play()
            return True
        
        return True


    def handle_difficulty_dialog_click(self, pos):
        # Manejar clics en dificultad
        x, y = pos
        
        # Área del diálogo
        dialog_rect = pygame.Rect(config.WIDTH//2 - 200, config.HEIGHT//2 - 150, 400, 300)
        
        if not dialog_rect.collidepoint(pos):
            return False
            
        if config.WIDTH//2 - 150 <= x <= config.WIDTH//2 + 150:
            if config.HEIGHT//2 - 100 <= y <= config.HEIGHT//2 - 50:
                self.dificultad = "Fácil"
                self.show_difficulty_dialog = False
               
                if self.button_click_sound:
                    self.button_click_sound.play()
                return True
            elif config.HEIGHT//2 - 30 <= y <= config.HEIGHT//2 + 20:
                self.dificultad = "Medio"
                self.show_difficulty_dialog = False
               
                if self.button_click_sound:
                    self.button_click_sound.play()
                return True
            elif config.HEIGHT//2 + 40 <= y <= config.HEIGHT//2 + 90:
                self.dificultad = "Difícil"
                self.show_difficulty_dialog = False
              
                if self.button_click_sound:
                    self.button_click_sound.play()
                return True
        
        if config.WIDTH//2 - 50 <= x <= config.WIDTH//2 + 50 and config.HEIGHT//2 + 110 <= y <= config.HEIGHT//2 + 150:
            self.show_difficulty_dialog = False
            
            if self.button_click_sound:
                self.button_click_sound.play()
            return True
        
        return True


    def main_loop(self):
        music_check_timer = 0
        while self.running:
            # Calcular delta time
            current_time = time.time()
            if not hasattr(self, 'last_update_time'):
                self.last_update_time = current_time
            
            dt = current_time - self.last_update_time
            self.last_update_time = current_time
            
            #  Verificar estado de música cada 2 segundos
            music_check_timer += dt
            if music_check_timer > 2.0:
                self.check_music_state()
                music_check_timer = 0

            # Manejar eventos primero
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.server_thread and self.es_anfitrion:
                        print(" Cerrando servidor...")
                        self.server_thread.stop()
                        time.sleep(0.5)
                    self.running = False

                #debug de audio
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1:
                        self.debug_audio()
                        
                # Manejar scroll en logros
                if self.show_achievements_dialog:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 4:  # Scroll up
                            self.achievements_scroll_y = max(0, self.achievements_scroll_y - 50)
                        elif event.button == 5:  # Scroll down
                            self.achievements_scroll_y = min(self.achievements_scroll_max, self.achievements_scroll_y + 50)
                        elif event.button == 1: 
                            self.handle_click(event.pos)
                    
                    elif event.type == pygame.MOUSEBUTTONUP:
                        # arrastre de scroll
                        if event.button == 1: 
                            self.scroll_dragging = False
                    
                    elif event.type == pygame.MOUSEMOTION:
                        # Manejar arrastre de scroll
                        if self.scroll_dragging:
                            delta_y = event.pos[1] - self.scroll_start_y
                            
                            # Calcular área de contenido para el ratio
                            content_rect = pygame.Rect(70, 170, config.WIDTH - 140, config.HEIGHT - 250)
                            
                            # Convertir movimiento de píxeles a scroll
                            scroll_delta = (delta_y / content_rect.height) * self.achievements_scroll_max
                            new_scroll = self.scroll_start_value + scroll_delta
                            self.achievements_scroll_y = max(0, min(self.achievements_scroll_max, new_scroll))
                    
                    elif event.type == pygame.KEYDOWN:
                        # Teclas para scroll
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.achievements_scroll_y = max(0, self.achievements_scroll_y - 50)
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.achievements_scroll_y = min(self.achievements_scroll_max, self.achievements_scroll_y + 50)
                        elif event.key == pygame.K_PAGEUP:
                            self.achievements_scroll_y = max(0, self.achievements_scroll_y - 150)
                        elif event.key == pygame.K_PAGEDOWN:
                            self.achievements_scroll_y = min(self.achievements_scroll_max, self.achievements_scroll_y + 150)
                        elif event.key == pygame.K_HOME:
                            self.achievements_scroll_y = 0
                        elif event.key == pygame.K_END:
                            self.achievements_scroll_y = self.achievements_scroll_max
                else:
                    # Eventos normales cuando no hay diálogo de logros
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_click(event.pos)
                
                if event.type == pygame.KEYDOWN:
                    if self.show_achievements_dialog:
                        pass
                    elif self.mostrar_tutorial and event.key == pygame.K_RETURN:
                        self.completar_tutorial()
                        self.start_game()
                        if self.button_click_sound:
                            self.play_sound(self.button_click_sound)
                    elif self.editing_name:
                        if event.key == pygame.K_RETURN:
                            self.editing_name = False
                            if self.input_text.strip() != "":
                                self.name = validar_nombre(self.input_text)
                            self.input_text = ""
                        elif event.key == pygame.K_ESCAPE:
                            self.editing_name = False
                            self.input_text = ""
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            if len(self.input_text) < config.MAX_NAME_LENGTH:
                                self.input_text += event.unicode
                    elif self.show_join_dialog:
                        if event.key == pygame.K_RETURN:
                            if self.input_text.strip() != "":
                                self.show_join_dialog = False
                                self.unirse_sala_con_codigo(self.input_text)
                            self.input_text = ""
                            if self.button_click_sound:
                                 self.play_sound(self.button_click_sound)
                        elif event.key == pygame.K_ESCAPE:
                            self.show_join_dialog = False
                            self.input_text = ""
                            if self.button_click_sound:
                                  self.play_sound(self.button_click_sound)
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                            if self.button_click_sound:
                                self.play_sound(self.button_click_sound)
                        else:
                            if len(self.input_text) < 4:
                                self.input_text += event.unicode.upper()
                                if self.button_click_sound:
                                    self.play_sound(self.button_click_sound)
                    elif event.key == pygame.K_ESCAPE:
                        if self.show_achievements_dialog:
                            self.show_achievements_dialog = False
                            self.achievements_scroll_y = 0
                            if self.button_click_sound:
                                  self.play_sound(self.button_click_sound)
                        elif self.state == "juego":
                            self.confirmar_salida()
                        elif self.state == "sala":
                            self.abandonar()
                        else:
                            self.show_modes_dialog = False
                            self.show_difficulty_dialog = False
                            self.show_records_dialog = False
                            self.show_join_dialog = False

            # actualizar y dibujar
            self.update(dt)
            self.draw()
            self.clock.tick(config.FPS)
        
        #  Asegurar que el servidor se cierre al terminar el programa 
        if self.server_thread and self.es_anfitrion:
            print(" Cerrando servidor (fin del programa como anfitrión)...")
            self.server_thread.stop()
            time.sleep(0.5)
        
        pygame.quit()
        sys.exit()


    def determinar_ganador_multijugador(self, scores, es_anfitrion):
        
        #Calcula el ganador de forma CONSISTENTE para todas las dificultades  
        if not isinstance(scores, list) or len(scores) != 2:
            print(" Error: Puntuaciones inválidas")
            return 2  # Empate por defecto
        
        puntaje_anfitrion = scores[0]
        puntaje_invitado = scores[1]
        
        if puntaje_anfitrion > puntaje_invitado:
            ganador = 0  # Jugador 1 (anfitrión) gana
            print(f" Ganador: Anfitrión ({puntaje_anfitrion} vs {puntaje_invitado})")
        elif puntaje_invitado > puntaje_anfitrion:
            ganador = 1  # Jugador 2 (invitado) gana
            print(f" Ganador: Invitado ({puntaje_invitado} vs {puntaje_anfitrion})")
        else:
            ganador = 2  # Empate
            print(f" Empate ({puntaje_anfitrion} vs {puntaje_invitado})")
        
        return ganador



    def manejar_fin_partida_multijugador(self):
        
        # Maneja el fin de partida de forma CONSISTENTE para todas las dificultades
        
        print(" Manejo de fin de partida multijugador")
        
        #CALCULAR GANADOR 
        self.winner = self.determinar_ganador_multijugador(self.scores, self.es_anfitrion)
        
        # CONFIGURAR ESTADO DE FIN DE JUEGO
        self.game_over = True
        self.timer_active = False
        self.temporizador_turno_activo = False
        self.mostrar_resultado_final = True
        self.tiempo_resultado = time.time()
        
        #REGISTRAR LOGRO DE FINALIZACIÓN
        tiempo_final = self.timer
        victoria = (self.winner == 0 and self.es_anfitrion) or (self.winner == 1 and not self.es_anfitrion)
        self.achievement_manager.finalizar_partida(tiempo_final, victoria)
        
        print(f"{self.name}: Enviando estado final al servidor - Winner: {self.winner}")
        
        # ENVIAR ESTADO FINAL AL SERVIDOR
        success = self.send_to_server({
            "flipped": True,
            "cartas": [card.copy() for card in self.cartas],
            "turno": self.turno,
            "scores": self.scores,
            "game_over": True,
            "winner": self.winner
        })
        
        if success:
            print(" Estado final enviado al servidor correctamente")
        else:
            print(" Error enviando estado final, pero continuando...")
        
        #  REPRODUCIR SONIDO APROPIADO
        if victoria:
            if self.victory_sound:
                self.victory_sound.play()
            print(" Sonido de victoria reproducido")
        else:
            if self.game_over_sound:
                self.game_over_sound.play()
            print(" Sonido de derrota reproducido")

    def load_audio(self):
        # Cargar todos los archivos de audio 
        try:
            mixer.init()
            
            # Música de fondo   
            self.background_music = "sounds/background_music.mp3"
            
            # Efectos de sonido 
            sound_paths = {
                "card_flip": "sounds/card_flip.wav",
                "card_match": "sounds/card_match.wav", 
                "button_click": "sounds/button_click.wav",
                "victory": "sounds/victory.wav",
                "game_over": "sounds/game_over.wav"
            }
            
            # Cargar sonidos con verificación
            self.card_flip_sound = None
            self.card_match_sound = None
            self.button_click_sound = None
            self.victory_sound = None
            self.game_over_sound = None
            
            for sound_name, path in sound_paths.items():
                if os.path.exists(path):
                    try:
                        if sound_name == "card_flip":
                            self.card_flip_sound = mixer.Sound(path)
                        elif sound_name == "card_match":
                            self.card_match_sound = mixer.Sound(path)
                        elif sound_name == "button_click":
                            self.button_click_sound = mixer.Sound(path)
                        elif sound_name == "victory":
                            self.victory_sound = mixer.Sound(path)
                        elif sound_name == "game_over":
                            self.game_over_sound = mixer.Sound(path)
                        print(f" Sonido cargado: {path}")
                    except Exception as e:
                        print(f" Error cargando {path}: {e}")
                else:
                    print(f" Archivo no encontrado: {path}")
            
            #  CONFIGURAR VOLÚMENES INICIALES MÁS ALTOS
            if self.card_flip_sound:
                self.card_flip_sound.set_volume(1.0)
            if self.card_match_sound:
                self.card_match_sound.set_volume(1.0)
            if self.button_click_sound:
                self.button_click_sound.set_volume(0.5)
            if self.victory_sound:
                self.victory_sound.set_volume(1.0)
            if self.game_over_sound:
                self.game_over_sound.set_volume(1.0)
                
            print(" Audio cargado correctamente")
            print(f" Música enabled: {self.music_enabled}, Volumen: {self.music_volume}")
            print(f" SFX enabled: {self.sfx_enabled}, Volumen: {self.sfx_volume}")
            
        except Exception as e:
            print(f" Error crítico en load_audio: {e}")
            # Sonidos por defecto
            self.card_flip_sound = None
            self.card_match_sound = None
            self.button_click_sound = None
            self.victory_sound = None
            self.game_over_sound = None

    def play_background_music(self):
        # Reproducir música de fondo 
        try:
            if not self.music_enabled:
                print(" Música desactivada - no se reproduce")
                return
                
            if os.path.exists("sounds/background_music.mp3"):
                # Solo cargar y reproducir
                if not mixer.music.get_busy():
                    mixer.music.load("sounds/background_music.mp3")
                    mixer.music.set_volume(self.music_volume)
                    mixer.music.play(-1)
                    print(f" Música de fondo INICIADA - Volumen: {self.music_volume}")
                else:
                    print(" Música ya está reproduciéndose")
            else:
                print(" Archivo de música no encontrado")
        except Exception as e:
            print(f" Error en play_background_music: {e}")       


    def play_sound(self, sound):
        # Reproducir efecto de sonido si está habilitado 
        if not self.sfx_enabled:
            return
            
        if sound:
            try:
                # Usar el volumen configurado
                sound.set_volume(self.sfx_volume)
                sound.play()
                print(f" Sonido reproducido (vol: {self.sfx_volume})")
            except Exception as e:
                print(f" Error reproduciendo sonido: {e}")

    def stop_background_music(self):
        # Detener música de fondo
        try:
            mixer.music.stop()
        except:
            pass

    def set_music_volume(self, volume):
        try:
            mixer.music.set_volume(max(0.0, min(1.0, volume)))
        except:
            pass

    def set_sfx_volume(self, volume):
        try:
            volume = max(0.0, min(1.0, volume))
            if self.card_flip_sound:
                self.card_flip_sound.set_volume(volume * 0.7)
            if self.card_match_sound:
                self.card_match_sound.set_volume(volume * 0.8)
            if self.button_click_sound:
                self.button_click_sound.set_volume(volume * 0.5)
        except:
            pass


    def draw_audio_buttons(self):
        # Botón de Música 
        music_color = config.GREEN if self.music_enabled else config.RED
        music_text = "MUSICA: ON" if self.music_enabled else "MUSICA: OFF"
        music_btn = pygame.Rect(config.WIDTH - 120, 20, 110, 25) 
        pygame.draw.rect(self.screen, music_color, music_btn, border_radius=6)
        pygame.draw.rect(self.screen, (255, 255, 255), music_btn, 2, border_radius=6)
        
        # Texto centrado
        ui_components.draw_text(self.screen, music_text, 12, config.BLACK, config.WIDTH - 65, 32, "center")
        
        # Botón de Efectos
        sfx_color = config.GREEN if self.sfx_enabled else config.RED
        sfx_text = "SONIDO: ON" if self.sfx_enabled else "SONIDO: OFF"
        sfx_btn = pygame.Rect(config.WIDTH - 120, 50, 110, 25)  
        pygame.draw.rect(self.screen, sfx_color, sfx_btn, border_radius=6)
        pygame.draw.rect(self.screen, (255, 255, 255), sfx_btn, 2, border_radius=6)
        
        # Texto centrado
        ui_components.draw_text(self.screen, sfx_text, 12, config.BLACK, config.WIDTH - 65, 62, "center")
        
        return music_btn, sfx_btn


    def toggle_music(self):
        """Alternar estado de la MÚSICA (solo música de fondo)"""
        self.music_enabled = not self.music_enabled
        print(f" Música: {'ON' if self.music_enabled else 'OFF'}")
        
        if self.music_enabled:
            self.play_background_music()
        else:
            mixer.music.stop()
        
        # Reproducir sonido de confirmación (si los efectos están activados)
        if self.button_click_sound and self.sfx_enabled:
            self.button_click_sound.play()
    
    def toggle_sound(self):
        #Alternar estado de los EFECTOS DE SONIDO 
        self.sfx_enabled = not self.sfx_enabled
        print(f" Efectos de sonido: {'ON' if self.sfx_enabled else 'OFF'}")
        
        # Reproducir sonido de confirmación
        if self.button_click_sound and self.sfx_enabled:
            self.button_click_sound.play()

    def toggle_sfx(self):
        #Alternar estado de efectos de sonido
        self.sfx_enabled = not self.sfx_enabled
        print(f" Efectos: {'ON' if self.sfx_enabled else 'OFF'}")
        # Reproducir sonido de confirmación
        if self.button_click_sound and self.sfx_enabled:
            self.button_click_sound.play()

    def draw_audio_dialog(self):
        #Dibujar diálogo completo de configuración de audio
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        dialog_rect = pygame.Rect(config.WIDTH//2 - 200, config.HEIGHT//2 - 150, 400, 350)
        pygame.draw.rect(self.screen, config.DIALOG_BG, dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 215, 0), dialog_rect, 3, border_radius=15)
        
        ui_components.draw_text(self.screen, "CONFIGURACIÓN DE AUDIO", 32, (255, 255, 0), 
                            config.WIDTH//2, config.HEIGHT//2 - 120, "center")
        
        # Botón de Música
        music_color = config.GREEN if self.music_enabled else config.RED
        music_text = " MÚSICA: ON" if self.music_enabled else " MÚSICA: OFF"
        music_btn = ui_components.draw_button(self.screen, music_text, 
                                            config.WIDTH//2 - 150, config.HEIGHT//2 - 70, 
                                            300, 50, music_color)
        
        # Barra de volumen de música
        ui_components.draw_text(self.screen, f"Volumen Música: {int(self.music_volume * 100)}%", 
                            20, config.WHITE, config.WIDTH//2, config.HEIGHT//2 - 10, "center")
        music_slider = pygame.Rect(config.WIDTH//2 - 100, config.HEIGHT//2 + 10, 200, 20)
        pygame.draw.rect(self.screen, (100, 100, 100), music_slider, border_radius=10)
        music_fill = pygame.Rect(config.WIDTH//2 - 100, config.HEIGHT//2 + 10, 
                            int(200 * self.music_volume), 20)
        pygame.draw.rect(self.screen, (0, 200, 0), music_fill, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), music_slider, 2, border_radius=10)
        
        # Botón de Efectos
        sfx_color = config.GREEN if self.sfx_enabled else config.RED
        sfx_text = " EFECTOS: ON" if self.sfx_enabled else " EFECTOS: OFF"
        sfx_btn = ui_components.draw_button(self.screen, sfx_text, 
                                        config.WIDTH//2 - 150, config.HEIGHT//2 + 50, 
                                        300, 50, sfx_color)
        
        # Barra de volumen de efectos
        ui_components.draw_text(self.screen, f"Volumen Efectos: {int(self.sfx_volume * 100)}%", 
                            20, config.WHITE, config.WIDTH//2, config.HEIGHT//2 + 110, "center")
        sfx_slider = pygame.Rect(config.WIDTH//2 - 100, config.HEIGHT//2 + 130, 200, 20)
        pygame.draw.rect(self.screen, (100, 100, 100), sfx_slider, border_radius=10)
        sfx_fill = pygame.Rect(config.WIDTH//2 - 100, config.HEIGHT//2 + 130, 
                            int(200 * self.sfx_volume), 20)
        pygame.draw.rect(self.screen, (0, 100, 200), sfx_fill, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), sfx_slider, 2, border_radius=10)
        
        # Botón de prueba de sonido
        test_btn = ui_components.draw_button(self.screen, " PROBAR SONIDO", 
                                        config.WIDTH//2 - 100, config.HEIGHT//2 + 170, 
                                        200, 40, config.BLUE)
        
        # Botón cerrar
        close_btn = ui_components.draw_button(self.screen, "CERRAR", 
                                            config.WIDTH//2 - 50, config.HEIGHT//2 + 220, 
                                            100, 40, config.RED)
        
        return music_btn, music_slider, sfx_btn, sfx_slider, test_btn, close_btn

    def handle_audio_dialog_click(self, pos, music_btn, music_slider, sfx_btn, sfx_slider, test_btn, close_btn):
        # Manejar clics en el diálogo de audio
        x, y = pos
        
        if close_btn.collidepoint(pos):
            self.show_audio_dialog = False
            if self.button_click_sound and self.sfx_enabled:
                self.button_click_sound.play()
            return True
        
        if music_btn.collidepoint(pos):
            self.toggle_music()
            return True
        
        if sfx_btn.collidepoint(pos):
            self.toggle_sfx()
            return True
        
        if test_btn.collidepoint(pos):
            # Probar sonido
            if self.card_flip_sound and self.sfx_enabled:
                self.card_flip_sound.set_volume(self.sfx_volume)
                self.card_flip_sound.play()
            return True
        
        # Manejar sliders de volumen
        if music_slider.collidepoint(pos):
            rel_x = x - music_slider.x
            self.music_volume = max(0.0, min(1.0, rel_x / music_slider.width))
            mixer.music.set_volume(self.music_volume)
            return True
        
        if sfx_slider.collidepoint(pos):
            rel_x = x - sfx_slider.x
            self.sfx_volume = max(0.0, min(1.0, rel_x / sfx_slider.width))
            return True
        
        return False
    

    def debug_audio(self):
        #Función para debug del audio
        print("\n DEBUG DE AUDIO ")
        print(f" Música: {self.music_enabled}, Volumen: {self.music_volume}")
        print(f" SFX: {self.sfx_enabled}, Volumen: {self.sfx_volume}")
        print(f" Mixer init: {mixer.get_init()}")
        print(f" Sonidos cargados:")
        print(f"  - Flip: {self.card_flip_sound is not None}")
        print(f"  - Match: {self.card_match_sound is not None}") 
        print(f"  - Click: {self.button_click_sound is not None}")
        print(f"  - Victory: {self.victory_sound is not None}")
        print(f"  - Game Over: {self.game_over_sound is not None}")
        
        # Probar reproducción forzada
        if self.card_flip_sound:
            print(" Probando sonido de flip...")
            self.card_flip_sound.play()



    def check_music_state(self):
        """Verificar y corregir el estado de la música"""
        if self.music_enabled and not mixer.music.get_busy():
            print(" Corrigiendo estado de música: debería estar sonando")
            self.play_background_music()
        elif not self.music_enabled and mixer.music.get_busy():
            print(" Corrigiendo estado de música: debería estar silenciada")
            mixer.music.stop()