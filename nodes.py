from state import State
from query_classifier import ClassifierModel
from evaluator import EvaluatorModel
import prompts
import models
import database
import tools
from bkt import BayesianKnowledgeTracing
from utils import concepts
from personality_rag import PersonalityRAG
from math_rag import MathRAG
from teacher_math import MathTeacher
from teacher import Teacher

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

        self.bkt = BayesianKnowledgeTracing(concepts)

        self.math_rag = MathRAG(
        database.MathRagDB(models.embedding_model))

        self.personality_rag = PersonalityRAG(
        database.PersonaDB(models.embedding_model))

        self.math_teacher = MathTeacher(
        models.teacher_model,
        prompts.MathTeacherPrompt(),
        database.MongoDBHandler("mongodb://172.16.0.177:27019"),
        [tools.get_archived_structured, tools.get_problem_structured]
        )

        self.teacher = Teacher(
        models.teacher_model,
        prompts.TeacherPrompt(),
        database.MongoDBHandler("mongodb://172.16.0.177:27019"),
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



