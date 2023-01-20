# Template project for ssdd-lab

# ENLACE GITHUB
https://github.com/MarioTriMar/SSDDMario

EL CÓDIGO DE LA ENTREGA FINAL SE ENCUENTRA EN LA RAMA "entrega2"

# CONFIGURACIÓN 
1. run_icestorm: este fichero no ha sido modificado, excepto el nombre del topic FileAvailabilityAnnounce, el cuál se nos proporcionó con una "s" al final cuando 
en la guía del laboratorio aparece que debe ser si "s".
2. run_service: respecto a la anterior entrega, se tuvo que cambiar el fichero .config, pasando de catalog.config a icestorm.config, de donde
el código obtiene  el TopicManager.
3. Además de esto, para que el run_service funcionase se hizo lo siguiente:
    - En el setuo.cfg sólo se dejó la línea del catálogo.
    - Se tuvo que crear a mano el fichero setup.py.
    - En el fichero iceflix/cli.py tuvimos que adaptar el método catalog_service para que este lanzara catalog.py
    - Después de esto en el directorio raíz se hizo pip install -e .
4. Hay que destacar la existencia de dos archivos de persistencia donde se guardarán el idMedia junto con su nombre ("mediaName.json") y los tags que cada usuario asigne a las diferentes medias ("mediaTags.json"). Estos dos archivos son leidos al arrancar el servicio para que las busquedas se hagan accediendo a memoria sin necesidad de leer cada vez 
que se necesite.
5. Cabe mencionar la existencia de los siguientes fichero:
    - Fichero "file.py" dentro de /iceflix el cuál fue usado durante la primera entrega como una  pequeña implementación del FileService para probar las invocaciones newMedia y removeMedia.
    - Fichero "client.py" dentro de /iceflix el cuál fue usado durante la primera entrega como una pequeña implementación para probar métodos con el addTags, removeTags, etc.
    - Fichero "authenticator.py" dentro de /iceflix el cuál fue usado durante la primera estrega como pequeña iplementación para probar la comunicación entre servicios.
    - Fichero "principal.py" dentro de /iceflix el cuál fue usado como una pequeña implementación del servicio principal para probar el funcionamiento del announce usando IceStorm.

En cuanto a las librerias utilizadas: 
  - Las necesarias para utilizar Ice (Ice, IceFlix).
  - La necesaria para usar IceStorm (IceStorm).
  - La librería estándar sys.
  - La librería para poder abrir hilos (threading)-
  - La librería os para poder cerrar el programa desde un hilo, ya que sys.exit no funcionaba correctamente. 
  - La librería random, usada para seleccionar servicios aleatorios.
  - La librería json para la persistencia.
# EJECUCIÓN SERVICIO CATÁLOGO
Para realizar la ejecución del servicio del catálogo haremos lo siguiente:

1. Situarnos en .../SSDDMario

2. Ejecutar ./run_icestorm

3. Ejecutar ./run_service. 

Una vez hecho esto el servicio se subscribirá y se hará publicador de los tres topics que necesita.  
Tras esto esperará 12 segundos mientras recibe anunciamientos y comprobará si hay algun servidor principal.  
Si no lo hay el programa abortará. En caso de que sí lo haya mirará si es el primer catálogo en anunciarse. Si es así avisará por terminal que es el primero en llegar y considerará que sus datos persistentes son los últimos. En caso contrario, pedirá al catalogo que ha llegado antes que informe sobre sus datos para actualizarse, mostrará por pantalla todos los cambios recibidos.  
Una vez hecho esto el catálogo se anunciará cada 8 segundos estando ya disponible para la ejecución de toda su funcionalidad.

En la terminal veremos los servicios que llegan nuevos y los que se refrescan cada X tiempo. En caso de que no se refresquen en 12 segundo estos serán supuestos por muertos y se borrarán.


# ACLARACIÓN DISABLES PYLINT
- C0103 -> Name doesn't fit the naming convention, esto se debe a que los nombres de la interfaz no se ajustan a las preferencias del lenguaje python. Se desactivo ya que no se puede modificar los nombres.
- C0301 -> Line too long, este se debe a algunas líneas de mi código, en especial algunos if, prints y creación de hilos sobrepasan la opción max-line-length de pylint. Este fue deshabilitado debido a que desde mi punto de vista es mas legible conforme está que no con saltos de linea.
- C0303 -> Trailing whitespace, este se debe a los espacios en blanco entre un final de linea y una nueva linea. Se deshabilitó debido a que me era imposible arreglarlos todos.
- WO613 -> Este nos dice que el argumento Current de los métodos de las interfaces no están siendo usados, pero, es necesaria su existencia.
- E1101 -> module IceStorm has no TopicManagerPrx/NoSuchTopic member. Se deshabilitó debido a no saber como ponerle solución sin afectar a la funcionalidad.

Tras deshabilitar estos mencionados y solucionar otros warnings la nota obtenida es de un 9'42


This repository is a Python project template.
It contains the following files and directories:

- `configs` has several configuration files examples.
- `iceflix` is the main Python package.
  You should rename it to something meaninful for your project.
- `iceflix/__init__.py` is an empty file needed by Python to
  recognise the `iceflix` directory as a Python module.
- `iceflix/cli.py` contains several functions to handle the basic console entry points
  defined in `python.cfg`.
  The name of the submodule and the functions can be modified if you need.
- `iceflix/iceflix.ice` contains the Slice interface definition for the lab.
- `iceflix/main.py` has a minimal implementation of a service,
  without the service servant itself.
  Can be used as template for main or the other services.
- `pyproject.toml` defines the build system used in the project.
- `run_client` should be a script that can be run directly from the
  repository root directory. It should be able to run the IceFlix
  client.
- `run_service` should be a script that can be run directly from the
  repository root directory. It should be able to run all the services
  in background in order to test the whole system.
- `setup.cfg` is a Python distribution configuration file for Setuptools.
  It needs to be modified in order to adeccuate to the package name and
  console handler functions.
