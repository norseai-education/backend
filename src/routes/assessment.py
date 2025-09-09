from fastapi import APIRouter
from fastapi import status

import time

from backend.src.models.requests import AssessmentRequest, UserGraphRequest
from backend.src.models.responses import GiveAssessmentResponse, AssessmentResultResponse, AssessmentStoreResponse, UserGraphResponse, RouteResponse
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
    problems_list = await assessment_service.get_assessment()

    return GiveAssessmentResponse(problems=problems_list, number_problems=len(problems_list), start_time=time.time())

@router.post("/submit", response_model = AssessmentResultResponse)
async def assessment_check(request: AssessmentRequest):
    """check assessment answers and return solutions"""
    result, number_correct = await assessment_service.evaluate_assessment(request.student_answers)
    
    return AssessmentResultResponse(solutions=result, total_correct=number_correct, duration_seconds=time.time() - request.start_time)

@router.post("/store_results/{student_id}/", response_model = AssessmentStoreResponse)
async def assessment_store(student_id: int, request: AssessmentRequest):
    id = await assessment_service.store_student_score(student_id, request.student_answers)

    return AssessmentStoreResponse(assessment_id=str(id))

@router.post("/update_knowledge/{assessment_id}/", response_model=UserGraphResponse)
async def update_knowledge_graph(assessment_id: str, request: UserGraphRequest):
    """Update student knowledge graph based on assessment results"""
    updated_graph = await assessment_service.update_graph(assessment_id, request.user_graph)

    return UserGraphResponse(user_graph=updated_graph)
    
