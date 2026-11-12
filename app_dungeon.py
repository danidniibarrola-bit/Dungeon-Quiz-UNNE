import streamlit as st
import mysql.connector
from mysql.connector import Error

# Configuración de página
st.set_page_config(page_title="Dungeon Quiz - UNNE", page_icon="⚔️", layout="centered")

# -----------------------------------------------------------------------------
# FUNCIÓN DE CONEXIÓN A LA BASE DE DATOS
# -----------------------------------------------------------------------------
def get_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='dungeon_quiz',
            autocommit=True  # Evita choques de lectura previa con start_transaction()
        )
        return connection
    except Error as e:
        st.error(f"Error crítico al conectar con MySQL: {e}")
        return None

# -----------------------------------------------------------------------------
# INICIALIZACIÓN Y LIMPIEZA DE ESTADOS (Session State)
# -----------------------------------------------------------------------------
def inicializar_sesion():
    variables_base = {
        'id_jugador': None, 'nombre_jugador': "", 'id_partida': None,
        'pregunta_actual': None, 'opciones_actuales': [],
        'respuestas_correctas': 0, 'estado_juego': "REGISTRO",
        'turno_respondido': False, 'mensaje_resultado': None, 'tipo_mensaje': None
    }
    for key, val in variables_base.items():
        if key not in st.session_state:
            st.session_state[key] = val

def resetear_estado_partida():
    """Limpia la memoria caché para evitar arrastrar errores o carteles a nuevas partidas."""
    st.session_state.pregunta_actual = None
    st.session_state.opciones_actuales = []
    st.session_state.respuestas_correctas = 0
    st.session_state.turno_respondido = False
    st.session_state.mensaje_resultado = None
    st.session_state.tipo_mensaje = None

inicializar_sesion()

# -----------------------------------------------------------------------------
# PANTALLA 1: REGISTRO / SELECCIÓN DE JUGADOR
# -----------------------------------------------------------------------------
st.title("⚔️ Dungeon Quiz RPG")

if st.session_state.estado_juego == "REGISTRO":
    st.subheader("Paso 1: Identificación del Héroe")
    
    conn = get_connection()
    jugadores_existentes = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_jugador, nombre, experiencia FROM jugador ORDER BY nombre")
        jugadores_existentes = cursor.fetchall()
        cursor.close()
        conn.close()

    opcion_ingreso = st.radio("¿Cómo deseas ingresar?", ["Seleccionar Jugador Existente", "Crear Nuevo Jugador"])
    
    # OPCIÓN A: JUGADOR EXISTENTE
    if opcion_ingreso == "Seleccionar Jugador Existente" and jugadores_existentes:
        dict_jugadores = {f"{j['nombre']} (Exp: {j['experiencia']})": j for j in jugadores_existentes}
        seleccion = st.selectbox("Elegí tu Héroe:", list(dict_jugadores.keys()))
        
        if st.button("Iniciar Partida con Héroe Elegido"):
            j_sel = dict_jugadores[seleccion]
            st.session_state.id_jugador = j_sel['id_jugador']
            st.session_state.nombre_jugador = j_sel['nombre']
            
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                
                # CORRECCIÓN 2: Restaurar salud al 100% ANTES de iniciar
                cursor.execute("UPDATE jugador SET vida = 100 WHERE id_jugador = %s", (st.session_state.id_jugador,))
                
                # Crear partida
                cursor.execute("INSERT INTO partida (id_jugador, resultado) VALUES (%s, 'En Progreso')", (st.session_state.id_jugador,))
                conn.commit()
                st.session_state.id_partida = cursor.lastrowid
                
                cursor.close()
                conn.close()
                
                resetear_estado_partida()
                st.session_state.estado_juego = "JUGANDO"
                st.rerun()

    # OPCIÓN B: JUGADOR NUEVO
    else:
        nuevo_nombre = st.text_input("Nombre de tu Héroe:")
        if st.button("Crear Héroe e Iniciar"):
            if nuevo_nombre.strip():
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO jugador (nombre, vida, experiencia) VALUES (%s, 100, 0)", (nuevo_nombre.strip(),))
                        st.session_state.id_jugador = cursor.lastrowid
                        st.session_state.nombre_jugador = nuevo_nombre.strip()
                        
                        cursor.execute("INSERT INTO partida (id_jugador, resultado) VALUES (%s, 'En Progreso')", (st.session_state.id_jugador,))
                        conn.commit()
                        st.session_state.id_partida = cursor.lastrowid
                        
                        resetear_estado_partida()
                        st.session_state.estado_juego = "JUGANDO"
                        st.rerun()
                    except Error as err:
                        st.error(f"El nombre de héroe ya existe o hubo un error: {err}")
                    finally:
                        # CORRECCIÓN 3: Cierre seguro de conexiones para evitar fugas (Memory Leak)
                        cursor.close()
                        conn.close()

# -----------------------------------------------------------------------------
# PANTALLA 2: MAZMORRA Y PREGUNTAS (TRANSACCIONES ATÓMICAS)
# -----------------------------------------------------------------------------
elif st.session_state.estado_juego == "JUGANDO":
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Traer status actual
    cursor.execute("SELECT vida, experiencia FROM jugador WHERE id_jugador = %s", (st.session_state.id_jugador,))
    datos_jugador = cursor.fetchone()
    vida_actual = datos_jugador['vida']
    exp_actual = datos_jugador['experiencia']
    
    st.sidebar.markdown(f"### 🛡️ Estado del Héroe")
    st.sidebar.markdown(f"**Jugador:** {st.session_state.nombre_jugador}")
    st.sidebar.markdown(f"**Vida:** ❤️ {vida_actual} / 100")
    st.sidebar.markdown(f"**Experiencia:** ⭐ {exp_actual}")
    st.sidebar.markdown(f"**Aciertos en la partida:** 🎯 {st.session_state.respuestas_correctas} / 5")
    
    # 2. Control de Fin de Partida
    if vida_actual <= 0:
        cursor.execute("UPDATE partida SET resultado = 'Derrota' WHERE id_partida = %s", (st.session_state.id_partida,))
        conn.commit()
        cursor.close()
        conn.close()
        st.session_state.estado_juego = "GAMEOVER"
        st.rerun()
    elif st.session_state.respuestas_correctas >= 5:
        cursor.execute("UPDATE partida SET resultado = 'Victoria' WHERE id_partida = %s", (st.session_state.id_partida,))
        conn.commit()
        cursor.close()
        conn.close()
        st.session_state.estado_juego = "GAMEOVER"
        st.rerun()

    # 3. Preparar el turno actual (Anti-repetir preguntas)
    if st.session_state.pregunta_actual is None:
        query_pregunta = """
            SELECT p.id_pregunta, p.enunciado, c.nombre_categoria, m.nombre AS monstruo, m.dano_base
            FROM pregunta p
            JOIN categoria c ON p.id_categoria = c.id_categoria
            JOIN monstruo m ON p.id_monstruo = m.id_monstruo
            WHERE p.id_pregunta NOT IN (
                SELECT id_pregunta FROM detalle_partida WHERE id_partida = %s
            )
            ORDER BY RAND() LIMIT 1
        """
        cursor.execute(query_pregunta, (st.session_state.id_partida,))
        st.session_state.pregunta_actual = cursor.fetchone()
        
        if st.session_state.pregunta_actual:
            cursor.execute("SELECT id_respuesta, texto_opcion, es_correcta FROM respuesta WHERE id_pregunta = %s ORDER BY RAND()", 
                           (st.session_state.pregunta_actual['id_pregunta'],))
            st.session_state.opciones_actuales = cursor.fetchall()

    preg = st.session_state.pregunta_actual
    if preg:
        st.markdown(f"### 👾 ¡Te enfrentas a: **{preg['monstruo']}**!")
        st.info(f"**Categoría:** {preg['nombre_categoria']} | **Daño por fallo:** {preg['dano_base']} HP")
        st.write(f"**Consigna:** {preg['enunciado']}")
        
        # 4. Turno Activo (Esperando respuesta)
        if not st.session_state.turno_respondido:
            dict_opciones = {opc['texto_opcion']: opc for opc in st.session_state.opciones_actuales}
            eleccion = st.radio("Seleccioná la respuesta correcta:", list(dict_opciones.keys()))
            
            if st.button("Responder y Atacar ⚔️"):
                opc_elegida = dict_opciones[eleccion]
                es_correcta = opc_elegida['es_correcta']
                
                try:
                    conn.start_transaction()
                    
                    cursor.execute("""
                        INSERT INTO detalle_partida (id_partida, id_pregunta, id_respuesta_elegida, fue_correcta)
                        VALUES (%s, %s, %s, %s)
                    """, (st.session_state.id_partida, preg['id_pregunta'], opc_elegida['id_respuesta'], es_correcta))
                    
                    if es_correcta:
                        cursor.execute("UPDATE jugador SET experiencia = experiencia + 20 WHERE id_jugador = %s", (st.session_state.id_jugador,))
                        cursor.execute("UPDATE partida SET puntaje_total = puntaje_total + 20 WHERE id_partida = %s", (st.session_state.id_partida,))
                        st.session_state.respuestas_correctas += 1
                        st.session_state.tipo_mensaje = "success"
                        st.session_state.mensaje_resultado = "¡Respuesta Correcta! Has derrotado al enemigo y sumaste +20 de Experiencia."
                    else:
                        dano = preg['dano_base']
                        # GREATEST apoya la Regla CHECK(vida>=0) desde Python de forma visual
                        cursor.execute("UPDATE jugador SET vida = GREATEST(0, vida - %s) WHERE id_jugador = %s", (dano, st.session_state.id_jugador))
                        st.session_state.tipo_mensaje = "error"
                        st.session_state.mensaje_resultado = f"¡Respuesta Incorrecta! El monstruo te infligió {dano} puntos de daño."

                    conn.commit()
                    
                except Error as e:
                    conn.rollback()
                    st.session_state.tipo_mensaje = "error"
                    st.session_state.mensaje_resultado = f"Error en transacción. Se ejecutó ROLLBACK: {e}"

                st.session_state.turno_respondido = True
                cursor.close()
                conn.close()
                st.rerun()
                
        # 5. Post-Turno (Viendo resultados)
        else:
            if st.session_state.tipo_mensaje == "success":
                st.success(st.session_state.mensaje_resultado)
            else:
                st.error(st.session_state.mensaje_resultado)
                
            if st.button("Siguiente Pregunta ➡️"):
                st.session_state.pregunta_actual = None
                st.session_state.opciones_actuales = []
                st.session_state.turno_respondido = False
                cursor.close()
                conn.close()
                st.rerun()

# -----------------------------------------------------------------------------
# PANTALLA 3: FIN DE PARTIDA Y TABLA DE CLASIFICACIÓN
# -----------------------------------------------------------------------------
elif st.session_state.estado_juego == "GAMEOVER":
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # CORRECCIÓN 1: Devolver el SELECT correcto para leer el estado de la partida
        cursor.execute("SELECT resultado FROM partida WHERE id_partida = %s", (st.session_state.id_partida,))
        res = cursor.fetchone()
        
        if res and res['resultado'] == 'Victoria':
            st.balloons()
            st.success("🎉 ¡VICTORIA! Has superado la mazmorra de Dungeon Quiz.")
        else:
            st.error("☠️ GAME OVER. Tus Puntos de Vida han llegado a 0.")
            
        st.subheader("🏆 Tabla de Clasificación de Héroes (Vista SQL)")
        cursor.execute("SELECT * FROM vista_leaderboard")
        leaderboard = cursor.fetchall()
        st.table(leaderboard)
        
        cursor.close()
        conn.close()
    
    if st.button("Volver a Jugar / Cambiar Héroe"):
        st.session_state.estado_juego = "REGISTRO"
        st.session_state.id_jugador = None
        st.session_state.id_partida = None
        # CORRECCIÓN 4: Uso de la función para limpiar el 100% de la basura de caché
        resetear_estado_partida()
        st.rerun()