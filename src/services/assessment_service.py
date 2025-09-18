from backend.src.utils import logging
from backend.src.services.MongoDBHandler import MongoDBHandler
import random
from bson import ObjectId
from backend.src.services.bkt import BayesianKnowledgeTracing
from backend.src.utils import knowledge_info


class AssessmentService:
    def __init__(self):
        self.logger = logging.set_logger(__name__)
        self.db = MongoDBHandler("mongodb://172.16.0.177:27019")
        self.db.connect('amc8_database')
        self.bkt = BayesianKnowledgeTracing(knowledge_info.amc8_concepts)

    async def check_need_assessment(self, student_id: int):
        """Check if student needs to take assessment for new lesson"""
        # Check if student has taken assessment before
        assessments = self.db.find_documents('assessments', {"student_id": student_id})
        if not assessments:
            logging.log(f"Student {student_id} has not taken any assessments. Needs to take assessment.", self.logger, 1)
            return True
        else:
            logging.log(f"Student {student_id} has already taken assessments. No need to take assessment.", self.logger, 1)
            return False

    async def get(self):
        """Give new assessment to user"""
        problems_list = []

        # Select 25 random problems from the database
        logging.log("Fetching assessment problems from database", self.logger, 1)

        for i in range(1,26):
            problems = self.db.find_documents('problems', {"problem_number": i}, ['problem_number', 'problem'])
            problem = random.choice(problems)
            problem['problem_id'] = str(problem['_id'])
            del problem['_id']
            problems_list.append(problem)
        print(problems_list)


        if len(problems_list) != 25:
            logging.log(f"Error: Retrieved {len(problems_list)} problems instead of 25", self.logger, 0)
        else:
            logging.log("Successfully retrieved 25 assessment problems", self.logger, 1)
        
        return problems_list

    async def evaluate_assessment(self, student_answers: dict):
        """Evaluate student's answers and return score for bkt algorithm to update student knowledge graph"""
        student_score = []
        for student_answer in student_answers:
            id = ObjectId(student_answer.get("problem_id"))
            answer = student_answer.get("student_answer")
            problem = self.db.find_documents('problems', {"_id": id}, ['correct_answer', 'solution'])[0]
            if answer.lower() == problem.get('correct_answer').lower():
                student_score.append({"problem_id": str(id), "correct": True, "correct_answer": problem.get('correct_answer'), "solution": problem.get('solution')})
            else:
                student_score.append({"problem_id": str(id), "correct": False, "correct_answer": problem.get('correct_answer'), "solution": problem.get('solution')})

        number_correct = 0
        for i in student_score:
            if i.get("correct"):
                number_correct += 1

        return student_score, number_correct
    
    async def store(self, student_id: int, assessment_score: list):
        """Store the assessment results in the database"""
        assessment_id = str(student_id) + "_" + str(ObjectId())
        try:
            for score in assessment_score:
                await self.db.insert_document('assessments', {
                    "student_id": student_id,
                    "assessment_id": assessment_id,
                    "problem_id": score.get("problem_id"),
                    "student_answer": score.get("student_answer"),
                    "time_spent": score.get("time_spent_seconds"),
                })
            logging.log(f"Stored assessment results for student {student_id}", self.logger, 1)

        except Exception as e:
            logging.log(f"Failed to store assessment results for student {student_id}: {e}", self.logger, 0)

        return assessment_id

    async def retrieve(self, student_id: int):
        """Retrieve past assessment for student"""
        try:
            assessment = self.db.find_documents('assessments', {"student_id": student_id})
            if assessment:
                problems = []
                number_correct = 0
                for entry in assessment:
                    problem_id = entry.get("problem_id")
                    problem_data = self.db.find_documents('problems', {"_id": ObjectId(problem_id)}, ['problem_number', 'problem', 'correct_answer'])[0]
                    problem_entry = {
                        "problem_id": problem_id,
                        "assessment_id": entry.get("assessment_id"),
                        "problem_number": problem_data.get("problem_number"),
                        "problem": problem_data.get("problem"),
                        "student_answer": entry.get("student_answer"),
                        "correct_answer": problem_data.get("correct_answer"),
                        "time_spent": entry.get("time_spent")   
                    }
                    problems.append(problem_entry)
                    if entry.get("student_answer").lower() == problem_data.get("correct_answer").lower():
                        number_correct += 1

                logging.log(f"Retrieved assessment for student {student_id}", self.logger, 1)
                return {
                    "problems": problems,
                    "number_correct": number_correct
                }
            else:
                logging.log(f"No assessment found for student {student_id}", self.logger, 0)
                return {
                    "problems": [],
                    "number_correct": 0
                }
        except Exception as e:
            logging.log(f"Failed to retrieve assessment for student {student_id}: {e}", self.logger, 0)
            return {
                "problems": [],
                "number_correct": 0
            }
    
    async def delete(self, assessment_id: str):
        """Delete assessment from database"""
        try:
            self.db.delete_document('assessments', {"assessment_id": assessment_id}, many=True)
            return True
        
        except:
            return False
        
    async def delete_all(self, student_id: int):
        """Delete all assessments for student"""
        try:
            self.db.delete_document('assessments', {"student_id": student_id}, many=True)
            return True
        
        except:
            return False

    async def update_graph(self, assessment_id: str, user_graph: dict):
        # try: 
        if not user_graph:
            user_graph = knowledge_info.amc8_knowledge_graph

        assessment = self.db.find_documents('assessments', {"assessment_id": assessment_id})

        if not assessment:
            logging.log(f"No assessment found with id {assessment_id}", self.logger, 0)
            return None
        
        # student_id = assessment[0].get("student_id")

        # Logic to update the student's knowledge graph based on assessment results
        for problem in assessment:
            grade = {}
            problem_id = problem.get("problem_id")
            student_answer = problem.get("student_answer")
            problem_data = self.db.find_documents('problems', {"_id": ObjectId(problem_id)}, ['concepts', 'difficulty', 'correct_answer'])[0]
            concepts = problem_data.get('concepts')
            difficulty = problem_data.get('difficulty')
            correct_answer = problem_data.get('correct_answer')

            for concept in concepts:
                grade[concept.lower()] = "correct" if student_answer == correct_answer else "incorrect"
            # Update student knowledge graph with assessment results
            # Using different damping factors based on difficulty
            correct_damping = 0.4 if difficulty == 1 else 0.6 if difficulty == 2 else 0.7 if difficulty == 3 else 0.8 if difficulty == 4 else 0.95
            incorrect_damping = 0.6 if difficulty == 1 else 0.5 if difficulty == 2 else 0.35 if difficulty == 3 else 0.2 if difficulty == 4 else 0.1
            print(f"Grade used for BKT: {grade}\n")
            print(f"Using graph: {user_graph}")
            if student_answer == correct_answer:
                try:
                    user_graph = self.bkt.bkt_algorithm(grade, user_graph, correct_damping)
                except Exception as e:
                    logging.log(f"Failed to update knowledge graph for assessment {assessment_id}: {e}", self.logger, 0)
                    continue
            else:
                try:    
                    user_graph = self.bkt.bkt_algorithm(grade, user_graph, incorrect_damping)
                except Exception as e:
                    logging.log(f"Failed to update knowledge graph for assessment {assessment_id}: {e}", self.logger, 0)
                    continue
        # self.db.insert_document('user_graphs', {"student_id": student_id, "assessment_id": assessment_id, "user_graph": user_graph})
        logging.log(f"Updated knowledge graph for assessment {assessment_id}", self.logger, 1)
        
        return user_graph

        # except Exception as e:
        #     logging.log(f"Failed to update knowledge graph for assessment {assessment_id}: {e}", self.logger, 0)
        #     return {}
            
    # async def retrieve_student_score(self, student_id: int):
    #     """Retrieve the assessment results from the database"""
    #     try:
    #         assessment = self.db.find_documents('assessments', {"student_id": student_id})
    #         if assessment:
    #             logging.log(f"Retrieved assessment results for student {student_id}", self.logger, 1)
    #             return assessment[-1]
    #         else:
    #             logging.log(f"No assessment results found for student {student_id}", self.logger, 0)
    #             return None
    #     except Exception as e:
    #         logging.log(f"Failed to retrieve assessment results for student {student_id}: {e}", self.logger, 0)
    #         return None