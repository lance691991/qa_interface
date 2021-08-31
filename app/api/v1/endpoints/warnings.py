from fastapi import APIRouter, Depends
from typing import Any
from app.api import deps
from app import service

router = APIRouter()

@router.get("/get-warning-logs-by-page", response_model=Any)
def get_list(
        db=Depends(deps.get_es_db),
        current_page: int = 1,
        load_per_page: int = 10
) -> Any:
    logs = service.warning_logs.get_by_page(db=db, current_page=current_page, load_per_page=load_per_page)
    return logs

@router.get("/get-warning-logs-by-today", response_model=Any)
def get_by_today(db=Depends(deps.get_es_db)) -> Any:
    logs = service.warning_logs.get_by_today(db=db)
    return logs

@router.post("/post-warning-probes", response_model=Any)
def post_warning_probes(
        db=Depends(deps.get_es_db),
        data: dict = None
) -> Any:
    return service.warning_logs.add_probes(db=db, data=data)

@router.post("/post-warning-scannings", response_model=Any)
def post_warning_scannings(
        db=Depends(deps.get_es_db),
        data: dict = None
) -> Any:
    return service.warning_logs.add_scannings(db=db, data=data)
