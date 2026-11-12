-- ============================================================================
-- TRABAJO PRÁCTICO INTEGRADOR: Dungeon Quiz
-- Universidad: UNNE | Carrera: Tecnicatura Universitaria en Informática
-- Asignatura: Informática II | Profesor: Ing. Juan Manuel Goya
-- Integrantes: Nicolás Ibarrola, Lucas Correa Dare, Marcelo Garcia Billordo, Emanuel Maidana
-- Archivo: script.sql
-- ============================================================================

-- Preparación del entorno sobre base vacía
DROP DATABASE IF EXISTS dungeon_quiz;
CREATE DATABASE dungeon_quiz CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dungeon_quiz;

-- ============================================================================
-- PARTE 1: DDL - CREACIÓN DE TABLAS Y RESTRICCIONES (Reglas del juego en BD)
-- ============================================================================

-- 1. Tabla Jugador (Regla 1: Vida inicial 100 y nunca negativa)
CREATE TABLE jugador (
    id_jugador INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    vida INT NOT NULL DEFAULT 100 CHECK (vida >= 0),
    experiencia INT NOT NULL DEFAULT 0 CHECK (experiencia >= 0)
) ENGINE=InnoDB;

-- 2. Tabla Categoria
CREATE TABLE categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- 3. Tabla Monstruo
CREATE TABLE monstruo (
    id_monstruo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    dano_base INT NOT NULL CHECK (dano_base > 0),
    nivel_dificultad INT NOT NULL CHECK (nivel_dificultad BETWEEN 1 AND 3)
) ENGINE=InnoDB;

-- 4. Tabla Pregunta (Regla 2: Dificultad válida entre 1 y 3)
CREATE TABLE pregunta (
    id_pregunta INT AUTO_INCREMENT PRIMARY KEY,
    enunciado TEXT NOT NULL,
    nivel_dificultad INT NOT NULL CHECK (nivel_dificultad BETWEEN 1 AND 3),
    id_categoria INT NOT NULL,
    id_monstruo INT NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_monstruo) REFERENCES monstruo (id_monstruo) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 5. Tabla Respuesta
CREATE TABLE respuesta (
    id_respuesta INT AUTO_INCREMENT PRIMARY KEY,
    id_pregunta INT NOT NULL,
    texto_opcion VARCHAR(255) NOT NULL,
    es_correcta BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (id_pregunta) REFERENCES pregunta (id_pregunta) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 6. Tabla Partida
CREATE TABLE partida (
    id_partida INT AUTO_INCREMENT PRIMARY KEY,
    id_jugador INT NOT NULL,
    fecha_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    puntaje_total INT NOT NULL DEFAULT 0 CHECK (puntaje_total >= 0),
    resultado VARCHAR(20) NOT NULL DEFAULT 'En Progreso' CHECK (resultado IN ('Victoria', 'Derrota', 'En Progreso')),
    FOREIGN KEY (id_jugador) REFERENCES jugador (id_jugador) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 7. Tabla Detalle_Partida (Regla 3: PK compuesta evita repetir pregunta en la misma partida)
CREATE TABLE detalle_partida (
    id_partida INT NOT NULL,
    id_pregunta INT NOT NULL,
    id_respuesta_elegida INT NOT NULL,
    fue_correcta BOOLEAN NOT NULL,
    PRIMARY KEY (id_partida, id_pregunta),
    FOREIGN KEY (id_partida) REFERENCES partida (id_partida) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_pregunta) REFERENCES pregunta (id_pregunta) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_respuesta_elegida) REFERENCES respuesta (id_respuesta) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- PARTE 2: DML - DATOS SEMILLA (60 Preguntas: 15 por temática)
-- ============================================================================

-- Carga de Jugadores (incluye uno sin partidas jugadas para probar Anti-JOIN)
INSERT INTO jugador (nombre, vida, experiencia) VALUES 
('Nico_Hero', 100, 120),
('Lucas_Knight', 0, 40),
('Marcelo_Mage', 100, 80),
('Ema_Novato', 100, 0);

-- Carga de Categorías (4 Temáticas)
INSERT INTO categoria (id_categoria, nombre_categoria) VALUES 
(1, 'Geografía Argentina'),
(2, 'Historia Argentina'),
(3, 'Deportes Argentinos'),
(4, 'Informática Básica');

-- Carga de Monstruos (5 niveles)
INSERT INTO monstruo (id_monstruo, nombre, dano_base, nivel_dificultad) VALUES 
(1, 'Goblin del Código', 15, 1),
(2, 'Esqueleto de Sintaxis', 20, 1),
(3, 'Orc de las Bases de Datos', 30, 2),
(4, 'Dragón del Stack Overflow', 40, 2),
(5, 'Demonio del Kernel', 50, 3);

-- Categoría 1: Geografía Argentina (IDs 1 al 15)
INSERT INTO pregunta (id_pregunta, enunciado, nivel_dificultad, id_categoria, id_monstruo) VALUES 
(1, '¿Cuál es la capital de la provincia de Corrientes?', 1, 1, 1),
(2, '¿Cuál es la montaña más alta de Argentina y de América?', 1, 1, 1),
(3, '¿En qué provincia se encuentran las Cataratas del Iguazú?', 1, 1, 2),
(4, '¿Cuál es la provincia argentina de menor superficie territorial continental?', 1, 1, 2),
(5, '¿Cuál es la capital de la provincia de Tierra del Fuego?', 1, 1, 2),
(6, '¿Qué cerro emblemático se encuentra cerca de El Chaltén en Santa Cruz?', 2, 1, 3),
(7, '¿Qué provincia es famosa por la región vitivinícola del Valle de Uco?', 2, 1, 3),
(8, '¿En qué provincia se ubica el Parque Nacional Talampaya?', 2, 1, 3),
(9, '¿Qué importantes humedales se encuentran en la provincia de Corrientes?', 2, 1, 4),
(10, '¿Qué río limita naturalmente a la Argentina con el Uruguay al este?', 2, 1, 4),
(11, '¿En qué provincia se encuentra el volcán Ojos del Salado?', 3, 1, 5),
(12, '¿Cuál es el punto más austral de la Argentina continental?', 3, 1, 5),
(13, '¿Qué gran lago comparten Argentina y Chile en la provincia de Santa Cruz?', 3, 1, 5),
(14, '¿Cuál es la provincia más poblada de la República Argentina?', 1, 1, 1),
(15, '¿En qué provincia se ubica la Quebrada de Humahuaca?', 1, 1, 2);

-- Categoría 2: Historia Argentina (IDs 16 al 30)
INSERT INTO pregunta (id_pregunta, enunciado, nivel_dificultad, id_categoria, id_monstruo) VALUES 
(16, '¿En qué año se declaró la Independencia Argentina?', 1, 2, 1),
(17, '¿En qué año ocurrió la Revolución de Mayo?', 1, 2, 1),
(18, '¿Quién fue el primer presidente de las Provincias Unidas del Río de la Plata?', 1, 2, 2),
(19, '¿Quién fue el creador de la Bandera Argentina?', 1, 2, 2),
(20, '¿En qué combate el General San Martín bautizó de fuego a sus Granaderos?', 1, 2, 2),
(21, '¿En qué año se sancionó la Constitución Nacional Argentina original?', 2, 2, 3),
(22, '¿Quién encabezó la gesta del Cruce de los Andes?', 2, 2, 3),
(23, '¿En qué año se libró el conflicto bélico de la Guerra de Malvinas?', 2, 2, 3),
(24, '¿Qué presidente impulsó la ley del voto secreto, universal y obligatorio en 1912?', 2, 2, 4),
(25, '¿En qué fecha se conmemora el Día de la Bandera en Argentina?', 1, 2, 1),
(26, '¿Qué prócer es reconocido como el Padre del Aula por su impulso educativo?', 2, 2, 4),
(27, '¿Qué acuerdo de 1852 sentó las bases organizativas para la Constitución?', 3, 2, 5),
(28, '¿En qué año retornó la democracia constitucional con Raúl Alfonsín?', 2, 2, 4),
(29, '¿Qué ley de 1947 consagró el derecho al voto femenino en Argentina?', 3, 2, 5),
(30, '¿En qué año se produjo el primer golpe de Estado institucional del siglo XX en Argentina?', 3, 2, 5);

-- Categoría 3: Deportes Argentinos (IDs 31 al 45)
INSERT INTO pregunta (id_pregunta, enunciado, nivel_dificultad, id_categoria, id_monstruo) VALUES 
(31, '¿En qué año ganó Argentina su primer Mundial de Fútbol masculino?', 1, 3, 1),
(32, '¿Qué tenista argentino ganó el torneo US Open en 2009?', 1, 3, 1),
(33, '¿Qué selección argentina de básquet ganó el Oro Olímpico en Atenas 2004?', 1, 3, 2),
(34, '¿Quién es el máximo goleador histórico de la Selección Argentina de Fútbol?', 1, 3, 2),
(35, '¿Qué piloto argentino fue 5 veces campeón mundial de Fórmula 1?', 1, 3, 2),
(36, '¿En qué país ganó la Selección Argentina su tercer Mundial de Fútbol en 2022?', 1, 3, 1),
(37, '¿Cómo se apoda popularmente a la Selección Femenina de Hockey sobre Césped?', 2, 3, 3),
(38, '¿Qué boxeador mendocino fue famoso por su estilo defensivo "Intocable"?', 2, 3, 3),
(39, '¿Qué club del fútbol argentino posee la mayor cantidad de Copas Libertadores?', 2, 3, 3),
(40, '¿Qué judoca argentina ganó la medalla de oro en los Juegos Olímpicos de Río 2016?', 2, 3, 4),
(41, '¿Cómo se denominó al emblemático segundo gol de Maradona a Inglaterra en 1986?', 2, 3, 4),
(42, '¿Cómo se apoda al seleccionado nacional masculino de Rugby de Argentina?', 1, 3, 1),
(43, '¿Qué tenista argentina ganó el torneo de Roland Garros en dobles y fue top 3 mundial?', 3, 3, 5),
(44, '¿Qué deporte criollo fue declarado oficialmente Deporte Nacional en 1953?', 3, 3, 5),
(45, '¿En qué disciplina se destacó Luciana Aymar, 8 veces elegida mejor jugadora del mundo?', 3, 3, 5);

-- Categoría 4: Informática Básica (IDs 46 al 60)
INSERT INTO pregunta (id_pregunta, enunciado, nivel_dificultad, id_categoria, id_monstruo) VALUES 
(46, '¿Qué significan las siglas CPU en una computadora?', 1, 4, 1),
(47, '¿Cuál de los siguientes es un sistema operativo de código abierto (Open Source)?', 1, 4, 1),
(48, '¿Qué memoria volátil almacena los datos de los programas en ejecución?', 1, 4, 2),
(49, '¿Qué unidad de almacenamiento no posee partes mecánicas ni platos giratorios?', 1, 4, 2),
(50, '¿Qué significa la sigla HTML en desarrollo y diseño web?', 1, 4, 2),
(51, '¿Cuál es el puerto de red estándar utilizado para conexiones seguras HTTPS?', 2, 4, 3),
(52, '¿Qué extensión distingue habitualmente a los archivos ejecutables en Windows?', 1, 4, 1),
(53, '¿Qué periférico de entrada es el principal para introducir texto en la computadora?', 1, 4, 1),
(54, '¿Cómo se denomina al software diseñado con fines maliciosos para dañar sistemas?', 2, 4, 3),
(55, '¿Qué protocolo de red se utiliza específicamente para enviar correo electrónico?', 2, 4, 4),
(56, '¿Qué memoria de solo lectura conserva la información básica del arranque?', 2, 4, 4),
(57, '¿Qué estructura de datos informática funciona bajo la filosofía LIFO?', 3, 4, 5),
(58, '¿Qué significan las siglas IP en la arquitectura de redes?', 2, 4, 3),
(59, '¿Cuál de los siguientes es un lenguaje de programación de alto nivel?', 1, 4, 1),
(60, '¿A cuántos Megabytes (MB) equivale exactamente 1 Gigabyte (GB)?', 3, 4, 5);

-- Respuestas (240 opciones en total: 4 por cada pregunta, 1 correcta)
INSERT INTO respuesta (id_pregunta, texto_opcion, es_correcta) VALUES 
-- Geografía Argentina
(1, 'Corrientes', TRUE), (1, 'Resistencia', FALSE), (1, 'Goya', FALSE), (1, 'Posadas', FALSE),
(2, 'Cerro Aconcagua', TRUE), (2, 'Monte Pissis', FALSE), (2, 'Cerro Chaltén', FALSE), (2, 'Nevado Ojos del Salado', FALSE),
(3, 'Misiones', TRUE), (3, 'Corrientes', FALSE), (3, 'Entre Ríos', FALSE), (3, 'Chaco', FALSE),
(4, 'Tucumán', TRUE), (4, 'Jujuy', FALSE), (4, 'Catamarca', FALSE), (4, 'La Pampa', FALSE),
(5, 'Ushuaia', TRUE), (5, 'Río Grande', FALSE), (5, 'Tolhuin', FALSE), (5, 'Río Gallegos', FALSE),
(6, 'Cerro Fitz Roy', TRUE), (6, 'Cerro Tronador', FALSE), (6, 'Cerro Catedral', FALSE), (6, 'Volcán Lanín', FALSE),
(7, 'Mendoza', TRUE), (7, 'San Juan', FALSE), (7, 'Salta', FALSE), (7, 'La Rioja', FALSE),
(8, 'La Rioja', TRUE), (8, 'San Luis', FALSE), (8, 'Córdoba', FALSE), (8, 'Catamarca', FALSE),
(9, 'Esteros del Iberá', TRUE), (9, 'Bañado la Estrella', FALSE), (9, 'Delta del Paraná', FALSE), (9, 'Laguna de Mar Chiquita', FALSE),
(10, 'Río Uruguay', TRUE), (10, 'Río Paraná', FALSE), (10, 'Río Paraguay', FALSE), (10, 'Río Colorado', FALSE),
(11, 'Catamarca', TRUE), (11, 'Jujuy', FALSE), (11, 'Neuquén', FALSE), (11, 'Chubut', FALSE),
(12, 'Cabo Vírgenes', TRUE), (12, 'Punta Mogotes', FALSE), (12, 'Puerto Madryn', FALSE), (12, 'Cabo Blanco', FALSE),
(13, 'Lago Buenos Aires', TRUE), (13, 'Lago Nahuel Huapi', FALSE), (13, 'Lago Argentino', FALSE), (13, 'Lago Viedma', FALSE),
(14, 'Buenos Aires', TRUE), (14, 'Córdoba', FALSE), (14, 'Santa Fe', FALSE), (14, 'Mendoza', FALSE),
(15, 'Jujuy', TRUE), (15, 'Salta', FALSE), (15, 'Tucumán', FALSE), (15, 'Catamarca', FALSE),

-- Historia Argentina
(16, '1816', TRUE), (16, '1810', FALSE), (16, '1825', FALSE), (16, '1853', FALSE),
(17, '1810', TRUE), (17, '1816', FALSE), (17, '1806', FALSE), (17, '1820', FALSE),
(18, 'Bernardino Rivadavia', TRUE), (18, 'Manuel Belgrano', FALSE), (18, 'José de San Martín', FALSE), (18, 'Justo José de Urquiza', FALSE),
(19, 'Manuel Belgrano', TRUE), (19, 'José de San Martín', FALSE), (19, 'Mariano Moreno', FALSE), (19, 'Cornelio Saavedra', FALSE),
(20, 'Combate de San Lorenzo', TRUE), (20, 'Batalla de Maipú', FALSE), (20, 'Batalla de Chacabuco', FALSE), (20, 'Batalla de Suipacha', FALSE),
(21, '1853', TRUE), (21, '1810', FALSE), (21, '1816', FALSE), (21, '1860', FALSE),
(22, 'José de San Martín', TRUE), (22, 'Manuel Belgrano', FALSE), (22, 'Martín Miguel de Güemes', FALSE), (22, 'Juan Lavalle', FALSE),
(23, '1982', TRUE), (23, '1978', FALSE), (23, '1983', FALSE), (23, '1976', FALSE),
(24, 'Roque Sáenz Peña', TRUE), (24, 'Hipólito Yrigoyen', FALSE), (24, 'Julio Argentino Roca', FALSE), (24, 'Carlos Pellegrini', FALSE),
(25, '20 de junio', TRUE), (25, '25 de mayo', FALSE), (25, '9 de julio', FALSE), (25, '17 de agosto', FALSE),
(26, 'Domingo Faustino Sarmiento', TRUE), (26, 'Nicolás Avellaneda', FALSE), (26, 'Bartolomé Mitre', FALSE), (26, 'Esteban Echeverría', FALSE),
(27, 'Acuerdo de San Nicolás', TRUE), (27, 'Pacto Federal', FALSE), (27, 'Tratado del Pilar', FALSE), (27, 'Pacto de Olivos', FALSE),
(28, '1983', TRUE), (28, '1981', FALSE), (28, '1985', FALSE), (28, '1989', FALSE),
(29, 'Ley Evita (Ley 13.010)', TRUE), (29, 'Ley Láinez', FALSE), (29, 'Ley de Residencia', FALSE), (29, 'Ley Palacios', FALSE),
(30, '1930', TRUE), (30, '1943', FALSE), (30, '1955', FALSE), (30, '1976', FALSE),

-- Deportes Argentinos
(31, '1978', TRUE), (31, '1986', FALSE), (31, '2022', FALSE), (31, '1974', FALSE),
(32, 'Juan Martín del Potro', TRUE), (32, 'David Nalbandian', FALSE), (32, 'Guillermo Coria', FALSE), (32, 'Gastón Gaudio', FALSE),
(33, 'La Generación Dorada', TRUE), (33, 'Los Leones', FALSE), (33, 'Los Pumas', FALSE), (33, 'La Garra', FALSE),
(34, 'Lionel Messi', TRUE), (34, 'Gabriel Batistuta', FALSE), (34, 'Diego Maradona', FALSE), (34, 'Hernán Crespo', FALSE),
(35, 'Juan Manuel Fangio', TRUE), (35, 'Carlos Reutemann', FALSE), (35, 'Froilán González', FALSE), (35, 'Oscar Gálvez', FALSE),
(36, 'Qatar', TRUE), (36, 'Brasil', FALSE), (36, 'Rusia', FALSE), (36, 'Alemania', FALSE),
(37, 'Las Leonas', TRUE), (37, 'Las Caimanes', FALSE), (37, 'Las Panteras', FALSE), (37, 'Las Yaguaretés', FALSE),
(38, 'Nicolino Locche', TRUE), (38, 'Carlos Monzón', FALSE), (38, 'Oscar Bonavena', FALSE), (38, 'Pascual Pérez', FALSE),
(39, 'Independiente', TRUE), (39, 'Boca Juniors', FALSE), (39, 'River Plate', FALSE), (39, 'Estudiantes de La Plata', FALSE),
(40, 'Paula Pareto', TRUE), (40, 'Gabriela Sabatini', FALSE), (40, 'Cecilia Carranza', FALSE), (40, 'Delfina Pignatiello', FALSE),
(41, 'El Gol del Siglo', TRUE), (41, 'La Mano de Dios', FALSE), (41, 'La Chilenita', FALSE), (41, 'El Bochinazo', FALSE),
(42, 'Los Pumas', TRUE), (42, 'Los Yaguarés', FALSE), (42, 'Los Cóndores', FALSE), (42, 'Los Teros', FALSE),
(43, 'Gabriela Sabatini', TRUE), (43, 'Paola Suárez', FALSE), (43, 'Gisela Dulko', FALSE), (43, 'Nadia Podoroska', FALSE),
(44, 'El Pato', TRUE), (44, 'El Polo', FALSE), (44, 'La Doma', FALSE), (44, 'El Padel', FALSE),
(45, 'Hockey sobre césped', TRUE), (45, 'Natación', FALSE), (45, 'Tenis', FALSE), (45, 'Vóley', FALSE),

-- Informática Básica
(46, 'Central Processing Unit', TRUE), (46, 'Computer Personal Unit', FALSE), (46, 'Central Process User', FALSE), (46, 'Core Program Unit', FALSE),
(47, 'Linux', TRUE), (47, 'Windows 11', FALSE), (47, 'macOS', FALSE), (47, 'MS-DOS', FALSE),
(48, 'Memoria RAM', TRUE), (48, 'Disco Rígido (HDD)', FALSE), (48, 'Memoria ROM', FALSE), (48, 'Memoria Caché L1', FALSE),
(49, 'Unidad de Estado Sólido (SSD)', TRUE), (49, 'Disco Rígido HDD', FALSE), (49, 'Disquetera', FALSE), (49, 'Lector de DVD', FALSE),
(50, 'HyperText Markup Language', TRUE), (50, 'High Technical Modern Language', FALSE), (50, 'Hyper Transfer Machine Logic', FALSE), (50, 'Home Tool Markup Level', FALSE),
(51, '443', TRUE), (51, '80', FALSE), (51, '21', FALSE), (51, '3306', FALSE),
(52, '.exe', TRUE), (52, '.txt', FALSE), (52, '.png', FALSE), (52, '.pdf', FALSE),
(53, 'Teclado', TRUE), (53, 'Monitor', FALSE), (53, 'Impresora', FALSE), (53, 'Altavoz', FALSE),
(54, 'Malware', TRUE), (54, 'Hardware', FALSE), (54, 'Firmware', FALSE), (54, 'Shareware', FALSE),
(55, 'SMTP', TRUE), (55, 'HTTP', FALSE), (55, 'FTP', FALSE), (55, 'DHCP', FALSE),
(56, 'ROM', TRUE), (56, 'RAM', FALSE), (56, 'SSD', FALSE), (56, 'USB', FALSE),
(57, 'Pila (Stack)', TRUE), (57, 'Cola (Queue)', FALSE), (57, 'Matriz (Array)', FALSE), (57, 'Grafo (Graph)', FALSE),
(58, 'Internet Protocol', TRUE), (58, 'Internal Process', FALSE), (58, 'Interconnected Port', FALSE), (58, 'Information Provider', FALSE),
(59, 'Python', TRUE), (59, 'Lenguaje Ensamblador', FALSE), (59, 'Código Máquina', FALSE), (59, 'Microcódigo', FALSE),
(60, '1024 MB', TRUE), (60, '1000 MB', FALSE), (60, '512 MB', FALSE), (60, '2048 MB', FALSE);

-- Carga de Partidas Semilla
INSERT INTO partida (id_partida, id_jugador, puntaje_total, resultado) VALUES 
(1, 1, 100, 'Victoria'),
(2, 2, 30, 'Derrota'),
(3, 3, 80, 'En Progreso');

-- Carga de Detalle de Partidas
INSERT INTO detalle_partida (id_partida, id_pregunta, id_respuesta_elegida, fue_correcta) VALUES 
(1, 1, 1, TRUE), (1, 16, 61, TRUE), (1, 31, 121, TRUE), (1, 46, 181, TRUE), (1, 2, 5, TRUE),
(2, 1, 1, TRUE), (2, 17, 66, FALSE), (2, 32, 126, FALSE),
(3, 1, 1, TRUE), (3, 16, 61, TRUE), (3, 31, 121, TRUE), (3, 46, 181, TRUE);

-- ============================================================================
-- PARTE 3: DIEZ CONSULTAS REQUERIDAS (Con enunciado y tipos de consulta obligatorios)
-- ============================================================================

-- Consulta 1 (OBLIGATORIA DEL PROYECTO): Tabla de clasificación / Leaderboard (ORDER BY + LIMIT)
SELECT j.nombre, j.experiencia, COUNT(p.id_partida) AS partidas_jugadas
FROM jugador j
LEFT JOIN partida p ON j.id_jugador = p.id_jugador
GROUP BY j.id_jugador, j.nombre, j.experiencia
ORDER BY j.experiencia DESC
LIMIT 5;

-- Consulta 2 (OBLIGATORIA DEL PROYECTO): Rendimiento por categoría (% de aciertos con GROUP BY)
SELECT 
    c.nombre_categoria,
    COUNT(dp.id_pregunta) AS total_respondidas,
    SUM(CASE WHEN dp.fue_correcta = TRUE THEN 1 ELSE 0 END) AS aciertos,
    ROUND((SUM(CASE WHEN dp.fue_correcta = TRUE THEN 1 ELSE 0 END) / COUNT(dp.id_pregunta)) * 100, 2) AS porcentaje_aciertos
FROM detalle_partida dp
JOIN pregunta p ON dp.id_pregunta = p.id_pregunta
JOIN categoria c ON p.id_categoria = c.id_categoria
GROUP BY c.id_categoria, c.nombre_categoria;

-- Consulta 3 (OBLIGATORIA DEL PROYECTO): Selección aleatoria de preguntas por dificultad
SELECT p.id_pregunta, p.enunciado, c.nombre_categoria, m.nombre AS monstruo, m.dano_base
FROM pregunta p
JOIN categoria c ON p.id_categoria = c.id_categoria
JOIN monstruo m ON p.id_monstruo = m.id_monstruo
WHERE p.nivel_dificultad = 1
ORDER BY RAND()
LIMIT 3;

-- Consulta 4 (TIPO OBLIGATORIO: JOIN de 3 o más tablas): Detalle completo de respuestas de jugadores
SELECT j.nombre AS jugador, par.id_partida, pre.enunciado, r.texto_opcion AS respuesta_elegida, dp.fue_correcta
FROM detalle_partida dp
JOIN partida par ON dp.id_partida = par.id_partida
JOIN jugador j ON par.id_jugador = j.id_jugador
JOIN pregunta pre ON dp.id_pregunta = pre.id_pregunta
JOIN respuesta r ON dp.id_respuesta_elegida = r.id_respuesta;

-- Consulta 5 (TIPO OBLIGATORIO: Anti-Join LEFT JOIN ... IS NULL): Jugadores que nunca jugaron una partida
SELECT j.id_jugador, j.nombre, j.vida, j.experiencia
FROM jugador j
LEFT JOIN partida p ON j.id_jugador = p.id_jugador
WHERE p.id_partida IS NULL;

-- Consulta 6 (TIPO OBLIGATORIO: Subconsulta Escalar): Preguntas con monstruos por encima del daño promedio
SELECT p.id_pregunta, p.enunciado, m.nombre AS monstruo, m.dano_base
FROM pregunta p
JOIN monstruo m ON p.id_monstruo = m.id_monstruo
WHERE m.dano_base > (SELECT AVG(dano_base) FROM monstruo);

-- Consulta 7 (TIPO OBLIGATORIO: GROUP BY con HAVING): Jugadores con al menos 1 partida jugada
SELECT j.nombre, COUNT(p.id_partida) AS total_partidas
FROM jugador j
JOIN partida p ON j.id_jugador = p.id_jugador
GROUP BY j.id_jugador, j.nombre
HAVING COUNT(p.id_partida) >= 1;

-- Consulta 8: Preguntas que nunca se presentaron en ninguna partida (Anti-Join secundario)
SELECT p.id_pregunta, p.enunciado, c.nombre_categoria
FROM pregunta p
LEFT JOIN detalle_partida dp ON p.id_pregunta = dp.id_pregunta
JOIN categoria c ON p.id_categoria = c.id_categoria
WHERE dp.id_pregunta IS NULL;

-- Consulta 9: Monstruo más temible (el que más daño infligió en respuestas incorrectas)
SELECT m.nombre AS monstruo, SUM(m.dano_base) AS dano_total_causado
FROM detalle_partida dp
JOIN pregunta p ON dp.id_pregunta = p.id_pregunta
JOIN monstruo m ON p.id_monstruo = m.id_monstruo
WHERE dp.fue_correcta = FALSE
GROUP BY m.id_monstruo, m.nombre
ORDER BY dano_total_causado DESC;

-- Consulta 10: Resumen general de victorias vs derrotas en el juego
SELECT resultado, COUNT(*) AS cantidad_partidas
FROM partida
WHERE resultado != 'En Progreso'
GROUP BY resultado;

-- ============================================================================
-- PARTE 4: TRANSACCIÓN ATÓMICA DE JUEGO (Regla 4: Con demostración de ROLLBACK)
-- ============================================================================

-- CASO A: Transacción Exitosa (Turno donde el jugador acierta)
START TRANSACTION;
INSERT INTO detalle_partida (id_partida, id_pregunta, id_respuesta_elegida, fue_correcta) 
VALUES (3, 3, 9, TRUE);
UPDATE jugador SET experiencia = experiencia + 20 WHERE id_jugador = 3;
UPDATE partida SET puntaje_total = puntaje_total + 20 WHERE id_partida = 3;
COMMIT;

-- ============================================================================
-- PARTE 5: VISTA DE PANTALLA (Se crea antes de la prueba de error)
-- ============================================================================

CREATE VIEW vista_leaderboard AS
SELECT 
    j.id_jugador,
    j.nombre AS jugador,
    j.experiencia,
    COUNT(CASE WHEN p.resultado = 'Victoria' THEN 1 END) AS victorias,
    COUNT(CASE WHEN p.resultado = 'Derrota' THEN 1 END) AS derrotas,
    COALESCE(MAX(p.puntaje_total), 0) AS mejor_puntaje
FROM jugador j
LEFT JOIN partida p ON j.id_jugador = p.id_jugador
GROUP BY j.id_jugador, j.nombre, j.experiencia
ORDER BY j.experiencia DESC;

-- ============================================================================
-- CASO B: Transacción con ROLLBACK (Simulación de daño letal - error esperado)
-- ============================================================================
START TRANSACTION;
UPDATE jugador SET vida = vida - 150 WHERE id_jugador = 2; 
ROLLBACK;