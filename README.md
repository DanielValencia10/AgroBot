# AgroBot

Proyecto universitario de Inteligencia Artificial (Universidad del Valle).

Un robot agricola se mueve sobre una cuadricula de 10x10 fertilizando cultivos
secos, usando opcionalmente una avioneta para desplazarse mas barato mientras
tenga combustible, y recargando fertilizante en un deposito. El problema se
resuelve con cinco algoritmos de busqueda: tres no informados (Amplitud,
Costo uniforme, Profundidad evitando ciclos) y dos informados (Avara, A*).

Este repositorio contiene por ahora solo el **esqueleto** del proyecto: la
estructura de carpetas, los archivos vacios de logica (cada uno con su
cabecera de documentacion) y la documentacion inicial. No hay implementacion
todavia.

## Arbol de carpetas

```
agrobot/
├── README.md
├── .gitignore
├── requirements.txt
├── docs/
│   └── informe/            (carpeta vacia con .gitkeep, para el informe del curso)
├── mundos/
│   └── Prueba1.txt         (mundo de referencia usado en los tests)
├── assets/
│   ├── README.md           (lista de sprites esperados, formato y tamano)
│   └── sprites/             (carpeta vacia con .gitkeep; aqui van las imagenes)
├── src/agrobot/
│   ├── __init__.py
│   ├── main.py              (punto de entrada; une todo)
│   ├── constantes.py        (codigos del mundo, capacidades, tamano de cuadricula)
│   ├── modelo/
│   │   ├── __init__.py
│   │   ├── mundo.py          (parte constante del mundo)
│   │   ├── estado.py         (estado dinamico s = (f, c, phi, e, k, P))
│   │   └── movimiento.py     (los cuatro movimientos y su desplazamiento)
│   ├── problema/
│   │   ├── __init__.py
│   │   ├── agrobot_problema.py  (estado inicial, meta, sucesores, costo)
│   │   ├── operadores.py        (precondiciones y efectos automaticos)
│   │   ├── costos.py             (costo de cada paso)
│   │   └── ciclos.py             (control de ciclos y sus excepciones)
│   ├── busqueda/
│   │   ├── __init__.py
│   │   ├── nodo.py            (nodo del arbol de busqueda)
│   │   ├── resultado.py       (contrato de salida hacia la GUI)
│   │   ├── no_informada/
│   │   │   ├── __init__.py
│   │   │   ├── amplitud.py
│   │   │   ├── costo_uniforme.py
│   │   │   └── profundidad.py
│   │   └── informada/
│   │       ├── __init__.py
│   │       ├── avara.py
│   │       ├── a_estrella.py
│   │       └── heuristica.py
│   ├── archivos/
│   │   ├── __init__.py
│   │   └── lector_mundo.py    (lectura y validacion del archivo de mundo .txt)
│   └── gui/
│       ├── __init__.py
│       ├── ventana_principal.py
│       ├── panel_control.py
│       ├── panel_mundo.py
│       ├── animacion.py
│       ├── panel_reporte.py
│       └── cargador_sprites.py  (unico archivo que lee assets/sprites/)
└── tests/
    ├── test_lector_mundo.py
    ├── test_operadores.py
    ├── test_heuristica.py
    └── test_algoritmos.py
```

> Nota: el paquete de lectura de archivos se llama `archivos/` y no `io/`
> para no chocar con el modulo estandar `io` de Python.

## Regla de dependencias

- `constantes.py` no importa nada del proyecto.
- `modelo/` solo importa de `constantes`.
- `problema/` importa de `modelo/` y `constantes`.
- `busqueda/` **no** importa de `problema/` ni de `gui/`. Los algoritmos
  reciben el objeto `problema` como parametro y solo dependen del contrato
  que ese objeto debe cumplir (estado inicial, es_meta, sucesores, costo).
  `busqueda/informada/` ademas importa su propio `heuristica.py`.
- `archivos/` importa de `modelo/` y `constantes`.
- `gui/` importa de `busqueda/`, `problema/`, `archivos/` y `modelo/`.
- `main.py` es el unico que une todo (composicion).
- Nada importa de `gui/` excepto `main.py`.
- Solo `gui/` puede leer `assets/`, y dentro de `gui/` solo
  `cargador_sprites.py` conoce la ruta de `assets/sprites/`; los demas
  paneles (`panel_mundo.py`, `animacion.py`) le piden los sprites por
  nombre en vez de leer la carpeta directamente.

## Decisiones pendientes del equipo

Estas son las decisiones marcadas como `PENDIENTE` en las cabeceras de los
archivos de codigo, y en que archivo viven:

- **Orden de los operadores/movimientos** al generar sucesores (afecta
  desempates y orden de expansion):
  - `src/agrobot/modelo/movimiento.py`
  - `src/agrobot/problema/operadores.py`
  - `src/agrobot/busqueda/no_informada/profundidad.py`
- **Orden exacto de evaluacion de los efectos automaticos** cuando una misma
  casilla pudiera activar mas de un efecto:
  - `src/agrobot/problema/operadores.py`
- **Costo exacto del movimiento que sube a la avioneta y del que gasta el
  ultimo combustible**, y representacion numerica de los costos (float,
  fraccion exacta, o escala entera):
  - `src/agrobot/problema/costos.py`
- **Que componentes del estado se comparan para el control de ciclos** y
  **como se aplica exactamente la excepcion** (avioneta, cultivo seco con
  fertilizante, deposito):
  - `src/agrobot/problema/ciclos.py`
- **Si la construccion del estado inicial completo vive en `estado.py` o se
  delega a `agrobot_problema.py`**:
  - `src/agrobot/modelo/estado.py`
- **Si se recibe el camino completo de la rama o una estructura mas liviana**
  para el control de ciclos al generar sucesores:
  - `src/agrobot/problema/agrobot_problema.py`
- **Criterios de desempate** en la frontera de cada algoritmo (Amplitud,
  Costo uniforme, Profundidad, Avara, A*):
  - `src/agrobot/busqueda/no_informada/amplitud.py`
  - `src/agrobot/busqueda/no_informada/costo_uniforme.py`
  - `src/agrobot/busqueda/no_informada/profundidad.py`
  - `src/agrobot/busqueda/informada/avara.py`
  - `src/agrobot/busqueda/informada/a_estrella.py`
- **Si se necesita un limite de profundidad** para Profundidad (DFS):
  - `src/agrobot/busqueda/no_informada/profundidad.py`
- **Definicion de la heuristica** (y su justificacion de admisibilidad para
  el informe):
  - `src/agrobot/busqueda/informada/heuristica.py`
- **Libreria de GUI a usar**:
  - `src/agrobot/gui/ventana_principal.py`
  - `src/agrobot/gui/panel_control.py`
  - `src/agrobot/gui/panel_mundo.py`
  - `src/agrobot/gui/animacion.py`
  - `src/agrobot/gui/panel_reporte.py`
- **Velocidad/control de reproduccion de la animacion**:
  - `src/agrobot/gui/animacion.py`
- **Tamano final en pixeles de cada sprite** (sugerido 64x64 px) y formato
  concreto de carga de imagenes (depende de la libreria de GUI elegida):
  - `src/agrobot/gui/cargador_sprites.py`
  - `assets/README.md`
- **Framework de pruebas a usar** (pytest o unittest):
  - `tests/test_lector_mundo.py`
  - `tests/test_operadores.py`
  - `tests/test_heuristica.py`
  - `tests/test_algoritmos.py`
