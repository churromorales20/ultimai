from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os

os.environ["GOOGLE_API_KEY"] = "AIzaSyDuz_7HUA9hfzkB6NU0tPEWvYG9uaKpnP8"
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

class PlayExplanation(BaseModel):
    rule: str = Field(description="El número de la regla relevante (por ejemplo, 2.5). **SIEMPRE DEBES PROPORCIONAR UN NÚMERO DE REGLA. NUNCA dejes este campo vacío. Da tu mejor shot")
    explanation: str = Field(description="EXPLANATION_OF_WHY_THIS_RULE_APPLIES, Una explicación concisa de por qué se aplica esta regla a la pregunta. Explica el razonamiento lo más claramente posible.")
    short_answer: str = Field(description="EG: Yes it applys, Un respuesta corta  y consisa a la pregunta basada en la explanation")


parser = PydanticOutputParser(pydantic_object=PlayExplanation)

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

def rule_detection_prompt():
    """Genera el prompt para el modelo de lenguaje."""
    return """Eres un experto juez de paz del Ultimate Frisbee. Responde a la siguiente pregunta analizando y aplicando tu criterio sobre el contexto proporcionado. Debes hacer todo lo posible por dar una respuesta aunque sea aproximada, y debes evaluar bien el contexto.
    

    
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

    {context}

    {format_instructions}

    """
def rule_interpreter():
    """Genera el prompt para el modelo de lenguaje."""
    return """Eres un experto del Ultimate Frisbee. Necestio que analizando y aplicando tu criterio sobre el contexto proporcionado, porporciones una interpretacion de las reglas del ultimate frisbee.

    
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

    {context}

    """
context = cargar_reglas_desde_archivo_raw('rules_translated_to_spanish.txt')

def combine_chains(inputs):
  """Combina la salida de chain1 como entrada para chain2."""
  play_explanation = inputs #The Result of chain1 is a PlayExplanation object from PydanticOutputParser
  return {"rule": play_explanation.rule, "context": context}



# Crear los prompts
system_message_prompt = SystemMessagePromptTemplate.from_template(rule_detection_prompt())
human_message_prompt = HumanMessagePromptTemplate.from_template("{question}")  # Agrega esto para la pregunta

# Crear el chat prompt.  Aquí, el contexto se incluye en el mensaje del sistema.
chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt]) #El mensaje del usuario va separado
chat_prompt2 = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(rule_interpreter()),
    HumanMessagePromptTemplate.from_template("Necesito tu interpretacion de la regla: {rule}")
])


# Cargar el contexto (reglas)


# Formatear las instrucciones
format_instructions = parser.get_format_instructions()

# Invocar el prompt con los parámetros
chain2 = chat_prompt2 | llm | (lambda x: x.content)

chain1 = chat_prompt | llm | (lambda x: x.content) | parser.parse
combined_chain = chain1 | combine_chains | chain2

try:
    answerObject = chain1.invoke({
        "question": "El juagdor me conto muy rapido, e hcie ell llamado de fast count, como se reinciao el conteo?",
        "context": context,
        "format_instructions": format_instructions
    })
    ##print(answerObject)
     print(answerObject.rule)
     print(answerObject.explanation)
     print(answerObject.short_answer)
except Exception as e:
    print(e)