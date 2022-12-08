# Template project for ssdd-lab

# ENLACE GITHUB
https://github.com/MarioTriMar/SSDDMario


# EJECUCIÓN SERVICIO CATÁLOGO
Para realizar la ejecución del servicio del catálogo haremos lo siguiente:

1º Necesitaremos el proxy del servicio principal, una vez lo sepamos debemos añadirselo al catalog.config (línea MainProxy.Proxy), ya que,
el servicio obtendrá el proxy desde ahí.

2º Ejecutar /run_service. 

Una vez hecho esto el servicio lo primero que hará será anunciarse en el servidor principal y continuará haciendolo cada 25 segundos.
Además de esto estará disponible para recibir invocaciones remotas.
Hay que destcar la existencia de dos archivos de persistencia donde se guardarán el idMedia junto con su nombre ("mediaName.json") y los tags que cada usuario asigne a las diferentes medias ("mediaTags.json").
Estos dos archivos son leidos al arrancar el servicio para que las busquedas se hagan accediendo a memoria sin necesidad de leer cada vez 
que se necesite.

Cabe mencionar la existencia de los siguientes fichero:
    - Fichero "file.py" dentro de /iceflix el cuál fue usado como una  pequeña implementación del FileService para probar las invocaciones newMedia y removeMedia.
    - Fichero "principal.py" dentro de /iceflix el cuál fue usado como una pequeña implementación del servicio principal para probar el funcionamiento de newService y de announce



# ACLARACIÓN DISABLES PYLINT
W0613 -> Unused argument.
Este warning aparecía debido al argumento argv.
C0103 -> Name doesn't fit the naming convention
Esto se debe a que los métodos del sirviente no se ajustan a los nombre de python.
C0116 -> Missing function docstring.
C0115 -> Missing class docstring.
C0301 -> Line too long.
Este se debe a algunas líneas de mi código, en especial algunos if, que sobrepasan la opción max-line-length de pylint.
C0303 -> Trailing whitespace.
Este se debe a los espacios en blanco entre un final de linea y una nueva linea.
C0413 -> Wrong import position
E0401 -> Import error.
Pylint no es capaz de importar un modulo.



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
