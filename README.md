# Gestión de carreras de galgos

Aplicación de escritorio académica desarrollada en Python para consultar información de perros, propietarios, cuidadores y carreras almacenada en MongoDB. El proyecto explora autenticación contra MongoDB, permisos por roles y relaciones entre colecciones desde una interfaz Tkinter.

> **Estado:** prototipo académico. La búsqueda y autenticación están implementadas; las operaciones de alta, actualización y eliminación continúan en desarrollo.

## Tecnologías

- Python
- Tkinter
- MongoDB y PyMongo
- Pillow

## Funcionalidades implementadas

- Inicio de sesión con usuarios de MongoDB.
- Distinción entre roles administrativos y limitados.
- Consulta de perros por nombre, origen, edad y color.
- Consulta de propietarios y cuidadores con sus perros asociados.
- Consulta de carreras por fecha, lugar, participantes y tiempos.
- Interfaz gráfica de escritorio.

## Ejecución local

### Requisitos

- Python 3
- MongoDB en ejecución en `localhost:27017`
- Un usuario de MongoDB con acceso a la base `galgos`

### Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python programa.py
```

En Windows, activa el entorno con:

```powershell
.venv\Scripts\Activate.ps1
```

La aplicación solicita las credenciales al iniciar sesión; no deben guardarse en el código ni versionarse.

## Modelo de datos

El proyecto utiliza las colecciones `perros`, `carreras`, `dueños` y `cuidadores`. Las relaciones se representan mediante identificadores de documentos.

## Enfoque de seguridad

- Credenciales ingresadas en tiempo de ejecución.
- Separación de permisos según roles de MongoDB.
- Conexión local para fines de aprendizaje.
- Recomendación de utilizar usuarios con privilegios mínimos.

## Próximas mejoras

- Completar las operaciones de creación, actualización y eliminación.
- Separar interfaz, lógica de negocio y acceso a datos.
- Incorporar validaciones y pruebas automatizadas.
- Parametrizar host, puerto y base de datos mediante variables de entorno.

## Autor

Maximiliano Pincheira — estudiante de Ingeniería Informática en INACAP.
