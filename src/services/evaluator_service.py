from src.services.MongoDBHandler import MongoDBHandler
from src.utils import logging

logger = logging.set_logger(__name__)

class EvaluatorService:
    def __init__(self):
        self.db = MongoDBHandler()
        self.db.connect('amc8_database')

    async def store_evaluation(self, evaluation: str, grade: dict, student_id: int, student_grade: dict, student_evaluation: str) -> dict:
        """Store the evaluation in the database"""
        try:
            await self.db.insert_document('evaluations', {
                "student_id": student_id,
                "evaluation": evaluation,
                "grade": grade,
                "student_grade": student_grade,
                "student_evaluation": student_evaluation
            })

            return {"message": "Evaluation stored successfully"}

        except Exception as e:
            return {"message": "Failed to store evaluation: " + str(e)}