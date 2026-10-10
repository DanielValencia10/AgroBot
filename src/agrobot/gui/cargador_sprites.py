"""
Archivo:       src/agrobot/gui/cargador_sprites.py
Objetivo:      Cargar los sprites desde assets/sprites/ y entregarlos por nombre a los
               paneles que dibujan la cuadricula y la animacion, siendo el unico
               archivo del proyecto que conoce la ruta de assets/.
Responsabilidad:
    SI hace:
        - Cargar desde disco cada imagen listada en assets/README.md
          (casilla_libre, obstaculo, robot, robot_en_avioneta, avioneta, deposito,
          cultivo_seco, cultivo_tratado) y mantenerlas disponibles en memoria.
        - Exponer un diccionario nombre -> imagen cargada, para que los paneles pidan
          el sprite por nombre sin conocer la ruta en disco.
        - Exponer la correspondencia entre cada codigo de celda del archivo de mundo
          (0 a 5, segun constantes.py) y el nombre del sprite que le corresponde por
          defecto (por ejemplo, codigo 3 -> "cultivo_seco"; el cambio a
          "cultivo_tratado" y a "robot_en_avioneta" lo decide cada panel segun el
          estado dinamico, no este archivo).
    NO hace:
        - No decide en que posicion de la cuadricula se dibuja cada sprite ni como se
          anima la transicion entre sprites (eso es de panel_mundo.py y animacion.py).
        - No conoce Estado ni logica de busqueda: solo traduce codigos de celda /
          nombres a imagenes.
        - No es usado por ningun archivo fuera de gui/ (es el unico que conoce
          assets/).
Importa de:
    - constantes: para los codigos de celda (CODIGO_LIBRE, CODIGO_OBSTACULO,
      CODIGO_AGROBOT, CODIGO_CULTIVO_SECO, CODIGO_DEPOSITO, CODIGO_AVIONETA) usados al
      mapear codigo -> nombre de sprite, y para el tamano de la cuadricula si se
      necesita al calcular el tamano de dibujo de cada sprite.
Lo importan:
    - gui/panel_mundo.py (para dibujar la cuadricula inicial con los sprites
      correctos).
    - gui/animacion.py (para dibujar cada paso de la animacion, incluyendo el cambio a
      "robot_en_avioneta" y "cultivo_tratado" segun el estado actual).
Contrato previsto:
    - cargar_sprites(): recorre assets/sprites/ y retorna un diccionario que mapea el
      nombre de cada sprite (sin extension, por ejemplo "robot",
      "robot_en_avioneta") a la imagen ya cargada en memoria.
    - obtener_nombre_sprite_por_codigo(codigo_de_celda): recibe un codigo de celda del
      archivo de mundo (0 a 5) y retorna el nombre de sprite que le corresponde por
      defecto (sin considerar aun el estado dinamico, que puede sobreescribir este
      valor en el panel que dibuja).
PENDIENTE:
    - Libreria de GUI a usar (depende de la misma decision de
      gui/ventana_principal.py), ya que determina el formato concreto en que se
      cargan y manipulan las imagenes.
    - Tamano final en pixeles de cada sprite (se sugiere 64x64 px en
      assets/README.md, a confirmar por el equipo).
"""
