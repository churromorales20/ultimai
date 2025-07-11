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
    def invoke(cls, question: str, identifier: str, lang: str):
        """Ejecuta el modelo con la pregunta y el contexto."""
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        parser = PydanticOutputParser(pydantic_object=PlayExplanation)
        system_message_prompt = SystemMessagePromptTemplate.from_template(cls.rule_detection_prompt(lang))
        human_message_prompt = HumanMessagePromptTemplate.from_template("Pregunta: {question}")

        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        format_instructions = parser.get_format_instructions()

        memory = cls.get_memory(identifier)

        chain1 = chat_prompt | llm | (lambda x: x.content) | parser.parse
        chat_history = cls._format_chat_history(memory.load_memory_variables({})["history"])

        result = chain1.invoke({
            "question": question,
            "context": cls.load_context(lang),
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
    def load_context(lang):
        return f"""
        {read_raw_text_file(f'data/introduction_{lang}.txt')}
        
        {read_raw_text_file(f'data/rules_{lang}.txt')}
        
        {read_raw_text_file(f'data/definitions_{lang}.txt')}
        """
    
    @staticmethod
    def load_rules_file(rules_file_path):
        return read_raw_text_file(rules_file_path)

    @staticmethod
    def rule_detection_prompt(lang):
        return read_raw_text_file(f'data/main_prompt_{lang}.txt')
    
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
