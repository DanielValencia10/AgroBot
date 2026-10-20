# AgroBot

Proyecto universitario de Inteligencia Artificial (Universidad del Valle).

Un robot agricola se mueve sobre una cuadricula de 10x10 fertilizando cultivos
secos, usando opcionalmente una avioneta para desplazarse mas barato mientras
tenga combustible, y recargando fertilizante en un deposito. El problema se
resuelve con cinco algoritmos de busqueda: tres no informados (Amplitud,
Costo uniforme, Profundidad evitando ciclos) y dos informados (Avara, A*).

Estado actual: funcionan la lectura y validacion de mundos, el problema (operadores,
costos y control de ciclos), la busqueda en **Amplitud**, **Costo uniforme** y
**Profundidad evitando ciclos** y **Avara** (con su heuristica), y toda la interfaz
(bienvenida, seleccion, animacion del camino, arbol de exploracion y reporte). A* aun no
esta implementado: al elegirlo la aplicacion avisa.

## Instalacion del entorno

Las dependencias (por ahora solo `pygame-ce`) se instalan dentro de un entorno
virtual local en la carpeta `.venv/`. Esa carpeta ya esta en `.gitignore`, asi
que no se sube al repositorio: cada integrante crea la suya.

Windows (PowerShell), desde la raiz del repositorio:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux / macOS:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecucion

Con el entorno activo, desde la raiz del repositorio:

```
python ejecutar.py
```

(tambien se puede, desde la carpeta `src/`: `python -m agrobot.main`). El flujo es:
bienvenida -> seleccion de mundo y algoritmo -> ventana principal -> de vuelta a la
seleccion. En la ventana principal: `Espacio` pausa, `Derecha` avanza un paso, `R`
reinicia, `Arriba`/`Abajo` cambian la velocidad y `Esc` vuelve a la seleccion.

Pruebas (desde la raiz, con el entorno activo):

```
python -m unittest tests.test_lector_mundo tests.test_operadores tests.test_algoritmos tests.test_sprites tests.test_panel_mundo tests.test_arbol_exploracion tests.test_seleccion_nodos tests.test_animacion tests.test_flujo
```

Las tipografias Pixelify Sans y DM Sans (gratuitas, de Google Fonts) van en
`src/agrobot/gui/fuentes/`, siguiendo el `LEEME.md` de esa carpeta; sin ellas la aplicacion
funciona igual, pero con una letra del sistema.

Si PowerShell no deja activar el entorno, ejecutar una vez
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. No instalar `pygame` y
`pygame-ce` en el mismo entorno: chocan entre si.

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
│       ├── arbol_exploracion.py  (arbol de exploracion que se arma durante la animacion)
│       ├── pantalla_aviso.py     (aviso: mundo invalido o algoritmo sin implementar)
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

## Decisiones del equipo

Resueltas (quedaron documentadas en la cabecera del archivo que las aplica):

- Orden de los movimientos: arriba, abajo, izquierda, derecha (`modelo/movimiento.py`).
- Orden de los efectos al entrar a una casilla: combustible, avioneta, deposito, cultivo
  (`problema/operadores.py`).
- Costos: el paso que sube a la avioneta cuesta 1 y el que gasta la ultima unidad de
  combustible cuesta 1/2; se usan `float` (`problema/costos.py`).
- Control de ciclos: se compara el estado completo y las excepciones se cumplen solas
  (`problema/ciclos.py`).
- El estado inicial se construye en `modelo/estado.py` y el robot arranca con 0 de
  fertilizante.
- Sucesores: `camino_de_la_rama` es cualquier contenedor de estados (`problema/agrobot_problema.py`).
- Ciclos: un sucesor se descarta si repite un estado de su rama comparando (f, c, phi, e, P);
  el combustible k se omite a proposito (`problema/ciclos.py`).
- Avioneta: un solo uso. Sube automaticamente al pisar su casilla sin usar (k = 30) y nunca
  vuelve a subir despues de agotarse (`problema/operadores.py`).
- Profundidad: apila los sucesores al reves para explorar primero el orden arriba, abajo,
  izquierda, derecha; solo evita ciclos dentro de la rama. Termina siempre (el espacio de
  estados es finito) pero puede tardar mucho en mundos sin solucion
  (`busqueda/no_informada/profundidad.py`).
- Avara: cola de prioridad por h(n) con desempate por orden de insercion; evita ciclos por
  rama como Profundidad. La heuristica se crea con el deposito del mundo
  (`crear_heuristica(deposito)`) y `gui/panel_control.py` se la pasa a `buscar_avara`.
- Amplitud: desempate por orden de los sucesores, conjunto de estados generados global y
  la meta tambien cuenta como nodo expandido (`busqueda/no_informada/amplitud.py`).
- Libreria de GUI: pygame-ce. Velocidad de la animacion: 400 ms por casilla, con pausa,
  paso a paso y cambio de velocidad (`gui/animacion.py`).
- Sprites de 64 x 64 px cargados por `gui/cargador_sprites.py`. Pruebas con `unittest`.

Pendientes (los algoritmos que faltan):

- **A***: `busqueda/informada/a_estrella.py` (criterio de desempate entre nodos con el mismo f).
  Puede reutilizar la heuristica de `busqueda/informada/heuristica.py`, que es admisible.
- **Justificacion de admisibilidad de la heuristica** para el informe: h = 0,5 x (distancia
  Manhattan al primer cultivo, pasando por el deposito si no hay fertilizante, + cultivos
  pendientes - 1). 0,5 es el costo minimo de un paso, asi que h nunca sobreestima.
- Cada algoritmo nuevo debe agregarse a `ALGORITMOS_DISPONIBLES` en
  `gui/panel_control.py` para que la interfaz pueda ejecutarlo.
