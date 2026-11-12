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

### 2. Instalar Librerías de Python
Ejecutar el siguiente comando en la terminal de comandos dentro de la carpeta del proyecto:
```bash
pip install streamlit mysql-connector-python