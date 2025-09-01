from fastapi import APIRouter, HTTPException

from backend.src.models.requests import AssessmentRequest
from backend.src.models.responses import AssessmentResponse
from backend.src.services.assessment_service import AssessmentService
from backend.src.services.bkt import BayesianKnowledgeTracing
from backend.src.utils import knowledge_info

router = APIRouter()
assessment_service = AssessmentService()
bkt = BayesianKnowledgeTracing(knowledge_info.amc8_concepts)

@router.post("/assessment/{student_id}", response_model=AssessmentResponse)
async def give_assessment(student_id: int):
    """give assessment test to new student"""
    problems_dict = await assessment_service.get_assessment()
    return AssessmentResponse(problems=problems_dict, student_id=student_id)

@router.post("/assessment_check/{student_id}/", response_model=AssessmentResponse)
async def assessment_check(student_id: int, request: AssessmentRequest):
    """check assessment answers and update student knowledge graph"""
    list_of_score = await assessment_service.evaluate_assessment(request.student_answers)
    
    for score in list_of_score:
        concepts = score.get("concepts")
        difficulty = score.get("difficulty")
        score = score.get("correct")
        if score == True:
            # update student knowledge graph with correct answer
            pass
        else:
            # update student knowledge graph with wrong answer
            pass

    # Save the updated knowledge graph to MongoDB
    
