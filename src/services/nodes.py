from backend.src.services.state import State
from backend.src.services.query_classifier import ClassifierModel
from backend.src.services.evaluator import EvaluatorModel
import backend.src.services.prompts as prompts
import backend.src.services.models as models
import backend.src.services.ChromaDBHandler as ChromaDBHandler
import backend.src.services.MongoDBHandler as MongoDBHandler
import backend.src.services.tools as tools
from backend.src.services.bkt import BayesianKnowledgeTracing
from backend.src.utils import knowledge_info
from backend.src.services.personality_rag import PersonalityRAG
from backend.src.services.math_rag import MathRAG
from backend.src.services.teacher_math import MathTeacher
from backend.src.services.teacher import Teacher

class Nodes:
    def __init__(self):

        self.classifier = ClassifierModel(
        models.classifier_model,
        prompts.classification_prompt,
        )

        self.evaluator = EvaluatorModel(
        models.evaluator_model,
        prompts.evaluator_prompt,
        [tools.get_math_context_structured, tools.math_engine])

        self.bkt = BayesianKnowledgeTracing(knowledge_info.amc8_concepts)

        self.math_rag = MathRAG(
        ChromaDBHandler.MathRagDB(models.embedding_model))

        self.personality_rag = PersonalityRAG(
        ChromaDBHandler.PersonaDB(models.embedding_model))

        self.math_teacher = MathTeacher(
        models.teacher_model,
        prompts.MathTeacherPrompt(),
        MongoDBHandler.MongoDBHandler("mongodb://172.16.0.177:27019"),
        [tools.get_archived_structured, tools.get_problem_structured]
        )

        self.teacher = Teacher(
        models.teacher_model,
        prompts.TeacherPrompt(),
        MongoDBHandler.MongoDBHandler("mongodb://172.16.0.177:27019"),
        [tools.get_archived_structured, tools.get_problem_structured]
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



