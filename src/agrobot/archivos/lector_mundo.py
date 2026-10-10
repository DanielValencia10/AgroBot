"""
Archivo:       src/agrobot/archivos/lector_mundo.py
Objetivo:      Leer un archivo de texto (.txt) que describe un mundo AgroBot (10 filas
               por 10 numeros separados por espacios) y construir el objeto Mundo
               correspondiente, validando el formato antes de construirlo.
Responsabilidad:
    SI hace:
        - Leer el archivo de texto dado y parsear sus 10 filas de 10 numeros cada una.
        - Validar el formato:
            - Tamano exacto de 10 filas por 10 columnas.
            - Todos los codigos deben ser validos segun constantes (0 a 5).
            - Debe haber exactamente un 2 (AgroBot), un 4 (deposito) y un 5 (avioneta).
            - Debe haber al menos un 3 (cultivo seco).
        - Construir y retornar un objeto Mundo con los datos ya validados: obstaculos,
          posicion del deposito, posicion inicial de la avioneta, posicion inicial del
          robot y conjunto de cultivos secos iniciales.
        - Reportar un error claro cuando el archivo no cumple alguna de las
          validaciones anteriores.
    NO hace:
        - No construye el Estado dinamico del problema (eso puede vivir en estado.py o
          en agrobot_problema.py, segun se resuelva ese PENDIENTE).
        - No conoce algoritmos de busqueda ni la GUI.
Importa de:
    - modelo.mundo (Mundo): para construir y retornar la instancia final.
    - constantes: para los codigos validos de celda (CODIGO_LIBRE, CODIGO_OBSTACULO,
      CODIGO_AGROBOT, CODIGO_CULTIVO_SECO, CODIGO_DEPOSITO, CODIGO_AVIONETA) y el
      tamano esperado de la cuadricula (TAMANO_CUADRICULA) usados en la validacion.
Lo importan:
    - gui/panel_control.py (para cargar el archivo de mundo elegido por el usuario).
    - main.py (eventualmente, si la carga inicial se hace fuera de la GUI).
    - tests/test_lector_mundo.py (para verificar las validaciones).
Contrato previsto:
    - leer_mundo_desde_archivo(ruta_del_archivo): recibe la ruta de un archivo .txt,
      valida su formato segun las reglas descritas arriba y retorna un objeto Mundo
      construido a partir de su contenido. Si el archivo no cumple el formato
      esperado, señala el error de validacion correspondiente en vez de construir un
      Mundo invalido.
"""
