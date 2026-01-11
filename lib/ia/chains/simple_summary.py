from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..core.llm import llm

def create_simple_summary_chain():
    prompt = ChatPromptTemplate.from_template(
        "Summarize the following text in a concise way:\n\n{text}"
    )
    return prompt | llm | StrOutputParser()

simple_summary = create_simple_summary_chain()
