# Agente de busqueda de empleos

Este proyecto usa CrewAI, Gemini y Tavily para buscar ofertas laborales en la web, analizarlas contra un CV en formato Markdown y generar un reporte final en `reporte_empleos.md`.

## Requisitos previos

- Python 3.10 o superior.
- Una API key de Gemini.
- Una API key de Tavily.
- PowerShell, CMD o una terminal compatible.

## 1. Crear el entorno virtual, instalar dependencias y ejecutar

### 1. Abrir una terminal en la carpeta del proyecto

Ubicate dentro de la carpeta donde clonaste o descargaste el proyecto:

```powershell
cd agente-empleos
```

Si el proyecto esta dentro de otra carpeta, primero navegá hasta esa ubicacion y luego entrá al directorio del repositorio.

### 2. Crear el entorno virtual

En Windows con PowerShell:

```powershell
python -m venv .venv
```

Si `python` no funciona, probá con:

```powershell
py -m venv .venv
```

### 3. Activar el entorno virtual

En Windows con PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación del entorno por permisos de ejecución, ejecutá:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Luego volvé a activar el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

Cuando el entorno esté activo, deberías ver `(.venv)` al inicio de la línea de la terminal.

### 4. Instalar los paquetes requeridos

Con el entorno virtual activo, instalá las dependencias del archivo `requirements.txt`:

```powershell
pip install -r requirements.txt
```

El archivo de requerimientos instala:

- `crewai`: framework para crear y coordinar agentes.
- `tavily-python`: cliente para realizar busquedas web con Tavily.
- `python-dotenv`: carga variables de entorno desde el archivo `.env`.

### 5. Configurar las API keys

Creá o editá el archivo `.env` en la raiz del proyecto con esta estructura:

```env
GEMINI_API_KEY=tu_api_key_de_gemini
TAVILY_API_KEY=tu_api_key_de_tavily
```

Importante: no compartas ni subas el archivo `.env` a repositorios publicos, porque contiene credenciales privadas.

### 6. Ejecutar el agente

Con el entorno virtual activo y las API keys configuradas, ejecutá:

```powershell
python src/main.py
```

El proceso:

1. Carga las variables del archivo `.env`.
2. Lee el CV desde `data/cv.md`.
3. Busca ofertas laborales usando Tavily.
4. Analiza las ofertas contra el perfil del CV.
5. Genera el archivo `reporte_empleos.md` en la raiz del proyecto.

## 2. Configurar el rol y el perfil de busqueda

La configuracion principal de la busqueda esta en `src/main.py`.

Actualmente el proyecto define dos agentes:

- `buscador`: se encarga de buscar ofertas laborales reales en la web.
- `analista`: se encarga de comparar las ofertas encontradas contra el CV y generar el reporte.

### Cambiar el rol objetivo

Para modificar el tipo de puestos que queres buscar, editá el agente `buscador` en `src/main.py`:

```python
buscador = Agent(
    role='Scouter de Empleos HSE y Medio Ambiente',
    goal='Encontrar links reales y vigentes de ofertas de empleo para el area ambiental e industrial en Argentina.',
    backstory='Sos un headhunter especialista en el mercado laboral argentino...',
    tools=[buscar_web_tool],
    llm=gemini_llm,
    verbose=True
)
```

Campos importantes:

- `role`: nombre del rol que cumple el agente.
- `goal`: objetivo concreto de la busqueda.
- `backstory`: contexto que ayuda al agente a decidir que resultados son relevantes.

Ejemplo para buscar puestos de Data Analyst:

```python
buscador = Agent(
    role='Scouter de empleos Data Analyst',
    goal='Encontrar ofertas reales y recientes para roles de Data Analyst, BI Analyst y Reporting Analyst en Argentina.',
    backstory='Sos un recruiter especializado en perfiles de datos, reporting, SQL, dashboards y herramientas de BI.',
    tools=[buscar_web_tool],
    llm=gemini_llm,
    verbose=True
)
```

### Cambiar los terminos de busqueda

Los terminos que usa el agente estan dentro de la tarea `tarea_busqueda`:

```python
tarea_busqueda = Task(
    description=f"Necesito que encuentres ofertas laborales reales y RECIENTES..."
                "1. 'Analista de Medio Ambiente Argentina'\n"
                "2. 'Coordinador Ambiental planta'\n"
                "3. 'Responsable de Medio Ambiente LinkedIn Argentina'\n"
                "4. 'Gestion de efluentes empleo'\n"
                "5. 'Seguridad e Higiene y Medio Ambiente'\n\n",
    expected_output="Un listado detallado de al menos 5 ofertas encontradas...",
    agent=buscador
)
```

Para adaptar la busqueda, cambiá esa lista por consultas relacionadas al rol objetivo.

Ejemplo para un perfil de Data Analyst:

```python
"1. 'Data Analyst Argentina'\n"
"2. 'Analista de Datos SQL Power BI'\n"
"3. 'Business Intelligence Analyst Argentina'\n"
"4. 'Reporting Analyst empleo remoto'\n"
"5. 'Data Analyst LinkedIn Argentina'\n\n"
```

### Cambiar el criterio de analisis

El agente `analista` decide que ofertas hacen mejor match con el perfil:

```python
analista = Agent(
    role='Auditor de Match Laboral',
    goal='Filtrar y seleccionar ofertas web que hagan un excelente match con el perfil...',
    backstory='Sos un selector de personal experto en medio ambiente...',
    llm=gemini_llm,
    verbose=True
)
```

Tambien podés ajustar la tarea `tarea_analisis` para priorizar ubicacion, modalidad o seniority:

```python
tarea_analisis = Task(
    description="Analizá exhaustivamente el listado crudo que consiguió el buscador. "
                "Comparalo con el CV de la persona en data/cv.md. "
                "Priorizá puestos remotos, híbridos o ubicados en Argentina.",
    expected_output="Un reporte detallado en Markdown...",
    agent=analista,
    output_file='reporte_empleos.md'
)
```

Recomendacion: cuanto mas especifico sea el rol, mejores resultados devuelve el agente. Conviene definir:

- Rol objetivo: por ejemplo, `Analista Ambiental`, `Data Analyst`, `Diseñador UX`, `Backend Developer`.
- Seniority: trainee, junior, semi senior, senior.
- Ubicacion: ciudad, provincia, pais o remoto.
- Modalidad: presencial, hibrido o remoto.
- Palabras clave tecnicas: herramientas, tecnologias, certificaciones o industrias.
- Portales o fuentes preferidas: LinkedIn, Computrabajo, Bumeran, paginas de empresas, etc.

## 3. CV en formato Markdown

El CV debe guardarse en:

```text
data/cv.md
```

El nombre del archivo debe ser exactamente:

```text
cv.md
```

Si el archivo no existe o tiene otro nombre, el programa no va a poder leer el perfil y va a mostrar un error.

### Estructura recomendada del CV

El CV deberia estar en formato Markdown, con secciones claras. Esta estructura funciona bien para que el agente pueda entender el perfil:

```markdown
# NOMBRE Y APELLIDO

**Ubicacion:** Ciudad, Provincia, Pais
**Contacto:** telefono | email | LinkedIn

## SOBRE MI

Resumen profesional breve. Incluir area de especializacion, experiencia principal,
tipo de roles buscados, industrias de interes y fortalezas diferenciales.

## EXPERIENCIA LABORAL

### Nombre del puesto
**Empresa** | Modalidad
*mes año - actualidad o mes año - mes año*

* Responsabilidad o logro principal.
* Herramientas, procesos o tecnologias utilizadas.
* Indicadores, resultados o impacto si aplica.
* Tareas relevantes para el tipo de empleo buscado.

### Otro puesto
**Empresa** | Modalidad
*mes año - mes año*

* Responsabilidad o logro.
* Responsabilidad o logro.

## EDUCACION

* **Titulo o carrera** | Institucion (año - año)
* **Otro estudio relevante** | Institucion (año)

## CERTIFICACIONES Y CURSOS

* **Nombre de la certificacion** | Institucion (año)
* **Nombre del curso** | Institucion (año)

## HABILIDADES

* **Tecnicas:** herramienta 1, herramienta 2, herramienta 3.
* **Blandas:** liderazgo, comunicacion, organizacion.
* **Idiomas:** idioma y nivel.

## PREFERENCIAS DE BUSQUEDA

* **Roles objetivo:** rol 1, rol 2, rol 3.
* **Ubicacion:** ciudad, provincia, pais o remoto.
* **Modalidad:** presencial, hibrido o remoto.
* **Seniority:** trainee, junior, semi senior, senior.
* **Industrias de interes:** industria 1, industria 2.
* **Disponibilidad:** inmediata, 15 dias, 30 dias, etc.
```

### Consejos para mejorar el match

- Usar nombres de puestos concretos, no solo descripciones generales.
- Incluir herramientas, tecnologias, normativas o metodologias relevantes.
- Agregar logros medibles cuando sea posible.
- Mantener el CV actualizado antes de ejecutar el agente.
- Incluir una seccion de preferencias de busqueda si queres orientar mejor los resultados.

## Archivos principales del proyecto

```text
agente-empleos/
├── data/
│   └── cv.md
├── src/
│   └── main.py
├── .env
├── requirements.txt
├── reporte_empleos.md
└── README.md
```

## Problemas comunes

### Error: faltan las API keys

Verificá que exista el archivo `.env` en la raiz del proyecto y que tenga:

```env
GEMINI_API_KEY=tu_api_key_de_gemini
TAVILY_API_KEY=tu_api_key_de_tavily
```

### Error: no se encontro `data/cv.md`

Verificá que el CV este guardado exactamente en:

```text
data/cv.md
```

### El reporte trae ofertas poco relacionadas

Revisá y ajustá:

- Los terminos de busqueda en `tarea_busqueda`.
- El `goal` y `backstory` del agente `buscador`.
- El criterio del agente `analista`.
- La seccion de preferencias dentro de `data/cv.md`.


### Para volver a ejecutar el agente (Cualquier otro día)

Cuando quieras volver a correr la búsqueda (por ejemplo, una vez por semana), no hace falta reinstalar nada. Solo abrí una terminal en la carpeta del proyecto y ejecutá:

```powershell
# 1. Activás el entorno virtual que ya existe
.\.venv\Scripts\Activate.ps1

# 2. Corrés el agente
python .\src\main.py
```