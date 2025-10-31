from src.services.MongoDBHandler import MongoDBHandler
from src.utils import logging
from bson import ObjectId
from typing import Any

logger = logging.set_logger(__name__)

class EvaluatorService:
    def __init__(self):
        self.db = MongoDBHandler()
        self.db.connect('amc8_database')

    async def store_evaluation(self, evaluation: str, grade: dict, student_id: int) -> dict:
        """Store the evaluation in the database"""
        try:
            insert_id = await self.db.insert_document('evaluations', {
                "student_id": str(student_id),
                "evaluation": evaluation,
                "grade": grade,
                "student_grade": {},
                "student_evaluation": ''
            })

            return {"message": str(insert_id)}

        except Exception as e:
            return {"message": "Failed to store evaluation: " + str(e)}

    async def update_evaluation(self, object_id: str, student_grade: dict, student_evaluation: str) -> dict:
        """Update the evaluation in the database"""
        try:
            update = self.db.update_document('evaluations', {"_id": ObjectId(object_id)}, {"student_grade": student_grade, "student_evaluation": student_evaluation})
            return {"message": "Evaluation updated successfully"}
        except Exception as e:
            return {"message": "Failed to update evaluation: " + str(e)}

    async def get_evaluations(self, student_id: int) -> list[dict[Any, Any]]:
        """Get the evaluations for a student"""
        try:
            evaluations = self.db.find_documents('evaluations', {"student_id": str(student_id)})
            for eval in evaluations:
                del eval['_id']
            return evaluations
        except Exception as e:
            return [{"message": "Failed to get evaluations: " + str(e)}]