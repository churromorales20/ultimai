import os
from typing import List, Dict, Union
from pydantic import BaseModel, Field
from utils.text_file_reader import read_raw_text_file
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage, SystemMessage, AIMessage

class PlayExplanation(BaseModel):
    id: str = Field(
        description="**Leave this field empty.** The system will generate the ID automatically."
    )
    signals: List[str] = Field(
        description="**List of applicable signals.** Each signal must be taken from the provided Signaling Map and must match the analyzed situation."
    )
    rule: str = Field(
        description="**Number of the relevant rule (e.g., '2.5').** You MUST ALWAYS PROVIDE a valid rule number that justifies the decision. Never leave this blank."
    )
    explanation: str = Field(
        description="**Detailed reasoning.** Clearly explain step by step WHY this rule applies to the situation, citing any observations or context used."
    )
    short_answer: str = Field(
        description="**Concise final answer.** Summarize your judgment in a clear, short sentence (e.g., 'Yes, it applies.' or 'No, not applicable.')"
    )

class UltimateRulesAssistantSrvc:
    _memories: Dict[str, ConversationBufferMemory] = {}  # Almacenar memorias por ID de usuario

    @classmethod
    def invoke(cls, question: str, identifier: str, lang: str):
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

        parser = PydanticOutputParser(pydantic_object=PlayExplanation)

        system_message_prompt = SystemMessagePromptTemplate.from_template(cls._rule_detection_prompt(lang))
        human_message_prompt = HumanMessagePromptTemplate.from_template("Pregunta: {question}")

        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        format_instructions = parser.get_format_instructions()

        memory = cls._get_memory(identifier)

        chain1 = chat_prompt | llm | (lambda x: x.content) | parser.parse

        chat_history = cls._format_chat_history(memory.load_memory_variables({})["history"])

        result = chain1.invoke({
            "question": question,
            "rulebook_excerpt": cls._load_rules(),
            "signaling_map_data": cls._load_signaling_map(),
            "format_instructions": format_instructions,
            "chat_history": chat_history
        })
    
        memory.save_context({"input": question}, {"output": result.explanation})

        return result
    
    @classmethod
    def remove_memory(cls, identifier: str):
        if identifier in cls._memories:
            del cls._memories[identifier]
        else:
            print(f"No memory found for the user: {identifier}")

    @classmethod
    def _get_memory(cls, identifier) -> ConversationBufferMemory:
        if identifier not in cls._memories:
            cls._memories[identifier] = ConversationBufferMemory(return_messages=True)
        return cls._memories[identifier]
    
    @staticmethod
    def _load_rules():
        return f"""
        {read_raw_text_file(f'data/introduction_en.txt')}
        
        {read_raw_text_file(f'data/rules_en.txt')}
        
        {read_raw_text_file(f'data/definitions_en.txt')}
        """
    
    @staticmethod
    def _load_signaling_map():
        return f"""
        {read_raw_text_file(f'data/signals_map_en.txt')}
        """
    
    @staticmethod
    def load_rules_file(rules_file_path):
        return read_raw_text_file(rules_file_path)

    @staticmethod
    def _rule_detection_prompt(lang):
        return read_raw_text_file(f'data/main_prompt_en.txt')
    
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
