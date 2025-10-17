from src.services.MongoDBHandler import MongoDBHandler
from bson import ObjectId

class ProblemHandler:
    def __init__(self):
        self.db_handler = MongoDBHandler()
        self.db_handler.connect("amc8_database")

    def get_problem(self, problem_id: str):
        # Validate problem_id before creating ObjectId
        if not problem_id or not problem_id.strip():
            return ""
        
        try:
            problem = self.db_handler.find_documents("problems", {"_id": ObjectId(problem_id)}, ["display_problem"])
            return problem.get("display_problem", "")
        except Exception as e:
            # Handle ObjectId validation errors gracefully
            return ""

    def delete_problem(self, problem_id: str):
        self.db_handler.delete_document("problems", {"_id": ObjectId(problem_id)})

    def update_problem(self, problem_id: str, problem: str, display: bool):
        if display:
            self.db_handler.update_document("problems", {"_id": ObjectId(problem_id)}, {"display_problem": problem})
        else:
            self.db_handler.update_document("problems", {"_id": ObjectId(problem_id)}, {"problem": problem})

    def update_solution(self, problem_id: str, solution: str, display: bool):
        if display:
            self.db_handler.update_document("problems", {"_id": ObjectId(problem_id)}, {"display_solution": solution})
        else:
            self.db_handler.update_document("problems", {"_id": ObjectId(problem_id)}, {"solution": solution})

    def update_correct_answer(self, problem_id: str, correct_answer: str):
        self.db_handler.update_document("problems", {"_id": ObjectId(problem_id)}, {"correct_answer": correct_answer})

    def update_concepts(self, problem_id: str, concepts: list):
        self.db_handler.update_document("problems", {"_id": ObjectId(problem_id)}, {"concepts": concepts})

    def update_difficulty(self, problem_id: str, difficulty: int):
        self.db_handler.update_document("problems", {"_id": ObjectId(problem_id)}, {"difficulty": difficulty})