from fastapi import APIRouter, Body, Depends, HTTPException
from app import service, models, schemas

router = APIRouter()

@router.post("/query/question")
def get_answer(query: schemas.QueryBase):
    query_input = query.query
    return service.qa_system.query(query_input)