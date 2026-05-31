import os
from datetime import datetime
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from tavily import TavilyClient

# Cargar variables de entorno del .env
load_dotenv()

def cargar_cv():
    ruta_cv = os.path.join("data", "cv.md")
    if not os.path.exists(ruta_cv):
        print("❌ Error: No se encontró el archivo de perfil en 'data/cv.md'")
        return None
    with open(ruta_cv, "r", encoding="utf-8") as f:
        return f.read()

# 1. Herramienta de búsqueda directa usando el cliente oficial de Tavily
@tool("Buscar empleos en la web")
def buscar_web_tool(query: str) -> str:
    """Útil para buscar ofertas de empleo vigentes en portales de trabajo usando una consulta de texto."""
    try:
        # Inicializamos el cliente oficial con tu API key
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        # Realizamos la búsqueda simple en la web (equivalente al search de LangChain)
        response = client.search(query=query, max_results=8)
        return str(response)
    except Exception as e:
        return f"Error al buscar en la web: {str(e)}"

def run_agent():
    if not os.getenv("GEMINI_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        print("❌ Error: Faltan las API keys en el archivo .env")
        return

    perfil_usuario = cargar_cv()
    if not perfil_usuario:
        return

    # 2. Configurar el LLM con la clase nativa de CrewAI v1
    gemini_llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=os.getenv("GEMINI_API_KEY")
    )

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    # 3. Definición de Agentes
    buscador = Agent(
        role='Scouter de Empleos HSE y Medio Ambiente',
        goal='Encontrar links reales y vigentes de ofertas de empleo para el área ambiental e industrial en Argentina.',
        backstory='Sos un headhunter especialista en el mercado laboral argentino. Sabés que las ofertas no siempre dicen "Entre Ríos", sino que buscan para plantas industriales. Tu prioridad absoluta es conseguir URLs reales de postulaciones en portales como LinkedIn, Computrabajo, Bumeran o páginas de empresas.',
        tools=[buscar_web_tool],
        llm=gemini_llm,
        verbose=True
    )

    analista = Agent(
        role='Auditor de Match Laboral',
        goal='Filtrar y seleccionar ofertas web que hagan un excelente match con el perfil de Nombre y Apelido.',
        backstory='Sos un selector de personal experto en medio ambiente. Revisás el listado del buscador y cruzás los datos con su experiencia en <detalle de experiencia, nombre y actividades>.',
        llm=gemini_llm,
        verbose=True
    )

    # 4. Definición de Tareas - AQUÍ ESTÁ EL AJUSTE CLAVE
    tarea_busqueda = Task(
        description=f"Necesito que encuentres ofertas laborales reales y RECIENTES (publicadas cerca de {fecha_hoy}). "
                    "Para tener éxito, debés realizar búsquedas en la herramienta combinando estos términos exactamente:\n"
                    "1. 'Analista de Medio Ambiente Argentina'\n"
                    "2. 'Coordinador Ambiental planta'\n"
                    "3. 'Responsable de Medio Ambiente LinkedIn Argentina'\n"
                    "4. 'Gestión de efluentes empleo'\n"
                    "5. 'Seguridad e Higiene y Medio Ambiente'\n\n"
                    "Trae CUALQUIER oferta de Argentina que use estos títulos en los últimos meses. No te limites solo a Entre Ríos en la caja de búsqueda, traé los resultados generales del país para que luego el analista filtre.",
        expected_output="Un listado detallado de al menos 5 ofertas encontradas. Cada una DEBE incluir de forma obligatoria: Título del puesto, Empresa, Ubicación (Ciudad/Provincia) y la URL exacta de origen (link web).",
        agent=buscador
    )

    tarea_analisis = Task(
        description="Analizá exhaustivamente el listado crudo que consiguió el buscador. "
                    "Comparalo con el CV (data/cv.md) y armá el reporte. "
                    "Si encontrás puestos en Entre Ríos o zonas cercanas, dales prioridad absoluta. "
                    "Si encontrás puestos remotos o corporativos nacionales que apliquen a su perfil, incluilos también.",
        expected_output="Un reporte detallado en Markdown ('reporte_empleos.md'). Cada puesto listado debe incluir:\n"
                        "1. Nombre del Puesto y Empresa.\n"
                        "2. Ubicación / Modalidad.\n"
                        "3. Enlace directo para postularse (debe ser un link real aportado por el buscador).\n"
                        "4. % de Match Estimado (0-100%).\n"
                        "5. Puntos fuertes.",
        agent=analista,
        output_file='reporte_empleos.md'
    )

    # 5. Orquestación e inicio
    crew = Crew(
        agents=[buscador, analista],
        tasks=[tarea_busqueda, tarea_analisis],
        process=Process.sequential
    )

    print("🚀 Buscando posiciones óptimas con la estrategia de rastreo ajustada...")
    crew.kickoff()
    print("\n✨ Proceso finalizado. Resultados listos en 'reporte_empleos.md'")

if __name__ == "__main__":
    run_agent()