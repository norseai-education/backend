from src.services.state import State
from typing import Literal
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from src.utils import logging

# Configure logging
logger = logging.set_logger(__name__)

class QueryClassifier(BaseModel):
    '''structure output of query classifier'''
    classification: Literal["mathematical", "non-mathematical"] = Field(
        ...,
        description="Classify if the input is mathematical or non-mathematical."
    )


class ClassifierModel:
    def __init__(self, model, prompt):
        
        self.model = model
        self.prompt = prompt

        self.output_parser = PydanticOutputParser(pydantic_object=QueryClassifier)

    def build_node(self, state: State):
        logging.log("Going through classifier node...", logger, 2)

        last_student_message = state["messages"][-1]
        
        if len(state["messages"]) < 8:
            class_prompt = self.prompt.format(context= state["messages"], student_input= last_student_message.content)
        else:
            class_prompt = self.prompt.format(context= state["messages"][-8:], student_input= last_student_message.content)

        # Get response 
        response = self.model.invoke(class_prompt) 

        classification = self.output_parser.parse(response.content if hasattr(response, 'content') else str(response))

        logging.log(f"Classification result: --{classification.classification}--", logger, 2)
        logging.log("Classifier node complete", logger, 2)

        return {'classification':classification.classification}
