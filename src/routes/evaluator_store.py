from fastapi import APIRouter, Depends
from fastapi import status
from src.models.requests import StoreEvaluationRequest
from src.models.responses import MessageResponse, EvaluationsResponse
from src.services.evaluator_service import EvaluatorService

router = APIRouter()
evaluator_service = EvaluatorService()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@router.post("/store_evaluation", response_model=MessageResponse)
async def store_evaluation(request: StoreEvaluationRequest):
    store_response = await evaluator_service.store_evaluation(request.evaluation, request.grade, request.student_id, request.student_grade, request.student_evaluation)
    return MessageResponse(message=store_response['message'])

@router.get("/get_evaluations/{student_id}", response_model=EvaluationsResponse)
async def get_evaluations(student_id: int):
    evaluations = await evaluator_service.get_evaluations(student_id)
    return EvaluationsResponse(evaluations=evaluations)