from backend.src.services.state import State
from backend.src.utils import logging

# Configure logging
logger = logging.set_logger(__name__)

class MathRAG:
    def __init__(self, database):
        self.math_rag = database
        self.math_rag_client = self.math_rag.connect_to_db()
        self.math_rag_collection = self.math_rag.get_collection(self.math_rag_client, "AMC8_math")
    
    def get_rag(self, student_input):
        return self.math_rag.retrieve(self.math_rag_collection, student_input, 1)
    
    def build_node(self, state: State):
        logging.log(f"Current state: \n{state}", logger, 2)
        logging.log(f"Going through math_rag node...", logger, 2)
        student_input = state["messages"][-1].content
        rag = self.get_rag(student_input)
        logging.log(f"Math rag result: {rag}", logger, 2)
        return {"math_context" : rag}