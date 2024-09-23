#Tópicos Especiales en Telemática


Estudiante(s): Juan Jose Velez Orozco, jjvelezo@eafit.edu.co, Juan Esteban Pavas, jepavase@eafit.edu.co

Profesor: JUAN CARLOS MONTOYA MENDOZA, jcmontoyay@eafit.edu.co

# Reto N1. Aplicaciones P2P

## 1. Breve descripción de la actividad

Este proyecto desarrolla un sistema de comunicación Peer-to-Peer (P2P) no estructurado utilizando gRPC para la transferencia de archivos entre peers. Cada peer puede actuar como cliente y servidor, permitiendo registrar y buscar archivos dentro de la red, así como descargar archivos directamente de otros peers.

### 1.1. Aspectos cumplidos o desarrollados de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

- Conexion entre webserver y redirecion al tracker.
- Manejo de registros en tracker.
- Tracker registra los archivos de cada peer en la red.
- Tracker permite la búsqueda de archivos en la red.
- Tracker se encarga de gestionar Fragmentación.
- Tracker encraga de gestionar replicación de archivos.
- Tracker asume la tarea de consistencia en la red.
- Los peers pueden preguntar a otros peers por el archivo (Comunicación directa)
- Manejo de Concurrencia en la red.
- Manejor de Varias Solicitudes al Tiempo.
- Uso de gRPC para la comunicación.



### 1.2. Aspectos NO cumplidos o desarrollados de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

- La replicacion se hace al azar (no por disponibilidad o geografia).
- No se guardan archivos en el tiempo (falta de persistencia).
- Manejo de archivos duplicados básico.
- Intento de desarrollo en Java.
- Manejo IDs.


## 2. Información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.

Este proyecto implementa una arquitectura Peer-to-Peer no estructurada con un enfoque en la eficiencia y robustez de la comunicación, usando gRPC para la interacción entre nodos. Cada nodo puede actuar tanto como cliente como servidor, facilitando una red descentralizada donde los peers se registran en un tracker centralizado para localizar archivos pero gestionan la transferencia de archivos directamente entre ellos.

###Arquitectura y patrones:
- **Peer-to-Peer No Estructurado:** Cada peer se registra en un tracker centralizado que facilita la búsqueda de archivos pero no interviene en la transferencia directa de archivos.
- **Comunicación Directa entre Peers:** Una vez que un archivo es localizado mediante el tracker, los peers involucrados establecen una conexión directa para la transferencia de archivos.

- **Cliente-Servidor:** Utilizado para la interacción entre los peers y el tracker para registrar y buscar información.

### Mejores prácticas:
- **Separación de responsabilidades:** Clara distinción entre la lógica de la interfaz de usuario y la lógica de manejo de red para mantener el código organizado y mantenible.





## 3. Descripción del ambiente de desarrollo y técnico

### Lenguaje de programación y herramientas utilizadas:
- Python 3.X
- gRPC 1.38.X
- Librerías: grpcio, grpcio-tools, socket (solo para conseguir la IP), futures, threading

### Como se compila y ejecuta:

- En AWS, se debe crear un entorno virtual y ejecutar:
`python3 -m venv venv
`source venv/bin/activate`
`pip install grpcio grpcio-tools``

- Para compilar y ejecutar se debe poner:
`nano tracker.py/webserver`
`nano torrent.proto`
`python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. torrent.proto`
Correr en cada PC: `python torrent.py/webserver.py/peernodo.py`

### Detalles técnicos y configuración de parámetros del proyecto:

- El web server escucha el puerto 50051, El tracker escucha el puerto 50052, entre peers escichan el peurto 50053.
- Los parametros de replicación y fragmentacion se pueden configurar.

### Estructura de directorios y archivos importantes del proyecto:

/
|-- tracker.py
|-- peernodo.py
|-- webserver.py
|-- torrent_pb2.py
|-- torrent_pb2_grpc.py
|-- torrent.proto


## 4. Descripción del ambiente de EJECUCIÓN (en producción)

### IP o nombres de dominio en nube o en la máquina servidor:

- La IP varia segun el momento que se ejecute la instancia (es variable).

### Como se lanza el servidor:

``python3 -m venv venv`
`source venv/bin/activate`
`pip install grpcio grpcio-tools`
`nano tracker.py/webserver`
`nano torrent.proto`
`python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. torrent.proto`
`python torrent.py/webserver.py/peernodo.py`

### Mini guía de usuario:

####1.Corre: `"peernodo.py"`:

'Menu:
1. Conectar al Tracker
2. Agregar archivo a la lista del peer  
3. Eliminar archivo de la lista del peer
4. Ver Lista del Peer
5. Salir'


####2.Subir Archivos:

'Ingresa tu opción: `2`
Ingresa el nombre del archivo a agregar: file3
Ingrese el tamaño del archivo en MB: `200`
Archivo 'file3' con tamaño 200 MB agregado a la lista del peer.'


####3.Ver lista de archivos:

'Menu:
1. Conectar al Tracker
2. Agregar archivo a la lista del peer
3. Eliminar archivo de la lista del peer
4. Ver Lista del Peer
5. Salir
Ingresa tu opción: `4`

Lista de archivos del peer:
- file3 (Size: 200)'



####4.Conexion al tracker:

'Menu:
1. Conectar al Tracker
2. Agregar archivo a la lista del peer
3. Eliminar archivo de la lista del peer
4. Ver Lista del Peer
5. Salir
Ingresa tu opción: `1`
Peer registrado con éxito: status: "Registered successfully"
updated_files {
  file_name: "file3_part0"
  file_size: 100
}
updated_files {
  file_name: "file3_part1"
  file_size: 100
}
'


####4. Buscar archivo:

'Menú del Tracker:
1. Buscar archivo
2. Salir del Tracker
Ingresa tu opción: `1`
Nombre del archivo para obtener: `file2`
Preguntando a 192.168.20.85 por el archivo 'file2'...
Recibiendo archivo...
Archivo recibido!'


####5. Desconexión del Tarcker

'Menú del Tracker:
1. Buscar archivo
2. Salir del Tracker
Ingresa tu opción: `2`
Respuesta del tracker: Unregistered successfully
Peer desconectado del Tracker y canal cerrado.'

## 5. Otra información relevante para esta actividad.

<Incluya cualquier otra información que considere relevante para comprender o utilizar el proyecto.>


# Referencias:

- https://www.ionos.com/digitalguide/server/know-how/what-is-p2p/?srsltid=AfmBOora1gSWBWlBdRJW4nMD9ZuNy2yfNKuWWUnKc02-s8xs56OVIts-
- https://reactiveprogramming.io/blog/es/estilos-arquitectonicos/cliente-servidor
- http://resources.pandasecurity.com/enterprise/solutions/8.%20WP%20PCIP%20que%20es%20p2p.pdf
- https://bth.diva-portal.org/smash/get/diva2:830386/FULLTEXT01.pdf
- https://reactiveprogramming.io/blog/es/estilos-arquitectonicos/p2p
- https://www.redeszone.net/tutoriales/internet/tipos-redes-p2p-peer-to-peer/#415251-redes-p2p-no-estructuradas
- https://driveuploader.com/blog/the-evolution-of-file-sharing-from-napster-to-blockchain/#:~:text=Napster%20was%20one%20of%20the,Gnutella%2C%20Kazaa%2C%20and%20eDonkey.
- https://www.tlm.unavarra.es/~daniel/docencia/doctorado/2007-08/slides/Tema4a-P2P.pdf
- https://www.redeszone.net/tutoriales/internet/tipos-redes-p2p-peer-to-peer/#415251-protocolo-de-busqueda-distribuida-en-redes-p2p-chord
- https://hazelcast.com/glossary/distributed-hash-table/
- https://repositorio.uniandes.edu.co/server/api/core/bitstreams/96a89b3f-6b01-4261-9613-1b2cc964958e/content
- https://es.wikibrief.org/wiki/Chord_%28peer-to-peer%29
- https://revistas.unisimon.edu.co/index.php/innovacioning/article/view/2021/4678
- https://www.britannica.com/technology/P2P
- https://revistas.unisimon.edu.co/index.php/innovacioning/article/view/2021/4678
- https://www.alotceriot.com/es/comprension-de-la-comunicacion-entre-pares-una-guia-completa/#:~:text=La%20comunicaci%C3%B3n%20entre%20pares%20
