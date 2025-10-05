from src.services.state import State
from src.utils import logging

# Configure logging
logger = logging.set_logger(__name__)

class MathRAG:
    def __init__(self, database):
        self.math_rag = database
    
    def get_rag(self, student_input):
        return self.math_rag.retrieve(student_input, n_results=1)
    
    def build_node(self, state: State):
        logging.log(f"Current state: \n{state}", logger, 2)
        logging.log(f"Going through math_rag node...", logger, 2)
        student_input = state["messages"][-1].content
        # logging.log(f"Student input: {student_input}", logger, 2)
        rag = self.get_rag(str(student_input))
        logging.log(f"Math rag result: {rag}", logger, 2)
        return {"math_context" : rag}