import os
from typing import List, Dict, Union
from pydantic import BaseModel, Field
from utils.text_file_reader import read_raw_text_file
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage, SystemMessage, AIMessage


os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "UltimaAI Agent"
os.environ["GOOGLE_API_KEY"] = "AIzaSyDuz_7HUA9hfzkB6NU0tPEWvYG9uaKpnP8"

class PlayExplanation(BaseModel):
    id: str = Field(description="LEFT this field empty")
    signals: List[str] = Field(description="List of signals (strings) to be used according to its criteria.")
    rule: str = Field(description="El número de la regla relevante (por ejemplo, 2.5). **SIEMPRE DEBES PROPORCIONAR UN NÚMERO DE REGLA. NUNCA dejes este campo vacío. Da tu mejor shot")
    explanation: str = Field(description="EXPLANATION_OF_WHY_THIS_RULE_APPLIES, Una explicación concisa de por qué se aplica esta regla a la pregunta. Explica el razonamiento lo más claramente posible.")
    short_answer: str = Field(description="EG: Yes it applys, Una respuesta corta y concisa a la pregunta basada en la explicación")

class UltimateRulesAssistantSrvc:
    _memories: Dict[str, ConversationBufferMemory] = {}  # Almacenar memorias por ID de usuario

    @classmethod
    def invoke(cls, question: str, identifier: str):
        """Ejecuta el modelo con la pregunta y el contexto."""
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        parser = PydanticOutputParser(pydantic_object=PlayExplanation)
        system_message_prompt = SystemMessagePromptTemplate.from_template(cls.rule_detection_prompt())
        human_message_prompt = HumanMessagePromptTemplate.from_template("Pregunta: {question}")

        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        format_instructions = parser.get_format_instructions()

        memory = cls.get_memory(identifier)

        chain1 = chat_prompt | llm | (lambda x: x.content) | parser.parse
        chat_history = cls._format_chat_history(memory.load_memory_variables({})["history"])

        result = chain1.invoke({
            "question": question,
            "context": cls.load_rules_file('rules_translated_to_spanish.txt'),
            "definitions": cls.load_rules_file('data/definitions_es.txt'),
            "format_instructions": format_instructions,
            "chat_history": chat_history
        })
    
        memory.save_context({"input": question}, {"output": result.explanation})

        return result
    
    @classmethod
    def remove_memory(cls, identifier: str):
        """Remueve la memoria asociada a un ID de usuario."""
        if identifier in cls._memories:
            del cls._memories[identifier]
        else:
            print(f"No se encontró memoria para el usuario: {identifier}")

    @classmethod
    def get_memory(cls, identifier) -> ConversationBufferMemory:
        """Obtiene o crea la memoria para un usuario específico."""
        if identifier not in cls._memories:
            cls._memories[identifier] = ConversationBufferMemory(return_messages=True)
        return cls._memories[identifier]
    
    @staticmethod
    def load_rules_file(rules_file_path):
        return read_raw_text_file(rules_file_path)

    @staticmethod
    def rule_detection_prompt():
        """Genera el prompt para el modelo de lenguaje."""

        
        return """Eres un juez de paz experto en Ultimate Frisbee. Responde a la siguiente pregunta analizando y aplicando tu criterio según el contexto proporcionado (las reglas más recientes del Ultimate Frisbee y sus definiciones). Debes hacer todo lo posible por dar una respuesta, aunque sea aproximada, debes evaluar bien el contexto y por favor, considera la conversación anterior para dar una respuesta coherente y relevante a la pregunta actual.

        Dado el *Mapa de señalizaciones*, debes proveerme la o las señales que apliquen segun la pregunta.

        Historial de la conversación anterior (si existe):
        {chat_history}


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

        Definiciones:
        {definitions}

        Mapa de señalizaciones:
        ```
        image: foul
        explanation: Se usa para indicar que se ha cometido una falta. El lanzador extiende un brazo y golpea el antebrazo del otro brazo, que está extendido.

        image: violation
        explanation: Señala una violación. Ambas manos se colocan sobre la cabeza, formando una forma de 'Y' con los puños cerrados.

        image: goal
        explanation: Se usa para indicar que se ha marcado un gol. Ambos brazos se levantan rectos, con las palmas mirando hacia adentro.

        image: contest
        explanation: Indica una llamada disputada. El lanzador extiende un brazo y golpea el antebrazo del otro brazo, que está extendido.

        image: uncontested
        explanation: Señala que una llamada es aceptada o no disputada. Los antebrazos se extienden hacia adelante, los codos apretados contra el cuerpo, con las palmas hacia arriba.

        image: in_or_out
        explanation: Indica si un jugador o el disco está dentro o fuera de los límites. Un brazo se extiende lateralmente, apuntando hacia adentro o hacia afuera del campo de juego.

        image: retract_accept
        explanation: Se usa cuando alguien se retracta de su llamada o cuando acepta una llamada/decisión. Se realiza un movimiento de barrido con ambos brazos extendidos frente al cuerpo, moviéndose hacia abajo.

        image: down
        explanation: Señala que el disco está en el suelo. Usa el dedo índice para apuntar al suelo.

        image: pick
        explanation: Se usa para indicar una obstrucción (pick). Los brazos se levantan, los codos doblados y los puños apuntando hacia la cabeza.

        image: up
        explanation: Señala que el disco está arriba, o siendo lanzado alto. Codo hacia abajo, antebrazo vertical y dedo índice apuntando arriba.

        image: timeout
        explanation: Indica un tiempo muerto. Forma una forma de 'T' con las manos. Se puede hacer con las dos manos formando la T o solo una con el disco en la otra mano.

        image: marking_infraction
        explanation: Señala una infracción de marcaje. Los brazos se extienden hacia los lados, con las palmas mirando hacia adelante.

        image: turnover
        explanation: Brazo derecho extendido frente al cuerpo, palma hacia arriba y entonces la rotamos hacia abajo.

        image: time_violation
        explanation: Toca tu cabeza repetidamente con la palma abierta de tu mano.

        image: 4_men
        explanation: Manos detras de la cabeza, codos hacia los lados.

        image: out_of_bounds
        explanation: Brazos cruzados y puños cerrados sobre la cabeza formando una X.

        image: spirit_of_the_game
        explanation: Forma una T invertida con las manos.

        image: technical_timeout
        explanation: Manos entrelazadas y brazos levantados sobre la cabeza.

        image: match_point
        explanation: Apunta con ambos brazos hacia arriba, con palmas hacia abajo.

        image: 4_women
        explanation: Brazos extendidos hacia los lados con puños cerrados.

        image: game_stopped
        explanation: Extiende los brazos y mueve los brazos en vaivén, en sentido transversal.

        image: travel
        explanation: Puños cerrados y gira las muñecas en círculo vertical.

        image: who_called_it
        explanation: Apunta con los brazos y manos extendidas.
        ```

        {format_instructions}
        """
    
    @staticmethod
    def _format_chat_history(chat_history: List[Union[HumanMessage, SystemMessage, AIMessage]]) -> str:
        buffer = ""
        for dialogue_turn in chat_history:
            if isinstance(dialogue_turn, HumanMessage):
                buffer += "\nHuman: " + dialogue_turn.content
            elif isinstance(dialogue_turn, AIMessage):
                buffer += "\nAssistant: " + dialogue_turn.content
            elif isinstance(dialogue_turn, SystemMessage):
                buffer += "\nSystem: " + dialogue_turn.content
        return buffer
