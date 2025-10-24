from src.services.state import State
from src.services.query_classifier import ClassifierModel
from src.services.evaluator import EvaluatorModel
import src.services.prompts as prompts
import src.services.models as models
import src.services.rag_service as rag_service
import src.services.MongoDBHandler as MongoDBHandler
import src.services.tools as tools
from src.services.bkt import BayesianKnowledgeTracing
from src.utils import knowledge_info
from src.services.personality_rag import PersonalityRAG
from src.services.math_rag import MathRAG
from src.services.teacher_math import MathTeacher
from src.services.teacher import Teacher

class Nodes:
    def __init__(self):

        self.classifier = ClassifierModel(
        models.classifier_model,
        prompts.classification_prompt,
        )

        self.evaluator = EvaluatorModel(
        models.evaluator_model,
        prompts.evaluator_prompt,
        [tools.get_math_context, tools.math_engine, tools.check_concepts])

        self.bkt = BayesianKnowledgeTracing(knowledge_info.amc8_concepts)

        self.math_rag = MathRAG(
        rag_service.MathRagDB())

        self.personality_rag = PersonalityRAG(
        rag_service.PersonaDB())

        self.math_teacher = MathTeacher(
        models.teacher_model,
        prompts.MathTeacherPrompt(),
        MongoDBHandler.MongoDBHandler("mongodb://172.16.0.177:27019"),
        [tools.get_archived, tools.get_problem]
        )

        self.teacher = Teacher(
        models.teacher_model,
        prompts.TeacherPrompt(),
        MongoDBHandler.MongoDBHandler("mongodb://172.16.0.177:27019"),
        [tools.get_archived, tools.get_problem]
        )


    def classifier_node(self, state):
        return self.classifier.build_node(state)

    def evaluator_node(self, state):
        return self.evaluator.build_node(state)

    def bkt_node(self, state):
        return self.bkt.build_node(state)

    def math_rag_node(self, state):
        return self.math_rag.build_node(state)

    def personality_rag_node(self, state):
        return self.personality_rag.build_node(state)

    def math_teacher_node(self, state):
        return self.math_teacher.build_node(state)

    def teacher_node(self, state):
        return self.teacher.build_node(state)



