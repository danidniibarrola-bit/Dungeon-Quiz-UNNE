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


def cerrar_conexion(conn, cursor=None):
    """Cierra cursor y conexión sin romper la app si ya estaban cerrados."""
    if cursor is not None:
        try:
            cursor.close()
        except Exception:
            pass
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass

# -----------------------------------------------------------------------------
# INICIALIZACIÓN Y LIMPIEZA DE ESTADOS (Session State)
# -----------------------------------------------------------------------------
def inicializar_sesion():
    variables_base = {
        'id_jugador': None, 'nombre_jugador': "", 'id_partida': None,
        'pregunta_actual': None, 'opciones_actuales': [],
        'respuestas_correctas': 0, 'estado_juego': "REGISTRO",
        'turno_respondido': False, 'mensaje_resultado': None,
        'tipo_mensaje': None, 'error_turno': None
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
    st.session_state.error_turno = None


inicializar_sesion()

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES DE BASE DE DATOS
# -----------------------------------------------------------------------------
def obtener_estado_jugador(id_jugador):
    """Devuelve (datos, error). datos = {vida, experiencia} o None."""
    conn = get_connection()
    if conn is None:
        return None, "No hay conexión con la base de datos."

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT vida, experiencia FROM jugador WHERE id_jugador = %s",
            (id_jugador,)
        )
        return cursor.fetchone(), None
    except Error as e:
        return None, f"No se pudo leer el estado del jugador: {e}"
    finally:
        cerrar_conexion(conn, cursor)


def cargar_pregunta(id_jugador):
    """
    Elige una pregunta que el jugador no haya respondido nunca.
    Devuelve (pregunta, opciones, error).
    Si el jugador ya respondió las 60, devuelve (None, [], None).
    """
    conn = get_connection()
    if conn is None:
        return None, [], "No hay conexión con la base de datos."

    cursor = conn.cursor(dictionary=True)
    try:
        # Anti-repetición por jugador: excluye preguntas respondidas en
        # cualquier partida anterior, no solo en la partida actual.
        cursor.execute("""
            SELECT p.id_pregunta, p.enunciado, c.nombre_categoria,
                   m.nombre AS monstruo, m.dano_base
            FROM pregunta p
            JOIN categoria c ON p.id_categoria = c.id_categoria
            JOIN monstruo m ON p.id_monstruo = m.id_monstruo
            WHERE p.id_pregunta NOT IN (
                SELECT dp.id_pregunta
                FROM detalle_partida dp
                JOIN partida pa ON pa.id_partida = dp.id_partida
                WHERE pa.id_jugador = %s
            )
            ORDER BY RAND() LIMIT 1
        """, (id_jugador,))

        pregunta = cursor.fetchone()
        if pregunta is None:
            return None, [], None

        cursor.execute("""
            SELECT id_respuesta, texto_opcion, es_correcta
            FROM respuesta
            WHERE id_pregunta = %s
            ORDER BY RAND()
        """, (pregunta['id_pregunta'],))

        return pregunta, cursor.fetchall(), None
    except Error as e:
        return None, [], f"No se pudo cargar la pregunta: {e}"
    finally:
        cerrar_conexion(conn, cursor)


def finalizar_partida(id_partida, resultado):
    """Marca la partida como Victoria o Derrota. Devuelve (ok, error)."""
    conn = get_connection()
    if conn is None:
        return False, "No hay conexión con la base de datos."

    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE partida SET resultado = %s WHERE id_partida = %s",
            (resultado, id_partida)
        )
        conn.commit()
        return True, None
    except Error as e:
        try:
            conn.rollback()
        except Error:
            pass
        return False, f"No se pudo guardar el resultado de la partida: {e}"
    finally:
        cerrar_conexion(conn, cursor)


def comprobar_respuesta_guardada(id_partida, id_pregunta):
    """
    Verifica que la respuesta de la pregunta actual quedó registrada.
    Devuelve (guardada, error).
    """
    conn = get_connection()
    if conn is None:
        return False, "No hay conexión con la base de datos."

    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 1
            FROM detalle_partida
            WHERE id_partida = %s AND id_pregunta = %s
        """, (id_partida, id_pregunta))
        return cursor.fetchone() is not None, None
    except Error as e:
        return False, f"No se pudo verificar la respuesta guardada: {e}"
    finally:
        cerrar_conexion(conn, cursor)

# -----------------------------------------------------------------------------
# PANTALLA 1: REGISTRO / SELECCIÓN DE JUGADOR
# -----------------------------------------------------------------------------
st.title("⚔️ Dungeon Quiz RPG")

if st.session_state.estado_juego == "REGISTRO":
    st.subheader("Paso 1: Identificación del Héroe")

    conn = get_connection()
    if conn is None:
        st.stop()

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_jugador, nombre, experiencia FROM jugador ORDER BY nombre")
        jugadores_existentes = cursor.fetchall()
    except Error as e:
        st.error(f"No se pudo cargar la lista de jugadores: {e}")
        st.stop()
    finally:
        cerrar_conexion(conn, cursor)

    opcion_ingreso = st.radio(
        "¿Cómo deseas ingresar?",
        ["Seleccionar Jugador Existente", "Crear Nuevo Jugador"]
    )

    # OPCIÓN A: JUGADOR EXISTENTE
    if opcion_ingreso == "Seleccionar Jugador Existente" and jugadores_existentes:
        dict_jugadores = {
            f"{j['nombre']} (Exp: {j['experiencia']})": j
            for j in jugadores_existentes
        }
        seleccion = st.selectbox("Elegí tu Héroe:", list(dict_jugadores.keys()))

        if st.button("Iniciar Partida con Héroe Elegido"):
            j_sel = dict_jugadores[seleccion]

            conn = get_connection()
            if conn is None:
                st.stop()

            cursor = conn.cursor()
            nuevo_id_partida = None
            error_inicio = None
            try:
                conn.start_transaction()

                # Restaurar salud al 100% antes de iniciar la nueva partida
                cursor.execute(
                    "UPDATE jugador SET vida = 100 WHERE id_jugador = %s",
                    (j_sel['id_jugador'],)
                )

                # Crear partida
                cursor.execute(
                    "INSERT INTO partida (id_jugador, resultado) VALUES (%s, 'En Progreso')",
                    (j_sel['id_jugador'],)
                )
                nuevo_id_partida = cursor.lastrowid
                conn.commit()
            except Error as e:
                try:
                    conn.rollback()
                except Error:
                    pass
                error_inicio = str(e)
            finally:
                cerrar_conexion(conn, cursor)

            if error_inicio:
                st.error(f"No se pudo iniciar la partida: {error_inicio}")
                st.stop()

            st.session_state.id_jugador = j_sel['id_jugador']
            st.session_state.nombre_jugador = j_sel['nombre']
            st.session_state.id_partida = nuevo_id_partida
            resetear_estado_partida()
            st.session_state.estado_juego = "JUGANDO"
            st.rerun()

    # OPCIÓN B: JUGADOR NUEVO
    else:
        nuevo_nombre = st.text_input("Nombre de tu Héroe:")
        if st.button("Crear Héroe e Iniciar"):
            if not nuevo_nombre.strip():
                st.warning("Ingresá un nombre para tu héroe.")
            else:
                conn = get_connection()
                if conn is None:
                    st.stop()

                cursor = conn.cursor()
                nuevo_id_jugador = None
                nuevo_id_partida = None
                error_creacion = None
                try:
                    conn.start_transaction()

                    cursor.execute(
                        "INSERT INTO jugador (nombre, vida, experiencia) VALUES (%s, 100, 0)",
                        (nuevo_nombre.strip(),)
                    )
                    nuevo_id_jugador = cursor.lastrowid

                    cursor.execute(
                        "INSERT INTO partida (id_jugador, resultado) VALUES (%s, 'En Progreso')",
                        (nuevo_id_jugador,)
                    )
                    nuevo_id_partida = cursor.lastrowid
                    conn.commit()
                except Error as err:
                    try:
                        conn.rollback()
                    except Error:
                        pass
                    error_creacion = str(err)
                finally:
                    cerrar_conexion(conn, cursor)

                if error_creacion:
                    st.error(f"El nombre de héroe ya existe o hubo un error: {error_creacion}")
                else:
                    st.session_state.id_jugador = nuevo_id_jugador
                    st.session_state.nombre_jugador = nuevo_nombre.strip()
                    st.session_state.id_partida = nuevo_id_partida
                    resetear_estado_partida()
                    st.session_state.estado_juego = "JUGANDO"
                    st.rerun()

# -----------------------------------------------------------------------------
# PANTALLA 2: MAZMORRA Y PREGUNTAS (TRANSACCIONES ATÓMICAS)
# -----------------------------------------------------------------------------
elif st.session_state.estado_juego == "JUGANDO":
    # 1. Traer status actual (conexión abierta solo para leer y cerrar)
    datos_jugador, error_estado = obtener_estado_jugador(st.session_state.id_jugador)
    if error_estado:
        st.error(error_estado)
        st.stop()
    if not datos_jugador:
        st.error("No se encontró el jugador de la partida actual.")
        st.session_state.estado_juego = "REGISTRO"
        st.rerun()

    vida_actual = datos_jugador['vida']
    exp_actual = datos_jugador['experiencia']

    st.sidebar.markdown("### 🛡️ Estado del Héroe")
    st.sidebar.markdown(f"**Jugador:** {st.session_state.nombre_jugador}")
    st.sidebar.markdown(f"**Vida:** ❤️ {vida_actual} / 100")
    st.sidebar.markdown(f"**Experiencia:** ⭐ {exp_actual}")
    st.sidebar.markdown(f"**Aciertos en la partida:** 🎯 {st.session_state.respuestas_correctas} / 5")

    # 2. Control de Fin de Partida
    if vida_actual <= 0:
        ok, error_fin = finalizar_partida(st.session_state.id_partida, "Derrota")
        if not ok:
            st.error(error_fin)
            st.stop()
        st.session_state.estado_juego = "GAMEOVER"
        st.rerun()
    elif st.session_state.respuestas_correctas >= 5:
        ok, error_fin = finalizar_partida(st.session_state.id_partida, "Victoria")
        if not ok:
            st.error(error_fin)
            st.stop()
        st.session_state.estado_juego = "GAMEOVER"
        st.rerun()

    # 3. Preparar el turno actual (anti-repetición por jugador)
    if st.session_state.pregunta_actual is None:
        pregunta, opciones, error_pregunta = cargar_pregunta(st.session_state.id_jugador)

        if error_pregunta:
            st.error(error_pregunta)
            st.stop()

        if pregunta is None:
            st.warning(
                "Ya respondiste todas las preguntas disponibles para este héroe. "
                "Podés volver al inicio y jugar con otro jugador."
            )
            if st.button("Volver al Inicio"):
                st.session_state.estado_juego = "REGISTRO"
                st.session_state.id_jugador = None
                st.session_state.id_partida = None
                resetear_estado_partida()
                st.rerun()
            st.stop()

        st.session_state.pregunta_actual = pregunta
        st.session_state.opciones_actuales = opciones
        st.session_state.error_turno = None

    preg = st.session_state.pregunta_actual
    if not preg:
        st.error("No hay una pregunta disponible para continuar.")
        st.stop()

    st.markdown(f"### 👾 ¡Te enfrentas a: **{preg['monstruo']}**!")
    st.info(
        f"**Categoría:** {preg['nombre_categoria']} | "
        f"**Daño por fallo:** {preg['dano_base']} HP"
    )
    st.write(f"**Consigna:** {preg['enunciado']}")

    # 4. Turno Activo (esperando respuesta)
    if not st.session_state.turno_respondido:
        if st.session_state.error_turno:
            st.error(st.session_state.error_turno)

        if not st.session_state.opciones_actuales:
            st.error("La pregunta no tiene opciones cargadas. Volvé al inicio e intentá de nuevo.")
            st.stop()

        dict_opciones = {
            opc['texto_opcion']: opc
            for opc in st.session_state.opciones_actuales
        }
        eleccion = st.radio(
            "Seleccioná la respuesta correcta:",
            list(dict_opciones.keys()),
            key=f"opciones_pregunta_{preg['id_pregunta']}"
        )

        if st.button("Responder y Atacar ⚔️", key=f"responder_pregunta_{preg['id_pregunta']}"):
            opc_elegida = dict_opciones[eleccion]
            es_correcta = bool(opc_elegida['es_correcta'])

            conn = get_connection()
            if conn is None:
                st.session_state.error_turno = "No se pudo conectar con la base de datos. Reintentá."
                st.rerun()

            cursor = conn.cursor()
            error_guardado = None
            try:
                conn.start_transaction()

                cursor.execute("""
                    INSERT INTO detalle_partida
                        (id_partida, id_pregunta, id_respuesta_elegida, fue_correcta)
                    VALUES (%s, %s, %s, %s)
                """, (
                    st.session_state.id_partida,
                    preg['id_pregunta'],
                    opc_elegida['id_respuesta'],
                    es_correcta
                ))

                if es_correcta:
                    cursor.execute(
                        "UPDATE jugador SET experiencia = experiencia + 20 WHERE id_jugador = %s",
                        (st.session_state.id_jugador,)
                    )
                    cursor.execute(
                        "UPDATE partida SET puntaje_total = puntaje_total + 20 WHERE id_partida = %s",
                        (st.session_state.id_partida,)
                    )
                else:
                    dano = preg['dano_base']
                    # GREATEST respeta la regla CHECK(vida >= 0)
                    cursor.execute(
                        "UPDATE jugador SET vida = GREATEST(0, vida - %s) WHERE id_jugador = %s",
                        (dano, st.session_state.id_jugador)
                    )

                conn.commit()
            except Error as e:
                try:
                    conn.rollback()
                except Error:
                    pass
                error_guardado = str(e)
            finally:
                cerrar_conexion(conn, cursor)

            if error_guardado:
                # La app NO avanza: la misma pregunta queda activa para reintentar.
                st.session_state.error_turno = (
                    f"No se pudo guardar la respuesta. Reintentá. Detalle: {error_guardado}"
                )
                st.rerun()

            # Estos cambios se hacen recién después del commit exitoso.
            st.session_state.error_turno = None
            if es_correcta:
                st.session_state.respuestas_correctas += 1
                st.session_state.tipo_mensaje = "success"
                st.session_state.mensaje_resultado = (
                    "¡Respuesta Correcta! Has derrotado al enemigo y sumaste +20 de Experiencia."
                )
            else:
                st.session_state.tipo_mensaje = "error"
                st.session_state.mensaje_resultado = (
                    f"¡Respuesta Incorrecta! El monstruo te infligió {preg['dano_base']} puntos de daño."
                )

            st.session_state.turno_respondido = True
            st.rerun()

    # 5. Post-Turno (viendo resultados)
    else:
        if st.session_state.tipo_mensaje == "success":
            st.success(st.session_state.mensaje_resultado)
        else:
            st.error(st.session_state.mensaje_resultado)

        if st.button("Siguiente Pregunta ➡️", key=f"siguiente_pregunta_{preg['id_pregunta']}"):
            guardada, error_verificacion = comprobar_respuesta_guardada(
                st.session_state.id_partida,
                preg['id_pregunta']
            )

            if error_verificacion or not guardada:
                # Cinturón de seguridad: no dejar avanzar si la respuesta no está en la BD.
                st.session_state.error_turno = (
                    error_verificacion
                    or "La respuesta anterior no se guardó. Reintentá para poder continuar."
                )
                st.session_state.turno_respondido = False
                st.session_state.mensaje_resultado = None
                st.session_state.tipo_mensaje = None
                st.rerun()

            st.session_state.pregunta_actual = None
            st.session_state.opciones_actuales = []
            st.session_state.turno_respondido = False
            st.session_state.mensaje_resultado = None
            st.session_state.tipo_mensaje = None
            st.session_state.error_turno = None
            st.rerun()

# -----------------------------------------------------------------------------
# PANTALLA 3: FIN DE PARTIDA Y TABLA DE CLASIFICACIÓN
# -----------------------------------------------------------------------------
elif st.session_state.estado_juego == "GAMEOVER":
    conn = get_connection()
    if conn is None:
        st.error("No se pudo conectar con la base de datos para mostrar el resultado.")
    else:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT resultado FROM partida WHERE id_partida = %s",
                (st.session_state.id_partida,)
            )
            res = cursor.fetchone()

            if res and res['resultado'] == 'Victoria':
                st.balloons()
                st.success("🎉 ¡VICTORIA! Has superado la mazmorra de Dungeon Quiz.")
            elif res and res['resultado'] == 'Derrota':
                st.error("☠️ GAME OVER. Tus Puntos de Vida han llegado a 0.")
            else:
                st.warning("No se encontró el resultado de la partida.")

            st.subheader("🏆 Tabla de Clasificación de Héroes (Vista SQL)")
            cursor.execute("SELECT * FROM vista_leaderboard")
            leaderboard = cursor.fetchall()
            st.table(leaderboard)
        except Error as e:
            st.error(f"No se pudo cargar el resultado o la clasificación: {e}")
        finally:
            cerrar_conexion(conn, cursor)

    if st.button("Volver a Jugar / Cambiar Héroe"):
        st.session_state.estado_juego = "REGISTRO"
        st.session_state.id_jugador = None
        st.session_state.id_partida = None
        resetear_estado_partida()
        st.rerun()
