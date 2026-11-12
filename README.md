# ⚔️ Dungeon Quiz RPG - Trabajo Práctico Integrador (UNNE)

Este proyecto implementa un juego de trivia relacional interactivo programado en Python (Streamlit) respaldado por una base de datos relacional MySQL/MariaDB normalizada en 3FN.

## 📋 Requisitos Previos

* Python 3.9 o superior.
* Servidor MySQL o MariaDB (vía XAMPP, WAMP o servicio local MySQL Server).

## 🚀 Pasos para Instalación y Ejecución

### 1. Preparar la Base de Datos

1. Abrir MySQL Workbench, phpMyAdmin o la consola de MySQL.
2. Ejecutar íntegramente el archivo `script.sql` en una base vacía.
3. El script creará la base `dungeon_quiz`, las 7 tablas, las restricciones de integridad, los datos semilla de las 60 preguntas, las 10 consultas, la transacción y la vista.

Desde la consola, dentro de la carpeta del proyecto:

```bash
mysql -u root --force < script.sql
```

> El bloque `CASO B` del final del script provoca un error **intencional** para demostrar el `ROLLBACK`. Por eso se usa `--force`: la importación continúa y la base queda creada correctamente.

En Linux con XAMPP, el cliente suele estar en `/opt/lampp/bin/mysql`:

```bash
/opt/lampp/bin/mysql -u root --force < script.sql
```

Verificación rápida:

```bash
/opt/lampp/bin/mysql -u root -e "USE dungeon_quiz; SHOW FULL TABLES; SELECT COUNT(*) FROM pregunta; SELECT COUNT(*) FROM respuesta;"
```

Deberían aparecer las 7 tablas, la vista `vista_leaderboard`, 60 preguntas y 240 respuestas.

### 2. Instalar Librerías de Python

Se recomienda usar un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación

```bash
streamlit run app_dungeon.py
```

Abrir en el navegador:

```
http://localhost:8501
```

Para detener la aplicación, presionar `Ctrl+C` en la terminal.

## ⚙️ Configuración de Conexión

La conexión está configurada en `app_dungeon.py` para:

* Host: `localhost`
* Usuario: `root`
* Contraseña: vacía
* Base de datos: `dungeon_quiz`

Si el servidor MySQL tiene otra contraseña o usuario, modificar la función `get_connection()`.

## 🎮 Reglas del Juego

* Cada partida comienza con 100 puntos de vida.
* Una respuesta correcta suma 20 de experiencia y 20 al puntaje de la partida.
* Una respuesta incorrecta resta el daño base del monstruo, sin bajar de 0 HP.
* Se gana al acumular 5 respuestas correctas.
* Se pierde cuando la vida llega a 0.
* Un jugador no repite preguntas ya respondidas en partidas anteriores.

## 📝 Notas

* El primer inicio de Streamlit puede pedir un correo; se puede omitir presionando `Enter`.
* Si el puerto 8501 está ocupado: `streamlit run app_dungeon.py --server.port 8502`.
* La app está pensada para ejecutarse localmente con fines académicos.
