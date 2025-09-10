from fastapi import APIRouter
from fastapi import status

import time

from backend.src.models.requests import AssessmentStoreRequest, AssessmentSubmitRequest, UserGraphRequest
from backend.src.models.responses import GiveAssessmentResponse, AssessmentResultResponse, AssessmentStoreResponse, UserGraphResponse, RouteResponse, AssessmentRetrieveResponse, MessageResponse
from backend.src.services.assessment_service import AssessmentService

router = APIRouter()
assessment_service = AssessmentService()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@router.post("/check/{student_id}", response_model=RouteResponse)
async def route_student(student_id: int):
    """Check if need to give assessment to new lesson or if assessment already done"""
    route = await assessment_service.check_need_assessment(student_id)
    if route: 
        return RouteResponse(give_assessment=True)
    else:
        return RouteResponse(give_assessment=False)

@router.get("/give_assessment", response_model = GiveAssessmentResponse)
async def give_assessment():
    """give assessment test to new student"""
    problems_list = await assessment_service.get()

    return GiveAssessmentResponse(problems=problems_list, number_problems=len(problems_list))

@router.post("/submit", response_model = AssessmentResultResponse)
async def assessment_check(request: AssessmentSubmitRequest):
    """check assessment answers and return solutions"""
    result, number_correct = await assessment_service.evaluate_assessment(request.student_answers)
    
    return AssessmentResultResponse(solutions=result, total_correct=number_correct)

@router.get("/retrieve_assessment/{student_id}", response_model = AssessmentRetrieveResponse)
async def retrieve_assessment(student_id: int):
    """Retrieve past assessment for student"""
    assessment = await assessment_service.retrieve(student_id)

    return AssessmentRetrieveResponse(problems=assessment.get("problems"), number_problems=len(assessment.get("problems")), number_correct=assessment.get("number_correct"))


@router.post("/store_assessment/{student_id}", response_model = AssessmentStoreResponse)
async def assessment_store(student_id: int, request: AssessmentStoreRequest):
    id = await assessment_service.store(student_id, request.student_answers)

    return AssessmentStoreResponse(assessment_id=str(id))

@router.post("/update_knowledge/{assessment_id}", response_model=UserGraphResponse)
async def update_knowledge_graph(assessment_id: str, request: UserGraphRequest):
    """Update student knowledge graph based on assessment results"""
    updated_graph = await assessment_service.update_graph(assessment_id, request.user_graph)

    return UserGraphResponse(user_graph=updated_graph)
    
@router.delete("/delete_assessment/{assessment_id}", response_model=MessageResponse)
async def delete_assessment(assessment_id: str):
    """Delete assessment from database"""
    result = await assessment_service.delete(assessment_id)

    if result:
        return MessageResponse(message=f"Successfully deleted assessment {assessment_id}")
    else:
        return MessageResponse(message=f"Failed to delete assessment {assessment_id}")
    
@router.delete("/delete_all/{student_id}", response_model=MessageResponse)
async def delete_all(student_id: int):
    """Delete all assessments corresponding to student id"""
    result = await assessment_service.delete_all(student_id)

    if result:
        return MessageResponse(message=f"Successfully deleted all assessments for {student_id}")
    else:
        return MessageResponse(message=f"Failed to delete assessments for {student_id}")