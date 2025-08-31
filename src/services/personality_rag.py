from backend.src.services.state import State
from backend.src.utils import logging

# Configure logging
logger = logging.set_logger(__name__)

class PersonalityRAG:
    def __init__(self, persona_db):
        self.persona_db = persona_db
        self.client = self.persona_db.connect_to_db()
        self.collection = self.persona_db.get_collection(self.client, "persona_db")

    def build_node(self, state: State):
        logging.log(f"Current State {state}", logger, 2)
        logging.log("Going through personality_rag node...", logger, 2)
        student_input = state["messages"][-1].content
        # Retrieve context from the persona database
        rag = self.persona_db.retrieve(self.collection, student_input, n_results=1, metadata_filter={"student_id": state["student_id"]})
        logging.log(f"personality rag result: {rag}", logger, 2)
        return {"personality_context": rag}
    
