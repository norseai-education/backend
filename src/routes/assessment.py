from fastapi import APIRouter
from fastapi import status

from backend.src.models.requests import AssessmentRequest
from backend.src.models.responses import AssessmentResponse
from backend.src.services.assessment_service import AssessmentService

router = APIRouter()
assessment_service = AssessmentService()


@router.post("/assessment/{student_id}", response_model = AssessmentResponse)
async def give_assessment(student_id: int):
    """give assessment test to new student"""
    problems_dict = await assessment_service.get_assessment()

    return AssessmentResponse(problems=problems_dict, student_id=student_id)

@router.post("/assessment_check/{student_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def assessment_check(student_id: int, request: AssessmentRequest):
    """check assessment answers and update student knowledge graph"""
    list_of_score = await assessment_service.evaluate_assessment(request.student_answers)
    await assessment_service.store_student_score(student_id, list_of_score)
    
