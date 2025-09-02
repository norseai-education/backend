from backend.src.utils import logging
from backend.src.services.MongoDBHandler import MongoDBHandler
import random

class AssessmentService:
    def __init__(self):
        self.logger = logging.set_logger(__name__)
        self.db = MongoDBHandler("mongodb://172.16.0.177:27019")
        self.db.connect('amc8_database')
        self.problems = {}

    async def get_assessment(self):
        """Retrieve assessment problems from the database"""

        # Select 25 random problems from the database
        for i in range(1,26):
            problems = self.db.find_documents('problems', {"problem_numer": i}, ['difficulty', 'concepts', 'problem', 'answer'])
            index = random.randint(0,len(problems)-1)
            problem = problems[index]
            self.problems[problem.get("_id")] = problem

        # return only the problem text for displaying the assessment
        assessment_problems = {}
        for key,value in self.problems.items():
            assessment_problems[key] = value.get("problem")

        return assessment_problems

    async def evaluate_assessment(self, student_answers: dict):
        """Evaluate student's answers and return score for bkt algorithm to update student knowledge graph"""
        student_score = []
        for problem_id, student_answer in student_answers.items():
            if self.problems[problem_id].get("answer") == student_answer:
                student_score.append({"concepts": self.problems[problem_id].get("concepts"), "difficulty": self.problems[problem_id].get("difficulty"), "correct": True})
            else:
                student_score.append({"concepts": self.problems[problem_id].get("concepts"), "difficulty": self.problems[problem_id].get("difficulty"), "correct": False})

        return student_score
    
    async def store_student_score(self, student_id: int, assessment_score: list):
        """Store the assessment results in the database"""
        try:
            assessment_record = {
            "student_id": student_id,
            "answers": assessment_score
            }

            self.db.insert_document('assessments', assessment_record)
            logging.log(f"Stored assessment results for student {student_id}", self.logger, 1)
        except Exception as e:
            logging.log(f"Failed to store assessment results for student {student_id}: {e}", self.logger, 0)

    async def retrieve_student_score(self, student_id: int):
        """Retrieve the assessment results from the database"""
        try:
            assessment = self.db.find_documents('assessments', {"student_id": student_id})
            if assessment:
                logging.log(f"Retrieved assessment results for student {student_id}", self.logger, 1)
                return assessment[-1]
            else:
                logging.log(f"No assessment results found for student {student_id}", self.logger, 0)
                return None
        except Exception as e:
            logging.log(f"Failed to retrieve assessment results for student {student_id}: {e}", self.logger, 0)
            return None