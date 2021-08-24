from fastapi import APIRouter, Depends
from typing import Any
from app.api import deps
from app import service

router = APIRouter()

@router.get("/get-list", response_model=Any)
def get_list(
        db=Depends(deps.get_es_db),
        current_page: int = 1,
        load_per_page: int = 10
) -> Any:
    logs = service.warning_logs.get_by_page(db=db, current_page=current_page, load_per_page=load_per_page)
    return logs
