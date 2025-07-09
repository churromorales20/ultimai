import psycopg2
import numpy as np
import google.generativeai as genai
import time

# *********************** CONFIGURACIÓN ***********************
# Credenciales de la base de datos PostgreSQL (¡usa variables de entorno!)


DB_NAME = "ultimate_db"
DB_USER = "ultimate_user"
DB_PASSWORD = "ultimate_password"
DB_HOST = "172.28.0.2"
DB_PORT = 5432

# Clave de API de Google AI Gemini (¡usa variables de entorno!)
GOOGLE_API_KEY = "AIzaSyDuz_7HUA9hfzkB6NU0tPEWvYG9uaKpnP8"

# Modelos de Gemini AI
EMBEDDING_MODEL = 'gemini-embedding-exp-03-07' #Dimension = 768
COMPLETIONS_MODEL = 'gemini-2.0-flash'  # o 'gemini-pro'

# Tamaño del chunk para dividir las reglas
CHUNK_SIZE = 300  # Número de palabras por chunk
CHUNK_OVERLAP = 50 # Número de palabras de superposición entre chunks

# Número de reglas similares a recuperar
TOP_K = 3

# *********************** CONEXIÓN A LA BASE DE DATOS ***********************
def conectar_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# *********************** FUNCIONES DE EMBEDDING ***********************
genai.configure(api_key=GOOGLE_API_KEY) # Inicializa la API key de Gemini

def obtener_embedding(text, model_name=EMBEDDING_MODEL):
    """Genera un embedding para el texto utilizando el modelo de Gemini."""
    
    #model = genai.EmbModel(model_name)
    try:
        response = genai.embed_content(model=model_name,
                                    content=text,
                                    task_type="classification")
        
        print(f"chunk: {text}")
        return response['embedding']
    except Exception as e:
        print(f"Error al obtener el embedding: {e}")
        return None

# *********************** FUNCIONES DE BASE DE DATOS ***********************
def crear_tabla_reglas(conn):
    """Crea la tabla para almacenar las reglas y sus embeddings."""
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reglas_ultimate (
                id SERIAL PRIMARY KEY,
                regla_texto TEXT,
                embedding VECTOR(3072)
            );
        """)
        conn.commit()
        print("Tabla 'reglas_ultimate' creada o ya existente.")
    except Exception as e:
        print(f"Error al crear la tabla: {e}")
        conn.rollback()
    finally:
        cur.close()


def insertar_regla(conn, regla_texto, embedding):
    """Inserta una regla y su embedding en la base de datos."""
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO reglas_ultimate (regla_texto, embedding) VALUES (%s, %s)",
            (regla_texto, np.array(embedding).tolist()) #Castea el embedding a una lista de python
        )
        conn.commit()
        #print("Regla insertada correctamente.")
    except Exception as e:
        print(f"Error al insertar regla: {e}")
        conn.rollback()
    finally:
        cur.close()


def buscar_reglas_similares(conn, embedding_pregunta, top_k=TOP_K):
    """Busca las reglas más similares al embedding de la pregunta."""
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT regla_texto, embedding <-> %s AS distancia
            FROM reglas_ultimate
            ORDER BY distancia
            LIMIT %s;
            """,
            (np.array(embedding_pregunta).tolist(), top_k) #Castea el embedding a una lista de python
        )
        resultados = cur.fetchall()
        return resultados
    except Exception as e:
        print(f"Error al buscar reglas similares: {e}")
        return []
    finally:
        cur.close()


# *********************** FUNCIONES DE CHUNKING ***********************
def chunk_texto(texto, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    """Divide el texto en chunks de tamaño especificado con superposición."""
    palabras = texto.split()
    chunks = []
    for i in range(0, len(palabras), chunk_size - chunk_overlap):
        chunk = " ".join(palabras[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


# *********************** GENERACIÓN DEL PROMPT ***********************
def generar_prompt(pregunta, contexto):
    """Genera el prompt para el modelo de lenguaje."""
    return f"""Eres un experto juez de paz del Ultimate Frisbee. Responde a la siguiente pregunta analizando y aplicando tu criterio sobre el contexto proporcionado. Debes hacer todo lo posible por dar una respuesta aunque sea aproximada, y debes evaluar bien el contexto.
    
    Pregunta: {pregunta}
    
    Contexto:
    **Reglas WFDF de Ultimate 2025-2028**

    Versión Oficial vigente a partir del 01-01-2025

    **Introducción**

    El Ultimate es un deporte de equipo de siete contra siete que se juega con un disco volador. Se juega en un campo rectangular, aproximadamente la mitad del ancho de un campo de fútbol americano, con una zona de anotación en cada extremo. El objetivo de cada equipo es anotar un gol al hacer que un jugador atrape un pase en la zona de anotación que están atacando. Un lanzador no puede correr con el disco, pero puede pasar el disco en cualquier dirección a cualquier compañero de equipo. Cada vez que un pase es incompleto, se produce una pérdida de posesión, y el otro equipo debe establecer la posesión e intentar anotar en la zona de anotación opuesta. Los partidos suelen jugarse a 15 goles o alrededor de 100 minutos. El Ultimate es auto-arbitrado y sin contacto. El Espíritu de Juego guía la forma en que los jugadores arbitran el juego y se comportan en el campo.

    Muchas de estas reglas son de carácter general y cubren la mayoría de las situaciones, sin embargo, algunas reglas cubren situaciones específicas y anulan el caso general.

    Se pueden utilizar variaciones de la estructura básica y las reglas para dar cabida a competiciones especiales, número de jugadores, edad de los jugadores o espacio disponible. Consulte el Apéndice correspondiente para conocer las reglas adicionales que se aplican en

    o la estructura básica y las reglas pueden utilizarse para adaptarse a competiciones especiales, número de jugadores,
    edad de los jugadores o espacio disponible. Consulte el Apéndice correspondiente para conocer las reglas adicionales que se aplican a tipos específicos de
    Eventos de la Federación Mundial de Disco Volador (WFDF).

    {contexto}

    Responde en el siguiente formato JSON:
    {{
      "rule": "RULE_NUMBER",  // El número de la regla relevante (por ejemplo, "2.5"). **SIEMPRE DEBES PROPORCIONAR UN NÚMERO DE REGLA. NUNCA dejes este campo vacío. Da tu mejor shot**
      "explanation": "EXPLANATION_OF_WHY_THIS_RULE_APPLIES" // Una explicación concisa de por qué se aplica esta regla a la pregunta. Explica el razonamiento lo más claramente posible.
      "short_answer": "EG: Yes it applys" //Un respuesta corta  y consisa a la pregunta basada en la explanation
    }}

    Respuesta:
    """

# *********************** GENERACIÓN DE LA RESPUESTA ***********************
def generar_respuesta(prompt, model_name=COMPLETIONS_MODEL):
    """Genera una respuesta utilizando el modelo de lenguaje de Gemini."""
    model = genai.GenerativeModel(model_name)
    try:
        generation_config = genai.types.GenerationConfig(
          temperature=1.2,
         )
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        print(f"Error al generar la respuesta: {e}")
        return None


# *********************** FUNCIÓN PRINCIPAL PARA RESPONDER PREGUNTAS ***********************
def responder_pregunta(conn, pregunta):
    """Responde a una pregunta utilizando las reglas del Ultimate Frisbee."""
    #embedding_pregunta = obtener_embedding(pregunta)

    #if embedding_pregunta is None:
        #return "No se pudo generar el embedding para la pregunta."

    #resultados = buscar_reglas_similares(conn, embedding_pregunta)

    #if not resultados:
    #    return "No se encontraron reglas relevantes."

    contexto = cargar_reglas_desde_archivo_raw('rules_translated_with_initial_pages.txt')
    prompt = generar_prompt(pregunta, contexto)

    #print(prompt)
    respuesta = generar_respuesta(prompt)

    return respuesta


# *********************** FUNCIÓN PARA CARGAR REGLAS DESDE UN ARCHIVO ***********************
def cargar_reglas_desde_archivo_raw(archivo_path):
    """Carga las reglas desde un archivo de texto, las divide en chunks,
    genera los embeddings y los inserta en la base de datos."""
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{archivo_path}' no fue encontrado.")
    except Exception as e:
        print(f"Error al cargar las reglas desde el archivo: {e}")
# *********************** FUNCIÓN PARA CARGAR REGLAS DESDE UN ARCHIVO ***********************
def cargar_reglas_desde_archivo(conn, archivo_path):
    """Carga las reglas desde un archivo de texto, las divide en chunks,
    genera los embeddings y los inserta en la base de datos."""
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            reglas_texto = f.read()

        chunks = chunk_texto(reglas_texto) #Divide las reglas en chunks

        count = 0
        for chunk in chunks:
            embedding = obtener_embedding(chunk, EMBEDDING_MODEL)

            if embedding:
                insertar_regla(conn, chunk, embedding)
                count = count +1

                if count > 3:
                  time.sleep(60)
                  count = 0
            else:
                print(f"No se pudo generar el embedding para el chunk: {chunk[:50]}...") #Muestra los primeros 50 caracteres

        print(f"Se cargaron {len(chunks)} chunks de reglas desde el archivo.")

    except FileNotFoundError:
        print(f"Error: El archivo '{archivo_path}' no fue encontrado.")
    except Exception as e:
        print(f"Error al cargar las reglas desde el archivo: {e}")


# *********************** EJEMPLO DE USO ***********************
if __name__ == "__main__":
    conn = conectar_db()

    if conn:
        crear_tabla_reglas(conn) # Asegura que la tabla exista.

        # 1. Cargar reglas desde un archivo (opcional):
        archivo_reglas = 'rules_translated_with_initial_pages.txt' # Cambia esto a la ruta de tu archivo.
        #cargar_reglas_desde_archivo(conn, archivo_reglas)


        # 2. Ejemplo de pregunta:
        pregunta = "Si al moemnto d eintnetar recibir un pull el recptor deja caer el el disco, es un turnover?"
        respuesta = responder_pregunta(conn, pregunta)
        print(f"Pregunta: {pregunta}")
        print(f"Respuesta: {respuesta}")

        conn.close()
    else:
        print("No se pudo conectar a la base de datos.")